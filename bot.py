import asyncio
import logging
import os
import re
from dotenv import load_dotenv
from typing import Dict, Any

from telebot.async_telebot import AsyncTeleBot
from telebot.types import InputMediaPhoto

from flight_service import FlightService
from image_utils import create_graph, create_map
from formatting import format_flight_details, format_flight_details_location

logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN not set")

bot = AsyncTeleBot(TOKEN)
service = FlightService()


@bot.message_handler(func=lambda message: True, content_types=["text"])
async def handle_message(message):
    flight_num = message.text
    reply_message = await bot.reply_to(message, "Flight number received. Searching...")

    flight_tracker = service.search(flight_num)
    try:
        if "live" in flight_tracker and flight_tracker["live"]:
            registration_number = flight_tracker["live"][0]["detail"]["reg"]
            current_flight = None
            flight_details = None
            for current_flight in service.get_flights(registration=registration_number, details=True):
                flight_details = service.get_flight_details(current_flight)
                current_flight.set_flight_details(flight_details)
            if current_flight and flight_details:
                await send_flight_information(message.chat.id, flight_details, registration_number, current_flight)
        else:
            raise ValueError("Flight information not found.")
    except Exception as e:
        await bot.send_message(chat_id=message.chat.id, text=str(e))
    finally:
        await bot.delete_message(chat_id=message.chat.id, message_id=reply_message.message_id)


@bot.message_handler(content_types=["location"])
async def handle_location(message):
    latitude = message.location.latitude
    longitude = message.location.longitude

    reply_message = await bot.reply_to(message, "Geolocation received. Processing flight data...")

    bounds = service.get_bounds_by_point(latitude, longitude, 25000)
    data = service.get_flights(bounds=bounds)

    registration_numbers_dict: Dict[str, str] = {}
    for item in data:
        registration_numbers = re.findall(r"\((\w+)\)\s*([\w-]+)\s*-", str(item))
        if registration_numbers:
            for match in registration_numbers:
                aircraft_type, reg_number = match
                registration_numbers_dict[reg_number] = aircraft_type

    unique_registration_numbers = list(registration_numbers_dict.keys())

    flight_info = "<b>Aircrafts near you (25 km):</b>\n\n"
    airport = service.get_airport("ULLI")

    count = 1
    for registration_number in unique_registration_numbers:
        for current_flight in service.get_flights(registration=registration_number, details=True):
            flight_details = service.get_flight_details(current_flight)
            current_flight.set_flight_details(flight_details)
            airport.latitude = latitude
            airport.longitude = longitude
            distance = current_flight.get_distance_from(airport)
            rounded_distance = round(distance * 1000)
            flight_info += (
                f"{count}) {format_flight_details_location(flight_details)}   Distance from you: {rounded_distance} m\n\n"
            )
            count += 1

    await bot.send_message(message.chat.id, flight_info, parse_mode="HTML")
    await bot.delete_message(chat_id=message.chat.id, message_id=reply_message.message_id)


async def send_flight_information(chat_id, flight_details, registration_number, current_flight):
    flight_info = format_flight_details(flight_details, registration_number, current_flight, service)
    photo_url = flight_details["aircraft"]["images"]["medium"][0]["link"]
    map_photo_path = create_map(flight_details, current_flight)
    graph_path = create_graph(flight_details)

    media = []
    if photo_url:
        media.append(InputMediaPhoto(media=photo_url, caption=f"Aircraft Photo: {registration_number}"))
    media.extend([
        InputMediaPhoto(media=open(map_photo_path, "rb"), caption="Flight Path Map"),
        InputMediaPhoto(media=open(graph_path, "rb"), caption="Flight Graph"),
    ])
    await bot.send_media_group(chat_id, media)
    await bot.send_message(chat_id, flight_info, parse_mode="HTML")


async def run_bot():
    logger.info("Starting bot")
    await bot.polling(none_stop=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_bot())

import io
import re
from datetime import datetime, timezone

import folium
import matplotlib.pyplot as plt
import telebot
from PIL import Image
from flightradar24 import FlightRadar24API
from telebot.types import InputMediaPhoto

# Initialize the bot with your token
bot = telebot.TeleBot("6895152225:AAGQPO22tS6EjY0eCWz1qLsk_rpKQ2rCDVc")

# Initialize Flightradar24 API
fr_api = FlightRadar24API()


class Flight:
    def __init__(self, registration, altitude, ground_speed, heading):
        self.registration = registration
        self.altitude = altitude
        self.ground_speed = ground_speed
        self.heading = heading

    def get_flight_level(self):
        # Implement your logic for getting flight level
        pass

    def get_vertical_speed(self):
        # Implement your logic for getting vertical speed
        pass


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    global flight_details_res, current_flight_res

    try:
        flight_num = message.text

        reply_message = bot.reply_to(message, "Flight number received. Searching...")

        # Get flight data
        flight_tracker = fr_api.search(flight_num)

        if 'live' in flight_tracker and flight_tracker['live']:
            registration_number = flight_tracker['live'][0]['detail']['reg']

            for current_flight_res in fr_api.get_flights(registration=registration_number, details=True):
                flight_details_res = fr_api.get_flight_details(current_flight_res)
                current_flight_res.set_flight_details(flight_details_res)

            # Send information to the user
            send_flight_information(message.chat.id, flight_details_res, registration_number, current_flight_res)

            bot.delete_message(chat_id=message.chat.id, message_id=reply_message.message_id)

        else:
            bot.delete_message(chat_id=message.chat.id, message_id=reply_message.message_id)
            bot.reply_to(message, "Flight information not found.", parse_mode='HTML')

    except Exception as e:
        # Обработка общих исключений
        print(f"An error occurred: {str(e)}")
        bot.reply_to(message, "An error occurred while processing your request.", parse_mode='HTML')


@bot.message_handler(content_types=['location'])
def handle_location(message):
    # Получаем данные о местоположении пользователя
    latitude = message.location.latitude
    longitude = message.location.longitude

    # Отправляем ответ пользователю
    reply_message = bot.reply_to(message, "Geolocation received. Processing flight data...")

    # Используем полученные координаты
    bounds = fr_api.get_bounds_by_point(latitude, longitude, 25000)
    data = fr_api.get_flights(bounds=bounds)

    registration_numbers_dict = {}

    for item in data:
        # Извлекаем регистрационные номера
        registration_numbers = re.findall(r'\((\w+)\)\s*([\w-]+)\s*-', str(item))

        # Исключаем случаи, когда не удалось извлечь регистрационные номера
        if registration_numbers:
            for match in registration_numbers:
                aircraft_type, reg_number = match
                # Сохраняем регистрационные номера в словаре
                registration_numbers_dict[reg_number] = aircraft_type

    # Преобразуем словарь в список
    unique_registration_numbers = list(registration_numbers_dict.keys())

    flight_info = "<b>Aircrafts near you:</b>\n\n"

    count = 1

    for registration_number in unique_registration_numbers:
        # Получаем данные о рейсе для текущего регистрационного номера
        for current_flight_res_1 in fr_api.get_flights(registration=registration_number, details=True):
            flight_details_res_1 = fr_api.get_flight_details(current_flight_res_1)
            current_flight_res_1.set_flight_details(flight_details_res_1)

            # Добавьте здесь дополнительные действия или вызов функций, если необходимо

            # Send information to the user
            flight_info += f"{count}) {format_flight_details_location(flight_details_res_1)}\n"
            count += 1

    bot.send_message(message.chat.id, flight_info, parse_mode='HTML')
    # Далее вы можете продолжить выполнение вашего кода с использованием полученных данных о рейсах
    # Например, вызвать функцию send_flight_information с новыми данными

    # Удаляем сообщение о геолокации после обработки
    bot.delete_message(chat_id=message.chat.id, message_id=reply_message.message_id)


def send_flight_information(chat_id, flight_details, registration_number, current_flight):
    # Format flight information
    flight_info = format_flight_details(flight_details, registration_number, current_flight)

    # Get the URL of the aircraft photo
    photo_url = flight_details['aircraft']['images']['medium'][0]['link']

    creating_map(flight_details)
    creating_graph(flight_details)

    map_photo_path = 'image.png'
    graph_path = 'graph.png'

    if photo_url is not None:
        media = [
            InputMediaPhoto(media=photo_url, caption=f'Aircraft Photo: {registration_number}'),
            InputMediaPhoto(media=open(map_photo_path, 'rb'), caption='Flight Path Map'),
            InputMediaPhoto(media=open(graph_path, 'rb'), caption='Flight Graph'),
        ]
        bot.send_media_group(chat_id, media)
    else:
        media = [
            InputMediaPhoto(media=open(map_photo_path, 'rb'), caption='Flight Path Map'),
            InputMediaPhoto(media=open(graph_path, 'rb'), caption='Flight Graph'),
        ]
        bot.send_media_group(chat_id, media)

    bot.send_message(chat_id, flight_info, parse_mode='HTML')


def creating_graph(flight_details):
    # Extract data from flight_details
    try:
        timestamps = [datetime.fromtimestamp(point['ts']).strftime('%Y-%m-%d %H:%M:%S')
                      for point in flight_details['trail']][::-1]
        speeds = [point['spd'] for point in flight_details['trail']][::-1]
        altitudes = [point['alt'] for point in flight_details['trail']][::-1]

        # Plot the graph
        fig, ax1 = plt.subplots()

        color = 'tab:red'
        ax1.set_ylabel('Speed (spd)', color=color)
        ax1.plot(timestamps, speeds, color=color)
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.set_xticks([])  # Hide x-axis ticks

        ax2 = ax1.twinx()
        color = 'tab:blue'
        ax2.set_ylabel('Altitude (alt)', color=color)
        ax2.plot(timestamps, altitudes, color=color)
        ax2.tick_params(axis='y', labelcolor=color)

        fig.tight_layout()
        plt.savefig('graph.png')
    except Exception as e:
        pass


def creating_map(flight_details):
    try:
        # Create a map
        flight_map = folium.Map(location=[flight_details['trail'][0]['lat'], flight_details['trail'][0]['lng']],
                                zoom_start=10)

        # Create flight path line
        flight_path = folium.PolyLine(locations=[(point['lat'], point['lng']) for point in flight_details['trail']],
                                      color='blue')

        # Add the line to the map
        flight_path.add_to(flight_map)

        # Reduce marker size
        for i, point in enumerate(flight_details['trail']):
            radius = 0.1 if i != 0 and i != len(
                flight_details['trail']) - 1 else 5

            color = 'blue' if i != len(flight_details['trail']) - 1 else 'red'

            if i == 0:
                # Add a plane icon to the first point
                folium.Marker(
                    location=[point['lat'], point['lng']],
                    icon=folium.Icon(color='green', icon='plane', fill=True),
                ).add_to(flight_map)

            folium.CircleMarker(location=[point['lat'], point['lng']], radius=radius, color=color, fill=True).add_to(
                flight_map)

        # Remove zoom in/out signs
        flight_map.options.update({'zoomControl': False})

        # Get coordinates for map scaling
        trail_coordinates = [(point['lat'], point['lng']) for point in flight_details['trail']]
        flight_map.fit_bounds(trail_coordinates)

        # Save the map as an image with 3:4 dimensions
        img_data = flight_map._to_png()
        img = Image.open(io.BytesIO(img_data))
        img.save('image.png')
    except Exception as e:
        pass


def find_aircraft_data(registration_number, aircraft_data):
    for aircraft in aircraft_data:
        if registration_number == aircraft.registration:
            return aircraft
    return None


def format_data(data):
    if data:
        try:
            formatted_data = f"  Altitude: {data.altitude}\n"
        except (KeyError, TypeError):
            formatted_data = f"  Altitude: N/A \n"

        try:
            formatted_data += f"  Ground Speed: {data.ground_speed}\n"
        except (KeyError, TypeError):
            formatted_data = f"  Ground Speed: N/A \n"

        try:
            formatted_data += f"  Heading: {data.heading}\n"
        except (KeyError, TypeError):
            formatted_data = f"  Heading: N/A \n"

        return formatted_data
    else:
        return "Aircraft data not found."


def status_data(data):
    if data:
        try:
            if data.altitude is not None and data.altitude > 100:
                formatted_data = f"  Status: In Flight\n"
            else:
                formatted_data = f"  Status: On Ground\n"
            return formatted_data
        except (KeyError, TypeError):
            formatted_data = f"  Status: N/A \n"
            return formatted_data


def format_flight_details(flight_details, registration_number, current_flight):
    formatted_info = "<b>Flight Details:</b>\n"
    try:
        formatted_info += f"  Callsign: {flight_details['identification']['callsign']}\n"
    except (KeyError, TypeError):
        formatted_info += "  Callsign: N/A\n"

    try:
        formatted_info += f"  Flight number: {flight_details['identification']['number']['default']}\n"
    except (KeyError, TypeError):
        formatted_info += "  Flight number: N/A\n"

    try:
        aircraft_data = fr_api.get_flights(flight_details['airline']['code']['icao'])
        found_data = find_aircraft_data(registration_number, aircraft_data)
        formatted_info += status_data(found_data)
    except TypeError:
        pass

    try:
        formatted_info += f"  Aircraft Model: {flight_details['aircraft']['model']['text']}\n"
    except (KeyError, TypeError):
        formatted_info += "  Aircraft Model: N/A\n"

    try:
        formatted_info += f"  Registration: {flight_details['aircraft']['registration']}\n"
    except (KeyError, TypeError):
        formatted_info += "  Registration: N/A\n"

    try:
        formatted_info += f"  Airline: {flight_details['airline']['name']} " \
                          f"({flight_details['airline']['code']['iata']}" \
                          f" / {flight_details['airline']['code']['icao']})\n\n"
    except (KeyError, TypeError):
        formatted_info += "  Airline: N/A\n\n"

    formatted_info += "<b>Aircraft Details:</b>\n"
    try:
        formatted_info += f"  Flight level: {current_flight.get_flight_level()}\n"
    except (KeyError, TypeError):
        formatted_info += "  Flight level: N/A\n"

    try:
        aircraft_data = fr_api.get_flights(flight_details['airline']['code']['icao'])
        found_data = find_aircraft_data(registration_number, aircraft_data)
        formatted_info += format_data(found_data)
    except TypeError:
        pass

    try:
        formatted_info += f"  Vertical speed: {current_flight.get_vertical_speed()}"
    except (KeyError, TypeError):
        formatted_info += "  Vertical speed: N/A\n\n"

    formatted_info += "\n\n<b>Airports Details:</b>\n"
    try:
        formatted_info += f"  Origin Airport: {flight_details['airport']['origin']['name']} " \
                          f"({flight_details['airport']['origin']['code']['iata']} / " \
                          f"{flight_details['airport']['origin']['code']['icao']})\n"
    except (KeyError, TypeError):
        formatted_info += "  Origin Airport: N/A\n"

    try:
        formatted_info += f"  Destination Airport: {flight_details['airport']['destination']['name']} " \
                          f"({flight_details['airport']['destination']['code']['iata']}/" \
                          f"{flight_details['airport']['destination']['code']['icao']})\n\n"
    except (KeyError, TypeError):
        formatted_info += "  Destination Airport: N/A\n\n"

    formatted_info += "<b>Time Details:</b>\n"

    try:
        scheduled_departure = datetime.fromtimestamp(flight_details['time']['scheduled']['departure']).astimezone(
            timezone.utc)
        formatted_info += f"  Scheduled Departure: {scheduled_departure.strftime('%H:%M')} (UTC)\n"
    except (KeyError, TypeError, OSError):
        formatted_info += "  Scheduled Departure: N/A\n"

    try:
        real_departure = datetime.fromtimestamp(flight_details['time']['real']['departure']).astimezone(timezone.utc)
        formatted_info += f"  Real Departure: {real_departure.strftime('%H:%M')} (UTC)\n"
    except (KeyError, TypeError, OSError):
        formatted_info += "  Real Departure: N/A\n"

    try:
        scheduled_arrival = datetime.fromtimestamp(flight_details['time']['scheduled']['arrival']).astimezone(
            timezone.utc)
        formatted_info += f"  Scheduled Arrival: {scheduled_arrival.strftime('%H:%M')} (UTC)\n"
    except (KeyError, TypeError, OSError):
        formatted_info += "  Scheduled Arrival: N/A\n"

    try:
        real_departure = datetime.fromtimestamp(flight_details['time']['estimated']['arrival']).astimezone(timezone.utc)
        formatted_info += f"  Estimated Arrival: {real_departure.strftime('%H:%M')} (UTC)\n"
    except (KeyError, TypeError, OSError):
        formatted_info += "  Estimated Arrival: N/A\n"

    try:
        formatted_info += f"\nhttps://www.flightradar24.com/{flight_details['identification']['id']}\n\n"
    except (KeyError, TypeError, IndexError):
        pass

    return formatted_info


def format_flight_details_location(flight_details):
    formatted_info = ""

    try:
        formatted_info = (f"<b>{flight_details['identification']['callsign']} "
                          f"({flight_details['identification']['number']['default']})</b>\n")
    except (KeyError, TypeError):
        formatted_info += "N/A (N/A)\n"

    try:
        formatted_info += f"   Aircraft Model: {flight_details['aircraft']['model']['text']}\n"
    except (KeyError, TypeError):
        formatted_info += "Aircraft Model: N/A\n"

    try:
        formatted_info += f"   Registration: {flight_details['aircraft']['registration']}\n"
    except (KeyError, TypeError):
        formatted_info += "   Registration: N/A\n"

    try:
        formatted_info += (f"   {flight_details['airport']['origin']['code']['icao']} — "
                           f"{flight_details['airport']['destination']['code']['icao']}\n")
    except (KeyError, TypeError):
        formatted_info += "   N/A — N/A\n"

    return formatted_info


if __name__ == "__main__":
    # Run the bot
    bot.polling(none_stop=True)

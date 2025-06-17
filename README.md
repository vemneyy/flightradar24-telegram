# Flight Tracker Bot

This is a Telegram bot that utilizes the Flightradar24 API to provide real-time information about flights. The bot can handle user queries for specific flight numbers and provide details about flights near the user's location.

## Requirements
- Python 3.6 or higher
- Required libraries can be installed using:
  ```bash
  pip install telebot FlightRadarAPI folium matplotlib pillow selenium
  ```

## Setup
1. Obtain a Telegram Bot Token by talking to [@BotFather](https://t.me/BotFather) on Telegram.
2. Export your token as an environment variable `TELEGRAM_BOT_TOKEN` before starting the bot.

## How to Use
1. Start the bot.
2. Send a message with the flight number to get information about a specific flight.
3. Share your location to get information about flights near you.

## Features
- **Flight Information**: Get details about a specific flight, including callsign, flight number, aircraft model, registration, airline, and more.
- **Nearby Flights**: Share your location, and the bot will provide information about aircraft near you.

## Screenshots
- ![Message](https://github.com/vemneyy/flightradar24-telegram/assets/78843201/17e1efd0-62fb-4bfc-8a43-f6d0eb1b5b1a)
- ![Aircraft Photo](https://github.com/vemneyy/flightradar24-telegram/assets/78843201/f4241f1c-97b9-4624-8042-b4186caf80eb)
- ![Flight Path Map](https://github.com/vemneyy/flightradar24-telegram/assets/78843201/4229d389-49cb-48b0-8f52-b08dd4062d74)  
- ![Flight Graph](https://github.com/vemneyy/flightradar24-telegram/assets/78843201/33cc5dd8-c211-4d94-9240-b1d8d1ab8d3c)

## Important Note
- This bot relies on the Flightradar24 API, and some features may be limited based on the API's availability and restrictions.

Feel free to contribute to the development or report issues. Enjoy tracking flights with the Flight Tracker Bot!

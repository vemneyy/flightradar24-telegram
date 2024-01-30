# Flight Tracker Bot

This is a Telegram bot that utilizes the Flightradar24 API to provide real-time information about flights. The bot can handle user queries for specific flight numbers and provide details about flights near the user's location.

## Requirements
- Python 3.6 or higher
- Required libraries can be installed using:
  ```bash
  pip install telebot flightradar24 folium matplotlib pillow
  ```

## Setup
1. Obtain a Telegram Bot Token by talking to [@BotFather](https://t.me/BotFather) on Telegram.
2. Replace `"token"` with your actual Telegram Bot Token in the code.

## How to Use
1. Start the bot.
2. Send a message with the flight number to get information about a specific flight.
3. Share your location to get information about flights near you.

## Features
- **Flight Information**: Get details about a specific flight, including callsign, flight number, aircraft model, registration, airline, and more.
- **Nearby Flights**: Share your location, and the bot will provide information about aircraft near you.

## Screenshots
- Aircraft Photo
- Flight Path Map
- Flight Graph

## Important Note
- This bot relies on the Flightradar24 API, and some features may be limited based on the API's availability and restrictions.

Feel free to contribute to the development or report issues. Enjoy tracking flights with the Flight Tracker Bot!

# Weather Insight Bot 🌦

A Telegram bot that analyzes today's weather and sends a beautifully formatted forecast — complete with a personalized tip for your day (what to wear, whether to grab an umbrella, etc).

## Features

- 🌡 **Live weather data** via the OpenWeather API (temperature, feels-like, min/max, humidity, pressure, wind speed & direction)
- 💡 **Smart daily advice** — dynamically generated tips based on temperature, wind, and conditions (rain, snow, storm, fog)
- ⏰ **Scheduled daily notifications** at a time set by each user
- ⚙️ **Per-user settings** — city, notification time, and on/off toggle, stored persistently
- 🔁 **Automatic retries** on failed API requests
- 🎨 **Clean HTML-formatted messages** with weather icons and emoji

## Commands

| Command | Description |
|---|---|
| `/start` | Register and get today's forecast |
| `/weather` | Get the current weather now |
| `/settings` | View your current settings |
| `/city <name>` | Change your city |
| `/time HH:MM` | Set daily notification time |
| `/notify on\|off` | Enable/disable daily notifications |

## Tech Stack

- **Python 3.10+**
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) — Telegram Bot API framework
- [OpenWeather API](https://openweathermap.org/api) — weather data
- `requests` — HTTP client
- `python-dotenv` — environment variable management
- JSON file storage for user settings

## Project Structure

```
├── bot.py            # Bot handlers, commands, scheduled notifier
├── config.py          # Environment variables & settings
├── formatter.py        # Message formatting & advice generation
├── storage.py          # User settings persistence (JSON)
├── weather_api.py       # OpenWeather API client
├── main1.py            # Entry point
└── requirements.txt
```

## Installation

1. Clone the repository
   ```bash
   git clone https://github.com/<your-username>/<repo-name>.git
   cd <repo-name>
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on `.env.example`
   ```
   BOT_TOKEN=your_telegram_bot_token
   OPENWEATHER_API_KEY=your_openweather_api_key
   DEFAULT_CITY=Astana
   DEFAULT_COUNTRY=KZ
   ```

4. Run the bot
   ```bash
   python main1.py
   ```

## How It Works

1. User sets their city and preferred notification time
2. A background job checks every minute whether it's time to send a forecast
3. The bot fetches live weather data from OpenWeather, formats it into a readable message, and generates a short piece of advice based on temperature, wind, and conditions
4. The message is sent to the user with HTML formatting and emoji

## License

MIT

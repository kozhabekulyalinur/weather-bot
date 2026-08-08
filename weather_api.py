import logging
import time
from typing import Any

import requests

from config import (
    API_RETRIES,
    API_RETRY_DELAY,
    DEFAULT_CITY,
    DEFAULT_COUNTRY,
    LANG,
    OPENWEATHER_API_KEY,
    UNITS,
)

logger = logging.getLogger(__name__)


class WeatherAPIError(Exception):
    pass


class CityNotFoundError(WeatherAPIError):
    pass


def _request(url: str, params: dict[str, Any]) -> dict[str, Any]:
    last_error: Exception | None = None

    for attempt in range(1, API_RETRIES + 1):
        try:
            response = requests.get(url, params=params, timeout=15)
            data = response.json()

            if response.status_code == 404 or data.get("cod") == "404":
                raise CityNotFoundError(data.get("message", "Город не найден"))

            if response.status_code != 200 or str(data.get("cod", "200")) != "200":
                raise WeatherAPIError(
                    data.get("message", f"Ошибка API: HTTP {response.status_code}")
                )

            return data
        except (requests.RequestException, ValueError) as exc:
            last_error = exc
            logger.warning(
                "Попытка %s/%s не удалась: %s", attempt, API_RETRIES, exc
            )
            if attempt < API_RETRIES:
                time.sleep(API_RETRY_DELAY * attempt)

    raise WeatherAPIError(
        f"Не удалось получить погоду после {API_RETRIES} попыток: {last_error}"
    )


def get_weather(city: str = DEFAULT_CITY, country: str = DEFAULT_COUNTRY) -> dict[str, Any]:
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": f"{city},{country}",
        "appid": OPENWEATHER_API_KEY,
        "units": UNITS,
        "lang": LANG,
    }
    data = _request(url, params)

    main = data["main"]
    weather = data["weather"][0]
    wind = data.get("wind", {})

    return {
        "city": data.get("name", city),
        "country": data.get("sys", {}).get("country", country),
        "temp": round(main["temp"]),
        "feels_like": round(main["feels_like"]),
        "temp_min": round(main["temp_min"]),
        "temp_max": round(main["temp_max"]),
        "humidity": main["humidity"],
        "pressure": main["pressure"],
        "description": weather["description"],
        "icon": weather["icon"],
        "wind": round(wind.get("speed", 0), 1),
        "wind_deg": wind.get("deg"),
        "visibility": data.get("visibility"),
    }

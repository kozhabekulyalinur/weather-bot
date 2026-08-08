from random import choice

from telegram.helpers import escape

ICON_MAP = {
    "01d": "☀️",
    "01n": "🌙",
    "02d": "🌤",
    "02n": "☁️",
    "03d": "☁️",
    "03n": "☁️",
    "04d": "☁️",
    "04n": "☁️",
    "09d": "🌧",
    "09n": "🌧",
    "10d": "🌦",
    "10n": "🌧",
    "11d": "⛈",
    "11n": "⛈",
    "13d": "❄️",
    "13n": "❄️",
    "50d": "🌫",
    "50n": "🌫",
}

GREETINGS = [
    "Доброе утро",
    "Приветствую",
    "Новый день — новые приключения",
    "С добрым утром, герой дня",
    "Просыпайся, пора побеждать этот день",
]

ENDINGS = [
    "Хорошего настроения сегодня",
    "Береги себя и будь на позитиве",
    "Пусть день будет лёгким и приятным",
    "Не забудь улыбнуться миру",
    "Желаю отличного дня и теплоты вокруг",
]

WIND_DIRECTIONS = [
    (337.5, 360, "С"),
    (0, 22.5, "С"),
    (22.5, 67.5, "СВ"),
    (67.5, 112.5, "В"),
    (112.5, 157.5, "ЮВ"),
    (157.5, 202.5, "Ю"),
    (202.5, 247.5, "ЮЗ"),
    (247.5, 292.5, "З"),
    (292.5, 337.5, "СЗ"),
]


def _wind_direction(deg: int | None) -> str:
    if deg is None:
        return ""
    for start, end, label in WIND_DIRECTIONS:
        if start <= deg < end:
            return label
    return ""


def _temp_emoji(temp: int) -> str:
    if temp <= -20:
        return "🥶"
    if temp <= -5:
        return "❄️"
    if temp <= 10:
        return "🧥"
    if temp <= 22:
        return "😊"
    if temp <= 30:
        return "☀️"
    return "🥵"


def _collect_advice(temp: int, desc: str, wind: float) -> list[str]:
    desc = desc.lower()
    parts: list[str] = []

    if temp <= -25:
        parts.append(
            choice(
                [
                    "На улице жуткий мороз — лучше остаться дома, если можно.",
                    "Экстремально холодно — даже пингвины бы не вышли.",
                    "Сегодня настоящий ледяной день, одевайся как полярник.",
                ]
            )
        )
    elif -25 < temp <= -15:
        parts.append(
            choice(
                [
                    "Мороз кусается — не забудь шапку и перчатки.",
                    "Холодно, укутайся потеплее.",
                    "Морозное утро — не геройствуй, тепло одевайся.",
                ]
            )
        )
    elif -15 < temp <= -5:
        parts.append(
            choice(
                [
                    "Свежо, но приятно — куртка и перчатки сегодня пригодятся.",
                    "Погода бодрящая, надень куртку и шарф.",
                    "На улице прохладно, без шарфа можно пожалеть.",
                ]
            )
        )
    elif -5 < temp <= 5:
        parts.append(
            choice(
                [
                    "Прохладно, но уже не мороз — отлично для прогулки.",
                    "Лёгкий холодок — время для стильной куртки.",
                    "Утром может поддувать, возьми кофту.",
                ]
            )
        )
    elif 5 < temp <= 15:
        parts.append(
            choice(
                [
                    "Комфортно и приятно — толстовка или ветровка самое то.",
                    "Тепло, но ветерок — лучше не в футболке.",
                    "Погода идеальна для прогулки.",
                ]
            )
        )
    elif 15 < temp <= 25:
        parts.append(
            choice(
                [
                    "Замечательная погода — наслаждайся днём.",
                    "Тепло и легко, отличное время для прогулки.",
                    "Самое то для лёгкой одежды и хорошего настроения.",
                ]
            )
        )
    elif 25 < temp <= 35:
        parts.append(
            choice(
                [
                    "Жарковато — не забудь бутылку воды.",
                    "Солнце активно, возьми головной убор.",
                    "Настоящее лето — лёгкая одежда спасёт.",
                ]
            )
        )
    else:
        parts.append(
            choice(
                [
                    "Экстремальная жара — лучше не выходить на улицу днём.",
                    "Пекло, осторожнее с солнцем.",
                    "Серьёзно жарко — кондиционер твой лучший друг.",
                ]
            )
        )

    if "дожд" in desc:
        parts.append(
            choice(
                [
                    "Похоже, дождь заглянет — возьми зонт.",
                    "На улице дождливо, но зато свежо.",
                    "Не забудь дождевик, небо хмурится.",
                ]
            )
        )
    if "снег" in desc:
        parts.append(
            choice(
                [
                    "На улице снежно — красиво, но скользко.",
                    "Снег — отличный повод достать варежки.",
                    "Зимняя сказка на дворе, не забудь шапку.",
                ]
            )
        )
    if "гроза" in desc:
        parts.append(
            choice(
                [
                    "Гроза приближается — лучше не планируй долгих прогулок.",
                    "На небе молнии — будь осторожен.",
                    "Громыхает — самое время посидеть дома с чаем.",
                ]
            )
        )
    if "туман" in desc:
        parts.append(
            choice(
                [
                    "Туманно и мистично — будь осторожен на дорогах.",
                    "Низкая видимость — не спеши.",
                ]
            )
        )
    if wind > 10:
        parts.append(
            choice(
                [
                    "Сильный ветер — держи зонт крепче.",
                    "Ветер шальной — надевай капюшон.",
                    "Дует прилично — не забудь шарф.",
                ]
            )
        )
    elif wind > 5:
        parts.append(
            choice(
                [
                    "Немного ветрено, но приятно.",
                    "Лёгкий ветерок добавит свежести.",
                ]
            )
        )

    return parts


def format_weather_message(data: dict, greeting: str | None = None) -> str:
    city = escape(str(data["city"]))
    country = escape(str(data["country"]))
    temp = data["temp"]
    feels = data["feels_like"]
    desc = escape(data["description"].capitalize())
    wind = data["wind"]
    humidity = data["humidity"]
    pressure = data["pressure"]
    temp_min = data["temp_min"]
    temp_max = data["temp_max"]
    icon = ICON_MAP.get(data.get("icon", ""), "🌡")
    temp_icon = _temp_emoji(temp)

    wind_dir = _wind_direction(data.get("wind_deg"))
    wind_text = f"{wind} м/с"
    if wind_dir:
        wind_text += f" ({wind_dir})"

    advice_lines = _collect_advice(temp, data["description"], wind)
    advice_block = "\n".join(f"• {escape(line)}" for line in advice_lines)

    header = escape(greeting or choice(GREETINGS))
    footer = escape(choice(ENDINGS))

    return (
        f"{icon} <b>{header}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📍 <b>{city}, {country}</b>\n\n"
        f"{temp_icon} <b>{temp:+d}°C</b>  ·  {desc}\n"
        f"🤔 Ощущается как <b>{feels:+d}°C</b>\n"
        f"↔️ Днём: <b>{temp_min:+d}° … {temp_max:+d}°</b>\n\n"
        f"💨 Ветер: {escape(wind_text)}\n"
        f"💧 Влажность: <b>{humidity}%</b>\n"
        f"🧭 Давление: <b>{pressure}</b> гПа\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 <b>Совет дня</b>\n"
        f"{advice_block}\n\n"
        f"<i>{footer}</i>"
    )


def format_settings(settings) -> str:
    status = "включены ✅" if settings.notify else "выключены 🔕"
    return (
        "⚙️ <b>Твои настройки</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📍 Город: <b>{escape(settings.city)}, {escape(settings.country)}</b>\n"
        f"⏰ Рассылка: <b>{escape(settings.notify_time)}</b>\n"
        f"🔔 Уведомления: <b>{status}</b>\n\n"
        "Команды:\n"
        "• /city Астана — сменить город\n"
        "• /time 07:30 — время рассылки\n"
        "• /notify on — включить уведомления\n"
        "• /notify off — выключить уведомления"
    )

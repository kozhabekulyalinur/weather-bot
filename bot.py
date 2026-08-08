import logging
import re
from datetime import datetime

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from config import BOT_TOKEN
from formatter import format_settings, format_weather_message
from storage import UserStorage
from weather_api import CityNotFoundError, WeatherAPIError, get_weather

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

storage = UserStorage()
LEGACY_USERS = []
TIME_PATTERN = re.compile(r"^([01]?\d|2[0-3]):([0-5]\d)$")


async def _send_weather(update: Update, user_id: int, greeting: str | None = None) -> None:
    settings = storage.get(user_id)
    try:
        data = get_weather(settings.city, settings.country)
        text = format_weather_message(data, greeting=greeting)
        await update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)
    except CityNotFoundError:
        await update.effective_message.reply_text(
            f"❌ Город «{settings.city}» не найден.\n"
            "Проверь название или попробуй /city Astana"
        )
    except WeatherAPIError as exc:
        logger.error("Ошибка погоды для user=%s: %s", user_id, exc)
        await update.effective_message.reply_text(
            "⚠️ Не удалось получить погоду. Попробуй позже — я уже повторил запрос несколько раз."
        )


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    storage.get(user.id)
    name = user.first_name or "друг"
    await update.message.reply_text(
        f"Привет, {name}! 👋\n\n"
        "Я присылаю красивую карточку погоды каждый день и по команде.\n\n"
        "📌 Команды:\n"
        "• /weather — погода сейчас\n"
        "• /settings — твои настройки\n"
        "• /city <город> — сменить город\n"
        "• /time HH:MM — время рассылки\n"
        "• /notify on|off — уведомления"
    )
    await _send_weather(update, user.id, greeting=f"Привет, {name}!")


async def cmd_weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _send_weather(update, update.effective_user.id)


async def cmd_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = storage.get(update.effective_user.id)
    await update.message.reply_text(
        format_settings(settings),
        parse_mode=ParseMode.HTML,
    )


async def cmd_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            "Укажи город, например:\n/city Astana\n/city Almaty"
        )
        return

    city = " ".join(context.args).strip()
    user_id = update.effective_user.id
    storage.update(user_id, city=city)

    await update.message.reply_text(f"📍 Город изменён на <b>{city}</b>", parse_mode=ParseMode.HTML)
    await _send_weather(update, user_id)


async def cmd_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            "Укажи время в формате HH:MM, например:\n/time 07:30"
        )
        return

    raw_time = context.args[0]
    match = TIME_PATTERN.match(raw_time)
    if not match:
        await update.message.reply_text(
            "❌ Неверный формат. Используй HH:MM, например 06:30 или 7:00"
        )
        return

    hour, minute = int(match.group(1)), int(match.group(2))
    notify_time = f"{hour:02d}:{minute:02d}"
    storage.update(update.effective_user.id, notify_time=notify_time)

    await update.message.reply_text(
        f"⏰ Ежедневная рассылка настроена на <b>{notify_time}</b>",
        parse_mode=ParseMode.HTML,
    )


async def cmd_notify(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args or context.args[0].lower() not in {"on", "off"}:
        await update.message.reply_text(
            "Используй:\n/notify on — включить\n/notify off — выключить"
        )
        return

    enabled = context.args[0].lower() == "on"
    storage.update(update.effective_user.id, notify=enabled)

    if enabled:
        await update.message.reply_text("🔔 Уведомления включены.")
    else:
        await update.message.reply_text("🔕 Уведомления выключены.")


async def daily_notifier(context: ContextTypes.DEFAULT_TYPE) -> None:
    now = datetime.now().strftime("%H:%M")

    for user_id, settings in storage.all_notifiable():
        if not storage.should_notify_now(user_id, now):
            continue

        try:
            data = get_weather(settings.city, settings.country)
            text = format_weather_message(data)
            await context.bot.send_message(
                chat_id=user_id,
                text=text,
                parse_mode=ParseMode.HTML,
            )
            storage.mark_notified(user_id)
            logger.info("Рассылка отправлена user=%s city=%s", user_id, settings.city)
        except CityNotFoundError:
            logger.warning("Город не найден для user=%s: %s", user_id, settings.city)
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    f"⚠️ Не могу найти город «{settings.city}».\n"
                    "Измени его командой /city Astana"
                ),
            )
        except WeatherAPIError as exc:
            logger.error("Ошибка рассылки user=%s: %s", user_id, exc)
        except Exception as exc:
            logger.exception("Неожиданная ошибка рассылки user=%s: %s", user_id, exc)


def build_app():
    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN не задан. Создай файл .env на основе .env.example"
        )
    if not storage.path.exists() or not storage._users:
        storage.migrate_legacy_users(LEGACY_USERS)

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("weather", cmd_weather))
    app.add_handler(CommandHandler("settings", cmd_settings))
    app.add_handler(CommandHandler("city", cmd_city))
    app.add_handler(CommandHandler("time", cmd_time))
    app.add_handler(CommandHandler("notify", cmd_notify))

    app.job_queue.run_repeating(
        daily_notifier,
        interval=60,
        first=10,
        name="weather_notifier",
    )

    return app


def run() -> None:
    logger.info("Запуск погодного бота...")
    app = build_app()
    app.run_polling(drop_pending_updates=True)

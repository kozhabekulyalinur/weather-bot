import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Optional

from config import DEFAULT_CITY, DEFAULT_COUNTRY, USERS_FILE

logger = logging.getLogger(__name__)


@dataclass
class UserSettings:
    city: str = DEFAULT_CITY
    country: str = DEFAULT_COUNTRY
    notify: bool = True
    notify_time: str = "06:30"
    last_notify_date: Optional[str] = None


class UserStorage:
    def __init__(self, path=USERS_FILE):
        self.path = path
        self._users: dict[str, UserSettings] = {}
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            self._users = {}
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            self._users = {
                user_id: UserSettings(**data) for user_id, data in raw.items()
            }
        except (json.JSONDecodeError, TypeError) as exc:
            logger.error("Не удалось прочитать users.json: %s", exc)
            self._users = {}

    def save(self) -> None:
        data = {user_id: asdict(settings) for user_id, settings in self._users.items()}
        self.path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def get(self, user_id: int) -> UserSettings:
        key = str(user_id)
        if key not in self._users:
            self._users[key] = UserSettings()
            self.save()
        return self._users[key]

    def update(self, user_id: int, **kwargs) -> UserSettings:
        settings = self.get(user_id)
        for name, value in kwargs.items():
            if hasattr(settings, name):
                setattr(settings, name, value)
        self.save()
        return settings

    def all_notifiable(self) -> list[tuple[int, UserSettings]]:
        return [
            (int(user_id), settings)
            for user_id, settings in self._users.items()
            if settings.notify
        ]

    def mark_notified(self, user_id: int) -> None:
        today = datetime.now().strftime("%Y-%m-%d")
        self.update(user_id, last_notify_date=today)

    def should_notify_now(self, user_id: int, current_time: str) -> bool:
        settings = self.get(user_id)
        if not settings.notify:
            return False
        if settings.notify_time != current_time:
            return False
        today = datetime.now().strftime("%Y-%m-%d")
        return settings.last_notify_date != today

    def migrate_legacy_users(self, user_ids: list[int]) -> None:
        changed = False
        for user_id in user_ids:
            key = str(user_id)
            if key not in self._users:
                self._users[key] = UserSettings()
                changed = True
        if changed:
            self.save()

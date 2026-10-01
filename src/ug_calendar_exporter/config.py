from dataclasses import dataclass
from datetime import tzinfo
from os import environ
from zoneinfo import ZoneInfo


@dataclass
class Config:
    HOST: str
    PORT: int
    TZ: tzinfo | None
    CALENDAR_URL: str
    SOURCE_WEBPAGE_URL: str

    @classmethod
    def from_env(cls) -> Config:
        tz_str = environ.get("TZ")
        return cls(
            HOST=environ.get("HOST", "localhost"),
            PORT=int(environ.get("PORT", "8080")),
            TZ=ZoneInfo(tz_str) if tz_str is not None else None,
            CALENDAR_URL=environ.get("CALENDAR_URL", "calendar"),
            SOURCE_WEBPAGE_URL=environ.get(
                "SOURCE_WEBPAGE_URL",
                "https://inf.ug.edu.pl/terminy-zjazdow-semestr-zimowy-2026-27.print",
            ),
        )

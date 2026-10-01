import logging
from http.server import HTTPServer
from typing import Any
from zoneinfo import ZoneInfo

from ug_calendar_exporter.config import Config
from ug_calendar_exporter.server import RequestHandler

TZ = ZoneInfo("Europe/Warsaw")

log = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    config = Config.from_env()

    def make_handler(*args: Any, **kwargs: Any) -> RequestHandler:
        return RequestHandler(config, *args, **kwargs)

    with HTTPServer((config.HOST, config.PORT), make_handler) as server:
        log.info("Starting server on %s:%s", config.HOST, config.PORT)
        log.info("Calendar available on %s", f"/{config.CALENDAR_URL}.ics")

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            log.info("Shutting down server")

    log.info("Bye")

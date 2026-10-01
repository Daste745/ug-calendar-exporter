import logging
from http.server import BaseHTTPRequestHandler
from typing import Any

import httpx

from ug_calendar_exporter.calendar import make_calendar
from ug_calendar_exporter.calendar_parser import CalendarParser
from ug_calendar_exporter.config import Config

log = logging.getLogger(__name__)


class RequestHandler(BaseHTTPRequestHandler):
    config: Config

    def __init__(self, config: Config, *args: Any, **kwargs: Any) -> None:
        self.config = config
        super().__init__(*args, **kwargs)

    def do_GET(self) -> None:
        if self.path == f"/{self.config.CALENDAR_URL}.ics":
            return self._calendar()

        self.send_response(404)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes("Not found\n", "utf-8"))

    def _calendar(self) -> None:
        try:
            res = httpx.get(self.config.SOURCE_WEBPAGE_URL)
            parser = CalendarParser()
            parser.feed(res.text)
            calendar = make_calendar(parser.parsed_rows, tz=self.config.TZ)
        except Exception:
            log.exception("Failed to create calendar")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(bytes("Internal server error\n", "utf-8"))
            return

        self.send_response(200)
        self.send_header("Content-type", "text/calendar")
        self.end_headers()
        self.wfile.write(bytes(calendar.serialize(), "utf-8"))

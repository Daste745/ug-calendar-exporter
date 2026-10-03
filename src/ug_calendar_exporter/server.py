import logging
from datetime import datetime
from http.server import BaseHTTPRequestHandler
from typing import Any

import httpx

from ug_calendar_exporter.calendar import Schedule, make_calendar
from ug_calendar_exporter.calendar_parser import CalendarParser, Row
from ug_calendar_exporter.config import Config
from ug_calendar_exporter.dates import parse_header_month
from ug_calendar_exporter.schedule_parser import ScheduleParser

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
            schedules: list[Schedule] = []
            for row in parser.parsed_rows:
                schedules.extend(self._get_schedules(row))

            calendar = make_calendar(schedules)

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

    def _get_schedules(self, row: Row) -> list[Schedule]:
        year, month = parse_header_month(row.header)
        schedules: list[Schedule] = []

        for cell in row.cells:
            day = int(cell.name)
            date = datetime(year, month, day, tzinfo=self.config.TZ)
            if cell.url is None:
                schedules.append(Schedule(date=date, url=None, items=[]))
            else:
                schedule_res = httpx.get(cell.url)
                schedule_parser = ScheduleParser()
                schedule_parser.feed(schedule_res.text)
                schedules.append(
                    Schedule(
                        date=date,
                        url=cell.url,
                        items=schedule_parser.parsed_items,
                    )
                )

        return schedules

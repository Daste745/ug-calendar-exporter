from zoneinfo import ZoneInfo

import httpx

from ug_calendar_exporter.calendar import make_calendar
from ug_calendar_exporter.calendar_parser import CalendarParser

CALENDAR_WEBPAGE_URL = (
    "https://inf.ug.edu.pl/terminy-zjazdow-semestr-zimowy-2026-27.print"
)
TZ = ZoneInfo("Europe/Warsaw")


def main() -> None:
    res = httpx.get(CALENDAR_WEBPAGE_URL)
    parser = CalendarParser()
    parser.feed(res.text)

    calendar = make_calendar(parser.parsed_rows)

    with open("out.ics", "w") as out:
        out.write(calendar.serialize())

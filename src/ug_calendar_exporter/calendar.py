from datetime import datetime, timedelta, tzinfo

import ics

from ug_calendar_exporter.calendar_parser import Row
from ug_calendar_exporter.dates import parse_header_month


def make_all_day_event(
    year: int,
    month: int,
    day: int,
    name: str,
    url: str | None,
    *,
    tz: tzinfo | None = None,
) -> ics.Event:
    begin = datetime(year, month, day, tzinfo=tz)
    end = begin + timedelta(days=1)

    event = ics.Event(
        name=name,
        begin=begin,
        end=end,
    )

    if url is not None:
        event.url = url

    return event


def make_calendar(rows: list[Row], *, tz: tzinfo | None = None) -> ics.Calendar:
    calendar = ics.Calendar()

    for row in rows:
        year, month = parse_header_month(row.header)

        for cell in row.cells:
            day = int(cell.name.strip())
            event = make_all_day_event(
                year,
                month,
                day,
                name="Zajęcia",
                url=cell.url,
                tz=tz,
            )
            calendar.events.add(event)

    return calendar

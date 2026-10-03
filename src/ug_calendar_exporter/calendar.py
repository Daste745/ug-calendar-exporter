from dataclasses import dataclass
from datetime import datetime, timedelta

import ics

from ug_calendar_exporter.dates import parse_time_string
from ug_calendar_exporter.schedule_parser import ScheduleItem


@dataclass
class Schedule:
    date: datetime
    url: str | None
    items: list[ScheduleItem]


def make_event(
    begin: datetime,
    end: datetime,
    name: str,
    location: str | None,
) -> ics.Event:
    event = ics.Event(
        name=name,
        begin=begin,
        end=end,
    )

    if location is not None:
        event.location = location

    return event


def make_all_day_event(
    begin: datetime,
    name: str,
    url: str | None,
) -> ics.Event:
    event = ics.Event(
        name=name,
        begin=begin,
        end=begin + timedelta(days=1),
    )

    if url is not None:
        event.url = url

    return event


def make_calendar(schedules: list[Schedule]) -> ics.Calendar:
    calendar = ics.Calendar()

    for schedule in schedules:
        if len(schedule.items) == 0:
            event = make_all_day_event(schedule.date, name="Zajęcia", url=schedule.url)
            calendar.events.add(event)
            continue

        for item in schedule.items:
            begin = parse_time_string(item.start, schedule.date)
            end = parse_time_string(item.end, schedule.date)
            group_str = f", gr. {item.group}" if item.group is not None else ""
            # Zaawansowane języki programowania, mgr Mateusz Miotk (laboratorium, gr. 2)
            name = f"{item.name}, {item.teacher} ({item.kind}{group_str})"
            calendar.events.add(make_event(begin, end, name, item.location))

    return calendar

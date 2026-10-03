from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Literal, Self

SCHEDULE_NAME = "Studia II stopnia, 1 rok"


class ScheduleItemBuilder:
    parts: list[str]

    def __init__(self) -> None:
        self.parts = []

    def add_part(self, part: str) -> Self:
        self.parts.append(part)
        return self

    def build(self) -> ScheduleItem:
        start: str | None = None
        end: str | None = None
        name: str | None = None
        location: str | None = None
        teacher: str | None = None
        kind: ScheduleItemKind | None = None
        group: str | None = None  # Null for kind="wykład"

        for idx, part in enumerate(filter(lambda p: p.strip() != ",", self.parts)):
            if idx == 0:
                start, end = part.split("—")
                continue

            if idx == 1:
                name = part
                continue

            if idx == 2:
                group_kind_parts = part.strip(",").strip(":").strip().split(",")
                if len(group_kind_parts) == 1:
                    kind = group_kind_parts[0]
                elif len(group_kind_parts) == 2:
                    kind, raw_group = group_kind_parts
                    group = raw_group.strip().lstrip("gr. ")
                continue

            if idx == 3:
                teacher = part
                continue

            if idx == 4:
                location = part
                continue

        if start is None:
            raise ValueError("Could not parse start time")
        if end is None:
            raise ValueError("Could not parse end time")
        if name is None:
            raise ValueError("Could not parse name")
        if location is None:
            raise ValueError("Could not parse location")
        if teacher is None:
            raise ValueError("Could not parse teacher")
        if kind is None:
            raise ValueError("Could not parse kind")

        return ScheduleItem(
            start.strip(","),
            end.strip(","),
            name.strip(),
            location.strip(",").strip(),
            teacher.strip(),
            kind.strip(),
            group,
        )


type ScheduleItemKind = Literal["wykład", "laboratorium"]


@dataclass
class ScheduleItem:
    start: str
    end: str
    name: str
    location: str
    teacher: str
    kind: ScheduleItemKind
    group: str | None


class ScheduleParser(HTMLParser):
    _in_header: bool = False
    _header_content: list[str]
    _in_schedule: bool = False
    _in_schedule_item: bool = False
    _schedule_item_builder: ScheduleItemBuilder | None = None
    _parsed_items: list[ScheduleItem]

    def __init__(self) -> None:
        super().__init__()
        self._header_content = []
        self._parsed_items = []

    @property
    def parsed_items(self) -> list[ScheduleItem]:
        return self._parsed_items

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "h1":
            self._in_header = True
            self._header_content = []
            return

        # Just left the header with the target schedule
        if (
            not self._in_header
            and tag == "ul"
            and "".join(self._header_content) == SCHEDULE_NAME
        ):
            self._in_schedule = True
            return

        if self._in_schedule and tag == "li":
            if self._schedule_item_builder is not None:
                raise ValueError("Unexpected start tag: li. Already in schedule item")
            self._in_schedule_item = True
            self._schedule_item_builder = ScheduleItemBuilder()
            return

    def handle_endtag(self, tag: str) -> None:
        if tag == "h1":
            if not self._in_header:
                raise ValueError("Unexpected end tag: h1. Not in header")
            self._in_header = False
            return

        # Only parse the first schedule matching SCHEDULE_NAME
        if tag == "ul" and self._in_schedule:
            self._in_schedule = False
            return

        if self._in_schedule_item and tag == "li":
            if self._schedule_item_builder is None:
                raise ValueError("Unexpected end tag: li. Not in schedule item")
            self._in_schedule_item = False
            self._parsed_items.append(self._schedule_item_builder.build())
            self._schedule_item_builder = None
            return

    def handle_data(self, data: str) -> None:
        if self._in_header:
            self._header_content.append(data.strip())
            return

        if self._in_schedule and self._in_schedule_item:
            if self._schedule_item_builder is None:
                raise ValueError("Unexpected data. Not in schedule item")
            self._schedule_item_builder.add_part(data.strip())

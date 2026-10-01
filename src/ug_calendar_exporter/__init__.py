import httpx

from ug_calendar_exporter.calendar_parser import CalendarParser
from ug_calendar_exporter.dates import parse_header_month

CALENDAR_WEBPAGE_URL = (
    "https://inf.ug.edu.pl/terminy-zjazdow-semestr-zimowy-2026-27.print"
)


def main() -> None:
    res = httpx.get(CALENDAR_WEBPAGE_URL)
    parser = CalendarParser()
    parser.feed(res.text)

    for row in parser.parsed_rows:
        year, month = parse_header_month(row.header)
        print(f"{year}-{month:<02}")

        for cell in row.cells:
            if cell.url is None:
                print(f" {cell.name}")
            else:
                print(f" {cell.name} -> {cell.url}")

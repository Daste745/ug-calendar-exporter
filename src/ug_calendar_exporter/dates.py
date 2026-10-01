MONTHS = {
    "styczeń": 1,
    "luty": 2,
    "marzec": 3,
    "kwiecień": 4,
    "maj": 5,
    "czerwiec": 6,
    "lipiec": 7,
    "sierpień": 8,
    "wrzesień": 9,
    "październik": 10,
    "listopad": 11,
    "grudzień": 12,
}


type Year = int
type Month = int


def parse_header_month(header: str) -> tuple[Year, Month]:
    month_str, year_str = header.split(" ")
    month = MONTHS.get(month_str.strip())
    if month is None:
        raise ValueError(f"Invalid month: {month_str}")
    return int(year_str.strip()), month

from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Self


class CellBuilder:
    name: str | None
    url: str | None

    def __init__(self) -> None:
        self.name = None
        self.url = None

    def set_name(self, value: str) -> Self:
        self.name = value
        return self

    def set_url(self, value: str) -> Self:
        self.url = value
        return self

    def build(self) -> Cell:
        if self.name is None:
            raise ValueError("Cannot build cell: name is not set")

        if self.url is None:
            raise ValueError("Cannot build cell: url is not set")

        return Cell(self.name, self.url)


@dataclass
class Cell:
    name: str
    url: str | None


class RowBuilder:
    header: str | None
    cells: list[Cell]

    def __init__(self) -> None:
        self.header = None
        self.cells = []

    def set_header(self, value: str) -> Self:
        self.header = value
        return self

    def add_cell(self, value: Cell) -> Self:
        self.cells.append(value)
        return self

    def build(self) -> Row:
        if self.header is None:
            raise ValueError("Cannot build row: header is not set")

        if len(self.cells) == 0:
            raise ValueError("Cannot build row: no cells")

        return Row(self.header, self.cells)


@dataclass
class Row:
    header: str
    cells: list[Cell]


class CalendarParser(HTMLParser):
    _in_table: bool = False
    _row_builder: RowBuilder | None = None
    _parsing_header: bool = False
    _parsing_cell: bool = False
    _cell_builder: CellBuilder | None = None
    _parsed_rows: list[Row]

    def __init__(self) -> None:
        super().__init__()
        self._parsed_rows = []

    @property
    def parsed_rows(self) -> list[Row]:
        return self._parsed_rows

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "table":
            self._in_table = True
            return

        if not self._in_table:
            return

        if tag == "tr":
            if self._row_builder is not None:
                raise ValueError("Unexpected start tag: tr. Already building a row")
            self._row_builder = RowBuilder()
            return

        if tag == "td":
            if self._row_builder is None:
                raise ValueError("Unexpected start tag: td. No row is being built")
            if self._row_builder.header is None:
                self._parsing_header = True
                return
            else:
                self._parsing_cell = True
                return

        if tag == "a" and self._parsing_cell:
            if self._row_builder is None:
                raise ValueError("Unexpected start tag: a. No row is being built")

            href = self._get_attr(attrs, "href")
            if href is None:
                raise ValueError("Link cell found without href attribute")

            self._cell_builder = CellBuilder().set_url(href.strip())
            return

    def handle_endtag(self, tag: str) -> None:
        if not self._in_table and tag == "table":
            raise ValueError("Unexpected end tag: table")

        if tag == "table":
            self._in_table = False
            return

        if not self._in_table:
            return

        if tag == "tr":
            if self._row_builder is None:
                raise ValueError("Unexpected end tag: tr. No row is being built")
            row = self._row_builder.build()
            self._parsed_rows.append(row)
            self._row_builder = None
            return

        if tag == "td":
            if self._row_builder is None:
                raise ValueError("Unexpected start tag: td. No row is being built")
            if self._parsing_header:
                self._parsing_header = False
                return
            if self._parsing_cell:
                self._parsing_cell = False
                return

        if tag == "a":
            if self._row_builder is None:
                raise ValueError("Unexpected start tag: a. No row is being built")
            if self._cell_builder is None:
                raise ValueError("Unexpected start tag: a. No link cell is being built")
            link = self._cell_builder.build()
            self._row_builder.add_cell(link)
            self._cell_builder = None
            return

    def handle_data(self, data: str) -> None:
        if not self._in_table:
            return

        if self._parsing_header:
            if self._row_builder is None:
                raise ValueError("Unexpected data: header cell found outside of a row")
            self._row_builder.set_header(data.strip())
            return

        if self._parsing_cell:
            if self._row_builder is None:
                raise ValueError("Unexpected data: cell found outside of a row")

            if data.strip() == "/":
                return

            if self._cell_builder is not None:
                self._cell_builder.set_name(data.strip())
            else:
                days = data.strip().split("/")
                for day in days:
                    self._row_builder.add_cell(Cell(name=day, url=None))

            return

    @staticmethod
    def _get_attr(
        attrs: list[tuple[str, str | None]],
        attr_name: str,
    ) -> str | None:
        for name, value in attrs:
            if name == attr_name:
                return value
        return None

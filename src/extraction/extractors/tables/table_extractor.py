from typing import List, Optional
from pdfplumber.page import Page


class TableExtractor:

    def __init__(self):
        self.tables: List[List[str]] = []
        self.min_rows = 2
        self.min_cols = 2
        self.max_empty_ratio = 0.5

    def on_page(self, page: Page) -> None:
        """Extract tables from a single PDF page"""
        table = page.extract_table()
        if table:
            self.tables.append(table)

    def build_result(self) -> List[str]:
        """Return processed tables after all pages have been handled"""
        self.tables = self.process_tables(self.tables)
        normalized_tables = self.normalize_tables(self.tables)
        return normalized_tables

    def process_tables(self, tables: List[List[str]]) -> List[List[str]]:
        """Filter tables according to min rows/cols and max empty cell ratio"""
        processed_tables = []

        for table in tables:
            rows = len(table)
            cols = max(len(row) for row in table) if table else 0
            if rows < self.min_rows or cols < self.min_cols:
                continue

            processed_rows = []
            for row in table:
                empty_cells = sum(1 for cell in row if not cell)
                num_cells = len(row)
                if num_cells == 0:
                    continue
                if empty_cells / num_cells <= self.max_empty_ratio:
                    processed_rows.append(row)

            if processed_rows:
                processed_tables.append(processed_rows)


        return processed_tables



    def normalize_tables(self, tables: List[List[List[str]]]) -> List[str]:
        normalized_rows: List[str] = []

        for table_index, table in enumerate(tables):
            if not table or len(table) < 2:
                continue

            headers = table[0]

            for row_index, row in enumerate(table[1:]):
                parts = []

                for header, cell in zip(headers, row):
                    cell = cell.strip()
                    header = header.strip()

                    if not cell or not header:
                        continue

                    # pomijamy czyste indeksy typu "1", "2"
                    if header.lower() in {"id", "lp", "no", "index"}:
                        continue

                    parts.append(f"{header}: {cell}")

                if parts:
                    text = (
                            f"Tabela {table_index + 1}, wiersz {row_index + 1}. "
                            + " | ".join(parts)
                    )
                    normalized_rows.append(text)

        return normalized_rows



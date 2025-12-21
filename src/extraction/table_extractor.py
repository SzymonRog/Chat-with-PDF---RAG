from pathlib import Path
from typing import List, Any
import pdfplumber

class TableExtractor:

    def __init__(self):
        self.tables = []
        self.min_rows = 2
        self.min_cols = 2
        self.max_empty_ratio = 0.5

    def extract(self, pdf_path: Path) -> List[Any]:
        """Extract tables from PDF"""
        with pdfplumber.open(pdf_path) as pdf:

            for page in pdf.pages:
                table = page.extract_table()
                if table is not None:
                    self.tables.append(table)


        processed_tables = self.process_tables(self.tables)
        return self.tables

    def process_tables(self, tables: List[Any]) -> List[Any]:
        """Process tables"""
        processed_tables = []
        for table in tables:
            rows = len(table)
            cols = max(len(row) for row in table)

            if rows < self.min_rows or cols < self.min_cols:
                continue

            processed_rows = []
            for row in table:

                empty_cells = sum(1 for cell in row if not cell)
                num_cells = len(row)
                ratio = empty_cells / num_cells
                if ratio > self.max_empty_ratio:
                    continue
                else:
                    processed_rows.append(row)

            if processed_rows:
                processed_tables.append(processed_rows)

            self.tables = processed_tables
        return processed_tables
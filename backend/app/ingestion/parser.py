import csv
import io
from pathlib import Path
from typing import IO


def _read_text(file: IO[bytes] | IO[str]) -> str:
    value = file.read()
    if isinstance(value, bytes):
        return value.decode("utf-8-sig")
    return value


def parse_csv(file: IO[bytes] | IO[str]) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(_read_text(file))))


def parse_file(file: IO[bytes] | IO[str], filename: str) -> list[dict[str, str]]:
    suffix = Path(filename).suffix.lower()
    if suffix == ".csv":
        return parse_csv(file)
    if suffix in {".xlsx", ".xls"}:
        try:
            import pandas as pd
        except ImportError as exc:
            raise ValueError("Excel uploads require the pandas dependency") from exc
        return pd.read_excel(file).fillna("").to_dict(orient="records")
    if suffix == ".pdf":
        try:
            import pdfplumber
        except ImportError as exc:
            raise ValueError("PDF uploads require the pdfplumber dependency") from exc
        rows: list[dict[str, str]] = []
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    headers = [str(header or "").strip() for header in table[0]]
                    rows.extend(dict(zip(headers, row)) for row in table[1:])
        if not rows:
            raise ValueError("No table found in PDF upload")
        return rows
    raise ValueError("Only CSV, Excel, and PDF uploads are supported")

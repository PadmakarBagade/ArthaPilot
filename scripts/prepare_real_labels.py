"""Prepare private hand labels without exposing private row contents."""

import csv
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.categorise.cleaner import clean_merchant


INPUT = ROOT / "data" / "private" / "labeled_raw.csv"
LABELS = ROOT / "data" / "private" / "labeled.csv"
SPLIT = ROOT / "data" / "private" / "labeled_split.csv"


def _usable_split(rows: list[dict[str, str]]) -> str | None:
    for name in ("split", "dataset_split", "train_test"):
        if name in rows[0] and {row.get(name, "").strip().lower() for row in rows} <= {
            "train",
            "test",
        }:
            return name
    return None


def prepare() -> dict[str, int | bool]:
    with INPUT.open(newline="", encoding="utf-8") as handle:
        source = list(csv.DictReader(handle))
    if not source:
        raise ValueError("labeled_raw.csv is empty")
    description_column = next(
        (name for name in ("raw_description", "description", "merchant") if name in source[0]),
        None,
    )
    category_column = next(
        (name for name in ("true_category", "category", "label") if name in source[0]),
        None,
    )
    if not description_column or not category_column:
        raise ValueError("labeled_raw.csv needs description and category columns")
    recurring_column = next(
        (name for name in ("is_recurring", "recurring") if name in source[0]), None
    )
    rows = []
    dropped = 0
    for row in source:
        category = row.get(category_column, "").strip()
        if not category:
            dropped += 1
            continue
        rows.append(
            {
                "raw_description": row.get(description_column, "").strip(),
                "true_category": category,
                "is_recurring": (
                    row.get(recurring_column, "False").strip().lower()
                    if recurring_column
                    else "False"
                ),
                "_source_split": row.get("split", row.get("dataset_split", row.get("train_test", ""))).strip().lower(),
            }
        )
    LABELS.parent.mkdir(parents=True, exist_ok=True)
    with LABELS.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["raw_description", "true_category", "is_recurring"])
        writer.writeheader()
        writer.writerows({key: row[key] for key in ("raw_description", "true_category", "is_recurring")} for row in rows)

    split_column = _usable_split(source)
    if split_column:
        split_rows = [{**row, "split": row["_source_split"]} for row in rows]
    else:
        by_merchant: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in rows:
            by_merchant[clean_merchant(row["raw_description"])].append(row)
        merchants = sorted(by_merchant)
        random.Random(42).shuffle(merchants)
        train_count = round(len(merchants) * 0.7)
        train_merchants = set(merchants[:train_count])
        split_rows = [
            {**row, "split": "train" if clean_merchant(row["raw_description"]) in train_merchants else "test"}
            for row in rows
        ]
    with SPLIT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["raw_description", "true_category", "is_recurring", "split"])
        writer.writeheader()
        writer.writerows(
            {key: row[key] for key in ("raw_description", "true_category", "is_recurring", "split")}
            for row in split_rows
        )
    counts = Counter(row["true_category"] for row in rows)
    print(f"rows={len(rows)} dropped={dropped} train_rows={sum(r['split'] == 'train' for r in split_rows)} test_rows={sum(r['split'] == 'test' for r in split_rows)}")
    print("rows_per_category=" + ",".join(f"{key}:{counts[key]}" for key in sorted(counts)))
    print(f"uncategorised={counts.get('Uncategorised', 0)}")
    print(f"used_existing_split={bool(split_column)}")
    return {"rows": len(rows), "dropped": dropped}


if __name__ == "__main__":
    prepare()

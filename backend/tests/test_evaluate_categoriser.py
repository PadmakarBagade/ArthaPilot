from pathlib import Path

import scripts.evaluate_categoriser as evaluator
from scripts.evaluate_categoriser import (
    split_by_merchant,
    write_report,
)


def test_merchant_level_split_has_no_overlap():
    rows = [
        {"raw_description": "UPI/ALPHA/111111", "true_category": "shopping"},
        {"raw_description": "UPI/ALPHA/222222", "true_category": "shopping"},
        {"raw_description": "BETA ONE", "true_category": "utilities"},
        {"raw_description": "GAMMA ONE", "true_category": "groceries"},
        {"raw_description": "DELTA ONE", "true_category": "income"},
    ]

    train, test = split_by_merchant(rows, seed=42)

    from app.categorise.cleaner import clean_merchant

    train_merchants = {clean_merchant(row["raw_description"]) for row in train}
    test_merchants = {clean_merchant(row["raw_description"]) for row in test}
    assert train_merchants.isdisjoint(test_merchants)


def test_real_section_is_skipped_when_files_are_missing(tmp_path: Path):
    evaluator.REAL_DATASET = tmp_path / "missing.csv"
    evaluator.REAL_SPLIT_DATASET = tmp_path / "missing_split.csv"
    assert evaluator._evaluate_real([]) is None

    report = tmp_path / "report.md"
    write_report([], report, skipped_real=True)

    content = report.read_text(encoding="utf-8")
    assert "Skipped" in content
    assert "Real held-out" not in content


def test_report_contains_no_private_text(tmp_path: Path):
    report = tmp_path / "report.md"
    result = {
        "source": "Real held-out",
        "rows": 1,
        "excluded": 0,
        "correct": 1,
        "total": 1,
        "accuracy": 1.0,
        "labels": ["Shopping"],
        "precision": [1.0],
        "recall": [1.0],
        "support": [1],
        "matrix": [[1]],
        "private_text": "PRIVATE_MERCHANT_TOKEN",
    }
    write_report([result], report)

    assert "PRIVATE_MERCHANT_TOKEN" not in report.read_text(encoding="utf-8")

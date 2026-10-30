"""Evaluate categorisation by data source without exposing transaction text."""

import argparse
import csv
import random
import sys
import tempfile
from pathlib import Path

from sklearn.metrics import confusion_matrix, precision_recall_fscore_support

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.categorise.cleaner import clean_merchant
from app.categorise.model import categorise_by_model, train_model
from app.recurring.detector import detect_recurring
from app.categorise.rules import UNCATEGORISED, categorise_by_rules


ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC_DATASET = ROOT / "data" / "labeled" / "labeled_synthetic.csv"
REAL_DATASET = ROOT / "data" / "private" / "labeled.csv"
REAL_SPLIT_DATASET = ROOT / "data" / "private" / "labeled_split.csv"
MODEL_PATH = ROOT / "backend" / "app" / "categorise" / "categoriser.joblib"
REPORT_PATH = ROOT / "docs" / "validation_report.md"
SPLIT_SEED = 42

CATEGORY_NAMES = {
    "debt": "EMI/Loan",
    "food_delivery": "Food Delivery",
    "groceries": "Groceries",
    "housing": "Rent",
    "income": "Other Income",
    "investments": "Investment/SIP",
    "shopping": "Shopping",
    "subscriptions": "Subscriptions",
    "utilities": "Utilities",
}


def _label(value: str) -> str:
    return CATEGORY_NAMES.get(value.strip().lower(), value.strip())


def _read_rows(dataset_path: Path) -> list[dict[str, str]]:
    with dataset_path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _merchant(row: dict[str, str]) -> str:
    return clean_merchant(row["raw_description"])


def split_by_merchant(
    rows: list[dict[str, str]],
    test_fraction: float = 0.2,
    seed: int = SPLIT_SEED,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Split rows while ensuring each cleaned merchant belongs to one side."""
    if not 0 < test_fraction < 1:
        raise ValueError("test_fraction must be between 0 and 1")
    merchants = sorted({_merchant(row) for row in rows})
    random.Random(seed).shuffle(merchants)
    test_count = max(1, round(len(merchants) * test_fraction))
    test_merchants = set(merchants[:test_count])
    train = [row for row in rows if _merchant(row) not in test_merchants]
    test = [row for row in rows if _merchant(row) in test_merchants]
    return train, test


def _write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["raw_description", "true_category"])
        writer.writeheader()
        writer.writerows(
            {key: row[key] for key in ("raw_description", "true_category")}
            for row in rows
        )


def _classify(description: str, model_path: Path) -> str:
    merchant = clean_merchant(description)
    category, confidence = categorise_by_rules(merchant)
    if confidence:
        return category
    return categorise_by_model(merchant, model_path)[0]


def _classify_with_layer(description: str, model_path: Path) -> tuple[str, str]:
    merchant = clean_merchant(description)
    category, confidence = categorise_by_rules(merchant)
    if confidence:
        return category, "rules"
    category, _ = categorise_by_model(merchant, model_path)
    return category, "ml" if category != UNCATEGORISED else "uncategorised"


def measure(
    rows: list[dict[str, str]],
    model_path: Path,
    source: str,
) -> dict:
    expected = [_label(row["true_category"]) for row in rows]
    classified = [_classify_with_layer(row["raw_description"], model_path) for row in rows]
    predicted = [item[0] for item in classified]
    layers = {layer: sum(current == layer for _, current in classified) for layer in ("rules", "ml", "uncategorised")}
    excluded = sum(label == UNCATEGORISED for label in expected)
    scored = [
        (actual, guess)
        for actual, guess in zip(expected, predicted)
        if actual != UNCATEGORISED
    ]
    scored_expected = [actual for actual, _ in scored]
    scored_predicted = [guess for _, guess in scored]
    labels = sorted(set(scored_expected) | set(scored_predicted))
    matrix = confusion_matrix(scored_expected, scored_predicted, labels=labels)
    precision, recall, _, support = precision_recall_fscore_support(
        scored_expected,
        scored_predicted,
        labels=labels,
        zero_division=0,
    )
    correct = sum(actual == guess for actual, guess in scored)
    total = len(scored)
    return {
        "source": source,
        "rows": len(rows),
        "excluded": excluded,
        "correct": correct,
        "total": total,
        "accuracy": correct / total if total else 0.0,
        "labels": labels,
        "precision": precision.tolist(),
        "recall": recall.tolist(),
        "support": support.tolist(),
        "matrix": matrix.tolist(),
        "layers": layers,
        "coverage": (len(rows) - layers["uncategorised"]) / len(rows) if rows else 0.0,
    }


def _format_measurement(result: dict) -> list[str]:
    lines = [
        f"### {result['source']}",
        "",
        f"- Rows evaluated: {result['rows']}",
        f"- Rows excluded (`Uncategorised` labels): {result['excluded']}",
        f"- Accuracy: {result['correct']} / {result['total']} "
        f"({result['accuracy']:.2%})",
        f"- Coverage: {result.get('coverage', 0.0):.2%}",
        "- Layer counts: " + ", ".join(
            f"{key}={value}" for key, value in result.get("layers", {}).items()
        ),
        "",
        "| Category | Precision | Recall | Support |",
        "|---|---:|---:|---:|",
    ]
    for label, precision, recall, support in zip(
        result["labels"], result["precision"], result["recall"], result["support"]
    ):
        lines.append(f"| {label} | {precision:.2%} | {recall:.2%} | {support} |")
    lines.extend(["", "Confusion matrix (rows = actual, columns = predicted):", ""])
    lines.append("| Actual \\ Predicted | " + " | ".join(result["labels"]) + " |")
    lines.append("|---|" + "---|" * len(result["labels"]))
    for label, row in zip(result["labels"], result["matrix"]):
        lines.append(f"| {label} | " + " | ".join(str(value) for value in row) + " |")
    return lines


def write_report(
    results: list[dict],
    report_path: Path,
    skipped_real: bool = False,
    recurring: dict | None = None,
) -> None:
    lines = [
        "# Validation Report",
        "",
        "Generated by `scripts/evaluate_categoriser.py`.",
        "",
        "Results contain counts and percentages only.",
        "",
        "## Categorisation accuracy",
        "",
    ]
    for result in results:
        lines.extend(_format_measurement(result))
        lines.append("")
    if skipped_real:
        lines.extend(
            [
                "## Real labelled data",
                "",
                "Skipped: `data/private/labeled.csv` and "
                "`data/private/labeled_split.csv` were not both present.",
                "",
            ]
        )
    if recurring is not None:
        lines.extend(
            [
                "## Recurring detection",
                "",
                f"- Precision: {recurring['precision']:.2%}",
                f"- Recall: {recurring['recall']:.2%}",
                f"- Predicted items: {recurring['predicted']}",
                f"- Expected items: {recurring['expected']}",
                "",
            ]
        )
    lines.extend(
        [
            "Income detection is validated by the backend unit tests.",
            "",
        ]
    )
    report_path.write_text("\n".join(lines), encoding="utf-8")


def _evaluate_synthetic() -> tuple[dict, list[dict[str, str]]]:
    rows = _read_rows(SYNTHETIC_DATASET)
    train_rows, test_rows = split_by_merchant(rows)
    with tempfile.TemporaryDirectory() as temporary:
        training_path = Path(temporary) / "synthetic_train.csv"
        model_path = Path(temporary) / "synthetic_eval.joblib"
        _write_rows(training_path, train_rows)
        train_model(training_path, model_path)
        result = measure(test_rows, model_path, "Synthetic held-out")
    return result, train_rows


def _evaluate_real(synthetic_train: list[dict[str, str]]) -> dict | None:
    if not REAL_DATASET.exists() or not REAL_SPLIT_DATASET.exists():
        return None
    real_rows = _read_rows(REAL_DATASET)
    split_rows = _read_rows(REAL_SPLIT_DATASET)
    split_by_id = {row["raw_description"]: row["split"].strip().lower() for row in split_rows}
    real_train = [row for row in real_rows if split_by_id.get(row["raw_description"]) == "train"]
    real_test = [row for row in real_rows if split_by_id.get(row["raw_description"]) == "test"]
    with tempfile.TemporaryDirectory() as temporary:
        training_path = Path(temporary) / "combined_train.csv"
        model_path = Path(temporary) / "real_eval.joblib"
        _write_rows(training_path, synthetic_train + real_train)
        train_model(training_path, model_path)
        return measure(real_test, model_path, "Real held-out")


def _evaluate_recurring() -> dict:
    expected: set[str] = set()
    predicted: set[str] = set()
    for persona in ("rahul", "priya", "arjun", "meera", "sam"):
        path = ROOT / "data" / "synthetic" / persona / "transactions.csv"
        rows = _read_rows(path)
        canonical = []
        for index, row in enumerate(rows):
            canonical.append(
                {
                    "txn_id": f"{persona}-{index}",
                    "date": __import__("datetime").date.fromisoformat(row["date"]),
                    "amount_paise": int(row["amount_paise"]),
                    "merchant": clean_merchant(row["description"]),
                    "is_recurring": row.get("is_recurring", "").lower() == "true",
                }
            )
        for row in canonical:
            if row["is_recurring"] and row["merchant"] and row["amount_paise"] < 0:
                expected.add(f"{persona}:{row['merchant']}")
        for item in detect_recurring(canonical):
            predicted.add(f"{persona}:{item['merchant']}")
    true_positive = len(expected & predicted)
    return {
        "precision": true_positive / len(predicted) if predicted else 0.0,
        "recall": true_positive / len(expected) if expected else 0.0,
        "predicted": len(predicted),
        "expected": len(expected),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, default=REPORT_PATH)
    args = parser.parse_args()

    synthetic_result, synthetic_train = _evaluate_synthetic()
    train_model(SYNTHETIC_DATASET, MODEL_PATH)
    real_result = _evaluate_real(synthetic_train)
    results = [synthetic_result] + ([real_result] if real_result else [])
    write_report(results, args.report, skipped_real=real_result is None, recurring=_evaluate_recurring())

    for result in results:
        print(
            f"{result['source']}: {result['correct']} / {result['total']} "
            f"({result['accuracy']:.2%}); excluded={result['excluded']}"
        )
    if real_result is None:
        print("Real held-out: skipped; required private files were not both present")
    print("Report:", args.report)


if __name__ == "__main__":
    main()

import csv
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GroupKFold, cross_val_score

from .rules import UNCATEGORISED


MODEL_CONFIDENCE_THRESHOLD = 0.5
DEFAULT_DATASET_PATH = (
    Path(__file__).resolve().parents[3] / "data" / "labeled" / "labeled_synthetic.csv"
)
DEFAULT_MODEL_PATH = Path(__file__).with_name("categoriser.joblib")

_CATEGORY_NAMES = {
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


def train_model(
    dataset_path: str | Path = DEFAULT_DATASET_PATH,
    model_path: str | Path = DEFAULT_MODEL_PATH,
) -> Path:
    descriptions: list[str] = []
    categories: list[str] = []
    with Path(dataset_path).open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            descriptions.append(row["raw_description"])
            categories.append(_CATEGORY_NAMES.get(row["true_category"], UNCATEGORISED))

    if not descriptions:
        raise ValueError("training dataset is empty")

    features = FeatureUnion(
        [
            ("word", TfidfVectorizer(ngram_range=(1, 2), lowercase=True, sublinear_tf=True)),
            ("char", TfidfVectorizer(analyzer="char", ngram_range=(3, 5), lowercase=True, sublinear_tf=True)),
        ]
    )
    pipeline = Pipeline(
        [
            ("features", features),
            (
                "classifier",
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=1000,
                    random_state=42,
                ),
            ),
        ]
    )
    pipeline.fit(descriptions, categories)

    destination = Path(model_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, destination)
    return destination


def merchant_grouped_cross_validate(rows: list[dict[str, str]], folds: int = 5) -> list[float]:
    """Score the model without allowing one merchant to cross a fold boundary."""
    if len(rows) < folds:
        raise ValueError("at least five labelled rows are required")
    descriptions = [row["raw_description"] for row in rows]
    categories = [_CATEGORY_NAMES.get(row["true_category"], row["true_category"]) for row in rows]
    groups = [row.get("merchant_key", row["raw_description"].upper()) for row in rows]
    groups_count = len(set(groups))
    if groups_count < folds:
        raise ValueError("at least five merchant groups are required")
    estimator = Pipeline(
        [
            ("features", FeatureUnion([
                ("word", TfidfVectorizer(ngram_range=(1, 2))),
                ("char", TfidfVectorizer(analyzer="char", ngram_range=(3, 5))),
            ])),
            ("classifier", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)),
        ]
    )
    return list(cross_val_score(estimator, descriptions, categories, groups=groups,
                                cv=GroupKFold(n_splits=folds)))


def categorise_by_model(
    merchant: str,
    model_path: str | Path = DEFAULT_MODEL_PATH,
) -> tuple[str, float]:
    if not isinstance(merchant, str):
        raise TypeError("merchant must be a string")
    if not merchant.strip():
        return UNCATEGORISED, 0.0

    pipeline = joblib.load(model_path)
    probabilities = pipeline.predict_proba([merchant])
    top_index = probabilities[0].argmax()
    confidence = float(probabilities[0][top_index])
    if confidence <= MODEL_CONFIDENCE_THRESHOLD:
        return UNCATEGORISED, confidence
    return str(pipeline.classes_[top_index]), confidence

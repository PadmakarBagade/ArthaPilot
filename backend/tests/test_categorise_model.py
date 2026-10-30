from pathlib import Path

import pytest

from app.categorise.model import (
    MODEL_CONFIDENCE_THRESHOLD,
    categorise_by_model,
    train_model,
)


def test_model_trains_saves_and_predicts(tmp_path: Path):
    model_path = train_model(model_path=tmp_path / "categoriser.joblib")

    assert model_path.exists()
    category, confidence = categorise_by_model("SWIGGY ORDER", model_path)
    assert category == "Food Delivery"
    assert confidence > MODEL_CONFIDENCE_THRESHOLD


def test_model_uses_uncategorised_for_low_confidence(tmp_path: Path):
    model_path = train_model(model_path=tmp_path / "categoriser.joblib")

    category, confidence = categorise_by_model("COMPLETELY UNKNOWN MERCHANT", model_path)

    assert confidence <= MODEL_CONFIDENCE_THRESHOLD
    assert category == "Uncategorised"


def test_model_requires_text(tmp_path: Path):
    model_path = train_model(model_path=tmp_path / "categoriser.joblib")
    with pytest.raises(TypeError, match="merchant must be a string"):
        categorise_by_model(None, model_path)

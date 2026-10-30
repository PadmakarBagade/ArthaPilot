import csv

from scripts.prepare_real_labels import prepare


def test_prepare_labels_drops_empty_categories_and_splits_by_merchant(tmp_path, monkeypatch):
    raw = tmp_path / "labeled_raw.csv"
    raw.write_text(
        "description,category,is_recurring\n"
        "UPI/ALPHA/111111,Shopping,False\n"
        "UPI/ALPHA/222222,Shopping,False\n"
        "BETA,Utilities,False\n"
        "EMPTY,,False\n",
        encoding="utf-8",
    )
    monkeypatch.setattr("scripts.prepare_real_labels.INPUT", raw)
    monkeypatch.setattr("scripts.prepare_real_labels.LABELS", tmp_path / "labeled.csv")
    monkeypatch.setattr("scripts.prepare_real_labels.SPLIT", tmp_path / "split.csv")
    result = prepare()
    assert result == {"rows": 3, "dropped": 1}
    with (tmp_path / "split.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert {row["split"] for row in rows}
    assert len({row["split"] for row in rows if "ALPHA" in row["raw_description"]}) == 1

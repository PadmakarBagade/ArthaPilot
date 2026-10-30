"""Build a hand-labelling sheet from the parsed GPay CSV.

Usage:
    python scripts/make_label_template.py data/private/gpay_transactions.csv \
        --out data/private/labeled_raw.csv --top 150

Groups transactions by a cleaned merchant key (case, spacing and leading
store numbers removed), then lists the most frequent groups first so that
labelling ~150 rows covers most of your transactions.

Self transfers are skipped: they are not spending or income, and the app
treats them as 'Transfers' automatically.
"""
import argparse
import csv
import re
from collections import defaultdict

PREFIXES = ("paid to ", "received from ")


def clean_key(description: str) -> str:
    s = description.lower().strip()
    for p in PREFIXES:
        if s.startswith(p):
            s = s[len(p):]
    s = s.replace("_", " ")
    s = re.sub(r"^\d+\s+", "", s)          # '02 TCI INDIA' -> 'tci india'
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_path")
    ap.add_argument("--out", default="data/private/labeled_raw.csv")
    ap.add_argument("--top", type=int, default=150)
    args = ap.parse_args()

    groups = defaultdict(lambda: {"example": "", "count": 0, "total": 0, "dirs": set()})
    total_rows = 0
    with open(args.csv_path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["is_self_transfer"] == "True":
                continue
            total_rows += 1
            g = groups[clean_key(r["raw_description"])]
            g["example"] = g["example"] or r["raw_description"]
            g["count"] += 1
            g["total"] += abs(int(r["amount_paise"]))
            g["dirs"].add(r["direction"])

    ranked = sorted(groups.items(), key=lambda kv: (-kv[1]["count"], kv[0]))
    top = ranked[: args.top]

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["raw_description", "times_seen", "total_rupees",
                    "direction", "true_category", "is_recurring"])
        for key, g in top:
            w.writerow([g["example"], g["count"], round(g["total"] / 100),
                        "/".join(sorted(g["dirs"])), "", ""])

    covered = sum(g["count"] for _, g in top)
    print(f"{len(groups)} unique merchants in {total_rows} transactions")
    print(f"Sheet has the top {len(top)} merchants, covering {covered} "
          f"transactions ({covered / total_rows:.0%}) -> {args.out}")


if __name__ == "__main__":
    main()

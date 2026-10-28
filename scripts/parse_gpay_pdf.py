"""Parse a Google Pay (GPay) transaction statement PDF into canonical CSV.

Usage:
    python scripts/parse_gpay_pdf.py data/private/gpay_statement.pdf \
        --out data/private/gpay_transactions.csv

Needs the `pdftotext` command (poppler-utils). Layout mode keeps each
transaction's date, details and amount on one line.

Output columns (canonical format from the build guide, Section 4.1):
    txn_id, date, time, amount_paise, direction, raw_description,
    counterparty, bank_account, is_self_transfer, source
amount_paise: positive = money in, negative = money out.
"""
import argparse
import csv
import hashlib
import re
import subprocess
import sys
from datetime import datetime

HEAD = re.compile(
    r"^\s*(\d{2} [A-Za-z]{3}, \d{4})\s+"
    r"(Paid to|Received from|Self transfer to)\s+(.+?)\s+₹([\d,]+(?:\.\d+)?)\s*$"
)
TIME_UPI = re.compile(
    r"^\s*(\d{2}:\d{2} [AP]M)\s+UPI Transaction ID:\s*(\d+)\s*$"
)
BANK = re.compile(r"^\s*(Paid by|Paid to)\s+(.+?)\s*$")
SENT = re.compile(r"₹([\d,]+(?:\.\d+)?)")


def to_paise(text: str) -> int:
    rupees, _, frac = text.replace(",", "").partition(".")
    frac = (frac + "00")[:2]
    return int(rupees) * 100 + int(frac)


def extract_text(pdf_path: str) -> str:
    """Return layout text. Prefers pdftotext; falls back to pdfplumber.

    pdfplumber's default x_tolerance=3 glues words together
    ('PaidtoANITA...'), so the fallback must use x_tolerance=1.5.
    """
    try:
        return subprocess.run(
            ["pdftotext", "-layout", pdf_path, "-"],
            check=True, capture_output=True, text=True,
        ).stdout
    except (FileNotFoundError, subprocess.CalledProcessError):
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            return "\f".join(
                (p.extract_text(x_tolerance=1.5, layout=True) or "")
                for p in pdf.pages
            )


def parse(text: str):
    lines = text.splitlines()
    rows, i = [], 0
    while i < len(lines):
        m = HEAD.match(lines[i])
        if not m:
            i += 1
            continue
        date_s, kind, name, amt = m.groups()
        time_s = upi = bank = None
        # the next few non-empty lines hold time + UPI id, then the bank line
        j = i + 1
        while j < len(lines) and j <= i + 6:
            t = TIME_UPI.match(lines[j])
            if t:
                time_s, upi = t.groups()
            else:
                b = BANK.match(lines[j])
                if b and time_s:
                    bank = b.group(2)
                    break
            j += 1
        if not (time_s and upi):
            print(f"WARNING: could not finish record near line {i}", file=sys.stderr)
            i += 1
            continue
        dt = datetime.strptime(f"{date_s} {time_s}", "%d %b, %Y %I:%M %p")
        paise = to_paise(amt)
        is_self = kind == "Self transfer to"
        sign = 1 if kind == "Received from" else -1
        rows.append({
            "txn_id": hashlib.sha1(f"{upi}|{dt.isoformat()}|{paise}".encode()).hexdigest()[:16],
            "date": dt.date().isoformat(),
            "time": dt.strftime("%H:%M"),
            "amount_paise": sign * paise,
            "direction": "in" if sign == 1 else "out",
            "raw_description": f"{kind} {name.strip()}",
            "counterparty": name.strip(),
            "bank_account": bank or "",
            "is_self_transfer": is_self,
            "source": "real_gpay",
        })
        i = j + 1
    return rows


def header_totals(text: str):
    """Read the 'Sent' and 'Received' totals printed on page 1."""
    first = text.split("\f")[0]
    nums = SENT.findall(first)
    # page 1 summary: sent total then received total appear before transactions
    cands = [n for n in nums if to_paise(n) > 1000]
    return cands[:2]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--out", default="data/private/gpay_transactions.csv")
    args = ap.parse_args()

    text = extract_text(args.pdf)
    rows = parse(text)
    if not rows:
        print('0 rows parsed. First lines of extracted text (check for missing spaces):')
        for ln in [l for l in text.splitlines() if l.strip()][:12]:
            print('  ', repr(ln[:100]))
        sys.exit(1)
    # remove exact duplicate UPI records (a UPI id appears once per txn)
    seen, unique = set(), []
    for r in rows:
        key = (r["txn_id"])
        if key not in seen:
            seen.add(key)
            unique.append(r)

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(unique[0].keys()))
        w.writeheader()
        w.writerows(unique)

    out = [r for r in unique if r["direction"] == "out" and not r["is_self_transfer"]]
    inn = [r for r in unique if r["direction"] == "in"]
    selft = [r for r in unique if r["is_self_transfer"]]
    sent = sum(-r["amount_paise"] for r in out) / 100
    recv = sum(r["amount_paise"] for r in inn) / 100
    print(f"Parsed {len(unique)} transactions -> {args.out}")
    print(f"  paid out (excl. self transfers): {len(out)} rows, Rs {sent:,.2f}")
    print(f"  received:                        {len(inn)} rows, Rs {recv:,.2f}")
    print(f"  self transfers (excluded):       {len(selft)} rows")
    print("Compare with the totals printed on page 1 of the statement:")
    print("  Sent and Received should match the two numbers above.")


if __name__ == "__main__":
    main()
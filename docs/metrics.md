# Financial health metrics

Phase 3 uses integer paise for every money value. Ratios and scores are
floating-point values. The executable definitions live in
[`backend/app/metrics/config.py`](../backend/app/metrics/config.py); tests
import those values rather than duplicating thresholds.

## Window

The default window is the last six complete calendar months, capped at six
even when the API `months` parameter is larger. A month is complete when the
transaction range covers its first through last day. If fewer than three
complete months exist, all months containing data are used and listed as
`partial_months`. Monthly averages use `months_used`.

## Money definitions

- **Income:** positive transactions categorised `Salary` or `Other Income`.
  Transfers, self-transfers, and transfer-labelled refunds are excluded.
- **Expenses:** negative transactions excluding rows flagged
  `is_self_transfer`, `Credit Card Payment`, and `Investment/SIP`. Outgoing
  `Transfers` to other people count as variable expenses; incoming transfers
  never count as income.
- **Savings:** income minus expenses. Investment/SIP is saved, not spent.
- **Fixed expenses:** `Rent`, `Utilities`, `EMI/Loan`, `Insurance`, and
  `Subscriptions`. All other included expenses are variable.
- **Debt payments:** EMI/Loan transactions plus card minimum dues, plus loan
  EMI values only when EMI transactions are not present.
- **Liquid savings:** balances of `savings` and `current` accounts only.
- Synthetic account balances are defined in the persona story before scoring
  and are loaded from each persona's `accounts.csv`. Credit-card accounts are
  retained for provenance but are not liquid.
- **Person-to-person outflow share:** outgoing non-self `Transfers` divided by
  included expenses. These rows are derived-tagged `person_to_person`; when the
  share exceeds 30%, the report says that this share cannot be classified.

## Raw metrics

| Key | Definition | Availability |
|---|---|---|
| `savings_rate` | `(income - expenses) / income`, averaged by month | Income required |
| `debt_to_income` | Average monthly debt payments / average monthly income | Income required |
| `emergency_runway_months` | Liquid savings / average monthly expenses | Liquid account and expenses required |
| `fixed_expense_ratio` | Average fixed expenses / average income | Informational; weight 0 |
| `credit_utilisation` | Total card balances / total card limits | No cards is `not_applicable` |
| `spending_volatility` | Population standard deviation / mean of monthly variable spend | At least 3 months |
| `income_stability` | `1 -` coefficient of variation of monthly income, clamped to 0..1 | At least 3 income months |

Unavailable metrics return `status` `not_available` and a plain reason.
No-card utilisation returns `not_applicable`; the implementation never
invents missing balances.

## Sub-score mappings

Sub-scores are piecewise linear and clamped outside the listed points:

- savings rate: `(-0.10, 0)`, `(0.00, 25)`, `(0.10, 60)`, `(0.20, 100)`
- debt to income: `(0.10, 100)`, `(0.20, 85)`, `(0.36, 60)`, `(0.50, 25)`, `(0.60, 0)`
- emergency runway: `(0, 0)`, `(1, 25)`, `(3, 60)`, `(6, 100)`
- credit utilisation: `(0.10, 100)`, `(0.30, 75)`, `(0.50, 40)`, `(0.75, 10)`, `(1.00, 0)`
- spending volatility: `(0.10, 100)`, `(0.25, 75)`, `(0.50, 40)`, `(1.00, 0)`
- income stability: `(0.50, 0)`, `(0.75, 35)`, `(0.95, 70)`, `(1.00, 100)`

Weights are savings rate 25, debt to income 20, emergency runway 20, credit
utilisation 15, spending volatility 10, and income stability 10. The score
renormalises these weights over metrics with status `ok`; coverage is the
original available weight divided by 100. Below 50% coverage, `total_score`
is null, `band` is `Not enough data`, and the internal-only `indicative_score`
contains the renormalised result. Otherwise bands are Strong (80+), Good
(60-79), Fair (40-59), and Poor (below 40).

Every metric includes source IDs, a total count, and a truncation flag when
more than 500 IDs are involved.

## Berka category mapping

Berka uses coded `operation` and `k_symbol` fields rather than merchant
categories. The loader maps them as follows:

| Berka field/value | Canonical category |
|---|---|
| Positive amount (any operation/code) | `Other Income` |
| `k_symbol=UVER` or `LEASING` | `EMI/Loan` |
| `k_symbol=POJISTNE` | `Insurance` |
| `k_symbol=SIPO` | `Utilities` |
| `k_symbol=SANKCE` | `Fees and Charges` |
| `operation=VYBER` | `Cash Withdrawal` |
| `operation=PREVOD Z UCTU` or `PREVOD NA UCET` | `Transfers` |
| `operation=VYBER KARTOU` | `Credit Card Payment` |
| Anything else | `Uncategorised` |

Berka has no reliable salary label, so credits are never labelled `Salary`.
They are labelled `Other Income`.

Berka liquid balances use the last running `balance` value for each selected
account, converted to integer paise-like subunits. Earlier balances are not
averaged.

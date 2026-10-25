# ArthaPilot: End-to-End Build Guide

Project name: ArthaPilot (Artha = wealth in Sanskrit, plus Pilot), tagline 'Your Financial Health Copilot'. *Written so you can give it to an AI coding agent one phase at a time. Part 1 covers setup, data and the understanding layer. Part 2 covers analytics, forecasting, simulation, chat, frontend, testing, deployment and interview prep.*

## 0. How to Use This Guide With an AI Agent

1. **Give the agent one phase at a time.** Never ask for the whole app in one prompt. Each phase has a ready-to-paste prompt.
2. **Run the 'Done when' checklist** at the end of each phase before moving on.
3. **Paste the Golden Rules below at the start of every agent session**, or save them as a `CLAUDE.md` / `AGENTS.md` file in the repo root.

### Golden Rules (paste into every session)

- The LLM never calculates money. All numbers come from tested Python functions. The LLM only chooses tools and explains verified results.
- Every number shown to the user must carry an evidence reference (transaction IDs or the formula used).
- Every answer has three separate sections: **Observed Fact**, **Prediction** (with confidence), **Recommendation** (with simulated impact).
- All money is stored as integer paise (₹1 = 100 paise) to avoid floating-point errors.
- Every module gets unit tests. No phase is finished until its tests pass.
- Never commit real user data. Real statements live only in `data/private/`, which is git-ignored.
- Mask personal data (names, account numbers, phone numbers, UPI IDs) before anything is sent to the LLM.

---

## 1. What You Are Building

ArthaPilot is a web app where a user loads their financial data (a demo persona, a public dataset, or their own statement), sees one unified health picture, asks questions in plain language, and gets answers that separate what happened from what is predicted from what to do, with the expected impact of each action.

**Core outcomes mapped to the problem statement**

| Requirement | Where it is built |
| --- | --- |
| Consolidated financial-health view | Phase 4 (metrics + score), Phase 8 (dashboard) |
| Spending patterns, recurring obligations, debt pressure, cash-flow gaps | Phases 3, 4, 5 |
| Conversational answers with personalised advice | Phase 7 |
| Expected impact of each action | Phase 6 (simulator) |
| Facts vs predictions vs recommendations, with confidence | Phase 7 (answer schema) and Phase 5 (confidence) |
| Recommendations change as new data is added | Phase 9 (live update + change explainer) |

---

## 2. Tech Stack (Decided, Do Not Debate)

| Layer | Choice | Why |
| --- | --- | --- |
| Backend | Python 3.11 + FastAPI | Fast to build, great for data work |
| Data and maths | pandas, numpy, scipy, statsmodels | Standard, well tested |
| ML (optional) | scikit-learn (TF-IDF + logistic regression for categorisation) | Cheap, explainable, measurable |
| Database | SQLite via SQLAlchemy 2.0 (Postgres-ready) | Zero setup; swap later |
| Validation | Pydantic v2 | Typed API contracts |
| LLM | Claude API with tool use (model name in an env variable `CLAUDE_MODEL`; check the Anthropic docs for the current model) | Reliable tool calling |
| Frontend | Next.js 14 (App Router) + TypeScript + Tailwind CSS | Production standard |
| Charts | Recharts | Easy forecast bands and bars |
| UI components | shadcn/ui | Clean, fast |
| Testing | pytest (backend), Vitest + Playwright (frontend) | Unit and end-to-end |
| Packaging | Docker + docker-compose | One-command run |
| Deployment | Backend on Render or Railway, frontend on Vercel | Free tiers available |
| CI | GitHub Actions | Runs tests on every push |

---

## 3. Repository Structure

```
arthapilot/
├── CLAUDE.md                  # Golden Rules
├── README.md
├── docker-compose.yml
├── .env.example
├── .gitignore                 # must include data/private/ and .env
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI entry
│   │   ├── config.py
│   │   ├── db.py              # SQLAlchemy engine/session
│   │   ├── models.py          # ORM tables
│   │   ├── schemas.py         # Pydantic models
│   │   ├── ingestion/         # parsers, cleaning, anonymiser, adapters
│   │   ├── categorise/        # rules, ML model, LLM fallback
│   │   ├── recurring/         # recurring + income detection
│   │   ├── metrics/           # health metrics + score
│   │   ├── forecast/          # cash-flow forecast, gaps, stress tests
│   │   ├── simulate/          # action simulator, ranking, goals
│   │   ├── copilot/           # tool definitions, orchestrator, answer builder
│   │   ├── insights/          # behaviour, anomalies, subscription creep
│   │   └── routers/           # API routes
│   ├── tests/
│   └── requirements.txt
├── data/
│   ├── synthetic/             # generated personas (committed)
│   ├── berka/                 # downloaded public dataset (not committed if large)
│   ├── private/               # real statements (git-ignored!)
│   └── labeled/               # hand-labelled transactions for accuracy tests
├── scripts/
│   ├── generate_personas.py
│   ├── load_berka.py
│   ├── anonymise_statement.py
│   └── evaluate_categoriser.py
├── frontend/
│   ├── app/                   # pages: dashboard, spending, forecast, chat, simulator, data
│   ├── components/
│   └── lib/api.ts
└── docs/                      # architecture diagram, validation report
```

---

## 4. The Three-Layer Data Strategy

All three layers feed **one canonical schema**. The engine never knows which layer the data came from. This is what makes the validation story credible.

### 4.1 Canonical Transaction Format

Every adapter must output these columns:

| Column | Type | Notes |
| --- | --- | --- |
| `txn_id` | string | Stable hash of date + amount + description + account |
| `user_id` | string | Persona or profile ID |
| `account_id` | string | Which account or card |
| `date` | date | ISO format |
| `amount_paise` | integer | Positive = money in, negative = money out |
| `raw_description` | string | Original text, untouched |
| `merchant` | string | Cleaned merchant name (filled in Phase 2) |
| `category` | string | Filled in Phase 2 |
| `category_confidence` | float | 0 to 1 |
| `is_recurring` | bool | Filled in Phase 2 |
| `source` | string | `synthetic`, `berka`, or `real` |

### 4.2 Layer 1: Synthetic Personas

**Purpose:** controlled demos and edge cases that real data cannot give you.

Build `scripts/generate_personas.py` producing 5 personas with 12 months of transactions each, seeded with a fixed random seed so results are reproducible.

| Persona | Profile | What it demonstrates |
| --- | --- | --- |
| **Rahul** | 28, salaried ₹65,000, one EMI, credit card debt | Main demo: cash gap near month end |
| **Priya** | 34, salaried ₹1,20,000, home loan, SIPs | Healthy user; recommendations are about growth |
| **Arjun** | 26, freelancer, irregular income | Low confidence, volatile forecast |
| **Meera** | 41, dual loans, high card utilisation | Debt pressure, avalanche method |
| **Sam** | 23, first job, no savings | Emergency-fund building, goal planning |

Each persona needs: salary or irregular income on realistic dates, rent, utilities, subscriptions (Netflix, Spotify, a forgotten gym), EMIs, SIP, food delivery, UPI spends, weekend spending spikes, one or two anomalies (duplicate charge, subscription price hike), and messy merchant strings such as `SWIGGY*ORDER 4482`, `UPI/4458221/ZOMATO`, `AMZN PAY IN`.

Also generate `loans.csv`, `cards.csv` (limit, balance, APR, minimum due, due date) and `investments.csv`.

**Scenario injectors** (functions that modify a persona to demo changes): `stop_income(months)`, `add_emi(amount)`, `raise_expenses(percent)`, `add_big_purchase(amount, date)`.

### 4.3 Layer 2: Berka Public Dataset

**Purpose:** prove the engine works on real banking patterns.

- The Berka dataset (Czech bank, around 1999) has accounts, transactions, loans, orders and clients. Download it from its public source (search 'PKDD 99 Berka dataset').
- Write `scripts/load_berka.py` as an adapter: convert to the canonical format. Scale or relabel currency to a single unit and document this clearly, because the data is not in rupees.
- Berka transactions have coded types (`k_symbol`, `operation`) instead of merchant names. Map those to categories (for example, loan payment, household, insurance, statement fee) and be honest in the README that this layer tests **cash-flow, recurring detection, forecasting and loan logic**, not merchant-name categorisation.
- Pick 20 to 50 accounts that have at least 12 months of data and use them for backtests (Phase 5).

### 4.4 Layer 3: Real Anonymised Statements

**Purpose:** prove upload and categorisation handle messy real-world data.

- Collect your own statement and, with written consent, 3 to 5 volunteers' statements (CSV, Excel or PDF).
- Write `scripts/anonymise_statement.py` that removes: names, account numbers, phone numbers, UPI IDs and emails (replace with tokens like `PERSON_1`, `UPI_ID_2`) while keeping merchant names, dates and amounts.
- Write bank-specific parsers in `ingestion/parsers/` (HDFC, SBI, ICICI, Axis, plus a generic column-mapping fallback). Handle: different date formats, separate debit/credit columns vs a single signed column, opening/closing balance rows, multi-line descriptions, and PDF tables (use `pdfplumber`).
- Real files stay in `data/private/` and are never committed.
- Hand-label 200 to 300 transactions into `data/labeled/labeled.csv` (columns: `raw_description`, `true_category`, `is_recurring`). This is your ground truth for accuracy numbers.

---

## 5. Database Schema

Tables (SQLAlchemy models):

- `users` (id, name, persona\_type, created\_at)
- `accounts` (id, user\_id, type \[savings/current/credit\_card\], institution, balance\_paise, credit\_limit\_paise)
- `transactions` (canonical columns from 4.1)
- `loans` (id, user\_id, type, principal\_paise, outstanding\_paise, emi\_paise, rate\_apr, tenure\_left\_months, next\_due\_date)
- `cards` (id, user\_id, limit\_paise, balance\_paise, apr, min\_due\_paise, due\_date)
- `investments` (id, user\_id, type, value\_paise, monthly\_sip\_paise)
- `recurring_items` (id, user\_id, merchant, amount\_paise, interval\_days, next\_due\_date, confidence, txn\_ids)
- `goals` (id, user\_id, name, target\_paise, deadline)
- `snapshots` (id, user\_id, created\_at, metrics\_json, forecast\_json, recommendations\_json) used for the 'what changed' feature
- `chat_messages` (id, user\_id, role, content, answer\_json, created\_at)

---

## Phase 0: Project Setup

**Goal:** an empty but runnable skeleton.

**Agent prompt:**

> Create the repository structure from Section 3 for a project named ArthaPilot (use this name in the app title, header, README and package names). Set up a FastAPI backend with a `/health` endpoint, SQLAlchemy with SQLite, Pydantic, pytest, and a Next.js 14 + TypeScript + Tailwind + shadcn/ui frontend that calls `/health` and displays the result. Add Dockerfiles, docker-compose, `.env.example` (ANTHROPIC\_API\_KEY, CLAUDE\_MODEL, DATABASE\_URL), `.gitignore` (include `.env`, `data/private/`, `data/berka/`), `CLAUDE.md` containing the Golden Rules, and a GitHub Actions workflow that runs pytest and the frontend build.

**Done when:** `docker-compose up` starts both services; the frontend shows 'backend OK'; CI is green.

---

## Phase 1: Data Layer (All Three Sources)

**Goal:** every data source ends up as clean canonical rows in the database.

**Agent prompt:**

> Implement the database models from Section 5. Then build: (1) `scripts/generate_personas.py` creating the 5 personas in Section 4.2 with a fixed seed, including loans, cards, investments and messy merchant strings, plus the scenario injector functions; (2) `scripts/load_berka.py` converting the Berka dataset to the canonical format as described in Section 4.3; (3) `ingestion/` with a generic CSV/Excel parser, bank-specific parsers, a PDF table parser, and a cleaning pipeline (dedupe by txn\_id, normalise dates, convert rupees to integer paise, sign the amounts correctly); (4) `scripts/anonymise_statement.py`; (5) API routes: `POST /upload` (file upload with column-mapping fallback), `GET /users`, `POST /users/{id}/load-persona`. Write tests with small fixture files for each parser, including edge cases (duplicate rows, split debit/credit columns, bad dates).

**Done when:** all five personas load into the DB; 20+ Berka accounts load; a sample real-style CSV uploads successfully; parser tests pass; no real data is tracked by git.

---

## Phase 2: Categorisation and Recurring Detection

**Goal:** turn raw lines into tagged transactions and a list of recurring obligations.

### 2A. Categorisation: three-step cascade

1. **Cleaning:** strip noise (`UPI/`, reference numbers, `*ORDER 4482`), uppercase, extract merchant token.
2. **Rules:** a dictionary of merchant keywords to categories (SWIGGY, ZOMATO → Food Delivery; NETFLIX, SPOTIFY, HOTSTAR → Subscriptions; IRCTC, UBER, OLA → Travel; AMAZON, FLIPKART → Shopping; LIC, HDFC LIFE → Insurance; ELECTRICITY, BESCOM, MSEB → Utilities). Confidence 0.95 on a rule hit.
3. **ML model:** TF-IDF (character n-grams) + logistic regression trained on the hand-labelled set and synthetic data. If the model's top probability is above 0.7, use it.
4. **LLM fallback:** only for what is still unresolved. Send only the cleaned merchant string (no amounts, no personal data), ask for one category from the fixed list, cache the result. Anything still unclear becomes `Uncategorised` and lowers the confidence score later.

Category list (fixed): Salary, Other Income, Rent, Utilities, Groceries, Food Delivery, Dining, Transport, Shopping, Entertainment, Subscriptions, Health, Insurance, Education, EMI/Loan, Credit Card Payment, Investment/SIP, Transfers, Cash Withdrawal, Fees and Charges, Travel, Uncategorised.

### 2B. Recurring detection

Group by cleaned merchant. A group is recurring if it has at least 3 occurrences, the gaps are close to a fixed interval (7, 14, 30, 90, 365 days; allow ±3 days), and amounts are within about ±10% (allow wider for utilities). Output interval, typical amount, next due date, and a confidence score based on regularity and number of occurrences.

### 2C. Income detection

Salary = the largest credit repeating monthly within a few days of the same date. Everything else = irregular income. Compute income regularity (coefficient of variation of monthly income) for use in confidence.

**Agent prompt:**

> Implement `categorise/` with the cascade above (cleaner, rules, scikit-learn model with saved artefact, cached LLM fallback that receives only cleaned merchant strings), `recurring/` with recurring and income detection, and `scripts/evaluate_categoriser.py` which runs on `data/labeled/labeled.csv` and prints accuracy, per-category precision/recall and a confusion matrix, saving a report to `docs/validation_report.md`. Add API routes `POST /users/{id}/process` and `GET /users/{id}/recurring`. Write unit tests for the cleaner, the rules, and recurring detection including irregular-gap edge cases.

**Done when:** categoriser accuracy on the labelled set is measured and written down (target 85%+ on real statements); recurring detection finds the planted subscriptions and EMIs in every persona; the report file exists.

---

## Phase 3: Financial Health Metrics and Score

**Goal:** the consolidated view, computed by pure, tested functions.

| Metric | Formula | Healthy range |
| --- | --- | --- |
| Savings rate | (income - expenses) / income | 20% or more |
| Debt-to-income (DTI) | monthly debt payments (EMIs + card minimums) / monthly income | under 36% |
| Emergency runway | liquid savings / average monthly expenses (months) | 6 or more |
| Fixed expense ratio | (rent + utilities + EMIs + insurance + subscriptions) / income | under 50% |
| Credit utilisation | card balances / card limits | under 30% |
| Spending volatility | std deviation / mean of monthly variable spend | lower is better |
| Income stability | 1 - coefficient of variation of monthly income | higher is better |

**Health Score (0 to 100):** weighted sum of sub-scores, each mapped to 0-100 using simple thresholds.

| Component | Weight |
| --- | --- |
| Savings rate | 25% |
| Debt-to-income | 20% |
| Emergency runway | 20% |
| Credit utilisation | 15% |
| Spending volatility | 10% |
| Income stability | 10% |

The function returns the total, every sub-score, the raw value behind each, and a plain-language reason (for example, 'Savings rate 8% is below the 20% target, costing you 12 points'). Store the weights in one config file so they can be tuned and explained.

Every metric also returns `evidence`: the list of `txn_id`s or loan/card rows it was computed from. This powers the evidence links later.

**Agent prompt:**

> Implement `metrics/` with one pure function per metric in the table, a `compute_health_score()` that returns total, sub-scores, raw values, reasons and evidence IDs, and a `GET /users/{id}/health` route. Use integer paise throughout. Write unit tests with hand-calculated expected values for at least three small synthetic cases, plus edge cases (zero income, no debt, no cards, one month of data).

**Done when:** Rahul scores noticeably lower than Priya; every metric has a test with a hand-verified number; the API returns reasons and evidence IDs.

---

## Phase 4: Data-Quality and Confidence Engine

**Goal:** an honest 0 to 100% confidence number with reasons, attached to every prediction and answer.

Confidence starts at 100 and loses points for:

| Issue | Penalty |
| --- | --- |
| Fewer than 6 months of data (scaled: 3 months = bigger penalty) | up to 30 |
| Irregular income (high coefficient of variation) | up to 20 |
| Uncategorised transactions above 5% | up to 15 |
| Credit card or loan accounts missing | 10 each |
| Large gaps in transaction dates | up to 10 |
| Few observations behind a recurring pattern | up to 10 |

Output: `{score: 78, level: 'Medium', reasons: ['Only 4 months of data', '6% uncategorised'], how_to_improve: ['Upload 8 more months', 'Link your credit card statement']}`.

**Agent prompt:**

> Implement `metrics/confidence.py` returning score, level (High 80+, Medium 55-79, Low below 55), reasons and how\_to\_improve actions, based on the penalty table. Add tests for each penalty and a route `GET /users/{id}/confidence`.

**Done when:** Arjun (freelancer) gets lower confidence than Priya, with clearly stated reasons.

---

## Phase 5: Prediction Engine (Cash-Flow Forecast)

**Goal:** a 90-day daily balance forecast with best/likely/worst bands, gap detection and stress tests.

### 5A. Forecast method (keep it explainable)

For each future day, expected balance change = scheduled items + expected variable spend.

1. **Scheduled inflows:** salary on its usual date (from income detection).
2. **Scheduled outflows:** every recurring item on its next due date, plus EMIs and card minimum dues.
3. **Variable spend:** average daily variable spend by day-of-week (captures weekend spikes), computed from the last 3 to 6 months.
4. **Uncertainty:** run a Monte Carlo simulation (1,000 runs). In each run, sample daily variable spend from the user's own historical distribution (bootstrap sampling), and shift irregular income within its historical range. Take the 10th, 50th and 90th percentile balances per day as worst, likely and best.
5. **Gap detection:** find days where the 10th-percentile balance goes below a safe threshold (default: one week of average spending, adjustable). Report the date, expected balance, and probability of going below zero.

### 5B. Stress tests (a unique feature)

Pre-built scenarios that re-run the forecast: income stops for 1, 2 or 3 months; expenses rise 15%; a one-off emergency expense of ₹50,000; a new EMI. Output: survival time in days and the first breach date.

### 5C. Backtesting (this is your proof of accuracy)

For Berka accounts and real statements: hide the last 30 to 60 days, forecast them from earlier data, and compare. Report **MAPE or MAE on balance**, and **how often the actual balance fell inside the 10-90 band** (a calibration number, ideally around 80%). Save to `docs/validation_report.md`.

**Agent prompt:**

> Implement `forecast/` with: `build_schedule()` (recurring + income + EMIs + card dues), `variable_spend_model()` (per-weekday daily averages and empirical distribution), `monte_carlo_forecast(days=90, runs=1000, seed=42)` returning p10/p50/p90 daily balances, `detect_gaps()`, and `stress_test(scenario)`. Add `scripts/backtest.py` that runs the hold-out test on Berka and real data and writes MAE and band-coverage to the validation report. Routes: `GET /users/{id}/forecast`, `GET /users/{id}/gaps`, `POST /users/{id}/stress-test`. Test with a deterministic persona where the expected gap date is known.

**Done when:** Rahul shows a gap near month end; stress test 'income stops 2 months' returns a survival number; backtest numbers are in the report.

---

## Phase 6: Simulation and Recommendation Engine

**Goal:** the heart of the project. Every recommendation is a simulated change with a measured before/after.

### 6A. The core simulator

One function: `simulate(user_state, action) -> {before, after, delta}`. It copies the user's state, applies the action, then re-runs metrics (Phase 3), the forecast and gap detection (Phase 5), and returns both results plus the differences.

**Action library** (each is a small class with `apply(state)`):

| Action | What it changes |
| --- | --- |
| Cut category by X% | Variable spend in a category |
| Cancel subscription(s) | Removes recurring items |
| Pay extra on a debt | Reduces outstanding, interest and future EMI burden |
| Avalanche or snowball payoff order | Allocates a monthly extra amount across debts |
| Move ₹X/month to savings or SIP | Adds an outflow, grows savings |
| Delay a purchase by N days | Shifts a one-off outflow |
| Make a purchase (cash / EMI) | Adds one-off outflow or new EMI |
| Refinance or prepay loan | Changes rate or tenure |
| Build emergency buffer | Targets runway of N months |

Debt payoff maths must be exact: monthly interest = outstanding x APR / 12; show total interest saved and months saved.

### 6B. Best Next Move ranking (unique feature)

Automatically simulate 5 to 8 relevant actions, then rank by `impact_score / effort_score`:

- **Impact** = weighted improvement in health score + cash gaps avoided + interest saved.
- **Effort** = how much lifestyle change is required (cancelling an unused subscription is low effort; cutting food by 40% is high).
- Show the top 1 as 'Best Next Move' and the rest as alternatives, each with the one-line reason.

### 6C. Affordability verdict

For 'Can I afford ₹X?': simulate three paths (pay cash now, 6-month EMI, wait N days). Verdict rules:

- **Yes:** the 10th-percentile balance stays above the safe threshold and runway stays above the minimum.
- **Risky:** the likely case is fine but the worst case breaches the threshold.
- **No:** the likely case already breaches the threshold or it pushes credit utilisation above 50%.

Always return the safer alternative and its impact.

### 6D. Goal planner

Input: target amount and deadline. Output: required monthly saving, feasibility (compared to current surplus), and the adjustments needed if it is not feasible.

### 6E. Guardrails

Never recommend: stopping debt payments, skipping the emergency fund for investing when runway is below 3 months, or high-risk investments. If confidence is Low, recommendations say so and suggest collecting more data first.

**Agent prompt:**

> Implement `simulate/` with the action library above, `simulate(state, action)`, `rank_actions(state)` returning Best Next Move plus alternatives with impact and effort scores, `affordability(state, amount, date)`, `goal_plan(state, target, deadline)`, and exact debt payoff maths (avalanche and snowball). Add the guardrails. Routes: `POST /users/{id}/simulate`, `GET /users/{id}/best-moves`, `POST /users/{id}/affordability`, `POST /users/{id}/goal`. Tests: debt payoff against hand-calculated amortisation, simulator purity (original state unchanged), ranking order on a known persona, guardrail cases.

**Done when:** for Rahul, the simulator shows a numeric before/after for 'cut food delivery 30%'; the affordability card returns Yes/Risky/No with alternatives; guardrail tests pass.

---

## Phase 7: The Conversational Copilot

**Goal:** natural-language Q&A where the LLM only routes and explains.

### 7A. Architecture

```
User question
   -> Claude (with tool definitions)
   -> picks a tool + arguments
   -> your Python runs the tool on real data
   -> returns structured JSON (numbers, evidence IDs, confidence)
   -> Claude writes the explanation, strictly from that JSON
   -> answer validator checks every number appears in the tool output
   -> UI renders Fact / Prediction / Recommendation cards
```

### 7B. Tools to expose

| Tool | Answers questions like |
| --- | --- |
| `get_spending_breakdown(period, category?)` | Where did my money go in March? |
| `explain_month_change(month_a, month_b)` | Why was my spending high in March? |
| `get_recurring_obligations()` | What bills do I have coming? |
| `get_health_score()` | How healthy are my finances? |
| `run_forecast(days)` and `get_gaps()` | Will I run short before salary? |
| `check_affordability(amount, date)` | Can I afford a ₹45,000 laptop? |
| `rank_best_moves()` | What should I do first? |
| `simulate_action(action, params)` | What if I cut dining out by 20%? |
| `debt_payoff_plan(extra_amount)` | Which debt should I pay first? |
| `stress_test(scenario)` | What if my income stops for 2 months? |
| `plan_goal(target, deadline)` | I want to save ₹1 lakh in 8 months |
| `get_confidence()` | How sure are you? |
| `get_transactions(filter)` | Show me the transactions behind that |

### 7C. Answer schema (mandatory)

Every answer is a JSON object validated by Pydantic before it reaches the UI:

```json
{
  "summary": "One-sentence direct answer",
  "facts": [{"text": "You spent ₹18,400 on food in 3 months", "evidence_ids": ["t1","t2"]}],
  "predictions": [{"text": "Balance likely dips to ₹2,900 on 27 Nov", "confidence": 78, "confidence_reasons": ["4 months of data"]}],
  "recommendations": [{"text": "Delay the purchase by 10 days", "impact": {"score_change": 4, "gap_avoided": true}}],
  "verdict": "Risky",
  "follow_ups": ["Show the cheaper EMI option"]
}
```

Rules enforced in code, not just in the prompt:

- Facts may only come from past data tools. Predictions only from forecast/stress tools. Recommendations only from simulator tools.
- Every number in the text must match a number in the tool results (a validator extracts numbers from the text and checks them; if any mismatch, regenerate once, then fall back to a template answer).
- If a needed tool returns low confidence, the answer must display it.
- Hindi and Marathi: add a `language` parameter; the explanation is written in the chosen language but numbers and structure are unchanged.

### 7D. Safety and privacy

- Send the LLM only aggregated tool outputs and masked merchant names, never raw statements.
- Add a visible 'What data is shared with the AI' panel.
- Add the disclaimer: 'This is guidance, not regulated financial advice.'
- Refuse or redirect questions about specific stocks, guaranteed returns or tax evasion.

**Agent prompt:**

> Implement `copilot/` using the Anthropic Python SDK with tool use. Define all tools in 7B as thin wrappers over the existing modules. Build an orchestrator loop (question -> tool calls -> structured answer). The final model output must be JSON matching the schema in 7C, validated with Pydantic. Add the number validator and a fallback template answer. Add a `language` option (en, hi, mr). Persist messages. Route: `POST /users/{id}/chat`. Write tests with a mocked LLM client that verify tool routing, schema validation, and that a fabricated number is rejected.

**Done when:** the five demo questions each return a valid three-part answer; a deliberately wrong number from a mocked model is caught; no raw transaction text is sent to the LLM.

---

## Phase 8: Frontend Screens

**Goal:** a polished, readable UI. Build with the design rules: blue for facts, orange for predictions, green for recommendations, red for risk.

| Screen | Contents |
| --- | --- |
| **1. Dashboard** | Health score gauge with breakdown, income vs expense, savings rate, debt pressure, confidence meter with reasons, 'Best Next Move' card |
| **2. Spending and Recurring** | Category donut and monthly trend, recurring obligations list with next due dates, subscription-creep and anomaly alerts, behaviour insights |
| **3. Forecast** | 90-day line with p10-p90 band, gap markers, **Danger Calendar** heatmap, stress-test buttons |
| **4. Copilot Chat** | Messages with Fact / Prediction / Recommendation cards, clickable evidence chips, verdict card, follow-up suggestions, language toggle |
| **5. Action Simulator** | Sliders and dropdowns for actions, before/after metric table, **two forecast lines (current path vs recommended path)** |
| **6. Add Data / Scenarios** | Add transaction, loan, income change, expense; scenario buttons; **What Changed** panel |
| **7. Data and Trust** | Data source switcher (Synthetic / Berka / Real upload), what is shared with AI, validation numbers, disclaimer |

**Evidence drawer:** clicking any number opens a side panel listing the exact transactions or the formula behind it.

**Agent prompt:**

> Following the UI/UX Design System in Phase 8A (simplicity rules, 4-tab navigation, design tokens), build the seven screens above in Next.js with Tailwind, shadcn/ui and Recharts, using a typed API client in `lib/api.ts`. Include the colour system, the evidence drawer, the Fact/Prediction/Recommendation card components, confidence meter with reasons, forecast band chart, calendar heatmap for gaps, and before/after dual-line chart. Add loading, empty and error states, mobile responsiveness, and a persona switcher in the header.

**Done when:** every screen renders for all five personas; clicking a number opens evidence; layout works on a phone.

---

## Phase 8A: UI/UX Design System (Minimal, Fintech, Usable by Anyone)

The interface must feel calm, trustworthy and simple: a first-time user should understand the home screen in 5 seconds without reading any instructions. The seven screens in Phase 8 are the content; this section controls how they are packaged. Where the two conflict, Phase 8A wins.

### The 10 Simplicity Rules

1. **One screen, one job.** Each screen answers one question (How am I doing? What should I ask? What if I do this?).
2. **Answer first, detail on demand.** Show the verdict and one number up front. Charts, evidence and formulas sit behind 'Show details' or the evidence drawer.
3. **Four main tabs only** (see navigation below). Everything else is a sub-view or lives in the profile menu.
4. **Plain words, no jargon.** Say 'Money left after bills', not 'DTI'. Say 'Months you can survive without income', not 'emergency runway'. Technical names appear only in an info tooltip.
5. **Every number gets a sentence.** Never show a bare metric; add a short line such as 'You keep 8 of every 100 rupees you earn. Target: 20.'
6. **One primary button per screen.** Secondary actions are plain text links.
7. **Three cards above the fold.** No more than three metric cards before the user scrolls, and one chart per card.
8. **Colour carries meaning only.** Blue = fact, orange = prediction, green = recommendation, red = risk. Nothing decorative uses these colours.
9. **Guided first run.** A new user is led through three steps, never dropped on a full dashboard.
10. **Safe and kind.** No blame language ('You overspent' becomes 'Food delivery was higher than usual'), undo for every data change, and a confirmation before anything destructive.

### Navigation: 4 Tabs

| Tab | What it contains | Replaces |
| --- | --- | --- |
| **Home** | Health score ring, Best Next Move card, top 3 alerts, small cash-flow preview | Dashboard |
| **Ask** | Chat, suggested-question chips, Fact / Prediction / Recommendation cards | Copilot chat |
| **Plan** | Segmented control with Forecast (including Danger Calendar), What-if simulator, Goals, Stress tests | Forecast, Simulator |
| **Money** | Spending, recurring bills, insights, and an 'Add data' button | Spending, Add Data |

Profile menu (top right): Data source switcher, Data and Trust, language, privacy panel, disclaimer. On phones use a bottom tab bar; on desktop use a slim left sidebar. Never nest navigation more than one level deep.

### Design Tokens (set once in Tailwind config)

| Token | Value |
| --- | --- |
| Font | Inter (fallback system-ui); numbers use tabular figures |
| Base size | 16 px body, 14 px helper text, 28 to 36 px for the main score |
| Page background | #F8FAFC |
| Card | White, 16 px radius, 1 px border #E2E8F0, soft shadow only on hover |
| Brand / primary button | #0F4C81 (deep trust blue) |
| Fact | #2563EB |
| Prediction | #D97706 |
| Recommendation | #16A34A |
| Risk | #DC2626 |
| Text | #0F172A main, #64748B secondary |
| Spacing | 8 px grid, generous white space between cards |
| Motion | 150 to 250 ms fades and number count-ups only; respect 'reduce motion' |
| Dark mode | Optional, use the same tokens inverted |

### Core Components to Build Once and Reuse

- **ScoreRing:** circular 0 to 100 score with a one-line meaning ('Fair: two things to fix').
- **MetricCard:** label in plain words, big number, one explanatory sentence, optional sparkline.
- **FactCard / PredictionCard / RecommendationCard:** coloured left border, small icon plus text label (not colour alone).
- **ConfidenceChip:** 'Confidence: Medium' that expands to reasons and how to improve it.
- **VerdictCard:** large Yes / Risky / No with the reason and a safer alternative.
- **EvidenceChip:** underlined number that opens the evidence drawer.
- **BeforeAfterBar:** two columns, current vs with this action, change shown as +/- with colour and arrow.
- **InfoTooltip:** the small 'i' that explains any financial term in one sentence.
- **Empty, Loading and Error states:** friendly one-liners and a single next step, never a blank panel.

### Indian Formats and Language

- Currency as ₹ with Indian digit grouping (₹1,25,000) and 'lakh' / 'crore' in headlines only.
- Dates as '27 Nov', never mixed formats. Show 'in 5 days' beside upcoming dates.
- Language toggle (English, Hindi, Marathi) in the profile menu; numbers and layout never change.

### First-Run Experience

1. **Landing:** one headline, one button 'Try a demo' and a secondary 'Upload my statement'. No signup needed.
2. **Step 1:** pick a demo persona or upload a file (with a short 'what we do with your data' note).
3. **Step 2:** a friendly progress screen ('Reading your transactions... finding your bills... building your forecast').
4. **Step 3:** land on Home with a gentle 10-second highlight tour (three tooltips: your score, your best next move, ask me anything).

On the Ask tab show 4 suggested question chips such as 'Can I afford a ₹45,000 laptop?' and 'Will I run short before salary?', so no one faces an empty text box.

### Trust Cues in the UI

- A small lock icon and 'Your data stays private' link in the footer and on the upload screen.
- 'Last updated' time and data period on Home ('Based on Jan to Dec, 4,210 transactions').
- 'Guidance, not financial advice' line in the footer and under every recommendation.
- Confidence shown beside every prediction; low confidence shown in amber with the reason.

### Accessibility and Responsiveness

- Mobile-first: design at 360 px wide first, then scale up.
- Contrast ratio at least 4.5:1; never use colour alone (add icon and label).
- Tap targets at least 44 px; full keyboard navigation; visible focus rings.
- Alt text and ARIA labels for charts, with a 'View as table' toggle on every chart.
- Lighthouse accessibility score of 90 or more.

### UI Acceptance Tests (all must pass before launch)

| Test | Pass condition |
| --- | --- |
| 5-second test | A new person can say what the Home screen is telling them after 5 seconds |
| First-task test | 5 first-time users each complete 'find out if I can afford a laptop' without help (at least 4 of 5 succeed) |
| Jargon check | No unexplained financial term appears on Home or Ask |
| Density check | No screen shows more than 3 metric cards or 2 charts above the fold |
| Phone check | All four tabs work one-handed on a 360 px screen |
| Accessibility | Lighthouse 90 or more; keyboard-only run-through works |

**Agent prompt:**

> Implement the design system from Phase 8A: set the design tokens in the Tailwind config, build the reusable components listed above with Storybook or a simple /components preview page, implement the 4-tab navigation (bottom bar on mobile, left sidebar on desktop) with Plan using a segmented control, build the 3-step first-run flow with suggested question chips, apply Indian currency and date formatting through one shared formatter, add info tooltips for every financial term through one glossary file, and add 'View as table' toggles to charts. Then run Lighthouse and fix anything below 90 accessibility.

**Done when:** every UI acceptance test passes and a person who has never seen the app can complete the laptop-affordability task alone.

---

## Phase 9: Live Update and 'What Changed' Explainer

**Goal:** the strongest demo moment. New data in, visible change out.

- Before applying any change, save a **snapshot** (metrics, forecast, top recommendations).
- Apply the change (new transaction, loan, income change, expense), then re-run processing.
- Compute a **diff**: score change, new or removed gaps, changed top recommendation, confidence change.
- Generate the explanation with a template first (deterministic), then optionally let the LLM rephrase it without changing numbers:

> 'After adding a ₹12,000 EMI: health score 72 -> 61 (DTI rose from 28% to 47%). A new cash gap appears on the 5th. Your top recommendation changed from "invest ₹5,000" to "build a buffer first".'

**Agent prompt:**

> Implement `snapshots` and a diff function. Routes: `POST /users/{id}/transactions`, `POST /users/{id}/loans`, `POST /users/{id}/income-change`, `GET /users/{id}/what-changed`. Frontend: on submit, recompute and animate the score, show the before/after cards and the What Changed panel. Test: adding an EMI to Rahul lowers the score, creates a gap, and changes the top recommendation.

**Done when:** the demo flow (add EMI) visibly changes score, gap and advice with a correct plain-language explanation.

---

## Phase 10: Unique Features Checklist

Build these after the core works, in this order of value:

1. **Evidence links on every number** (Phase 8 drawer plus evidence IDs from the engine).
2. **Confidence meter with reasons and 'how to improve'** (Phase 4).
3. **Best Next Move ranking** (Phase 6B).
4. **Danger Calendar** heatmap (Phase 8).
5. **Stress testing** (Phase 5B).
6. **Current vs recommended path chart** (Phase 8).
7. **What Changed explainer** (Phase 9).
8. **Affordability verdict card with safer alternatives** (Phase 6C).
9. **Goal planner** (Phase 6D).
10. **Behaviour insights**: weekday vs weekend spend, post-salary spending spike (spend in the 3 days after salary vs average), month-end squeeze.
11. **Anomaly and subscription-creep alerts**: duplicate charge same day, amount more than 30% above the merchant's usual, subscription price hikes, overlapping services in the same category.
12. **Hindi/Marathi mode** (Phase 7C).
13. **Privacy panel and responsible-AI disclaimer** (Phase 7D).
14. **Validation page** showing real accuracy numbers (Phase 11).

**Agent prompt for 10 and 11:**

> Implement `insights/` with: weekday-vs-weekend analysis, post-salary spending spike detection, month-end squeeze detection, duplicate-charge detection, merchant amount anomalies (z-score above 3 or 30% over the median), subscription price-hike detection, and overlapping-subscription detection. Return each insight with a plain-language message, severity and evidence IDs. Route `GET /users/{id}/insights`. Test each detector with planted cases from the synthetic personas.

---

## Phase 11: Validation and Testing (What Makes It Credible)

| Test | How | What to record |
| --- | --- | --- |
| Categorisation accuracy | Run on 200-300 hand-labelled real transactions | Accuracy, per-category precision and recall |
| Recurring detection | Compare with hand-marked recurring items | Precision and recall |
| Forecast accuracy | Hold-out backtest on Berka and real data | MAE and 10-90 band coverage |
| Simulator correctness | Hand-calculated debt payoff and savings maths | Exact match tests |
| LLM faithfulness | 30 test questions, check every number against tool output | % answers with zero mismatched numbers |
| End-to-end | Playwright runs the full demo flow | Pass or fail |

Publish all numbers in `docs/validation_report.md` and show them on the Data and Trust screen. Report real numbers only, even if modest, and write what you would improve next.

---

## Phase 12: Deployment and Production Readiness

- **Environment:** all secrets in env variables; `.env.example` committed, `.env` never.
- **Backend:** Dockerised FastAPI on Render or Railway; add CORS for your frontend domain only; rate-limit the chat route; request-size limit on uploads; accept only CSV, XLSX and PDF.
- **Frontend:** deploy on Vercel with the backend URL as an env variable.
- **Database:** SQLite for the demo; document the one-line switch to Postgres.
- **Demo mode:** a 'Try a demo persona' button that works with no signup and no upload, so reviewers can test in 10 seconds. Real uploads are kept in memory or deleted after the session, with a clear notice.
- **Observability:** structured logs, error handling that never leaks user data, a `/health` endpoint.
- **Cost control:** cache LLM results (categories, repeated questions); set a maximum tokens limit.
- **CI/CD:** GitHub Actions runs pytest, frontend build and Playwright on every push.

**Done when:** a public URL works end to end with a demo persona, and a fresh clone runs with `docker-compose up`.

---

## Phase 13: README, Demo and Interview Preparation

### README sections

1. ArthaPilot one-line pitch and a GIF of the live-update demo
2. Problem and what the app does
3. Architecture diagram (the 7A flow plus the module map)
4. **Data and Validation** (three layers, what each proves, honest limits)
5. Key features and the unique features list
6. How to run (Docker, and manual)
7. Validation numbers table
8. Privacy, safety and limitations
9. Future work (Account Aggregator integration, bank API sandbox, more languages)

### 5-minute demo script

1. Load **Rahul** and show the health score with reasons and confidence.
2. Ask: 'Will I have trouble paying bills this month?' and read the Fact / Prediction / Recommendation answer.
3. Ask: 'Can I afford a ₹45,000 laptop?' and show the verdict card with the current vs recommended path chart.
4. Click a number to open the evidence drawer.
5. Add a ₹12,000 EMI and show the score drop, new gap and changed advice.
6. Run the 'income stops for 2 months' stress test.
7. Switch to a **real anonymised statement** and show the validation page.

### Resume bullets (fill in only measured numbers)

- Built ArthaPilot, an AI financial-health copilot that unifies transactions, loans and cards into a 0-100 health score and a 90-day Monte Carlo cash-flow forecast with confidence bands.
- Achieved \[X\]% categorisation accuracy on \[N\] hand-labelled real transactions; forecast 10-90 band covered \[Y\]% of actuals in hold-out tests on the Berka dataset.
- Designed a tool-calling architecture where the LLM never computes: every figure comes from tested code and is validated against tool output, with evidence links to source transactions.
- Built an action simulator that ranks recommendations by impact and effort with before/after metrics.

### Likely interview questions

| Question | Strong answer direction |
| --- | --- |
| Why three data layers? | Synthetic for edge-case scenarios, Berka for real patterns, real statements for messiness; all go through one canonical schema |
| How do you stop hallucinated numbers? | Tools compute, the LLM explains, and a validator checks every number against tool output |
| How accurate is the forecast? | Quote your MAE and band-coverage from the backtest and the limits |
| How do you handle privacy? | Masking before the LLM, local processing, nothing raw stored or committed |
| What would you do in production? | Account Aggregator consent flow, Postgres, auth, audit logs, regulated-advice review |

---

## Suggested Timeline

| Week | Phases |
| --- | --- |
| 1 | 0, 1, 2 (setup, data, categorisation) |
| 2 | 3, 4, 5 (metrics, confidence, forecast) |
| 3 | 6, 7 (simulator, copilot) |
| 4 | 8, 9 (frontend, live update) |
| 5 | 10, 11, 12, 13 (unique features, validation, deploy, README) |

## Final Master Checklist

- [ ] Three data layers load through one canonical schema
- [ ] Categorisation, recurring and income detection tested with measured accuracy
- [ ] Health score with reasons, evidence and confidence
- [ ] 90-day forecast with bands, gaps, stress tests and backtest numbers
- [ ] Simulator with ranking, affordability and goals
- [ ] Chat with tool use, strict three-part schema and number validator
- [ ] Seven screens, evidence drawer, danger calendar, dual-path chart
- [ ] Live update with What Changed explainer
- [ ] Insights, anomalies, multilingual mode, privacy panel and disclaimer
- [ ] Validation report, CI, Docker, public deployment, README and demo script

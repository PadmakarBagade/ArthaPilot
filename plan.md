# ArthaPilot: Master Build Plan

**Audit date:** 2026-11-14 · **Audited against:** repository zip `ArthaPilot-main`, `AGENTS.md`, `docs/BUILD_GUIDE.md`, `docs/metrics.md`, `docs/validation_report.md`
**Purpose:** one file that lets any AI coding agent (Copilot, Antigravity, Claude Code, Cursor, Codex, or a plain chat) build the whole application end to end, in order, without skipping anything.

> **How the user starts an agent:** "Read `plan.md` and build the application." The agent follows Section 0.

---

## 0. Operating contract for the agent (read this first, every session)

1. **Read order:** `AGENTS.md` → Sections 0 to 3 of this file → Section 4.3 (defect register) → Section 12 (progress ledger). Then read only the active task in Section 6 and the sections it references. Do not load the whole file into a small context.
2. **Pick the work:** take the first task in the ledger (Section 12) whose status is `TODO` or `PARTIAL` and whose dependencies are `DONE`. Build it exactly as its task block says.
3. **One task at a time.** Implement, run the task's acceptance tests and the regression gates (Section 10), then update the ledger: status, date, and one evidence line containing counts only. Then take the next task.
4. **Never mark `DONE` unless every acceptance item passes.** If something is unfinished, mark `PARTIAL: <exact reason>`. Never skip silently.
5. **Stop conditions:** (a) a decision or secret is needed from the user; (b) context is nearly full, so write a handoff entry in Section 13 and stop; (c) a gate still fails after 3 fix attempts, so record a blocker in Section 13 and continue with any independent task.
6. **Git policy:** never run `git push`. Never run `git commit` unless the user says "auto-commit"; in that case commit locally per task with message `<task id>: <title>`. Otherwise finish each task by printing `git status` and the exact `git add <files>` commands (never `git add .`).
7. **Truthfulness:** every number in `README.md`, `docs/validation_report.md` or the UI that describes quality must be produced by a script in this repo. Never invent, round up or hand-edit measured values. Label in-sample results as in-sample. Failed targets are reported as measured.
8. **If you cannot run commands** (chat-only mode): output complete file contents and the exact commands for the user to run, and mark the task `UNVERIFIED` in the ledger until the user pastes passing output.
9. **Do not redo `BASELINE` items** (Section 4.2). Protect them with regression tests.
10. **Windows and Linux:** give commands for both bash and PowerShell when you document a command. Use `pathlib`, never hard-coded separators.

---

## 1. Product definition

**ArthaPilot** ("Your Financial Health Copilot") unifies a person's transactions, loans, cards and balances into one health picture, predicts cash-flow trouble, simulates the impact of each action, and answers questions in plain language. Every answer separates **what happened** (Observed Fact), **what is predicted** (Prediction, with confidence) and **what to do** (Recommendation, with simulated impact).

**Data layers (all feed one canonical schema):** (1) synthetic personas for controlled scenarios, (2) the Berka public banking dataset for real transaction patterns, (3) a real anonymised statement (own Google Pay export, private) for messy-data proof.

**Primary demo story (must work end to end):**
1. Load **Rahul** (28, salaried, one vehicle EMI, high-APR card). Home shows a qualified score, confidence with reasons, and a Best Next Move.
2. Ask "Will I have trouble paying bills this month?" and get a three-part answer that names a month-end gap.
3. Ask "Can I afford a ₹45,000 laptop?" and get a Yes/Risky/No verdict card with a current-path vs recommended-path forecast.
4. Click any number and see the exact transactions or the formula behind it.
5. Add a ₹12,000 EMI: the score drops, a gap appears or moves earlier, the top recommendation changes, and a plain-language "What changed" explanation matches the computed diff.
6. Run the stress test "income stops for 2 months" and see survival days.
7. Open Data and Trust to see the measured validation numbers, the privacy panel and the disclaimer.

**Non-goals:** regulated financial advice, bank API integration (documented as future work: Account Aggregator), multi-user authentication.

---

## 2. Non-negotiable rules (from `AGENTS.md`, plus build rules)

**Golden Rules (verbatim intent of `AGENTS.md`):**
- The LLM never calculates money. All numbers come from tested Python functions. The LLM only chooses tools and explains verified results.
- Every number shown to the user carries an evidence reference (transaction IDs, entity IDs, or the formula used).
- Every answer has three separate sections: Observed Fact, Prediction (with confidence), Recommendation (with simulated impact).
- All money is stored as integer paise (₹1 = 100 paise). Ratios and scores may be floats. TypeScript never recomputes financial values; it only formats them.
- Every module gets unit tests. No task is done until its tests pass.
- Never commit real user data. Real statements live only in `data/private/`, which is git-ignored.
- Mask personal data (names, account numbers, phone numbers, UPI IDs, emails) before anything is sent to an LLM.

**Build rules:**
- Errors are surfaced explicitly (HTTP 4xx/5xx with a message). No silent fallbacks to invented or success-shaped data.
- No engine function reads the wall clock. Time comes from an injected `as_of` date (DEC-05).
- No engine function touches the database, the network or an LLM. Services load data; engines are pure.
- Routes are thin: validate, call a service, return a typed Pydantic model.
- Private data never appears in logs, test fixtures, reports, commit messages, code comments or chat output. Only counts and percentages leave `data/private/`.
- Real-trained model artefacts are never saved inside the repo. The committed `categoriser.joblib` is trained on synthetic data only.

---

## 3. Fixed decisions (do not re-debate; change only with a dated note here)

| ID | Decision |
|---|---|
| DEC-01 | Backend: Python 3.12, FastAPI, SQLAlchemy 2, Pydantic v2, pandas, numpy, scikit-learn. SQLite for the demo, Postgres-ready. No Prophet/statsmodels: the forecast is a seeded bootstrap Monte Carlo. |
| DEC-02 | Frontend: Next.js 14 App Router, TypeScript, Tailwind 3, shadcn-style components, Recharts, lucide-react, Geist fonts (already bundled; this replaces "Inter" in the guide). Tests: Vitest + Testing Library; E2E: Playwright. |
| DEC-03 | Navigation is **four tabs: Home, Ask, Plan, Money** (guide Phase 8A). This supersedes the six-tab prototype (Home/Spending/Forecast/Ask/Plan/Data) and the older plan's tab list. Spending, Recurring, Insights and Add Data live under **Money**. Forecast, Simulator, Goals and Stress tests live under **Plan** as a segmented control. Data source, language, privacy and validation live in the profile menu. |
| DEC-04 | The copilot is provider-agnostic. `LLM_PROVIDER` is one of `none` (default), `anthropic`, `gemini`, `ollama`. A deterministic intent router plus templates is mandatory and is the fallback, so the whole product works with no API key. No model names are hard-coded; they come from `LLM_MODEL`. |
| DEC-05 | **Demo clock:** personas and Berka data are historical. All time logic uses `as_of = max(transaction date) + 1 day` unless a request supplies `as_of`. Engines receive `as_of`; they never call `date.today()`. |
| DEC-06 | One `UserState` dataclass (transactions, accounts, loans, cards, recurring items, income, goals, `as_of`) is built once per request by a service and passed to engines. The simulator works on immutable copies. |
| DEC-07 | Every metric, forecast point, simulation, insight and answer carries `evidence = {txn_ids, entity_ids, formula_id, formula_text}`. Formulas are registered in `backend/app/evidence/formulas.py` and resolvable through `GET /users/{id}/evidence`. |
| DEC-08 | The category list is fixed (Appendix A). Synthetic generators, label files and models use these exact names. |
| DEC-09 | Schema management: `create_all` plus the documented SQLite shim for the demo; an Alembic baseline migration is added in V2 before any Postgres deployment. |
| DEC-10 | Liquid balance = balances of `savings` and `current` accounts only. Credit-card accounts are never cash. One function (`finance/defs.py`) defines it for metrics, forecast and affordability. |
| DEC-11 | Validation outputs are generated: `docs/validation_report.md` (human) and `docs/validation_report.json` (machine, served by `GET /validation`). Nothing in them is hand-edited. |
| DEC-12 | Demo works without signup. Uploaded private data is local to the instance and deletable via `DELETE /users/{id}`. |

---

## 4. Verified audit of the current repository

### 4.1 Baseline verified on 2026-11-14

| Check | Result |
|---|---|
| `cd backend && python -m pytest -q` | **87 passed**, 1 Starlette/httpx deprecation warning |
| `cd frontend && npm ci && npm run build` | Succeeds (one static page, 93.6 kB first load) |
| End-to-end API smoke (load, process, health, confidence, forecast, gaps, stress, best-moves, affordability, simulate, chat, add loan, what-changed) on all five personas | All routes return 200; defects below were found by this smoke run |
| Frontend tests, E2E tests | **None exist** |

### 4.2 Module status

| Area | Status | Notes |
|---|---|---|
| Models, schemas, SQLite, integer paise | BASELINE (solid) | 10 tables present; SQLite `ALTER` shim in `db.py` |
| Ingestion (`cleaning`, `parser`, `anonymise`, `gpay`), upload size limit | BASELINE (solid) | Needs content-sniffing hardening (B8) |
| Synthetic personas, scenario injectors, Berka loader, GPay parser scripts | BASELINE (partial) | Persona stories do not yet produce the demo (D-08); label file is poor (D-01) |
| Recurring and income detection | BASELINE (solid) | Planted-case precision 88.64%, recall 97.50% (from the validation report) |
| Health metrics and score (`metrics/`) | BASELINE (solid, one defect) | Definitions in `docs/metrics.md`; debt service double-count rule (D-05) |
| Categorisation cascade | **DEFECTIVE** | Rules work; ML layer never fires (D-01) |
| Confidence engine (`metrics/confidence.py`) | PARTIAL | Exists with route and tests; needs coverage and p2p penalties (B1) |
| Forecast engine (`forecast/`) | PARTIAL, defects | D-02, D-03, D-04 |
| Simulator (`simulate/`) | STUB | 3 actions only; wrong income definition; no re-run of metrics/forecast (D-07) |
| Copilot (`copilot/`) | STUB | Two canned answers; no tools, no provider, validator unused (D-06) |
| Snapshots and What Changed | PARTIAL | Works mechanically; the EMI demo does not change anything (D-05) |
| Insights, evidence service, language support | MISSING | |
| Frontend | PROTOTYPE | One 220-line `page.tsx`, six tabs, no components, no chart library, no tests |
| Docker | DEFECTIVE | D-09 |
| CI | PARTIAL | Backend pytest + frontend build only |
| Docs | PARTIAL | `README.md` and the previous `plan.md` were stale (D-12); `validation_report.md` is honest but low |

### 4.3 Defect register (fix tasks are named; fix these before building on top)

| ID | Severity | Defect and evidence | Fix |
|---|---|---|---|
| D-01 | Critical | **ML categoriser is trained on broken labels.** `categorise/model.py` maps labels with `_CATEGORY_NAMES.get(label, "Uncategorised")`, but the label file uses canonical names, so 440 of 697 training rows become `Uncategorised`, 240 are `food_delivery`, and about 17 are anything else. The saved model has only 10 classes. `labeled_synthetic.csv` also has 12× more food-delivery rows than other categories and corrupted strings (for example `C@SHWITHDRAWAL`). Report shows ML layer count 0 on both sets; synthetic held-out 22/90 (24.44%), coverage 24.47%; real held-out 10/29 (34.48%), coverage 26.67%. README wrongly says categorisation is "Done". | F4 |
| D-02 | High | **Forecast starts from the wrong balance.** `main._forecast_state` sums every account including the credit-card account. For Rahul this is ₹1,50,000 (savings ₹25,000 + card balance ₹1,25,000) while affordability uses ₹25,000. | F5 |
| D-03 | High | **Variable spend model samples single transactions, not daily totals**, so each simulated day spends one random transaction regardless of how many that day normally has. | B2 |
| D-04 | High | **Gap threshold defaults to 0** instead of one week of average spending (guide Phase 5), and Rahul shows no gap, so the demo story has nothing to show. | B2, F6 |
| D-05 | Critical | **Adding a loan EMI changes nothing.** The score stays 66.79 after adding a ₹12,000 EMI because loan EMIs are ignored whenever EMI transactions exist. The headline demo fails. | F5 |
| D-06 | Critical | **Copilot is a stub.** "Can I afford a 45000 laptop?" returns the generic health summary with `verdict: null`. No tool routing, no provider, `validate_numbers` is never called. | B7 |
| D-07 | High | **Simulator uses a different income definition** (all credits, including transfers) from the metrics module, and never re-runs metrics, forecast or confidence. Only three action types exist. Affordability ignores the forecast. | F5, B3 |
| D-08 | High | **Persona stories do not match their roles.** Arjun (irregular freelancer) scores 85.9 "Strong" with High confidence (85); Rahul scores 66.8 "Good" with no gap. | F6 |
| D-09 | Critical | **Docker demo is broken.** The backend image copies only `app/`, but persona loading reads `<repo>/data/synthetic`, so `load-persona` returns 404 in a container. Nothing seeds demo users, so a fresh UI is empty. `.env.example` sets `LLM_PROVIDER=anthropic`, and `LLMClient` raises `RuntimeError("Unsupported LLM provider")` for any merchant the rules and model cannot place, which makes `/process` return 500 after `cp .env.example .env`. | F1, F2 |
| D-10 | Medium | `main.py` is a 451-line monolith with business logic inside routes; simulate, best-moves, affordability and goal routes return untyped dicts; CORS origins are hard-coded to localhost. | F3, F1 |
| D-11 | Medium | Frontend is one monolithic `page.tsx` with a six-tab layout, no chart library (forecast drawn with CSS bars), no component library, no tests. | U1 to U9 |
| D-12 | Medium | `README.md` status table and the previous `plan.md` contradict the code (say forecast, simulation and copilot are not implemented while stubs exist; say categorisation is Done). | F1, V3 |
| D-13 | Low | `.gitignore` lacks `frontend/.next/`, `.pytest_cache/`, `.env.local`, `playwright-report/`; `requirements.txt` is unpinned and omits numpy/openpyxl if used; the Starlette warning is unaddressed; `rules.py` has duplicate dictionary keys (`BESCOM`) and generic words (`GAS`, `LIC`, `OLA`, `MART`) that cause false matches. | F1, F4 |

---

## 5. Target architecture and contracts

### 5.1 Layers and data flow

`source -> parser/adapter -> canonical transactions -> categorise -> recurring/income -> UserState -> metrics/confidence -> forecast -> simulate/recommend -> insights -> copilot tools -> typed API -> UI`

Backend layout to reach (existing names kept where they exist):

```
backend/app/
  main.py                # app factory, middleware, router registration only
  config.py              # settings (env), cors, data_dir, llm settings
  db.py  models.py  schemas.py
  routers/               # users, ingest, analytics, forecast, simulate, copilot, updates, insights, demo, system
  services/              # user_state.py (builds UserState), processing.py, snapshots.py, validation.py
  finance/defs.py        # single definitions: income, expense, liquid balance, debt service
  ingestion/  categorise/  recurring/  metrics/  forecast/  simulate/  insights/
  evidence/formulas.py   # formula registry; evidence resolver
  copilot/               # tools.py, router.py, providers/, orchestrator.py, validator.py, masking.py, i18n.py, refusals.py
```

### 5.2 API contract (every route has a Pydantic request and response model)

| Method and path | Purpose | Status |
|---|---|---|
| `GET /health`, `GET /ready` | liveness; readiness (DB reachable, model artefact loads, personas seeded) | health exists; ready new |
| `GET /users`, `DELETE /users/{id}` | list; delete a user and all their data | list exists; delete new |
| `POST /upload` | CSV/XLSX/PDF statement upload with validation | exists, harden (B8) |
| `GET /demo/personas`, `POST /demo/seed` | list and idempotently load the five personas and process them | new |
| `POST /users/{id}/load-persona`, `POST /users/{id}/process` | load and categorise | exist |
| `GET /users/{id}/overview` | one aggregated payload for Home (health, confidence, best move, next gap, data period, last updated) | new |
| `GET /users/{id}/health?months=` | score, metrics, evidence | exists |
| `GET /users/{id}/confidence` | confidence score, level, reasons, how to improve | exists |
| `GET /users/{id}/transactions`, `GET /users/{id}/spending` | transactions; category and monthly breakdown | transactions exist; spending new |
| `GET /users/{id}/recurring` | recurring obligations with evidence | exists |
| `GET /users/{id}/insights` | behaviour and anomaly insights | new |
| `GET /users/{id}/forecast?days=`, `GET /users/{id}/gaps`, `POST /users/{id}/stress-test` | forecast, gaps, stress tests | exist, rebuild (B2) |
| `POST /users/{id}/simulate`, `GET /users/{id}/best-moves`, `POST /users/{id}/affordability`, `POST /users/{id}/goal`, `POST /users/{id}/debt-plan` | simulation family | exist (debt-plan new), rebuild (B3) |
| `POST /users/{id}/chat` | copilot (request has `question`, optional `language`) | exists, rebuild (B7) |
| `POST /users/{id}/transactions`, `POST /users/{id}/loans`, `POST /users/{id}/income-change`, `POST /users/{id}/expenses` | mutations; each saves a snapshot first | transactions, loans, income-change exist; expenses new |
| `GET /users/{id}/what-changed`, `GET /users/{id}/snapshots`, `POST /users/{id}/reset` | diff, history, restore the originally loaded data | what-changed exists; others new |
| `GET /users/{id}/evidence?ids=` | resolve evidence ids to transactions, entities and formulas | new |
| `GET /validation` | serve `docs/validation_report.json` | new |

Errors: 404 unknown user or persona; 422 invalid or insufficient data (message says what is missing); 413 oversize upload; 415 unsupported type; 429 chat rate limit.

### 5.3 Canonical transaction (unchanged; enforced)

`txn_id` (stable hash), `user_id`, `account_id`, `date` (ISO), `amount_paise` (signed int), `raw_description`, `merchant` (cleaned), `category`, `category_confidence`, `is_recurring`, `is_self_transfer`, `source` (`synthetic` | `berka` | `real`).

### 5.4 Answer schema (copilot, mandatory)

```json
{
  "summary": "one-sentence direct answer",
  "verdict": "Yes | Risky | No | null",
  "facts": [{"text": "...", "evidence": {"txn_ids": [], "entity_ids": [], "formula_id": "", "formula_text": ""}}],
  "predictions": [{"text": "...", "confidence": 0, "confidence_reasons": [], "evidence": {}}],
  "recommendations": [{"text": "...", "impact": {"score_delta": 0, "gaps_avoided": 0, "monthly_cash_gain_paise": 0}, "evidence": {}}],
  "follow_ups": [],
  "tools_used": [],
  "language": "en",
  "disclaimer": "Guidance, not regulated financial advice."
}
```

---

## 6. Build backlog (execute in this order; dependencies are listed)

Task block format: **Goal · Depends · Steps · Acceptance**. Acceptance items are tests or commands; all must pass.

### Track F: Fix the foundation (do first)

#### F1. Reproducible environment and repo hygiene · Depends: none
**Steps**
1. `requirements.txt`: pin direct dependencies to the versions that currently pass (`pip freeze` from a passing venv), and add `numpy` and `openpyxl` and `pdfplumber` only if the code imports them. Keep `httpx`.
2. `.gitignore`: add `frontend/.next/`, `.pytest_cache/`, `.env.local`, `playwright-report/`, `test-results/`, `*.sqlite`, and `data/private/` stays.
3. `.env.example`: `LLM_PROVIDER=none`; add `LLM_MODEL=`, `LLM_BASE_URL=` (for Ollama), `CORS_ORIGINS=http://localhost:3000`, `SEED_DEMO=true`, `DATA_DIR=`, `CHAT_RATE_LIMIT_PER_MIN=10`, `LOG_LEVEL=INFO`.
4. `config.py`: add `cors_origins`, `data_dir`, `seed_demo`, `llm_provider` (default `none`), `llm_model`, `llm_base_url`, `chat_rate_limit_per_min`. `LLMClient` and the copilot read these settings, not `os.environ` (fixes D-09). CORS origins come from settings.
5. Backend Docker: build context is the repo root (`context: .`, `dockerfile: backend/Dockerfile`), copy `backend/app`, `data/synthetic`, and `scripts` if imported; set `DATA_DIR=/app/data`. The persona loader uses `settings.data_dir`, not `Path(__file__).parents[2]`. Add `HEALTHCHECK` using `/ready`.
6. `pytest.ini`: filter the Starlette/httpx warning with a comment explaining why.
7. CI: backend tests run from `backend/` and from the repo root; frontend `npm run lint`, `npx tsc --noEmit`, `npm run build`; a Docker build job (no push).
8. `scripts/smoke.sh` and `scripts/smoke.ps1`: start the stack, wait for `/ready`, seed, process, call `/health` endpoints, exit non-zero on any failure.
9. Correct `README.md` status tables to match this plan's ledger (no "Done" without evidence).
**Acceptance:** tests pass from `backend/` and repo root with zero warnings; `docker compose up --build` gives `/ready` 200; `cp .env.example .env` then `/users/{id}/process` returns 200 (regression test with `LLM_PROVIDER=none`); `git ls-files` shows no ignored files.

#### F2. Demo seeding · Depends: F1
**Steps:** add `services/processing.py` with `seed_demo()`: for each folder in `data/synthetic/`, load persona, load accounts/loans/cards, run process, idempotent by user id. Run it on startup when `settings.seed_demo`. Add `GET /demo/personas`, `POST /demo/seed`, `POST /users/{id}/reset` (reload original data). Frontend never starts empty.
**Acceptance:** fresh database plus startup gives five users all processed; second call changes nothing (test); reset restores a mutated user to its original score (test).

#### F3. Service layer and thin routes · Depends: F1
**Steps:** create `services/user_state.py` (`build_user_state(db, user_id, as_of=None) -> UserState`), split `main.py` into `routers/*`, move business logic from routes into services, add `response_model` to every route that lacks one, add request-id middleware and JSON error shape. No behaviour change.
**Acceptance:** all 87 existing tests still pass; `main.py` is under 80 lines; every route has a response model (test enumerates `app.routes`); one test proves `build_user_state` is the only place that queries transactions for analytics.

#### F4. Categoriser repair (fixes D-01, part of D-13) · Depends: F3
**Steps**
1. Update `scripts/generate_personas.py`: write canonical category names (Appendix A) into transactions and `data/labeled/labeled_synthetic.csv` (columns `raw_description,true_category,is_recurring,merchant_key`). At least 20 distinct merchants per category. Noise: at most one character edit on at most 15% of rows, spaces preserved (no tokens like `C@SH`). Imbalance across categories at most 3×. Fixed seed. Regenerate `data/synthetic/*` and update dependent tests.
2. `categorise/model.py`: delete `_CATEGORY_NAMES`; train on canonical labels; exclude `Uncategorised` rows from training; word plus character TF-IDF, balanced logistic regression, confidence threshold from config (default 0.5); `merchant_key` groups for cross-validation. Artefact trained on synthetic data only.
3. `categorise/rules.py`: ordered list of `(pattern, category)` (specific before generic), word-boundary matching, no duplicate keys. Fix ambiguous words: `GAS` only with `BHARAT|HP|INDANE|CYLINDER`; `OLA`, `LIC`, `MART` only as whole words or known phrases. Add Indian merchant terms from the guide (medical, petroleum, sweets, kirana, dairy, prepaid, xerox and similar).
4. Move the transfer logic now inline in `process_user` (self transfers, "Received from" a person without an income word) into `categorise/transfers.py` with tests.
5. `scripts/evaluate_categoriser.py` must call the real cascade (`categorise()`), report counts per layer (rules, ml, llm, uncategorised), accuracy on answered rows, coverage, per-category precision and recall, and a confusion matrix, for: synthetic held-out (merchant-level 80/20, fixed seed) and real held-out (if the private files exist; training uses synthetic plus real train rows in a temporary directory outside the repo; `Uncategorised` real rows are excluded from accuracy and counted).
6. The old numbers (24.44%, 34.48%) are kept in the report as a labelled "before repair" history line.
**Acceptance:** synthetic held-out accuracy on answered rows **at least 85%** and coverage **at least 85%**; ML layer answers more than 0 rows; every category has recall above 0 on the synthetic test set; a test asserts the model has no class holding more than 25% of training rows; real held-out is **measured and reported as "X / N" with coverage and no target** (person-name payees are expected to stay `Transfers` or `Uncategorised`); privacy search of the diff finds zero matches; test set was run once after tuning (state it in the report).

#### F5. One set of finance definitions (fixes D-02, D-05, D-07 in part) · Depends: F3
**Steps**
1. Create `finance/defs.py` with `is_income`, `is_expense`, `FIXED_CATEGORIES`, `liquid_balance_paise(accounts)` (DEC-10), `monthly_debt_service_paise(loans, cards, transactions)`. Metrics, forecast, simulator, insights and affordability all import these.
2. Debt service rule: the `loans` table is authoritative. Match EMI/Loan transactions to loans (amount within 5% and day-of-month within 5 days of the loan's due day); a matched transaction is the same obligation and is never counted twice; unmatched EMI transactions are counted. Card minimum dues come from `cards`.
3. Forecast and affordability start from `liquid_balance_paise`.
4. Add the hand-calculated test: adding a ₹12,000 monthly EMI loan to a persona raises DTI by exactly 12000/(monthly income in rupees), lowers the DTI sub-score and the total score, and the evidence lists the new loan id.
5. Update `docs/metrics.md` to match.
**Acceptance:** the Rahul-plus-EMI test passes with arithmetic in comments; Rahul's forecast start balance equals his savings balance only; metrics and simulator `income` and `expenses` are equal for the same state (property test on all five personas); all earlier metrics tests still pass.

#### F6. Persona stories and the demo scenario (fixes D-04, D-08) · Depends: F4, F5
**Steps:** define each persona's story in a comment **before** computing results, then adjust the generator: Rahul has a ₹65,000 salary, a vehicle EMI, a high-APR card, and a month-end low balance so that at the default threshold the forecast shows a gap in the last five days before salary; Priya is healthy (Strong, High confidence); Arjun has irregular income (Fair, Medium confidence, lowest income stability); Meera has the highest debt pressure and card utilisation (Poor or Fair); Sam has no savings (lowest runway). Add `data/synthetic/<persona>/meta.json` with the story text. Credit-card account balances must equal `cards.csv`.
**Acceptance:** `tests/test_persona_story.py` asserts: Priya band Strong and confidence High; Arjun confidence level Medium; Arjun lowest income-stability sub-score; Meera lowest utilisation or debt sub-score; Sam lowest runway; Rahul has at least one forecast gap date within 5 days before his salary date; Priya's score is above Rahul's. Do not relax a check to make it pass; fix the generator and note what changed.

### Track B: Backend engines

#### B1. Confidence engine completion · Depends: F5
**Steps:** keep the existing penalty model. Add: penalty when `score_coverage` of the health score is below 0.5 (key metrics unavailable), penalty when p2p outflow share exceeds 30% (classification ambiguity), reasons that include counts, `how_to_improve` actions that name the missing data. Confidence never reads the health score. Add typed `ConfidenceResponse` and API tests.
**Acceptance:** one test per penalty with hand-computed points; confidence stays Low or Medium for a user with high score but 2 months of data (independence test); Priya High, Arjun Medium, the local real user not High.

#### B2. Forecast v2 (fixes D-03, D-04) · Depends: F5, F6
**Steps**
1. Variable spend: build the empirical distribution of **daily totals per weekday** from the last up to 6 months of non-recurring, non-transfer, non-self-transfer, non-card-payment debits, **including zero-spend days**. Each simulated day draws one daily total from the same weekday's set (seeded bootstrap).
2. Schedule: salary on its day of month (clamped to month end), recurring items, loan EMIs monthly from `next_due_date`, card minimum monthly from `due_date`. Do not double count a recurring item that matches a loan or card payment (same rule as F5).
3. Output per day `p10`, `p50`, `p90`, `probability_below_zero`, plus `safe_threshold_paise` (default `7 × mean daily variable spend`, overridable) and gap records `{date, expected_balance_paise, probability_below_zero, evidence}`. Each scheduled event carries evidence ids; each model value carries the formula id.
4. Stress tests with parameters: `income_stops(months 1 to 3)`, `expenses_rise(percent, default 15)`, `emergency_expense(amount, default ₹50,000)`, `new_emi(amount, start_in_days)`. Return survival days (first day p10 is below 0, else the horizon), first breach date, minimum p10 balance, and the full forecast.
5. `scripts/backtest.py`: for each Berka account with at least 9 months (and the private labelled data when present), hide the last 60 days, forecast from earlier data, report counts only: accounts tested, MAE of p50 in paise and as a share of average monthly expenses, and the share of days where the actual balance fell inside p10 to p90 (calibration). Write results to the validation JSON.
**Acceptance:** same seed gives identical output (test); a deterministic fixture has a known gap date; Rahul has a gap before salary (F6); stress scenarios are reproducible and ordered (3 months of lost income survives fewer days than 1); backtest runs and publishes measured MAE and coverage; if coverage is below 60% it is reported as a known limitation, not hidden.

#### B3. Simulator, recommendations, affordability, goals · Depends: B2
**Steps**
1. `simulate(state, action)` copies the state, applies the action, then **re-runs metrics, confidence, forecast and gap detection**, and returns `before`, `after`, `delta` (score points, raw metrics, savings rate, runway months, gap dates avoided or added, monthly cash change) with evidence.
2. Action library (each a small validated class): `cut_category(category, percent)`, `cancel_subscription(merchant)`, `extra_debt_payment(amount, strategy)`, `move_to_savings(amount)`, `start_sip(amount)`, `delay_purchase(amount, days)`, `purchase_cash(amount)`, `purchase_emi(amount, months, apr)`, `refinance(loan_id, new_apr, new_tenure)`, `build_buffer(target_months)`.
3. Debt payoff: exact integer-paise amortisation (monthly interest `= round_half_up(balance × apr / 12 / 100)`), avalanche and snowball order, minimums from loan EMIs and card minimum dues; output total interest, months to clear, and interest and months saved against a minimum-only baseline.
4. Ranking: simulate 5 to 8 relevant actions. `impact = score_delta + 3 × min(gaps_avoided, 5) + 10 × min(1, monthly_cash_gain / (0.05 × monthly_income))`. `effort` (1 to 10): cancel subscription 1, delay purchase 2, cut category `ceil(percent/10) + 1`, extra debt payment 4, move to savings 3, build buffer 5, refinance 6. `priority = impact / effort`, ties by impact. Return `best_move` plus alternatives, each with a one-line reason.
5. Affordability for "Can I afford ₹X": simulate three paths (cash now, 6-month EMI at an assumed APR parameter, wait until after the next salary). Verdict: **Yes** if the forecast p10 minimum stays above the safe threshold and runway stays at or above 1 month; **Risky** if p50 stays above the threshold but p10 does not; **No** if p50 breaches or card utilisation would exceed 50%. Always return a safer alternative with its own simulated impact.
6. Goal planner: `required_monthly = ceil(target / months)`; feasibility against surplus; if not feasible return the months needed at current surplus and the cuts (from ranked categories) that would close the gap.
7. Guardrails (enforced in code and tested): never recommend stopping debt payments, never recommend investing or SIP while runway is below 3 months, never recommend specific stocks or guaranteed returns; low confidence adds "collect more data first" to recommendations.
**Acceptance:** state purity (original unchanged, test); hand-calculated amortisation matches to the paise; avalanche saves at least as much interest as snowball on the Meera fixture; ranking order is correct on a known fixture; affordability returns each verdict on three crafted fixtures; guardrail tests pass; the simulator's income and expenses equal the metrics module's (F5).

#### B4. Insights and anomaly detectors · Depends: F5
**Steps:** `insights/` with detectors returning `{id, kind, severity (info|watch|alert), text, evidence}`: weekend-versus-weekday spend ratio at least 1.3 over at least 8 weeks; post-salary spike (spend in the 3 days after salary at least 1.5× the average 3-day window); month-end squeeze (balance in the last 5 days below 20% of the salary); duplicate charge (same merchant and amount within 24 hours, excluding person-to-person); merchant anomaly (amount above median + 3×MAD and at least 1.3× median); subscription price hike (latest amount at least 10% above the median of earlier ones); overlapping subscriptions (two or more active in the same service group). Thresholds live in `insights/config.py`. Document false-positive limits in `docs/insights.md`.
**Acceptance:** each detector has a planted synthetic case that triggers it with correct evidence ids and a negative case that does not; `GET /users/{id}/insights` is typed; empty or short histories return an empty list, not an error.

#### B5. Evidence service · Depends: B2, B3, B4
**Steps:** `evidence/formulas.py` registers every formula id with plain text and input names. `GET /users/{id}/evidence?ids=` resolves transaction ids, entity ids (loan, card, account, recurring) and formula ids. Truncate lists above 500 ids (`truncated: true`). Every response from metrics, forecast, simulation, insights and copilot includes `evidence`.
**Acceptance:** a test walks every analytic response and asserts each number-bearing field has an evidence object whose ids resolve (no dangling ids); unknown ids return 404 with a message.

#### B6. Live update and What Changed · Depends: B3, B5
**Steps:** every mutation route (`transactions`, `loans`, `income-change`, `expenses`) first saves a snapshot (metrics, confidence, gap dates, top three recommendations, key raw metrics), applies the change, reprocesses, then returns. `what-changed` returns a structured diff: score, each raw metric, confidence, gaps added and removed, top recommendation before and after, and a deterministic explanation built from templates using only diff values (the LLM may rephrase later, never change numbers). `snapshots` lists history; `reset` restores the original data.
**Acceptance:** adding a ₹12,000 EMI to Rahul: score decreases, DTI rises, a gap appears or moves earlier, the top recommendation changes, and every number in the explanation equals the diff (test compares parsed numbers). Adding income or removing an EMI moves the score the other way. The what-changed response before any change says so explicitly.

#### B7. Copilot (fixes D-06) · Depends: B3, B5, B6, B4
**Steps:** implement Section 7 completely: tools, deterministic router, provider interface (`none`, `anthropic`, `gemini`, `ollama`), orchestrator, number validator, masking, language templates, refusals, rate limit, sanitised persistence, `POST /users/{id}/chat`.
**Acceptance:** the six demo questions (Section 7.6) return schema-valid three-part answers with the correct tool; a mocked provider that returns a fabricated number is rejected, regenerated once, then replaced by the template; a captured provider payload contains no raw descriptions, names, phone numbers, emails or UPI ids (canary test); out-of-scope requests are refused or redirected; works with `LLM_PROVIDER=none` and no network.

#### B8. Ingestion hardening and real-data adapters · Depends: F3
**Steps:** upload validation by extension **and** content sniffing (CSV decodes as text with consistent columns; XLSX is a valid zip; PDF magic bytes); size limit from settings; clear 413/415/422 messages; column-mapping response when columns cannot be detected; duplicate rows removed by `txn_id`; reprocessing is idempotent; Google Pay PDF/CSV adapter keeps `is_self_transfer` and maps bank account to `account_id`; private uploads get `source = real`, are local to the instance, and are deletable with `DELETE /users/{id}`; raw content is never logged.
**Acceptance:** tests for malformed, oversized, wrong-type and duplicate files; reprocessing twice changes nothing; no raw statement text in logs (captured-log test).

### Track U: Frontend (start after F3, B2, B3 contracts are stable; follow Section 8)

#### U1. Foundation · Depends: F3
Install Recharts, Vitest, Testing Library, Playwright. Set design tokens (Section 8.2) in Tailwind and `globals.css`. Create `lib/api.ts` (typed client for every route, one error type), `lib/format.ts` (Indian ₹ grouping, lakh and crore in headlines only, dates like "27 Nov", "in 5 days"), `lib/glossary.ts` (plain-language labels, Appendix C), `lib/i18n.ts` (en, hi, mr string tables), and `hooks/useUserData.ts`.
**Acceptance:** unit tests for the formatters (including 1,25,000 grouping and negative paise); `tsc` and lint clean; no financial arithmetic in TypeScript beyond formatting (grep test for forbidden patterns on money fields).

#### U2. Component library · Depends: U1
Build once, with Vitest tests and a `/components` preview page: `ScoreRing`, `MetricCard`, `FactCard`, `PredictionCard`, `RecommendationCard`, `ConfidenceChip` (expands to reasons and how to improve), `VerdictCard`, `EvidenceChip`, `EvidenceDrawer`, `BeforeAfterBar`, `InfoTooltip`, `EmptyState`, `LoadingState`, `ErrorState`, `ChartTableToggle`, `NavTabs`, `ProfileMenu`.
**Acceptance:** every component renders its loading, empty and error states; cards show a text label and icon, never colour alone; keyboard operable.

#### U3. Shell, first run, navigation · Depends: U2, F2
Four tabs (DEC-03): bottom bar on mobile, slim sidebar on desktop. Landing: "Try a demo" (persona picker) and "Upload my statement" with the privacy note. Progress screen with friendly steps. A three-tooltip tour. Profile menu: data source switcher, language, privacy panel ("what is shared with the AI"), disclaimer, validation link. Persist onboarding in `localStorage` with try/catch.
**Acceptance:** a fresh visit reaches Home with Rahul in at most three clicks; works at 360 px width.

#### U4. Home · U5. Ask · U6. Plan · U7. Money · Depends: U3 and the matching backend tasks
- **Home:** ScoreRing with meaning line; at most three metric cards above the fold; Best Next Move card; top three alerts; small forecast preview; confidence chip; "based on Jan to Dec, N transactions, updated at" cue; score shown as "Not enough data" when the API returns null.
- **Ask:** four suggested-question chips; messages as Fact (blue), Prediction (orange, confidence), Recommendation (green, impact) cards; VerdictCard; evidence chips on every number; follow-up chips; language toggle; privacy note and disclaimer.
- **Plan:** segmented control: Forecast (p10/p50/p90 band chart, gap markers, **Danger Calendar** heatmap, stress buttons, table view), What-if simulator (controls per action, before/after table, **current path vs recommended path** dual-line chart, guardrail messages), Goals (inputs, feasibility, adjustments).
- **Money:** spending by category and month, recurring obligations with due dates, insights list with severity, **Add data** panel (transaction, loan, income change, expense) with the **What Changed** panel and animated before/after (animation never changes values).
**Acceptance:** each screen has a Vitest test with mocked API data and an accessible table alternative for every chart; no more than 3 metric cards or 2 charts above the fold; no unexplained financial term on Home or Ask (glossary check).

#### U8. Data and Trust (profile menu pages) · Depends: V1 (JSON), U3
Data source switcher (synthetic, Berka, real upload), upload with progress and errors, delete-my-data, privacy panel, validation numbers from `GET /validation` (counts, "X / N", limitations), disclaimer.
**Acceptance:** numbers shown equal the JSON file's values (test); delete removes the user from the list.

#### U9. Accessibility, responsiveness, E2E · Depends: U4 to U8, B7
Playwright flows (desktop and 360 px): (1) demo load and Home score; (2) bills question; (3) laptop affordability with evidence drawer; (4) add ₹12,000 EMI and the What Changed panel; (5) income-stop stress test; (6) language switch; (7) upload error handling. Lighthouse accessibility at least 90 on Home and Ask. Contrast at least 4.5:1, tap targets at least 44 px, focus rings, reduced motion respected.
**Acceptance:** all Playwright flows pass against the seeded stack; Lighthouse threshold met; keyboard-only run-through works.

### Track V: Validate, ship, document

#### V1. Validation suite · Depends: F4, B2, B3, B7
`scripts/run_validation.py` runs and records, **counts and percentages only**: categorisation (synthetic held-out, real held-out), recurring precision and recall, forecast MAE and band coverage (backtest), simulator hand-calculation tests, persona ordering checks, and **LLM faithfulness** (30 fixed questions through the router and a mocked provider; report the share of answers with zero mismatched numbers). Output `docs/validation_report.md` and `docs/validation_report.json`. Each number records its date, data source and test-set size. State limitations (small real test set, person-name payees, synthetic-only scenarios).
**Acceptance:** rerunning reproduces identical numbers (fixed seeds); no private strings in either file; every claim in `README.md` appears in the JSON.

#### V2. Deployment and production readiness · Depends: V1, U9
Restrict CORS to `CORS_ORIGINS`; chat rate limit (default 10 per minute per client) returning 429; structured JSON logs with request ids and redaction; `/ready` checks; Alembic baseline migration and a CI job that runs the suite against Postgres; bounded LLM token limits and a result cache keyed by cleaned inputs; `render.yaml` (backend) and Vercel settings (frontend) documented; deployment smoke script.
**Acceptance:** `docker compose up --build` from a fresh clone completes the Section 1 demo with `LLM_PROVIDER=none`; CI green including Playwright; the Postgres job passes.

#### V3. Documentation and demo · Depends: V2
Refresh `README.md` (status from the ledger, measured numbers only, run instructions for Docker and manual, privacy, limitations, responsible AI); add `docs/ARCHITECTURE.md` (mermaid data-flow and module map), `docs/DEMO.md` (five-minute script from Section 1), `docs/DATA.md` (three layers, what each proves, private-data handling), `docs/PROJECT_SUMMARY.md` (resume bullets and interview answers with **measured** values filled in from the JSON), and contribution guidance that forbids real financial data in issues and pull requests. Fix any contradiction between README, this plan, the build guide and the code.
**Acceptance:** a link checker finds no broken relative links; every number in `PROJECT_SUMMARY.md` appears in `validation_report.json`.

#### V4. Final release gate · Depends: V3
Run every gate in Section 10 plus the Definition of Done (Section 11). Print the final report in the format of Section 0, item 3 of the ledger update, and list known limitations.

---

## 7. Copilot specification (used by B7 and U5)

### 7.1 Principle
Tools compute; the model (or the template) explains. The router and validator are deterministic and always present.

### 7.2 Tools (thin wrappers over services; each returns structured JSON with evidence)

| Tool | Answers |
|---|---|
| `get_spending_breakdown(period, category?)` | Where did my money go? |
| `explain_month_change(month_a, month_b)` | Why was March high? |
| `get_recurring_obligations()` | What bills are coming? |
| `get_health_score()` | How healthy am I? |
| `run_forecast(days)` and `get_gaps()` | Will I run short before salary? |
| `check_affordability(amount, date?)` | Can I afford ₹X? |
| `rank_best_moves()` | What should I do first? |
| `simulate_action(action, params)` | What if I cut dining by 20%? |
| `debt_payoff_plan(extra_amount)` | Which debt first? |
| `stress_test(scenario, params)` | What if income stops? |
| `plan_goal(target, deadline)` | Save ₹1 lakh in 8 months |
| `get_confidence()` | How sure are you? |
| `get_transactions(filter)` | Show the transactions behind that |
| `get_insights()` | Any unusual spending? |

### 7.3 Deterministic router (default and fallback)
Case-insensitive patterns pick tools (several may apply): amount plus `afford|buy|purchase|laptop|phone` → `check_affordability`; `bill|recurring|due|subscription` → `get_recurring_obligations`; `short|gap|run out|trouble paying|before salary` → `run_forecast` + `get_gaps`; `why|high|spend` with a month name → `explain_month_change`; `debt|loan|card|pay first` → `debt_payoff_plan`; `stress|income stops|lose my job|lose income` → `stress_test`; `goal|save ₹X in N months` → `plan_goal`; `score|health|how am i` → `get_health_score`; `sure|confident|reliable` → `get_confidence`; `what should i do|best move|next step` → `rank_best_moves`; `what if|cut|reduce|cancel` → `simulate_action`; `show|transactions|evidence` → `get_transactions`; anything else → a valid schema answer that lists what the copilot can help with (never an invented answer). Amount parsing handles `45000`, `45,000`, `₹45k`, `1.2 lakh`.

### 7.4 Providers
`LLMProvider` interface: `choose_tools(question, tool_specs) -> calls` and `compose(question, tool_results, language) -> Answer JSON`. `none` uses the router and templates. `anthropic`, `gemini` and `ollama` receive **only masked, aggregated** tool output (`mask_for_llm`), never raw statement text. Provider failures return a clear 502 message or fall back to the template, and the answer says which path produced it.

### 7.5 Validation and guardrails
- **Number validator:** normalise Indian formats (`1,25,000`, `₹`, `%`, `lakh`, `crore`) and extract every number from `summary`, `facts`, `predictions` and `recommendations`; each must exist in the tool outputs (formatted forms included), be a date, or be a count of listed items. On failure, regenerate once, then use the template.
- **Section integrity:** facts only from past-data tools; predictions only from forecast, stress and confidence tools; recommendations only from simulation, ranking, affordability, goal and debt tools.
- **Refusals and redirects:** specific stocks or funds, guaranteed returns, tax evasion, loans from unlicensed lenders, and requests to ignore these rules. The refusal is a schema-valid answer with a safe alternative.
- **Privacy:** `mask_for_llm` removes names, account numbers, phone numbers, emails and UPI ids; a canary test proves it. Persist only the sanitised answer JSON.
- **Language:** `en`, `hi`, `mr`. Fixed sentences are translated through `i18n.py` templates; numbers, evidence and structure are unchanged; missing translations fall back to English with `language_fallback: true`.
- **Rate limit:** `CHAT_RATE_LIMIT_PER_MIN` per client; 429 with a message.

### 7.6 The six demo questions (must pass, with and without a provider)
1. "How healthy are my finances?" 2. "Will I have trouble paying bills this month?" 3. "Can I afford a ₹45,000 laptop?" 4. "Which debt should I pay first?" 5. "What if my income stops for 2 months?" 6. "What should I do first?"

---

## 8. Frontend specification (used by U1 to U9)

### 8.1 Simplicity rules (10)
One screen, one job. Answer first, details on demand. Four tabs only. Plain words (Appendix C), jargon only in tooltips. Every number has a sentence. One primary button per screen. At most three metric cards above the fold. Colour carries meaning only. A guided first run. Safe and kind wording (no blame, undo for data changes).

### 8.2 Design tokens

| Token | Value |
|---|---|
| Font | Geist (bundled), numbers with tabular figures; 16 px body, 14 px helper, 28 to 36 px main score |
| Page / card | `#F8FAFC` page, white card, 16 px radius, 1 px `#E2E8F0` border |
| Brand / primary | `#0F4C81` |
| Fact / Prediction / Recommendation / Risk | `#2563EB` / `#D97706` / `#16A34A` / `#DC2626` |
| Text | `#0F172A` main, `#64748B` secondary |
| Spacing and motion | 8 px grid; 150 to 250 ms fades and count-ups; respect `prefers-reduced-motion` |

### 8.3 Accessibility and formats
360 px mobile first; contrast at least 4.5:1; tap targets at least 44 px; visible focus; ARIA labels and a "View as table" toggle on every chart; Lighthouse accessibility at least 90. ₹ with Indian grouping, dates like "27 Nov", "in 5 days" beside upcoming dates, one formatter for the whole app.

### 8.4 Trust cues
Lock icon and "Your data stays private" link; data period and last-updated line on Home; "Guidance, not financial advice" under every recommendation; confidence beside every prediction (amber when Low, with the reason).

---

## 9. Data, validation and privacy rules

- **Layers:** synthetic (`data/synthetic/`, committed), Berka (`data/berka/`, not committed), real (`data/private/`, never committed). Adapters output the canonical schema; engines never know the source.
- **Real statement workflow (already scripted):** `scripts/parse_gpay_pdf.py` (must reconcile to the totals printed on page 1), `scripts/make_label_template.py`, `scripts/prepare_real_labels.py` (writes `data/private/labeled.csv` and `labeled_split.csv`, merchant-level 70/30, seed 42). Labels use the Appendix A list; unknown payees are `Uncategorised` and excluded from accuracy but counted.
- **Split discipline:** write rules and tune models without looking at test rows; run each test set once at the end; if you change anything afterwards, the test set is no longer unseen and the report says so.
- **Reports:** counts and percentages only; never merchant names, person names, raw descriptions, phone numbers or emails from `data/private/`; no in-sample number as a headline.
- **Privacy scan (run before every commit suggestion):** `git ls-files data/private` prints nothing; searching staged changes for phone-number and email patterns and for any string drawn from private files returns zero matches.
- **Claims:** accuracy targets in this plan apply to synthetic data. Real-statement numbers are reported as measured, with the small-sample caveat (one wrong row moves 45-row accuracy by about 2 points).

---

## 10. Quality gates and commands

Run these before marking any task `DONE`. Give both shell forms in docs.

| Gate | bash | PowerShell |
|---|---|---|
| Backend tests (CI style) | `cd backend && python -m pytest -q` | `Set-Location backend; python -m pytest -q` |
| Backend tests (repo root) | `python -m pytest backend/tests -q` | `python -m pytest backend/tests -q` |
| Frontend | `cd frontend && npm ci && npm run lint && npx tsc --noEmit && npm run build && npm test` | same with `;` separators |
| E2E | `cd frontend && npx playwright test` | same |
| Stack smoke | `bash scripts/smoke.sh` | `./scripts/smoke.ps1` |
| Validation | `python scripts/run_validation.py` | same |
| Privacy | `git ls-files data/private` (must be empty) and the pattern searches in Section 9 | same |

A task fails its gate if any command errors, a test is skipped without a written reason, or a warning appears that is not documented.

---

## 11. Definition of done (whole application)

1. Fresh clone plus `docker compose up --build` serves the app with five seeded personas and no API key.
2. The Section 1 demo story works end to end, including Add EMI producing a correct What Changed explanation.
3. Health score, confidence, forecast with bands and gaps, stress tests, simulator, Best Next Move, affordability and goals all return typed responses with resolvable evidence.
4. Copilot answers are schema-valid, three-part, evidence-backed and number-validated, with and without an LLM provider, in English, Hindi and Marathi.
5. Four-tab UI works on 360 px and desktop; Playwright flows and Lighthouse accessibility 90 or more pass.
6. `docs/validation_report.*` contains only measured, reproducible numbers with limitations; `README.md`, this plan, the build guide and the code agree.
7. No private data in git history, logs, reports or fixtures.
8. CI green: backend (backend/ and root), frontend lint/type/build/unit, Playwright, Docker build, Postgres job.

---

## 12. Progress ledger (the agent updates this table; evidence is counts only)

| ID | Task | Depends | Status | Date | Evidence |
|---|---|---|---|---|---|
| F1 | Reproducible environment and hygiene | none | TODO | | |
| F2 | Demo seeding | F1 | TODO | | |
| F3 | Service layer and thin routes | F1 | TODO | | |
| F4 | Categoriser repair | F3 | TODO | | |
| F5 | One set of finance definitions | F3 | TODO | | |
| F6 | Persona stories and demo scenario | F4, F5 | TODO | | |
| B1 | Confidence completion | F5 | PARTIAL: exists, needs coverage and p2p penalties | | |
| B2 | Forecast v2 and backtest | F5, F6 | PARTIAL: engine exists with D-02/03/04 | | |
| B3 | Simulator, ranking, affordability, goals | B2 | PARTIAL: stub (3 actions) | | |
| B4 | Insights | F5 | TODO | | |
| B5 | Evidence service | B2, B3, B4 | TODO | | |
| B6 | Live update and What Changed | B3, B5 | PARTIAL: mechanics exist, demo fails (D-05) | | |
| B7 | Copilot | B3, B4, B5, B6 | PARTIAL: stub (D-06) | | |
| B8 | Ingestion hardening | F3 | PARTIAL: size limit only | | |
| U1 | Frontend foundation | F3 | TODO | | |
| U2 | Component library | U1 | TODO | | |
| U3 | Shell, first run, navigation | U2, F2 | TODO | | |
| U4 | Home screen | U3, B1 | TODO | | |
| U5 | Ask screen | U3, B7 | TODO | | |
| U6 | Plan screens | U3, B2, B3 | TODO | | |
| U7 | Money screens | U3, B4, B6 | TODO | | |
| U8 | Data and Trust | U3, V1 | TODO | | |
| U9 | Accessibility and E2E | U4 to U8, B7 | TODO | | |
| V1 | Validation suite | F4, B2, B3, B7 | TODO | | |
| V2 | Deployment and production readiness | V1, U9 | TODO | | |
| V3 | Documentation and demo | V2 | TODO | | |
| V4 | Final release gate | V3 | TODO | | |

**Order of execution when nothing else dictates:** F1, F2, F3, F4, F5, F6, B1, B2, B3, B4, B5, B6, B7, B8, U1 to U9 (U tasks may start as soon as their backend dependencies are `DONE`), V1 to V4.

---

## 13. Handoff log and blockers (append only)

| Date | Agent or platform | Task | Note (what is done, what is next, any blocker) |
|---|---|---|---|
| | | | |

---

## Appendix A. Fixed category list

Salary, Other Income, Rent, Utilities, Groceries, Food Delivery, Dining, Transport, Shopping, Entertainment, Subscriptions, Health, Insurance, Education, EMI/Loan, Credit Card Payment, Investment/SIP, Transfers, Cash Withdrawal, Fees and Charges, Travel, Uncategorised.

## Appendix B. Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./arthapilot.db` | database |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | backend URL for the frontend |
| `CORS_ORIGINS` | `http://localhost:3000` | allowed origins, comma separated |
| `DATA_DIR` | repo `data/` or `/app/data` | personas and labels |
| `SEED_DEMO` | `true` | seed personas at startup |
| `LLM_PROVIDER` | `none` | `none`, `anthropic`, `gemini`, `ollama` |
| `LLM_MODEL`, `LLM_BASE_URL` | empty | provider model name; Ollama URL |
| `ANTHROPIC_API_KEY`, `GEMINI_API_KEY` | empty | needed only for those providers |
| `CHAT_RATE_LIMIT_PER_MIN` | `10` | chat rate limit |
| `UPLOAD_MAX_SIZE_MB` | `10` | upload limit |
| `LOG_LEVEL` | `INFO` | logging |

## Appendix C. Plain-language labels (UI never shows the technical name first)

| Technical | Plain label |
|---|---|
| savings_rate | Share of income you keep |
| debt_to_income | Debt payments vs income |
| emergency_runway_months | Months you could last without income |
| fixed_expense_ratio | Fixed bills vs income |
| credit_utilisation | Credit card used |
| spending_volatility | How much your spending swings |
| income_stability | How steady your income is |
| p10 / p50 / p90 | Worst case / likely / best case |
| Monte Carlo band | Range of likely outcomes |

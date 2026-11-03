# ArthaPilot End-to-End Build Plan

## 1. Purpose and source of truth

This plan turns the requirements in [README.md](README.md), [docs/BUILD_GUIDE.md](docs/BUILD_GUIDE.md), and [AGENTS.md](AGENTS.md) into an executable delivery sequence. The build guide is the product specification; this file is the current-state assessment, dependency order, implementation checklist, and release gate.

The project is a local-first financial-health web app:

1. A user loads a demo persona, public banking data, or a private statement.
2. The backend normalises it into one canonical transaction model.
3. Deterministic Python modules calculate facts, forecasts, and simulations.
4. An LLM may select tools and explain verified results, but never calculates money.
5. The frontend presents separate Fact, Prediction, and Recommendation experiences.
6. Every displayed number is traceable to transaction/entity evidence or an explicit formula.

## 2. Non-negotiable engineering rules

These rules come from [AGENTS.md](AGENTS.md) and must be applied to every phase:

- Keep all monetary values as integer paise. Ratios and scores may be floating point.
- The LLM only chooses tools and explains structured tool output; Python owns all calculations.
- Every answer has separate Observed Fact, Prediction, and Recommendation sections.
- Every number includes evidence IDs or the formula used to derive it.
- Mask names, account numbers, phone numbers, and UPI IDs before any LLM call.
- Keep real statements only under `data/private/`; never commit them.
- Add unit tests for every module. A phase is not complete until its tests pass.
- Surface errors explicitly; do not silently fall back to invented or success-shaped data.
- Preserve the existing canonical schema and evidence provenance when adding modules.

## 3. Current status assessment

### 3.1 Verified baseline

Before creating this plan, the working tree had no tracked-file modifications. The following validation was run from the repository root:

```powershell
Set-Location backend
python -m pytest
Set-Location ..\frontend
npm run build
```

The backend suite passes all collected tests, and the Next.js production build succeeds. The test command emits a Starlette/httpx deprecation warning that should be cleaned up before production, but it does not currently fail the build.

### 3.2 Implemented foundations

- Repository structure, Docker files, environment examples, and GitHub Actions CI exist.
- FastAPI backend and SQLAlchemy models exist for users, accounts, transactions, loans, cards, investments, recurring items, goals, snapshots, and chat messages.
- SQLite configuration and integer-paise fields are in place.
- Ingestion includes cleaning, anonymisation, parser/adapters, and a Google Pay adapter.
- Synthetic personas, scenario helpers, Berka scripts, label/evaluation scripts, and private-data boundaries exist.
- Categorisation contains merchant cleaning, rules, a scikit-learn artefact path, and an LLM fallback.
- Recurring detection and income detection exist.
- Health metrics and score computation exist, with configurable mappings, evidence payloads, coverage, partial-month handling, and API response schemas.
- Existing API routes include health, user listing, upload, persona loading, processing, recurring results, and health results.
- The frontend is a functioning Next.js shell with a backend health check and a reusable button component.

### 3.3 Implemented but not yet release-quality

- Categorisation is present but the recorded validation report shows low coverage and low held-out accuracy. The report must be regenerated after fixing the cascade, model training/data split, label coverage, and evaluation methodology.
- Phase 2 is therefore code-complete in breadth, but not acceptance-complete against the build guide's quality target.
- The frontend does not yet expose the implemented ingestion, recurring, or health APIs as a product workflow.
- Docker and CI exist, but an end-to-end fresh-clone run and deployment smoke test still need to be verified.
- The database has no documented migration/versioning strategy for future schema changes.
- The backend has no forecast, confidence, simulation, copilot, insight, snapshot-diff, or production API modules yet.

### 3.4 Not implemented

The following build-guide phases are still outstanding:

- Data-quality/confidence engine.
- Cash-flow forecast, gap detection, stress tests, and backtesting.
- Action simulator, debt payoff, affordability, goal planning, and recommendation ranking.
- Tool-calling copilot, number validator, answer schema, language option, and privacy guardrails.
- Complete frontend information architecture, charts, evidence drawer, responsive/accessibility system, and first-run flow.
- Live update and What Changed snapshots/diff.
- Insights and anomaly/subscription-creep detectors.
- Full validation report, Playwright flow, deployment, observability, and final demo documentation.

## 4. Target architecture

### Backend layers

1. **Persistence and contracts:** SQLAlchemy models, Pydantic schemas, database session, migrations/versioning.
2. **Ingestion:** file validation, parser selection, canonical transaction conversion, anonymisation, source metadata.
3. **Understanding:** merchant cleaning, category cascade, recurring detection, income detection.
4. **Deterministic analytics:** metrics, confidence, forecast, stress tests, simulations, insights.
5. **Application services:** orchestration around one user state, snapshots, diff generation, evidence lookup.
6. **Copilot:** tool definitions, safe context builder, provider adapter, validator, fallback templates.
7. **API:** thin routes that validate input, call services, and return typed responses.

### Frontend layers

1. Typed API client and query/loading/error states.
2. Shared formatters for paise, Indian digit grouping, dates, confidence, and evidence links.
3. Reusable Fact/Prediction/Recommendation, metric, score, confidence, verdict, evidence, and before/after components.
4. Four-tab product navigation: Home, Spending, Forecast, and Ask; secondary flows for Plan and Data.
5. Charts with accessible table views and responsive mobile-first layouts.
6. Demo onboarding, scenario controls, privacy panel, and What Changed experience.

### Data flow

`source -> parser -> canonical transactions -> clean/categorise -> recurring/income -> metrics/confidence -> forecast -> simulate/recommend -> copilot/tools -> validated UI`

No layer may bypass canonical data or recompute financial values in TypeScript/LLM text.

## 5. Delivery sequence

### Phase 0 - Stabilise the foundation

**Goal:** make the existing project reproducible before adding features.

- Confirm Python, Node, Docker, environment variables, and database paths on Windows and CI.
- Ensure `data/private/`, `.env`, databases, generated artefacts, and dependency directories remain ignored.
- Decide whether to add Alembic now or document controlled `create_all` for the demo; use migrations before production.
- Update dependency pins and remove the Starlette/httpx warning where compatible.
- Add a single documented smoke script for backend health, frontend build, and Docker startup.
- Ensure CORS is explicit and environment-driven rather than permissive.

**Exit gate:** fresh clone runs the documented commands; backend tests, frontend build, and Docker health checks pass.

### Phase 1 - Canonical data and ingestion hardening

**Goal:** guarantee that every source produces the same safe transaction shape.

- Document and enforce required canonical fields: stable transaction ID, user/account IDs, ISO date, signed integer paise, raw description, cleaned merchant, category/confidence, recurring flag, and source.
- Add strict CSV/XLSX/PDF upload validation, size limits, extension/content checks, and clear errors.
- Keep raw private statement content out of logs and LLM context.
- Add duplicate transaction handling and deterministic transaction IDs.
- Verify persona, Berka, and private GPay paths all persist valid users/accounts/transactions.
- Add API tests for malformed files, oversized files, unsupported types, and reprocessing.

**Exit gate:** three data layers load through one contract and all ingestion tests pass without exposing private data.

### Phase 2 - Categorisation, recurring, and income quality

**Goal:** finish the existing understanding layer and make its measurements trustworthy.

- Expand merchant cleaning and rules to cover the fixed category list, Indian UPI variants, transfers, refunds, card payments, EMI, and utilities.
- Fix the model training/evaluation path so the saved artefact is actually used when appropriate.
- Define confidence thresholds and make fallback layer selection observable in reports.
- Improve label coverage and split discipline; distinguish model coverage from accuracy.
- Preserve recurring evidence IDs, next due date, interval, amount tolerance, and confidence.
- Validate salary versus irregular income and transfer exclusions.
- Regenerate [docs/validation_report.md](docs/validation_report.md) with honest held-out metrics.

**Exit gate:** recurring planted cases pass; category metrics are measured on representative labelled data; no claim is made without a generated report.

### Phase 3 - Health metrics and score integration

**Goal:** expose the existing pure metrics as a useful product contract.

- Keep metric calculations pure and integer-paise based.
- Confirm savings rate, DTI, emergency runway, fixed expenses, utilisation, volatility, and income stability definitions against [docs/metrics.md](docs/metrics.md).
- Keep unavailable metrics unavailable; do not invent balances or scores.
- Return raw value, unit, status, sub-score, points, reason, and evidence provenance.
- Add API response fixtures for healthy, debt-heavy, irregular-income, no-card, zero-income, and insufficient-history users.
- Build the first frontend dashboard around the existing health endpoint.

**Exit gate:** backend metric tests pass, evidence is navigable, and a user can load a persona and see a correctly qualified score.

### Phase 4 - Confidence and data quality

**Goal:** attach an honest confidence result to every prediction and answer.

- Implement `metrics/confidence.py` with penalties for history length, income irregularity, uncategorised share, missing debt/card data, date gaps, and sparse recurring evidence.
- Return score, High/Medium/Low level, reasons, and concrete improvement actions.
- Make confidence independent from health score; low confidence must not be hidden by a good-looking score.
- Add `GET /users/{id}/confidence`.
- Add tests for each penalty, thresholds, combinations, and Arjun-versus-Priya behavior.

**Exit gate:** confidence is visible in API contracts and can explain exactly how to improve it.

### Phase 5 - Forecast and stress testing

**Goal:** produce an explainable 90-day daily cash-flow forecast.

- Build a deterministic schedule from income, recurring items, EMIs, and card dues.
- Model variable spend by weekday using recent history and an empirical distribution.
- Implement seeded Monte Carlo forecasting with p10, p50, and p90 daily balances.
- Return source/evidence references for scheduled items and formula references for model-derived values.
- Detect safe-threshold breaches, breach dates, expected balance, and probability of going below zero.
- Implement income-stop, expense-rise, emergency-expense, and new-EMI stress tests.
- Add a hold-out backtest script for Berka and private labelled data, recording MAE and band coverage.
- Add forecast, gaps, and stress-test routes with typed schemas.

**Exit gate:** deterministic persona gap dates are tested; stress-test survival output is reproducible; backtest results are published without fabricated values.

### Phase 6 - Simulation and recommendations

**Goal:** turn advice into measurable before/after scenarios.

- Define an immutable user-state snapshot consumed by `simulate(state, action)`.
- Implement category cuts, subscription cancellation, extra debt payments, avalanche/snowball, savings/SIP changes, delayed purchases, cash/EMI purchases, refinancing, and emergency-buffer actions.
- Use exact paise and amortisation maths; expose interest saved and months saved with formulas/evidence.
- Re-run metrics, confidence, forecast, and gap detection after each action.
- Rank actions by impact versus effort and expose Best Next Move plus alternatives.
- Implement affordability as Yes/Risky/No with safer alternatives.
- Implement goal planning with required monthly saving, feasibility, and adjustment options.
- Enforce guardrails against skipped debt payments, insufficient emergency funds, and high-risk investment advice.
- Add simulator, best-moves, affordability, and goal routes.

**Exit gate:** state purity, hand-calculated debt maths, ranking, affordability, goal, and guardrail tests pass.

### Phase 7 - Conversational copilot

**Goal:** add natural language without giving the model calculation authority.

- Define typed tools for spending, changes, recurring obligations, health, forecast, gaps, affordability, best moves, simulation, debt payoff, stress tests, goals, confidence, and evidence transactions.
- Build a provider-neutral interface; configure Anthropic/Claude through environment variables only.
- Send only aggregated outputs and masked merchant names.
- Validate model output with a Pydantic answer schema containing summary, facts, predictions, recommendations, verdict, and follow-ups.
- Enforce that facts come from fact tools, predictions from forecast tools, and recommendations from simulation tools.
- Extract every number from generated text and compare it with tool output; regenerate once, then use a deterministic template fallback.
- Persist chat messages without persisting unsafe raw prompts or statement data.
- Add English/Hindi/Marathi language selection without changing numeric structure.
- Add refusal/redirect handling for specific-stock, guaranteed-return, tax-evasion, and other out-of-scope requests.
- Add `POST /users/{id}/chat`.

**Exit gate:** five demo questions return valid three-part answers; fabricated numbers are rejected; tests prove no raw statement text reaches the LLM.

### Phase 8 - Frontend product experience

**Goal:** replace the health-check shell with a trustworthy, accessible application.

- Build typed API hooks and shared request/error/loading states.
- Implement first-run demo persona/upload flow and progress messaging.
- Build Home dashboard: score ring, metric cards, confidence, health issues, Best Next Move, last-updated/data-period cues.
- Build Spending: category breakdown, trends, recurring obligations, behaviour and anomaly placeholders/results.
- Build Forecast: p10/p50/p90 chart, gap markers, danger calendar, stress-test controls, table view.
- Build Ask: suggested questions, chat messages, Fact/Prediction/Recommendation cards, verdict, follow-ups, language toggle.
- Build Plan/Simulator: action controls, before/after metrics, dual forecast paths, guardrail messaging.
- Build Data/Trust: source switcher, upload, privacy panel, validation results, disclaimer.
- Add evidence drawer for every number and formula.
- Use Indian currency/date formatting through shared utilities.
- Apply colour plus text/icon labels; meet keyboard, focus, contrast, tap-target, chart-ARIA, responsive, and reduced-motion requirements.

**Exit gate:** Playwright can load a demo, ask an affordability question, inspect evidence, and complete the primary flow on a narrow viewport.

### Phase 9 - Live updates and What Changed

**Goal:** demonstrate that new data changes advice deterministically.

- Save a snapshot before every transaction, loan, income, or expense change.
- Reprocess the user and recompute metrics, confidence, forecast, gaps, and recommendations.
- Diff score, raw metrics, confidence, gaps, top recommendation, and relevant evidence.
- Generate a deterministic explanation first; optionally use the LLM only to rephrase verified text.
- Add transaction, loan, income-change, and What Changed routes.
- Animate before/after changes in the frontend without changing values.

**Exit gate:** adding an EMI to Rahul changes score, gap, and recommendation, and the explanation matches the computed diff.

### Phase 10 - Insights and trust features

**Goal:** deliver the high-value differentiators after the core path is reliable.

- Implement weekday/weekend, post-salary, and month-end spending insights.
- Detect duplicate charges, merchant anomalies, subscription price hikes, and overlapping subscriptions.
- Return severity, plain-language text, and evidence IDs.
- Add privacy panel, responsible-AI disclaimer, confidence explanations, and validation display.
- Add Hindi/Marathi UI copy only after English flows are stable.

**Exit gate:** planted synthetic cases trigger the correct insight and evidence; false positives are documented.

### Phase 11 - Validation and release testing

**Goal:** prove correctness and communicate limits honestly.

- Run category accuracy, precision/recall, recurring precision/recall, forecast MAE, forecast band coverage, simulator hand calculations, and LLM faithfulness tests.
- Run full Playwright demo flow against a seeded test database.
- Publish only measured values in [docs/validation_report.md](docs/validation_report.md).
- Add regression fixtures for every fixed bug and every API contract.
- Run accessibility checks and performance checks on the production build.

**Exit gate:** all backend tests, frontend type/build checks, browser tests, and validation scripts pass; known limitations are written down.

### Phase 12 - Deployment and production readiness

**Goal:** make the app safe and reproducible outside the development machine.

- Deploy the backend to Render or Railway and the frontend to Vercel, with separate environment configuration.
- Restrict CORS to the deployed frontend origin.
- Add upload content/size limits, rate limiting for chat, structured logs, request IDs, and redacted error reporting.
- Keep SQLite for the demo but document and test the Postgres migration path.
- Cache category and repeated copilot results with safe keys and bounded token usage.
- Ensure demo mode works without signup and private uploads are session-scoped or deleted as documented.
- Add health/readiness checks and a deployment smoke test.
- Run CI on backend tests, frontend build, and Playwright.

**Exit gate:** a fresh clone starts with Docker and the deployed URL completes the demo flow using a demo persona.

### Phase 13 - Documentation and demonstration

**Goal:** package the work for users, reviewers, and future maintainers.

- Update README status and validation tables from measured results.
- Add architecture/data-flow diagrams and setup troubleshooting.
- Document privacy boundaries, limitations, and responsible-AI behavior.
- Record a five-minute demo: Rahul dashboard, bill-risk question, laptop affordability, evidence drawer, EMI change, income-stop stress test, and validation view.
- Fill resume/interview claims only with measured values.
- Add contribution guidance that forbids real financial data in issues and pull requests.

**Exit gate:** README, build guide, validation report, and demo script agree with the shipped behavior.

## 6. Dependency-aware execution order

Do not start a later phase until its prerequisites are green:

```text
Phase 0
  -> Phase 1
  -> Phase 2 hardening
  -> Phase 3 API/frontend integration
  -> Phase 4 confidence
  -> Phase 5 forecast
  -> Phase 6 simulation
  -> Phase 7 copilot
  -> Phase 8 frontend completion
  -> Phase 9 live updates
  -> Phase 10 insights
  -> Phase 11 validation
  -> Phase 12 deployment
  -> Phase 13 final documentation
```

Within each phase, use this loop:

1. Write or update typed contracts.
2. Implement pure domain logic.
3. Add unit tests with hand-verified fixtures.
4. Add service/API integration tests.
5. Wire the frontend only after the API contract is stable.
6. Run targeted tests, then the full regression suite.
7. Update validation/docs and record any measured limitation.

## 7. Definition of done for the complete app

- A demo persona can be loaded in under the documented first-run workflow.
- A private statement can be uploaded safely and processed through the canonical schema.
- Dashboard health metrics include reasons, confidence, and evidence.
- Forecasts include daily p10/p50/p90 balances, gaps, and stress tests.
- Recommendations show deterministic before/after impact and guardrails.
- Copilot answers are schema-valid, three-part, evidence-backed, and number-validated.
- Frontend screens work on mobile and desktop with accessible chart alternatives.
- Adding data produces a correct What Changed explanation.
- Validation numbers are measured, reproducible, and honestly reported.
- Docker, CI, deployment, privacy controls, and documentation all match the actual implementation.

## 8. Immediate next work

1. Stabilise Phase 0 reproducibility and CORS/upload/database boundaries.
2. Resolve the Phase 2 categorisation quality/coverage gap and regenerate its report.
3. Integrate the existing health API into the first dashboard flow.
4. Implement and test the confidence engine.
5. Proceed through forecast, simulation, copilot, and frontend in dependency order.

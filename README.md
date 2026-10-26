# ArthaPilot

**Your Financial Health Copilot.** ArthaPilot brings your bank accounts, cards, loans and investments into one clear picture, predicts upcoming cash-flow trouble, and tells you what to do next, with the expected impact of every suggestion.

![Status](https://img.shields.io/badge/status-in%20development-orange)
![Phase](https://img.shields.io/badge/phase-1%20complete-blue)
![License](https://img.shields.io/badge/license-MIT-green)

> **Project status:** Phase 1 (data layer) is complete. Features below marked "Planned" are not built yet. See the [Roadmap](#roadmap) for exact progress. This README is updated at the end of every phase.

---

## Table of Contents

1. [The Problem](#the-problem)
2. [What ArthaPilot Does](#what-arthapilot-does)
3. [Key Features](#key-features)
4. [How It Works (Architecture)](#how-it-works-architecture)
5. [Data and Validation](#data-and-validation)
6. [Tech Stack](#tech-stack)
7. [Getting Started](#getting-started)
8. [Project Structure](#project-structure)
9. [Roadmap](#roadmap)
10. [Validation Results](#validation-results)
11. [Privacy and Responsible AI](#privacy-and-responsible-ai)
12. [Limitations](#limitations)
13. [Testing](#testing)
14. [Contributing](#contributing)
15. [License and Author](#license-and-author)

---

## The Problem

Most people have several accounts, cards, loans, investments and recurring payments, but no single view of their overall financial health. They find out about a cash shortfall only when it happens, and they rarely know which action would help most.

## What ArthaPilot Does

- Builds one **consolidated financial-health view** from transaction and financial-history data.
- Finds **spending patterns, recurring bills, debt pressure and future cash-flow gaps**.
- Answers questions in **plain language**, such as "Can I afford a 45,000 rupee laptop?"
- Shows the **expected impact** of every recommended action (before vs after), not just the current position.
- Keeps **observed facts, model predictions and recommendations clearly separate**, with a confidence level wherever information is incomplete.
- **Recalculates live** when new transactions, income, loans or expenses are added, and explains what changed.

## Key Features

Status key: Done, In progress, Planned.

| Feature | Status |
|---|---|
| Runnable backend and frontend skeleton, Docker, CI | Done |
| Three-layer data pipeline (synthetic, Berka, real statements) | Done |
| Transaction categorisation and recurring-bill detection | Planned |
| Financial Health Score (0 to 100) with reasons | Planned |
| Confidence meter with reasons and "how to improve" | Planned |
| 90-day cash-flow forecast with best, likely and worst bands | Planned |
| Danger Calendar (risky days highlighted) | Planned |
| Stress tests (income stops, expenses rise, emergency expense) | Planned |
| Action simulator with before/after impact | Planned |
| Best Next Move ranking | Planned |
| Affordability verdict (Yes / Risky / No) with safer alternatives | Planned |
| Goal planner | Planned |
| Conversational copilot with Fact / Prediction / Recommendation cards | Planned |
| Evidence links (click a number to see the transactions behind it) | Planned |
| Live update with a "What changed" explainer | Planned |
| Anomaly, duplicate and subscription-creep alerts | Planned |
| Hindi and Marathi mode | Planned |

## How It Works (Architecture)

The most important design rule: **the AI never does the maths.**

```
User question
   -> LLM picks a tool and its arguments
   -> Python code runs the calculation on real data
   -> Tool returns structured results (numbers, evidence IDs, confidence)
   -> LLM explains the verified result in simple language
   -> Validator checks every number in the answer against the tool output
   -> UI shows Fact / Prediction / Recommendation cards
```

Every answer has three visibly separate parts:

| Part | Meaning | Shown with |
|---|---|---|
| Observed Fact | What happened, from your data | Blue, with evidence links |
| Prediction | What is likely to happen | Orange, with confidence and reasons |
| Recommendation | What to do | Green, with simulated impact |

Core modules (backend): ingestion, categorise, recurring, metrics, forecast, simulate, copilot, insights.

## Data and Validation

ArthaPilot uses three data layers that all feed one common transaction format, so the engine never knows which source it is reading.

| Layer | Purpose | What it proves |
|---|---|---|
| **Synthetic personas** (5 profiles, 12 months each) | Controlled demos and edge cases such as income stops or a new EMI | The engine reacts correctly to specific scenarios |
| **Berka public banking dataset** | Real anonymised banking patterns | Cash-flow, recurring detection, forecasting and loan logic work on real transaction patterns |
| **Real anonymised statements** (own and consenting volunteers) | Messy real-world data | Upload parsing and categorisation handle real statements |

Honest notes: the Berka dataset is from a Czech bank and is not in rupees, so it tests cash-flow logic rather than merchant-name categorisation. Synthetic data is used only for scenario testing, never as proof of accuracy. Accuracy numbers come from real and public data only.

No real user data is ever committed to this repository.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI, SQLAlchemy, Pydantic |
| Data and maths | pandas, numpy, scipy, statsmodels, scikit-learn |
| Database | SQLite (Postgres-ready) |
| LLM | Provider-agnostic client (configurable through environment variables) |
| Frontend | Next.js 14, TypeScript, Tailwind CSS, shadcn/ui, Recharts |
| Testing | pytest, Vitest, Playwright |
| DevOps | Docker, docker-compose, GitHub Actions |

## Getting Started

### Prerequisites

- Git
- Python 3.11 or newer
- Node.js 18 or newer
- Docker Desktop (optional but recommended)

### Option A: Run with Docker (recommended)

```bash
git clone https://github.com/<your-username>/arthapilot.git
cd arthapilot
cp .env.example .env
docker-compose up --build
```

Then open:

- Frontend: http://localhost:3000
- Backend health check: http://localhost:8000/health
- API docs: http://localhost:8000/docs

### Option B: Run manually

**Backend**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend** (in a second terminal)

```bash
cd frontend
npm install
npm run dev
```

### Environment variables

Copy `.env.example` to `.env` and fill in what you need. Never commit `.env`.

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Database connection (default: SQLite) |
| `NEXT_PUBLIC_API_URL` | Backend URL used by the frontend |
| `LLM_PROVIDER` | Which LLM provider to use (set up in Phase 7) |
| `LLM_MODEL` | Model name for that provider |
| `ANTHROPIC_API_KEY`, `GEMINI_API_KEY` | API key for the provider you choose (only needed from Phase 7) |

## Project Structure

```
arthapilot/
├── CLAUDE.md              # Golden Rules for AI coding agents
├── README.md
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── app/               # FastAPI app (routers, models, modules)
│   └── tests/
├── frontend/              # Next.js app
├── data/
│   ├── synthetic/         # Generated personas (committed)
│   ├── berka/             # Public dataset (not committed)
│   ├── private/           # Real statements (git-ignored, never committed)
│   └── labeled/           # Hand-labelled transactions for accuracy tests
├── scripts/               # Data generators, loaders, evaluation scripts
└── docs/
    └── BUILD_GUIDE.md     # Full phase-by-phase build guide
```

## Roadmap

| Phase | Goal | Status |
|---|---|---|
| 0 | Project skeleton: backend, frontend, Docker, CI | Done |
| 1 | Data layer: personas, Berka loader, upload and cleaning | Next |
| 2 | Categorisation and recurring/income detection | Planned |
| 3 | Health metrics and 0 to 100 score | Planned |
| 4 | Data-quality and confidence engine | Planned |
| 5 | Cash-flow forecast, gap detection, stress tests, backtests | Planned |
| 6 | Action simulator, Best Next Move, affordability, goals | Planned |
| 7 | Conversational copilot with tool use and number validator | Planned |
| 8 and 8A | Frontend screens and UI/UX design system | Planned |
| 9 | Live update and "What changed" explainer | Planned |
| 10 | Insights, anomaly alerts and extra features | Planned |
| 11 | Validation and testing report | Planned |
| 12 | Deployment and production readiness | Planned |
| 13 | Final README, demo and interview preparation | Planned |

The detailed plan for each phase is in [`docs/BUILD_GUIDE.md`](docs/BUILD_GUIDE.md).

## Validation Results

These numbers will be filled in only after they are measured. No figures are claimed until then.

| Test | Data used | Result |
|---|---|---|
| Categorisation accuracy | Hand-labelled real transactions | To be measured |
| Recurring-bill detection (precision / recall) | Hand-marked recurring items | To be measured |
| Forecast error (MAE) | Hold-out backtest on Berka and real data | To be measured |
| Forecast band coverage (10 to 90 percent) | Same backtest | To be measured |
| LLM answer faithfulness (answers with zero mismatched numbers) | 30 test questions | To be measured |

Full methodology and results will be published in `docs/validation_report.md`.

## Privacy and Responsible AI

- **Local first:** calculations run on your own machine or server.
- **Masking:** names, account numbers, phone numbers and UPI IDs are masked before any text is sent to an LLM.
- **Minimum sharing:** the LLM receives only aggregated results and cleaned merchant names, never raw statements.
- **No real data in git:** `data/private/` and `.env` are git-ignored.
- **Disclaimer:** ArthaPilot provides guidance, not regulated financial advice. It will not recommend specific stocks, guaranteed returns, stopping debt payments, or skipping an emergency fund for investing.

## Limitations

- The forecast is a statistical estimate. Accuracy depends on how much history is available and how regular income and spending are.
- Confidence is lower with fewer than 6 months of data, irregular income, uncategorised transactions or missing accounts. The app shows this and explains why.
- Berka data is not in rupees and has no merchant names.
- Parsers support a limited set of bank formats and a generic column-mapping fallback.

## Testing

```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm run build
```

Continuous integration runs these checks on every push through GitHub Actions.

## Contributing

This is currently a personal portfolio project. Suggestions and issues are welcome. Please never include real financial data in an issue or pull request.

## License and Author

Released under the MIT License. See `LICENSE`.

Built by **<Your Name>**. Connect on [LinkedIn](https://www.linkedin.com/in/padmakarbagade2005) or [GitHub](https://github.com/PadmakarBagade).

# AGENTS.md

**Start here:** read `plan.md` (Sections 0 to 3, then the active task in the progress ledger). It is the single source of truth for what to build and in what order. If you are told "read plan.md and build the application", follow plan.md Section 0.

## Golden Rules (apply to every task)

- The LLM never calculates money. All numbers come from tested Python functions. The LLM only chooses tools and explains verified results.
- Every number shown to the user must carry an evidence reference (transaction IDs, entity IDs, or the formula used).
- Every answer has three separate sections: Observed Fact, Prediction (with confidence), Recommendation (with simulated impact).
- All money is stored as integer paise (1 rupee = 100 paise) to avoid floating-point errors.
- Every module gets unit tests. No task is finished until its tests pass.
- Never commit real user data. Real statements live only in `data/private/`, which is git-ignored.
- Mask personal data (names, account numbers, phone numbers, UPI IDs, emails) before anything is sent to an LLM.
- Never run `git push`. Do not run `git commit` unless the user asks for auto-commit.
- Report only measured numbers. Never invent or round up validation results.
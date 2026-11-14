# Two-minute demo

## Before the interview

Run `streamlit run app.py` from the activated environment and keep the test result available in a second terminal. Use only the disposable SQLite demonstration database.

## 0:00–0:20 — Frame the problem

“This is a support-engineering lab for ten recurring wholesale-system incidents. Each exercise uses the same investigation structure: symptom, safe reproduction, evidence query, root cause, correction, prevention, and automated verification.”

Show the incident list and point out that the local database is disposable.

## 0:20–1:10 — Investigate one incident

Choose **Duplicate payments**. Show the symptom, reproduce it, and run the investigation. Explain why grouping by the business payment reference exposes a problem that a unique surrogate key would not. Apply the correction and show that the verification now passes.

## 1:10–1:35 — Show safety and breadth

Reset the database. Briefly show **Incorrect order totals** and the failed-import or missing-index exercise. Explain that SQL Server deadlock material is included separately because the local concurrency simulation is not equivalent to a verified SQL Server deadlock run.

## 1:35–2:00 — Prove engineering discipline

Show `pytest -q` and `docs/incidents.md`. Close with: “The project demonstrates how I communicate an incident, preserve evidence, correct data safely, and add a regression check—not just how I write a query.”

## Do not claim

- Do not describe SQLite execution as SQL Server validation.
- Do not claim Docker or the deadlock script was run unless you run it yourself.
- Do not present synthetic incidents as client or employment experience.


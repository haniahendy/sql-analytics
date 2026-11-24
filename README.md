# sql-analytics

Product-analytics SQL practice on SQLite, wrapped in tests: signup-to-purchase funnel, weekly signups with a running total (window function), and 7-day retention by signup-month cohort (correlated EXISTS subquery).

## Run
```bash
pip install -r requirements.txt
python -m pytest -q   # 4 tests
python run.py
```

## Measured output (synthetic data, seed 1, 300 users)
Funnel: 300 signups, 186 activated, 104 purchased. 7-day retention: about 47% for the January and February cohorts (the March cohort has only 8 users).

Retention logic is also tested on a hand-built 2-user table, where the answer is known (0.5).

## Limits
Synthetic events. SQLite week numbers (`%W`) start the year at week 00, which is not ISO. "Retained" here means any event 7 or more days after signup, a loose definition. No indexes or query-plan work.

## Provenance
A learning and portfolio project.

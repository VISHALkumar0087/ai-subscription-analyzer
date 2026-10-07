# AI Monthly Subscription Analyzer

Analyzes your monthly subscriptions, finds spending patterns, and highlights unnecessary or excessive expenses.

## Features
- Auto-categorizes subscriptions (Entertainment, Learning, Fitness, Productivity)
- Shows spend per category and yearly cost
- Scores each subscription using rules: unused for 30+ days, takes 25%+ of budget, overlapping services
- Verdict for each: **Keep / Review / Cancel**, plus estimated savings
- Generates a shareable `report.html`

## Run
```bash
python analyzer.py                 # uses subscriptions.csv
python analyzer.py my_data.csv     # use your own file
```
Open `report.html` in a browser to see the report. Needs only Python 3, with no extra libraries.

## CSV format
```
name,monthly_cost,last_used_days_ago
Netflix,649,2
```

## How the "AI" works
It is a rule-based scoring engine: keyword text classification for categories, plus threshold rules for waste detection. Possible upgrades: train an ML classifier for categories, or connect an LLM API for personalised advice.

## Tech
Python, HTML

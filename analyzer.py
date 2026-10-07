"""AI Monthly Subscription Analyzer.

Reads subscriptions from a CSV, categorizes them, finds spending patterns
and flags subscriptions that look unnecessary or excessive.
The "AI" here is a rule-based scoring engine (no external API needed).

Usage:  python analyzer.py [subscriptions.csv]
Output: terminal summary + report.html
"""
import csv
import sys
from collections import defaultdict

# Keyword -> category (simple text classification)
CATEGORY_KEYWORDS = {
    "Entertainment": ["netflix", "prime", "hotstar", "disney", "spotify", "youtube", "music", "video"],
    "Learning": ["coursera", "udemy", "course", "learn", "duolingo"],
    "Fitness": ["gym", "fitness", "yoga"],
    "Productivity": ["notion", "adobe", "office", "cloud", "storage", "drive"],
}
UNUSED_DAYS = 30        # not used for this long -> candidate to cancel
HIGH_COST_SHARE = 0.25  # one item above 25% of total -> excessive


def categorize(name):
    n = name.lower()
    for cat, words in CATEGORY_KEYWORDS.items():
        if any(w in n for w in words):
            return cat
    return "Other"


def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = []
        for r in csv.DictReader(f):
            rows.append({
                "name": r["name"].strip(),
                "cost": float(r["monthly_cost"]),
                "idle": int(r["last_used_days_ago"]),
            })
    for r in rows:
        r["category"] = categorize(r["name"])
    return rows


def analyze(rows):
    total = sum(r["cost"] for r in rows)
    by_cat = defaultdict(float)
    for r in rows:
        by_cat[r["category"]] += r["cost"]

    for r in rows:
        reasons, score = [], 0
        if r["idle"] >= UNUSED_DAYS:
            reasons.append(f"not used for {r['idle']} days")
            score += 2
        if r["cost"] / total >= HIGH_COST_SHARE:
            reasons.append(f"takes {r['cost'] / total:.0%} of your budget")
            score += 1
        if r["category"] == "Entertainment" and sum(
                1 for x in rows if x["category"] == "Entertainment") >= 4 and r["idle"] > 14:
            reasons.append("overlaps with many entertainment services")
            score += 1
        r["score"], r["reasons"] = score, reasons
        r["verdict"] = "Cancel" if score >= 2 else "Review" if score == 1 else "Keep"

    savings = sum(r["cost"] for r in rows if r["verdict"] == "Cancel")
    return {"total": total, "by_cat": dict(by_cat), "rows": rows, "savings": savings}


def print_report(res):
    print(f"\nTotal monthly spend: Rs {res['total']:,.0f}  (Rs {res['total'] * 12:,.0f} / year)")
    print("\nSpend by category:")
    for cat, amt in sorted(res["by_cat"].items(), key=lambda x: -x[1]):
        print(f"  {cat:<14} Rs {amt:>7,.0f}  {amt / res['total']:.0%}")
    print("\nSubscriptions:")
    for r in sorted(res["rows"], key=lambda x: -x["score"]):
        why = "; ".join(r["reasons"]) or "in regular use"
        print(f"  [{r['verdict']:<6}] {r['name']:<22} Rs {r['cost']:>6,.0f}  - {why}")
    print(f"\nPotential saving if you cancel flagged items: Rs {res['savings']:,.0f}/month "
          f"(Rs {res['savings'] * 12:,.0f}/year)\n")


def write_html(res, path="report.html"):
    color = {"Cancel": "#b3261e", "Review": "#a86a00", "Keep": "#1f7a4d"}
    rows = "".join(
        f"<tr><td>{r['name']}</td><td>{r['category']}</td><td>Rs {r['cost']:,.0f}</td>"
        f"<td style='color:{color[r['verdict']]};font-weight:bold'>{r['verdict']}</td>"
        f"<td>{'; '.join(r['reasons']) or 'in regular use'}</td></tr>"
        for r in sorted(res["rows"], key=lambda x: -x["score"]))
    bars = "".join(
        f"<div style='margin:6px 0'>{c} - Rs {a:,.0f}<div style='background:#2c5fa8;height:12px;"
        f"width:{a / res['total'] * 100:.0f}%'></div></div>"
        for c, a in sorted(res["by_cat"].items(), key=lambda x: -x[1]))
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Subscription Report</title>
<style>body{{font-family:Georgia,serif;max-width:860px;margin:30px auto;padding:0 16px;color:#1c2430}}
table{{border-collapse:collapse;width:100%}}td,th{{border-bottom:1px solid #d5dae1;padding:8px;text-align:left}}</style></head>
<body><h1>Monthly Subscription Report</h1>
<p>Total: <b>Rs {res['total']:,.0f}</b> per month. Potential saving: <b>Rs {res['savings']:,.0f}</b> per month.</p>
<h2>By category</h2>{bars}<h2>Details</h2>
<table><tr><th>Name</th><th>Category</th><th>Cost</th><th>Verdict</th><th>Why</th></tr>{rows}</table></body></html>"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "subscriptions.csv"
    result = analyze(load(csv_path))
    print_report(result)
    write_html(result)
    print("HTML report saved to report.html")

import matplotlib.pyplot as plt
from models import get_monthly_summary, filter_expenses
from collections import defaultdict


def plot_monthly_category_pie(year, month):
    summary = get_monthly_summary(year, month)
    if not summary:
        print(f"No expenses found for {year}-{month:02d}.")
        return

    labels = [row["category"] for row in summary]
    amounts = [row["total"] for row in summary]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(amounts, labels=labels, autopct="%1.1f%%", startangle=140)
    ax.set_title(f"Expenses by Category (INR) - {year}/{month:02d}")
    plt.tight_layout()
    plt.show()


def plot_monthly_bar(year, month):
    summary = get_monthly_summary(year, month)
    if not summary:
        print(f"No expenses found for {year}-{month:02d}.")
        return

    categories = [row["category"] for row in summary]
    totals = [row["total"] for row in summary]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(categories, totals, color="steelblue")
    ax.set_xlabel("Category")
    ax.set_ylabel("Amount (₹)")
    ax.set_title(f"Monthly Expenses (INR) - {year}/{month:02d}")
    ax.bar_label(bars, fmt="₹%.2f")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()


def plot_daily_trend(year, month):
    date_prefix = f"{year:04d}-{month:02d}"
    expenses = filter_expenses(start_date=f"{date_prefix}-01", end_date=f"{date_prefix}-31")

    if not expenses:
        print(f"No expenses found for {year}-{month:02d}.")
        return

    daily = defaultdict(float)
    for exp in expenses:
        day = exp["date"]
        daily[day] += exp["amount_in_inr"]

    sorted_days = sorted(daily.keys())
    amounts = [daily[d] for d in sorted_days]
    day_labels = [d.split("-")[2] for d in sorted_days]

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(day_labels, amounts, marker="o", linewidth=2, color="teal")
    ax.fill_between(day_labels, amounts, alpha=0.2, color="teal")
    ax.set_xlabel("Day")
    ax.set_ylabel("Amount (₹)")
    ax.set_title(f"Daily Spending Trend (INR) - {year}/{month:02d}")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def plot_yearly_overview(year):
    monthly_totals = []
    month_labels = []

    for m in range(1, 13):
        summary = get_monthly_summary(year, m)
        total = sum(row["total"] for row in summary)
        monthly_totals.append(total)
        month_labels.append(f"{m:02d}")

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(month_labels, monthly_totals, color="coral")
    ax.set_xlabel("Month")
    ax.set_ylabel("Total Amount (₹)")
    ax.set_title(f"Yearly Expense Overview (INR) - {year}")
    plt.tight_layout()
    plt.show()

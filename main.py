import sys
from datetime import datetime
from database import initialize_db
from models import (
    get_all_categories,
    add_category,
    delete_category,
    add_expense,
    edit_expense,
    delete_expense,
    get_all_expenses,
    filter_expenses,
    get_monthly_summary,
    get_expense_by_id,
)
from export_csv import export_expenses_to_csv
from analytics import (
    plot_monthly_category_pie,
    plot_monthly_bar,
    plot_daily_trend,
    plot_yearly_overview,
)
from currency import convert_to_inr, SUPPORTED_CURRENCIES


def print_header(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_expenses(expenses):
    if not expenses:
        print("  No expenses found.")
        return
    print(f"  {'ID':<5} {'Date':<12} {'Category':<15} {'Amount':>10} {'Curr':<5} {'INR':>10} {'Description'}")
    print(f"  {'-'*5} {'-'*12} {'-'*15} {'-'*10} {'-'*5} {'-'*10} {'-'*20}")
    for exp in expenses:
        print(f"  {exp['id']:<5} {exp['date']:<12} {exp['category']:<15} {exp['amount']:>10.2f} {exp['currency']:<5} ₹{exp['amount_in_inr']:>9.2f} {exp['description']}")


def get_currency_input():
    currencies_str = "/".join(SUPPORTED_CURRENCIES)
    while True:
        currency = input(f"  Currency ({currencies_str}) [INR]: ").strip().upper()
        if not currency:
            return "INR"
        if currency in SUPPORTED_CURRENCIES:
            return currency
        print(f"  Invalid currency. Choose from: {currencies_str}")


def get_date_input(prompt="  Date (YYYY-MM-DD) [today]: ", default=None):
    while True:
        date_str = input(prompt).strip()
        if not date_str:
            if default:
                return default
            return datetime.now().strftime("%Y-%m-%d")
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            print("  Invalid date format. Use YYYY-MM-DD.")


def menu_add_expense():
    print_header("Add New Expense")
    categories = get_all_categories()
    print("\n  Categories:")
    for cat in categories:
        print(f"    {cat['id']}. {cat['name']}")

    try:
        cat_id = int(input("\n  Category ID: "))
        amount = float(input("  Amount: "))
        currency = get_currency_input()
        amount_in_inr = convert_to_inr(amount, currency)
        description = input("  Description: ")
        date_str = get_date_input()

        add_expense(amount, currency, amount_in_inr, description, cat_id, date_str)
        print(f"\n  Expense added! ({amount} {currency} = ₹{amount_in_inr})")
    except ValueError as e:
        print(f"\n  Error: Invalid input - {e}")


def menu_edit_expense():
    print_header("Edit Expense")
    expense_id = int(input("  Expense ID to edit: "))
    expense = get_expense_by_id(expense_id)
    if not expense:
        print("  Expense not found.")
        return

    print(f"  Current: {expense['amount']} {expense['currency']} (₹{expense['amount_in_inr']}) | {expense['category']} | {expense['description']} | {expense['date']}")
    categories = get_all_categories()
    print("\n  Categories:")
    for cat in categories:
        print(f"    {cat['id']}. {cat['name']}")

    try:
        cat_id = input(f"  Category ID [{expense['category_id']}]: ").strip()
        cat_id = int(cat_id) if cat_id else expense["category_id"]

        amount = input(f"  Amount [{expense['amount']}]: ").strip()
        amount = float(amount) if amount else expense["amount"]

        currencies_str = "/".join(SUPPORTED_CURRENCIES)
        currency = input(f"  Currency ({currencies_str}) [{expense['currency']}]: ").strip().upper()
        currency = currency if currency in SUPPORTED_CURRENCIES else expense["currency"]

        amount_in_inr = convert_to_inr(amount, currency)

        description = input(f"  Description [{expense['description']}]: ").strip()
        description = description if description else expense["description"]

        date_str = get_date_input(f"  Date [{expense['date']}]: ", default=expense["date"])

        edit_expense(expense_id, amount, currency, amount_in_inr, description, cat_id, date_str)
        print(f"\n  Expense updated! ({amount} {currency} = ₹{amount_in_inr})")
    except ValueError as e:
        print(f"\n  Error: Invalid input - {e}")


def menu_delete_expense():
    print_header("Delete Expense")
    expense_id = int(input("  Expense ID to delete: "))
    expense = get_expense_by_id(expense_id)
    if not expense:
        print("  Expense not found.")
        return
    confirm = input(f"  Delete {expense['amount']} {expense['currency']} - {expense['description']}? (y/n): ")
    if confirm.lower() == "y":
        delete_expense(expense_id)
        print("  Expense deleted.")


def menu_view_expenses():
    print_header("All Expenses")
    expenses = get_all_expenses()
    print_expenses(expenses)


def menu_filter_expenses():
    print_header("Filter Expenses")
    categories = get_all_categories()
    print("  Categories (leave blank for all):")
    for cat in categories:
        print(f"    {cat['id']}. {cat['name']}")

    cat_id = input("\n  Category ID: ").strip()
    start = input("  Start date (YYYY-MM-DD): ").strip()
    end = input("  End date (YYYY-MM-DD): ").strip()
    min_amt = input("  Min amount (INR): ").strip()
    max_amt = input("  Max amount (INR): ").strip()

    results = filter_expenses(
        category_id=int(cat_id) if cat_id else None,
        start_date=start if start else None,
        end_date=end if end else None,
        min_amount=float(min_amt) if min_amt else None,
        max_amount=float(max_amt) if max_amt else None,
    )
    print_expenses(results)


def menu_monthly_summary():
    print_header("Monthly Summary (in INR)")
    year = int(input("  Year: "))
    month = int(input("  Month (1-12): "))
    summary = get_monthly_summary(year, month)

    if not summary:
        print("  No expenses for this month.")
        return

    total = 0
    print(f"\n  {'Category':<20} {'Count':>6} {'Total (INR)':>14}")
    print(f"  {'-'*20} {'-'*6} {'-'*14}")
    for row in summary:
        print(f"  {row['category']:<20} {row['count']:>6} ₹{row['total']:>12.2f}")
        total += row["total"]
    print(f"  {'-'*42}")
    print(f"  {'TOTAL':<27} ₹{total:>12.2f}")


def menu_manage_categories():
    print_header("Manage Categories")
    categories = get_all_categories()
    for cat in categories:
        print(f"    {cat['id']}. {cat['name']}")

    print("\n  1. Add category")
    print("  2. Delete category")
    print("  3. Back")
    choice = input("\n  Choice: ").strip()

    if choice == "1":
        name = input("  New category name: ").strip()
        if name:
            add_category(name)
            print("  Category added!")
    elif choice == "2":
        cat_id = int(input("  Category ID to delete: "))
        confirm = input("  This will delete all expenses in this category. Continue? (y/n): ")
        if confirm.lower() == "y":
            delete_category(cat_id)
            print("  Category deleted.")


def menu_export_csv():
    print_header("Export to CSV")
    expenses = get_all_expenses()
    if not expenses:
        print("  No expenses to export.")
        return
    filepath = export_expenses_to_csv(expenses)
    print(f"  Exported {len(expenses)} expenses to:\n  {filepath}")


def menu_analytics():
    print_header("Analytics Dashboard (INR)")
    print("  1. Monthly category pie chart")
    print("  2. Monthly category bar chart")
    print("  3. Daily spending trend")
    print("  4. Yearly overview")
    print("  5. Back")

    choice = input("\n  Choice: ").strip()

    if choice in ("1", "2", "3"):
        year = int(input("  Year: "))
        month = int(input("  Month (1-12): "))
        if choice == "1":
            plot_monthly_category_pie(year, month)
        elif choice == "2":
            plot_monthly_bar(year, month)
        elif choice == "3":
            plot_daily_trend(year, month)
    elif choice == "4":
        year = int(input("  Year: "))
        plot_yearly_overview(year)


def main():
    initialize_db()

    while True:
        print_header("Personal Expense Tracker")
        print("  1. Add expense")
        print("  2. Edit expense")
        print("  3. Delete expense")
        print("  4. View all expenses")
        print("  5. Filter expenses")
        print("  6. Monthly summary")
        print("  7. Manage categories")
        print("  8. Export to CSV")
        print("  9. Analytics dashboard")
        print("  0. Exit")

        choice = input("\n  Choice: ").strip()

        if choice == "1":
            menu_add_expense()
        elif choice == "2":
            menu_edit_expense()
        elif choice == "3":
            menu_delete_expense()
        elif choice == "4":
            menu_view_expenses()
        elif choice == "5":
            menu_filter_expenses()
        elif choice == "6":
            menu_monthly_summary()
        elif choice == "7":
            menu_manage_categories()
        elif choice == "8":
            menu_export_csv()
        elif choice == "9":
            menu_analytics()
        elif choice == "0":
            print("\n  Goodbye!\n")
            sys.exit(0)
        else:
            print("  Invalid choice. Try again.")


if __name__ == "__main__":
    main()

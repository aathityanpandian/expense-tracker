import csv
import os
from datetime import datetime
from config import EXPORT_DIR
from models import get_all_expenses


def export_expenses_to_csv(expenses=None, filename=None):
    os.makedirs(EXPORT_DIR, exist_ok=True)

    if expenses is None:
        expenses = get_all_expenses()

    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"expenses_{timestamp}.csv"

    filepath = os.path.join(EXPORT_DIR, filename)

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Date", "Category", "Amount", "Currency", "Amount (INR)", "Description"])
        for exp in expenses:
            writer.writerow([
                exp["id"],
                exp["date"],
                exp["category"],
                exp["amount"],
                exp["currency"],
                exp["amount_in_inr"],
                exp["description"],
            ])

    return filepath

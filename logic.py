from datetime import datetime
import csv
from db import (
    add_transaction, get_transactions, reset_transactions,
    init_db, update_transaction, delete_transaction, filter_advanced
)

init_db()

def add_new_transaction(type_, amount, category, description, date, tax_percent=0):
    if type_ == "income" and tax_percent > 0:
        amount = amount * (1 - tax_percent / 100)
    add_transaction(type_, amount, category, description, date, tax_percent)

def get_all_transactions():
    raw = get_transactions()
    return [
        {
            "id": r[0],
            "type": r[1],
            "amount": r[2],
            "category": r[3],
            "description": r[4],
            "date": r[5],
            "tax_percent": r[6],
        } for r in raw
    ]

def filter_transactions(start_date=None, end_date=None, type_=None, category=None):
    start_str = start_date.strftime("%Y-%m-%d") if start_date else None
    end_str = end_date.strftime("%Y-%m-%d") if end_date else None
    raw = filter_advanced(start_str, end_str, type_, category)
    return [
        {
            "id": r[0],
            "type": r[1],
            "amount": r[2],
            "category": r[3],
            "description": r[4],
            "date": r[5],
            "tax_percent": r[6],
        } for r in raw
    ]

def reset_all_transactions():
    reset_transactions()

def export_to_csv(filename="transactions_export.csv"):
    data = get_all_transactions()
    if not data:
        raise ValueError("No data to export")
    with open(filename, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "type", "amount", "category", "description", "date", "tax_percent"])
        writer.writeheader()
        for row in data:
            writer.writerow(row)

def import_from_csv(filename):
    imported = []
    with open(filename, mode="r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                type_ = row["type"].lower()
                amount = float(row["amount"])
                category = row["category"].lower()
                description = row["description"]
                date = row["date"]
                tax_percent = float(row.get("tax_percent", 0))
                datetime.strptime(date, "%Y-%m-%d")
                add_transaction(type_, amount, category, description, date, tax_percent)
                imported.append(row)
            except Exception:
                continue
    return imported

def update_transaction_by_id(txn_id, type_, amount, category, description, date, tax_percent):
    update_transaction(txn_id, type_, amount, category, description, date, tax_percent)

def delete_transaction_by_id(txn_id):
    delete_transaction(txn_id)

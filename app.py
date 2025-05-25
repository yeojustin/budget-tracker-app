from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import json
from datetime import datetime
import os
import io
import matplotlib.pyplot as plt
from collections import defaultdict
import calendar

import matplotlib
matplotlib.use('Agg')  # using this for the non-GUI backend for Flask

from flask import Response
import matplotlib.pyplot as plt
from io import BytesIO
from collections import defaultdict
from datetime import datetime

import csv
from flask import make_response

app = Flask(__name__)

DATA_FILE = "transactions.json"
CPF_RATE = 0.20
CPF_CAP = 6000

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def calculate_net_salary(amount):
    capped_amount = min(amount, CPF_CAP)
    cpf = CPF_RATE * capped_amount
    return amount - cpf, cpf

# Helper: find transaction by index
def find_transaction(idx):
    data = load_data()
    if 0 <= idx < len(data):
        return data[idx]
    return None

@app.route('/')
def index():
    # Get filters from query params
    filter_type = request.args.get('type', '').lower()
    filter_category = request.args.get('category', '').lower()
    filter_start = request.args.get('start_date', '')
    filter_end = request.args.get('end_date', '')

    data = load_data()
    filtered = []

    for i, tx in enumerate(data):
        # Filters
        if filter_type and tx['type'].lower() != filter_type:
            continue
        if filter_category and filter_category not in tx['category'].lower():
            continue
        # Date filters
        tx_date = datetime.strptime(tx['date'], "%Y-%m-%d %H:%M:%S")
        if filter_start:
            try:
                start_date = datetime.strptime(filter_start, "%Y-%m-%d")
                if tx_date < start_date:
                    continue
            except ValueError:
                pass
        if filter_end:
            try:
                end_date = datetime.strptime(filter_end, "%Y-%m-%d")
                if tx_date > end_date:
                    continue
            except ValueError:
                pass

        filtered.append((i, tx))

    filtered.sort(key=lambda x: x[1]['date'], reverse=True)
    return render_template("index.html", transactions=filtered,
                           filter_type=filter_type,
                           filter_category=filter_category,
                           filter_start=filter_start,
                           filter_end=filter_end)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        type_ = request.form['type'].lower()
        try:
            amount = float(request.form['amount'])
        except ValueError:
            flash("Invalid amount")
            return redirect(url_for('add'))

        category = request.form['category'].strip().lower()
        description = request.form['description'].strip()
        date_str = request.form['date'].strip()
        if date_str:
            try:
                datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                date = date_str
            except ValueError:
                flash("Invalid date format, must be YYYY-MM-DD HH:MM:SS")
                return redirect(url_for('add'))
        else:
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if type_ not in ['income', 'expense']:
            flash("Invalid transaction type")
            return redirect(url_for('add'))

        data = load_data()
        data.append({
            "type": type_,
            "amount": amount,
            "category": category,
            "description": description,
            "date": date
        })
        save_data(data)
        flash("Transaction added!")
        return redirect(url_for('index'))

    return render_template("add.html")

@app.route('/edit/<int:idx>', methods=['GET', 'POST'])
def edit(idx):
    tx = find_transaction(idx)
    if not tx:
        flash("Transaction not found.")
        return redirect(url_for('index'))

    if request.method == 'POST':
        type_ = request.form['type'].lower()
        try:
            amount = float(request.form['amount'])
        except ValueError:
            flash("Invalid amount")
            return redirect(url_for('edit', idx=idx))

        category = request.form['category'].strip().lower()
        description = request.form['description'].strip()
        date_str = request.form['date'].strip()
        if date_str:
            try:
                datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                date = date_str
            except ValueError:
                flash("Invalid date format, must be YYYY-MM-DD HH:MM:SS")
                return redirect(url_for('edit', idx=idx))
        else:
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if type_ not in ['income', 'expense']:
            flash("Invalid transaction type")
            return redirect(url_for('edit', idx=idx))

        data = load_data()
        data[idx] = {
            "type": type_,
            "amount": amount,
            "category": category,
            "description": description,
            "date": date
        }
        save_data(data)
        flash("Transaction updated!")
        return redirect(url_for('index'))

    return render_template("edit.html", idx=idx, tx=tx)

@app.route('/delete/<int:idx>', methods=['POST'])
def delete(idx):
    data = load_data()
    if 0 <= idx < len(data):
        removed = data.pop(idx)
        save_data(data)
        flash(f"Deleted transaction: {removed['description']} (${removed['amount']:.2f})")
    else:
        flash("Transaction not found.")
    return redirect(url_for('index'))

@app.route('/summary')
def summary():
    data = load_data()
    total_income = 0
    total_expense = 0
    cpf_deductions = 0

    for x in data:
        if x.get("type") == "income":
            category = x.get("category", "").lower()
            amount = x["amount"]

            if category == "salary":
                capped_amount = min(amount, CPF_CAP)
                cpf = CPF_RATE * capped_amount
                net_salary = amount - cpf
                cpf_deductions += cpf
                total_income += net_salary
            else:
                total_income += amount

        elif x.get("type") == "expense":
            total_expense += x["amount"]

    net_savings = total_income - total_expense

    return render_template("summary.html",
                           total_income=total_income,
                           cpf_deductions=cpf_deductions,
                           total_expense=total_expense,
                           net_savings=net_savings)

@app.route('/expense-chart.png')
def expense_chart():
    data = load_data()
    categories = defaultdict(float)
    for entry in data:
        if entry.get("type") == "expense":
            cat = entry.get("category", "Uncategorized")
            categories[cat] += entry["amount"]

    if not categories:
        # Return a placeholder image or 204 no content
        return Response(status=204)

    labels = list(categories.keys())
    amounts = list(categories.values())

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(amounts, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.set_title("Expenses by Category")
    ax.axis('equal')

    img = BytesIO()
    plt.savefig(img, format='png')
    plt.close(fig)
    img.seek(0)
    return Response(img.getvalue(), mimetype='image/png')

@app.route('/income-expense-line.png')
def income_expense_line_chart():
    data = load_data()

    # Group by month-year
    monthly = defaultdict(lambda: {'income': 0, 'expense': 0})

    for entry in data:
        dt = datetime.strptime(entry['date'], "%Y-%m-%d %H:%M:%S")
        key = dt.strftime("%Y-%m")
        if entry['type'] == 'income':
            monthly[key]['income'] += entry['amount']
        elif entry['type'] == 'expense':
            monthly[key]['expense'] += entry['amount']

    # Sort by date
    sorted_months = sorted(monthly.keys())
    income_values = [monthly[m]['income'] for m in sorted_months]
    expense_values = [monthly[m]['expense'] for m in sorted_months]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(sorted_months, income_values, marker='o', label='Income')
    ax.plot(sorted_months, expense_values, marker='o', label='Expense')
    ax.set_xlabel('Month')
    ax.set_ylabel('Amount ($)')
    ax.set_title('Monthly Income vs Expense')
    ax.legend()
    plt.xticks(rotation=45)

    img = BytesIO()
    plt.tight_layout()
    plt.savefig(img, format='png')
    plt.close(fig)
    img.seek(0)
    return Response(img.getvalue(), mimetype='image/png')

@app.route("/export_csv")
def export_csv():
    data = load_data()
    filter_type = request.args.get("type", "").strip()
    filter_category = request.args.get("category", "").strip().lower()
    start_date = request.args.get("start", "").strip()
    end_date = request.args.get("end", "").strip()

    filtered = []
    for i, t in enumerate(data):
        if filter_type and t["type"] != filter_type:
            continue
        if filter_category and filter_category not in t["category"].lower():
            continue
        if start_date and t["date"] < start_date:
            continue
        if end_date and t["date"] > end_date:
            continue
        filtered.append(t)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Type", "Amount", "Category", "Description"])
    for tx in filtered:
        writer.writerow([tx["date"], tx["type"], tx["amount"], tx["category"], tx["description"]])

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=transactions.csv"
    response.headers["Content-Type"] = "text/csv"
    return response

@app.route("/export_all_csv")
def export_all_csv():
    data = load_data()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Type", "Amount", "Category", "Description"])
    for tx in data:
        writer.writerow([tx["date"], tx["type"], tx["amount"], tx["category"], tx["description"]])

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=all_transactions.csv"
    response.headers["Content-Type"] = "text/csv"
    return response


if __name__ == '__main__':
    app.run(debug=True)

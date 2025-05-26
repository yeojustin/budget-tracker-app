import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import matplotlib.pyplot as plt

import logic

CATEGORIES = ["salary", "food", "rent", "transport", "entertainment", "utilities", "others"]
TYPES = ["income", "expense"]

root = tk.Tk()
root.title("Smart Budget Tracker")
root.geometry("1400x700")
root.minsize(800, 500)

# Variables
type_var = tk.StringVar(value="income")
category_var = tk.StringVar()
tax_var = tk.StringVar(value="0")

# Helper functions
def clear_inputs():
    amount_entry.delete(0, tk.END)
    description_entry.delete(0, tk.END)
    tax_entry.delete(0, tk.END)
    tax_var.set("0")
    category_combo.set("")
    date_entry.delete(0, tk.END)
    date_entry.insert(0, "DD-MM-YYYY")
    type_var.set("income")

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%d-%m-%Y")
    except ValueError:
        return None

def load_transactions(data=None):
    for row in tree.get_children():
        tree.delete(row)
    if data is None:
        data = logic.get_all_transactions()
    total_income = 0
    total_expense = 0
    for i, entry in enumerate(sorted(data, key=lambda x: x["date"], reverse=True), 1):
        amt = float(entry["amount"])
        tree.insert("", "end", values=(
            i,
            entry["type"].capitalize(),
            f"${amt:.2f}",
            entry["category"].capitalize(),
            entry["description"],
            datetime.strptime(entry["date"], "%Y-%m-%d").strftime("%d-%m-%Y"),
            f"{entry.get('tax_percent', 0):.1f}%"
        ))
        if entry["type"] == "income":
            total_income += amt
        else:
            total_expense += amt
    income_total_var.set(f"Total Income: ${total_income:.2f}")
    expense_total_var.set(f"Total Expense: ${total_expense:.2f}")

def submit_transaction():
    type_ = type_var.get()
    try:
        amount = float(amount_entry.get())
        if amount <= 0:
            raise ValueError
    except Exception:
        messagebox.showerror("Invalid Input", "Please enter a valid positive amount.")
        return

    category = category_var.get().lower()
    if not category:
        messagebox.showerror("Invalid Input", "Please select or enter a category.")
        return

    description = description_entry.get().strip()

    date_str = date_entry.get()
    date_obj = parse_date(date_str)
    if not date_obj:
        messagebox.showerror("Invalid Date", "Please enter a valid date in DD-MM-YYYY format.")
        return
    date_db_str = date_obj.strftime("%Y-%m-%d") 

    try:
        tax_percent = float(tax_entry.get())
        if tax_percent < 0 or tax_percent > 100:
            raise ValueError
    except Exception:
        messagebox.showerror("Invalid Input", "Please enter a valid tax percentage (0-100).")
        return

    logic.add_new_transaction(type_, amount, category, description, date_db_str, tax_percent)
    messagebox.showinfo("Success", "Transaction added!")
    clear_inputs()
    load_transactions()

def filter_transactions():
    start_str = start_date_entry.get()
    end_str = end_date_entry.get()

    start_date = parse_date(start_str)
    end_date = parse_date(end_str)
    if not start_date or not end_date:
        messagebox.showerror("Invalid Date", "Please enter valid start and end dates in DD-MM-YYYY format.")
        return
    if start_date > end_date:
        messagebox.showerror("Invalid Date Range", "Start date must be before end date.")
        return

    filter_type = filter_type_var.get()
    filter_cat = filter_category_var.get().lower()

    filtered = logic.filter_transactions(start_date, end_date, filter_type, filter_cat)
    load_transactions(filtered)
    # Store last filtered data for chart
    global last_filtered_data
    last_filtered_data = filtered

def reset_filter():
    start_date_entry.delete(0, tk.END)
    start_date_entry.insert(0, "DD-MM-YYYY")
    end_date_entry.delete(0, tk.END)
    end_date_entry.insert(0, "DD-MM-YYYY")
    filter_type_var.set("")
    filter_category_combo.set("")
    load_transactions()
    global last_filtered_data
    last_filtered_data = None

def reset_data():
    if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all transactions?"):
        logic.reset_all_transactions()
        load_transactions()
        messagebox.showinfo("Reset", "All transactions have been deleted.")

def export_csv():
    filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if not filename:
        return
    try:
        logic.export_to_csv(filename)
        messagebox.showinfo("Export Successful", f"Data exported to {filename}")
    except Exception as e:
        messagebox.showerror("Export Failed", str(e))

def import_csv():
    filename = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if not filename:
        return
    try:
        imported = logic.import_from_csv(filename)
        messagebox.showinfo("Import Successful", f"Imported {len(imported)} transactions.")
        load_transactions()
    except Exception as e:
        messagebox.showerror("Import Failed", str(e))

def show_chart():
    data = last_filtered_data if last_filtered_data is not None else logic.get_all_transactions()
    expenses = {}
    for entry in data:
        if entry["type"] == "expense":
            cat = entry["category"].lower()
            expenses[cat] = expenses.get(cat, 0) + float(entry["amount"])

    if not expenses:
        messagebox.showinfo("No Expenses", "No expense data available to plot.")
        return

    labels = [c.capitalize() for c in expenses.keys()]
    amounts = list(expenses.values())

    plt.style.use('ggplot')
    plt.figure(figsize=(8, 6))
    plt.pie(amounts, labels=labels, autopct="%1.1f%%", startangle=90)
    plt.title("Expenses by Category")
    plt.axis('equal')
    plt.tight_layout()
    plt.show()

# UI Setup
frame = ttk.Frame(root, padding=10)
frame.pack(fill=tk.X)

# Transaction input row 1
ttk.Label(frame, text="Type:").grid(row=0, column=0, sticky="w")
ttk.Radiobutton(frame, text="Income", variable=type_var, value="income").grid(row=0, column=1)
ttk.Radiobutton(frame, text="Expense", variable=type_var, value="expense").grid(row=0, column=2)

ttk.Label(frame, text="Amount:").grid(row=0, column=3, sticky="w")
amount_entry = ttk.Entry(frame, width=15)
amount_entry.grid(row=0, column=4, padx=5)

ttk.Label(frame, text="Category:").grid(row=0, column=5, sticky="w")
category_combo = ttk.Combobox(frame, values=CATEGORIES, textvariable=category_var)
category_combo.grid(row=0, column=6, padx=5)
category_combo.set("")

ttk.Label(frame, text="Tax % (income only):").grid(row=0, column=7, sticky="w")
tax_entry = ttk.Entry(frame, width=8, textvariable=tax_var)
tax_entry.grid(row=0, column=8, padx=5)

# Transaction input row 2
ttk.Label(frame, text="Date (DD-MM-YYYY):").grid(row=1, column=0, sticky="w", pady=5)
date_entry = ttk.Entry(frame, width=18)
date_entry.grid(row=1, column=1, padx=5, pady=5)
date_entry.insert(0, "DD-MM-YYYY")

ttk.Label(frame, text="Description:").grid(row=1, column=3, sticky="w", pady=5)
description_entry = ttk.Entry(frame, width=50)
description_entry.grid(row=1, column=4, columnspan=4, padx=5, pady=5, sticky="w")

submit_btn = ttk.Button(frame, text="Add Transaction", command=submit_transaction)
submit_btn.grid(row=1, column=8, padx=5, pady=5)

# Transactions Table + Scrollbar
table_frame = ttk.Frame(root)
table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

cols = ("ID", "Type", "Amount", "Category", "Description", "Date", "Tax %")
tree = ttk.Treeview(table_frame, columns=cols, show="headings")
for col in cols:
    tree.heading(col, text=col)
    tree.column(col, width=110 if col != "Description" else 250, anchor="center")

vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=vsb.set)
tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
vsb.pack(side=tk.RIGHT, fill=tk.Y)

# Totals below table
totals_frame = ttk.Frame(root, padding=10)
totals_frame.pack(fill=tk.X, padx=10, pady=0)

income_total_var = tk.StringVar(value="Total Income: $0.00")
expense_total_var = tk.StringVar(value="Total Expense: $0.00")
ttk.Label(totals_frame, textvariable=income_total_var, font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT, padx=10)
ttk.Label(totals_frame, textvariable=expense_total_var, font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT, padx=30)

# Filter Frame
filter_frame = ttk.Frame(root, padding=10)
filter_frame.pack(fill=tk.X, padx=10, pady=5)

ttk.Label(filter_frame, text="Filter Start Date (DD-MM-YYYY):").grid(row=0, column=0, padx=5, sticky="w")
start_date_entry = ttk.Entry(filter_frame, width=15)
start_date_entry.grid(row=1, column=0, padx=5)
start_date_entry.insert(0, "DD-MM-YYYY")

ttk.Label(filter_frame, text="Filter End Date (DD-MM-YYYY):").grid(row=0, column=1, padx=5, sticky="w")
end_date_entry = ttk.Entry(filter_frame, width=15)
end_date_entry.grid(row=1, column=1, padx=5)
end_date_entry.insert(0, "DD-MM-YYYY")

ttk.Label(filter_frame, text="Filter Type:").grid(row=0, column=2, padx=5, sticky="w")
filter_type_var = tk.StringVar()
filter_type_combo = ttk.Combobox(filter_frame, values=["", "income", "expense"], textvariable=filter_type_var, width=12)
filter_type_combo.grid(row=1, column=2, padx=5)
filter_type_combo.set("")

ttk.Label(filter_frame, text="Filter Category:").grid(row=0, column=3, padx=5, sticky="w")
filter_category_var = tk.StringVar()
filter_category_combo = ttk.Combobox(filter_frame, values=CATEGORIES, textvariable=filter_category_var, width=15)
filter_category_combo.grid(row=1, column=3, padx=5)
filter_category_combo.set("")

filter_btn = ttk.Button(filter_frame, text="Apply Filter", command=filter_transactions)
filter_btn.grid(row=1, column=4, padx=10)

reset_filter_btn = ttk.Button(filter_frame, text="Reset Filter", command=reset_filter)
reset_filter_btn.grid(row=1, column=5, padx=10)

# Bottom Buttons
bottom_frame = ttk.Frame(root, padding=10)
bottom_frame.pack(fill=tk.X, padx=10, pady=10)

reset_btn = ttk.Button(bottom_frame, text="Reset All Data", command=reset_data)
reset_btn.pack(side=tk.LEFT, padx=10)

export_btn = ttk.Button(bottom_frame, text="Export to CSV", command=export_csv)
export_btn.pack(side=tk.LEFT, padx=10)

import_btn = ttk.Button(bottom_frame, text="Import from CSV", command=import_csv)
import_btn.pack(side=tk.LEFT, padx=10)

chart_btn = ttk.Button(bottom_frame, text="Show Expense Chart", command=show_chart)
chart_btn.pack(side=tk.RIGHT, padx=10)

# Load initial data
last_filtered_data = None
load_transactions()

root.mainloop()

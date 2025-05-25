import json
from datetime import datetime
import matplotlib.pyplot as plt

DATA_FILE = "transactions.json"
CPF_RATE = 0.20
CPF_CAP = 6000

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def calculate_net_salary(amount):
    capped_amount = min(amount, CPF_CAP)
    cpf = CPF_RATE * capped_amount
    return amount - cpf, cpf

def add_transaction():
    type_ = input("Enter type (income/expense): ").strip().lower()
    if type_ not in ["income", "expense"]:
        print("Invalid type. Please enter 'income' or 'expense'.")
        return

    try:
        amount = float(input("Enter amount: "))
        if amount <= 0:
            raise ValueError
    except ValueError:
        print("Invalid amount. Please enter a positive number.")
        return

    category = input("Enter category: ").strip().lower()
    description = input("Enter description: ").strip()
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data = load_data()
    data.append({
        "type": type_,
        "amount": amount,
        "category": category,
        "description": description,
        "date": date
    })
    save_data(data)
    print("Transaction added!")

def view_transactions():
    data = load_data()
    if not data:
        print("No transactions yet.")
        return

    data.sort(key=lambda x: x["date"], reverse=True)
    print("\n--- Transaction History ---")
    for entry in data:
        sign = "+" if entry["type"] == "income" else "-"
        print(f"[{entry['date']}] {entry['type'].upper()} {sign}${entry['amount']:.2f} | {entry['category']} | {entry['description']}")
    print("----------------------------\n")

def summary():
    data = load_data()
    total_income = 0
    total_expense = 0
    cpf_deductions = 0

    for x in data:
        type_ = x.get("type")
        category = x.get("category", "").lower()
        amount = x["amount"]

        if type_ == "income":
            if category == "salary":
                net_salary, cpf = calculate_net_salary(amount)
                total_income += net_salary
                cpf_deductions += cpf
            else:
                total_income += amount

        elif type_ == "expense":
            total_expense += amount

    net_savings = total_income - total_expense
    print(f"\nTotal Income (after CPF): ${total_income:.2f}")
    print(f"Total CPF Deducted      : ${cpf_deductions:.2f}")
    print(f"Total Expense           : ${total_expense:.2f}")
    print(f"Net Savings             : ${net_savings:.2f}\n")

def show_chart():
    data = load_data()
    categories = {}

    for entry in data:
        if entry.get("type") == "expense":
            cat = entry.get("category", "uncategorized").strip().lower()
            categories[cat] = categories.get(cat, 0) + entry["amount"]

    if not categories:
        print("Nothing to show.")
        return

    labels = list(categories.keys())
    amounts = list(categories.values())

    with plt.style.context('ggplot'):
        plt.figure(figsize=(10, 6))
        plt.pie(amounts, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.title("Expenses by Category")
        plt.axis('equal')
        plt.tight_layout()
        plt.show()

def exit_program():
    print("Exiting. Goodbye!")

def main():
    menu = {
        "1": add_transaction,
        "2": view_transactions,
        "3": summary,
        "4": show_chart,
        "5": exit_program
    }

    while True:
        print("\n--- Smart Budget Tracker ---")
        print("1. Add Transaction")
        print("2. View Transactions")
        print("3. Show Summary")
        print("4. Show Expense Chart")
        print("5. Exit")
        choice = input("Choose an option: ").strip()

        if choice in menu:
            if choice == "5":
                menu[choice]()
                break
            else:
                menu[choice]()
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    main()

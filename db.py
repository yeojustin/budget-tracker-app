import sqlite3

DB_NAME = "transactions.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT CHECK(type IN ('income', 'expense')),
            amount REAL NOT NULL,
            category TEXT,
            description TEXT,
            date TEXT,
            tax_percent REAL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def add_transaction(type_, amount, category, description, date, tax_percent=0):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO transactions (type, amount, category, description, date, tax_percent) 
        VALUES (?, ?, ?, ?, ?, ?)""",
              (type_, amount, category, description, date, tax_percent))
    conn.commit()
    conn.close()

def get_transactions():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM transactions ORDER BY date DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def filter_transactions(start_date, end_date):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM transactions WHERE date BETWEEN ? AND ? ORDER BY date DESC", 
              (start_date, end_date))
    rows = c.fetchall()
    conn.close()
    return rows

def reset_transactions():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM transactions")
    conn.commit()
    conn.close()

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

def update_transaction(txn_id, type_, amount, category, description, date, tax_percent):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        UPDATE transactions 
        SET type=?, amount=?, category=?, description=?, date=?, tax_percent=?
        WHERE id=?
    """, (type_, amount, category, description, date, tax_percent, txn_id))
    conn.commit()
    conn.close()

def delete_transaction(txn_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM transactions WHERE id=?", (txn_id,))
    conn.commit()
    conn.close()

def filter_advanced(start_date=None, end_date=None, type_=None, category=None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    query = "SELECT * FROM transactions WHERE 1=1"
    params = []

    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)
    if type_:
        query += " AND type = ?"
        params.append(type_)
    if category:
        query += " AND category = ?"
        params.append(category)

    query += " ORDER BY date DESC"
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return rows
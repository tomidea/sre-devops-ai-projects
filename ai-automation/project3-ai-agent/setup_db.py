import sqlite3


db = sqlite3.connect("business.db")
cursor = db.cursor()

#Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    plan TEXT,
    monthly_spend REAL,
    signup_date TEXT
    )""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS support_tickets (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    subject TEXT,
    status TEXT,
    created_at TEXT
    )""")

# Insert smaple data
customers = [
    (1, "Sarah Chen", "sarah@techcorp.com", "enterprise", 499.99, "2024-01-15"),
    (2, "Mike Johnson", "mike@startup.io", "pro", 79.99, "2024-03-22"),
    (3, "Lisa Park", "lisa@agency.com", "enterprise", 499.99, "2023-11-08"),
    (4, "James Wilson", "james@freelance.com", "free", 0, "2024-06-01"),
    (5, "Emma Davis", "emma@bigco.com", "pro", 79.99, "2024-02-14"),
]

tickets = [
    (1, 1, "API rate limit hitting too often", "open", "2026-03-01"),
    (2, 1, "Need custom integration", "closed", "2026 -02-15"),
    (3, 2, "Billing error on last invoice", "open", "2026-03-10"),
    (4, 3, "Dashboard ;oading slowly", "open", "2026-03-05"),
    (5, 4, "How to upgrade plan", "closed", "2026-03-05"),
    (6, 5, "Feature request: dark mode", "open", "2026-03-12"),
    (7, 2, "Cannot export reports", "open", "2026-03-11"),
]

cursor.executemany("INSERT OR REPLACE INTO customers VALUES (?,?,?,?,?,?)", customers)
cursor.executemany("INSERT OR REPLACE INTO support_tickets VALUES (?,?,?,?,?)", tickets)
db.commit()

# Verify
print("Customers:")
for row in cursor.execute("SELECT * FROM customers"):
    print(f" {row}")
print(f"\nTickets:")
for row in cursor.execute("SELECT * FROM Support_tickets"):
    print(f" {row}")

db.close()
print("\nDatabase created: business.db")


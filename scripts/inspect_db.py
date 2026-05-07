# scripts/inspect_db.py

import sqlite3

connection = sqlite3.connect("data/portfolio_builder.sqlite")
cursor = connection.cursor()

cursor.execute("SELECT COUNT(*) FROM daily_prices")
print("Rows:", cursor.fetchone()[0])

cursor.execute("""
    SELECT ticker, MIN(date), MAX(date), COUNT(*)
    FROM daily_prices
    GROUP BY ticker
""")

for row in cursor.fetchall():
    print(row)

connection.close()

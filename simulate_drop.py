import sqlite3

con = sqlite3.connect("pricewatch.db")
ids = [r[0] for r in con.execute(
    "SELECT id FROM products ORDER BY RANDOM() LIMIT 5")]

for pid in ids:
    con.execute("""
        UPDATE price_history SET price = ROUND(price * 1.25, 2)
        WHERE id = (SELECT MAX(id) FROM price_history WHERE product_id = ?)
    """, (pid,))
con.commit()
print(f"Raised stored price of {len(ids)} products by 25%.")
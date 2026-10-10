import sqlite3

con = sqlite3.connect("pricewatch.db")
print("Products:", con.execute("SELECT COUNT(*) FROM products").fetchone()[0])
print("Price records:", con.execute("SELECT COUNT(*) FROM price_history").fetchone()[0])

print("\nBiggest discounts:")
rows = con.execute("""
    SELECT p.title, h.price, h.compare_at_price,
           (h.compare_at_price - h.price) AS discount
    FROM products p JOIN price_history h ON h.product_id = p.id
    WHERE h.compare_at_price IS NOT NULL
    ORDER BY discount DESC LIMIT 5
""").fetchall()
for r in rows:
    print(r)
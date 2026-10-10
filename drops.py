import sqlite3

con = sqlite3.connect("pricewatch.db")
rows = con.execute("""
    SELECT title, prev_price, price,
           ROUND((prev_price - price) * 100.0 / prev_price, 1) AS pct
    FROM (
        SELECT p.title, h.price,
               LAG(h.price) OVER (PARTITION BY h.product_id ORDER BY h.id) AS prev_price,
               ROW_NUMBER() OVER (PARTITION BY h.product_id ORDER BY h.id DESC) AS rn
        FROM price_history h JOIN products p ON p.id = h.product_id
    )
    WHERE rn = 1 AND prev_price IS NOT NULL AND price < prev_price
    ORDER BY pct DESC
""").fetchall()

print(f"{len(rows)} price drops found")
for title, prev, now_, pct in rows:
    print(f"-{pct}%  {prev} -> {now_}  {title[:60]}")
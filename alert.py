import os
import sqlite3
import urllib.parse
import urllib.request
import urllib.error

MIN_DROP_PCT = 5.0   # only alert on drops of at least this much
MAX_PER_RUN = 10     # max drops in one message

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

con = sqlite3.connect("pricewatch.db")
con.execute("""
    CREATE TABLE IF NOT EXISTS alerts_sent (
        price_id INTEGER PRIMARY KEY,
        sent_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
""")

rows = con.execute("""
    SELECT price_id, title, url, prev_price, price,
           ROUND((prev_price - price) * 100.0 / prev_price, 1) AS pct
    FROM (
        SELECT h.id AS price_id, p.title, p.url, h.price,
               LAG(h.price) OVER (PARTITION BY h.product_id ORDER BY h.id) AS prev_price,
               ROW_NUMBER() OVER (PARTITION BY h.product_id ORDER BY h.id DESC) AS rn
        FROM price_history h JOIN products p ON p.id = h.product_id
    )
    WHERE rn = 1 AND prev_price IS NOT NULL AND price < prev_price
      AND (prev_price - price) * 100.0 / prev_price >= ?
      AND price_id NOT IN (SELECT price_id FROM alerts_sent)
    ORDER BY pct DESC
""", (MIN_DROP_PCT,)).fetchall()

print(f"{len(rows)} new drops (>= {MIN_DROP_PCT}%)")
batch = rows[:MAX_PER_RUN]
if not rows:
    raise SystemExit

for i in range(0, len(rows), MAX_PER_RUN):
    batch = rows[i:i + MAX_PER_RUN]

    lines = ["Price drops found:\n"]
    for _, title, url, prev, price, pct in batch:
        lines.append(f"-{pct}%  {prev:.0f} -> {price:.0f}\n{title[:70]}\n{url}\n")
    message = "\n".join(lines)

    if TOKEN and CHAT_ID:
        data = urllib.parse.urlencode({"chat_id": CHAT_ID, "text": message}).encode()
        try:
            urllib.request.urlopen(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage", data=data, timeout=20)
            print(f"Sent {len(batch)} drops to Telegram.")
        except urllib.error.HTTPError as e:
            print("Telegram rejected it:", e.read().decode())
            raise SystemExit(1)
    else:
        print("(Dry run: no Telegram settings found.)\n")
        print(message)

    # Mark this batch as sent only after it went out successfully.
    con.executemany("INSERT OR IGNORE INTO alerts_sent (price_id) VALUES (?)",
                    [(r[0],) for r in batch])
    con.commit()
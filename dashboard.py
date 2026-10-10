import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="PriceWatch", layout="wide")
st.title("PriceWatch")


@st.cache_data(ttl=60)
def load(query, params=()):
    con = sqlite3.connect("pricewatch.db")
    df = pd.read_sql_query(query, con, params=params)
    con.close()
    return df


# ---------- Top numbers ----------
products = load("SELECT COUNT(*) AS n FROM products").n[0]
records = load("SELECT COUNT(*) AS n FROM price_history").n[0]
runs = load("SELECT COUNT(*) AS n FROM scrape_runs").n[0]

c1, c2, c3 = st.columns(3)
c1.metric("Products tracked", f"{products:,}")
c2.metric("Price records", f"{records:,}")
c3.metric("Scrape runs", f"{runs:,}")

tab1, tab2, tab3 = st.tabs(["Price history", "Latest drops", "Run log"])

# ---------- Tab 1: price history chart ----------
with tab1:
    search = st.text_input("Search a product", "airdopes")
    found = load(
        "SELECT id, title FROM products WHERE title LIKE ? ORDER BY title LIMIT 50",
        (f"%{search}%",),
    )
    if found.empty:
        st.info("No products match that search.")
    else:
        choice = st.selectbox("Pick one", found.title.tolist())
        pid = int(found[found.title == choice].id.iloc[0])
        hist = load(
            "SELECT scraped_at, price, compare_at_price FROM price_history "
            "WHERE product_id = ? ORDER BY id",
            (pid,),
        )
        hist["scraped_at"] = pd.to_datetime(hist["scraped_at"])
        fig = px.line(hist, x="scraped_at", y=["price", "compare_at_price"],
                      markers=True, title="Price vs. original price")
        fig.update_layout(yaxis_title="Price (₹)", xaxis_title="Scraped at",
                          legend_title="")
        st.plotly_chart(fig, use_container_width=True)# ---------- Tab 2: latest drops ----------
with tab2:
    drops = load("""
        SELECT title, prev_price, price,
               ROUND((prev_price - price) * 100.0 / prev_price, 1) AS drop_pct
        FROM (
            SELECT p.title, h.price,
                   LAG(h.price) OVER (PARTITION BY h.product_id ORDER BY h.id) AS prev_price,
                   ROW_NUMBER() OVER (PARTITION BY h.product_id ORDER BY h.id DESC) AS rn
            FROM price_history h JOIN products p ON p.id = h.product_id
        )
        WHERE rn = 1 AND prev_price IS NOT NULL AND price < prev_price
        ORDER BY drop_pct DESC
    """)
    st.write(f"{len(drops)} products whose latest price is a drop")
    st.dataframe(drops, use_container_width=True)

# ---------- Tab 3: run log ----------
with tab3:
    log = load("SELECT * FROM scrape_runs ORDER BY id DESC LIMIT 50")
    st.dataframe(log, use_container_width=True)
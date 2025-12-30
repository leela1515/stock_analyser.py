# -*- coding: utf-8 -*-
"""
Created on Tue Dec 30 20:13:45 2025

@author: ATL AFSH
"""

import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt

st.set_page_config(page_title="Simple Stock Analyzer", layout="centered")

st.title("📊 Simple Stock Analyzer")
st.caption("Made for normal investors • No finance jargon")

# ---------------- MODE SELECTION ----------------
mode = st.radio(
    "How do you want to analyse the stock?",
    ["🔢 Enter values manually", "🌐 Fetch live data using stock name"]
)

st.divider()

# ---------------- INPUTS ----------------
if mode == "🔢 Enter values manually":
    roe = st.number_input("Profit efficiency (ROE %) ", min_value=0.0)
    pe = st.number_input("Share Price vs Earnings (P/E)", min_value=0.0)
    pb = st.number_input("Share Price vs Company Value (P/B)", min_value=0.0)
    eps = st.number_input("Profit per share (EPS ₹)", min_value=0.0)
    debt_equity = st.number_input("Debt compared to own money (Debt/Equity)", min_value=0.0)
    sales_growth = st.number_input("Average sales growth (%)", min_value=0.0)
    profit_growth = st.number_input("Average profit growth (%)", min_value=0.0)

else:
    ticker = st.text_input("Enter stock name (Yahoo format)", placeholder="TCS.NS, INFY.NS")

    if ticker:
        stock = yf.Ticker(ticker)
        info = stock.info
        financials = stock.financials
        balance = stock.balance_sheet

        roe = info.get("returnOnEquity", 0) * 100
        pe = info.get("trailingPE", 0)
        pb = info.get("priceToBook", 0)
        eps = info.get("trailingEps", 0)

        debt = balance.loc["Total Debt"][0] if "Total Debt" in balance.index else 0
        equity = balance.loc["Total Stockholder Equity"][0] if "Total Stockholder Equity" in balance.index else 1
        debt_equity = debt / equity if equity else 0

        def calc_cagr(series):
            years = len(series) - 1
            if years <= 0:
                return 0
            return ((series.iloc[0] / series.iloc[-1]) ** (1/years) - 1) * 100

        sales_growth = calc_cagr(financials.loc["Total Revenue"]) if "Total Revenue" in financials.index else 0
        profit_growth = calc_cagr(financials.loc["Net Income"]) if "Net Income" in financials.index else 0

st.divider()

# ---------------- SCORING ----------------
score = 0
explanations = []

# ROE
if roe >= 18:
    score += 2
    explanations.append(f"✅ The company earns about ₹{roe:.0f} for every ₹100 invested. This is very good.")
elif roe >= 12:
    score += 1
    explanations.append(f"⚠ The company earns about ₹{roe:.0f} for every ₹100 invested. Acceptable, not great.")
else:
    explanations.append(f"❌ The company earns very little from investors’ money.")

# P/E
if pe <= 25:
    score += 2
    explanations.append(f"✅ You are paying ₹{pe:.0f} to earn ₹1 today. This is reasonable.")
elif pe <= 40:
    score += 1
    explanations.append(f"⚠ You are paying ₹{pe:.0f} to earn ₹1. Stock expects high future growth.")
else:
    explanations.append(f"❌ You are paying ₹{pe:.0f} to earn ₹1. Very expensive.")

# P/B
if pb <= 3:
    score += 2
    explanations.append("✅ Share price is close to company’s real value.")
elif pb <= 6:
    score += 1
    explanations.append("⚠ Share price is much higher than company value.")
else:
    explanations.append("❌ Share price is far above company’s actual worth.")

# Growth
if sales_growth >= 10 and profit_growth >= 10:
    score += 2
    explanations.append("✅ Sales and profits are growing well year after year.")
elif sales_growth >= 5:
    score += 1
    explanations.append("⚠ Growth is present but slow.")
else:
    explanations.append("❌ Business growth is weak.")

# Debt
if debt_equity <= 0.5:
    score += 2
    explanations.append("✅ Company does not depend much on loans.")
elif debt_equity <= 1:
    score += 1
    explanations.append("⚠ Company uses some loans, manageable.")
else:
    explanations.append("❌ Company depends heavily on borrowed money.")

# ---------------- FINAL RESULT ----------------
st.subheader("📌 Final Result")

if score >= 8:
    verdict = "🟢 GOOD STOCK (Worth considering)"
elif score >= 5:
    verdict = "🟡 AVERAGE (Wait & watch)"
else:
    verdict = "🔴 RISKY (Better avoid)"

st.markdown(f"### Score: {score} / 10")
st.markdown(f"## {verdict}")

st.divider()

# ---------------- EXPLANATION ----------------
st.subheader("🧠 Explained in Simple Words")
for e in explanations:
    st.write("•", e)

# ---------------- GRAPH ----------------
st.subheader("📊 Strength Overview")
labels = ["Profit", "Valuation", "Growth", "Debt"]
values = [
    min(roe / 10, 2),
    2 if pe <= 25 else 1 if pe <= 40 else 0,
    2 if sales_growth >= 10 else 1 if sales_growth >= 5 else 0,
    2 if debt_equity <= 0.5 else 1 if debt_equity <= 1 else 0
]

fig, ax = plt.subplots()
ax.bar(labels, values)
ax.set_ylim(0, 2)
st.pyplot(fig)

st.caption("⚠ Educational tool. Always combine with long-term thinking.")

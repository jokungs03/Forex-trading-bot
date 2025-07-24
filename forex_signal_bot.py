# create_requirements.py

modules = [
    "streamlit",
    "yfinance",
    "pandas",
    "ta"
]

with open("requirements.txt", "w") as f:
    for module in modules:
        f.write(module + "\n")

print("requirements.txt créé avec succès.")

# Optionnel : installation automatique (nécessite que pip soit accessible)
import os
os.system("pip install -r requirements.txt")
import streamlit as st
import yfinance as yf
import pandas as pd
import ta

st.set_page_config(page_title="Forex Signal Bot", layout="centered")
st.title("📊 Forex Signal Bot - Analyse Automatique")
st.markdown("Ce robot analyse les paires Forex/CFD et te donne un **signal clair : BUY ou SELL**.")

# Available pairs
forex_pairs = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "JPY=X",
    "USD/CHF": "CHF=X",
    "AUD/USD": "AUDUSD=X",
    "NZD/USD": "NZDUSD=X",
    "USD/CAD": "CAD=X",
    "EUR/GBP": "EURGBP=X",
    "EUR/JPY": "EURJPY=X",
    "GBP/JPY": "GBPJPY=X"
}

pair_name = st.selectbox("Choisis une paire :", list(forex_pairs.keys()))
timeframe = st.selectbox("Choisis le timeframe :", ["1m", "5m", "15m"])

if st.button("Analyser"):
    symbol = forex_pairs[pair_name]
    interval = {"1m": "1m", "5m": "5m", "15m": "15m"}[timeframe]

    st.info("📥 Chargement des données en cours...")

    try:
        df = yf.download(tickers=symbol, period="1d", interval=interval)
        df.dropna(inplace=True)

        # Calculate indicators
        df['rsi'] = ta.momentum.RSIIndicator(close=df['Close']).rsi()
        macd = ta.trend.MACD(close=df['Close'])
        df['macd'] = macd.macd()
        df['signal'] = macd.macd_signal()
        df['ema_9'] = ta.trend.EMAIndicator(close=df['Close'], window=9).ema_indicator()
        df['ema_21'] = ta.trend.EMAIndicator(close=df['Close'], window=21).ema_indicator()

        last = df.iloc[-1]
        signal_summary = []

        # Signal analysis
        if last['rsi'] < 30:
            signal_summary.append("RSI < 30 → Survente ✅")
        elif last['rsi'] > 70:
            signal_summary.append("RSI > 70 → Surachat ❌")

        if last['macd'] > last['signal']:
            signal_summary.append("MACD haussier ✅")
        else:
            signal_summary.append("MACD baissier ❌")

        if last['ema_9'] > last['ema_21']:
            signal_summary.append("EMA9 > EMA21 → Tendance haussière ✅")
        else:
            signal_summary.append("EMA9 < EMA21 → Tendance baissière ❌")

        # Final decision
        bullish = sum("✅" in s for s in signal_summary)
        bearish = sum("❌" in s for s in signal_summary)
        final_signal = "BUY ✅" if bullish > bearish else "SELL ❌"

        st.subheader("📈 Résultat de l'analyse :")
        for s in signal_summary:
            st.write("- " + s)
        st.markdown(f"### 🚨 SIGNAL FINAL : **{final_signal}**")

    except Exception as e:
        st.error("Erreur lors de la récupération des données ou de l'analyse.")
        st.text(str(e))

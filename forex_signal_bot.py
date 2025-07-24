import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import plotly.graph_objs as go

st.set_page_config(page_title="📊 Forex Signal Bot", layout="wide")
st.title("📊 Forex Signal Bot - Analyse Automatique")
st.markdown("""
Ce robot analyse les paires Forex/CFD en temps réel et te donne un **signal clair : BUY ou SELL** avec visualisation.
""")

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

pair_name = st.selectbox("Choisis une paire Forex :", list(forex_pairs.keys()))
timeframe = st.selectbox("Choisis le timeframe :", ["1m", "5m", "15m", "1h", "1d"])
period_map = {
    "1m": "7d",   # yfinance limite 1m à 7 jours max
    "5m": "60d",
    "15m": "60d",
    "1h": "730d",  # ~2 ans
    "1d": "max"
}

interval = timeframe
period = period_map[timeframe]

if st.button("Analyser"):

    with st.spinner(f"Chargement des données {pair_name} en {timeframe}..."):
        try:
            symbol = forex_pairs[pair_name]
            df = yf.download(tickers=symbol, period=period, interval=interval)
            if df.empty:
                st.warning("Aucune donnée récupérée, essaie un autre timeframe ou paire.")
                st.stop()
            df.dropna(inplace=True)

            # Indicateurs techniques
            df['rsi'] = ta.momentum.RSIIndicator(close=df['Close'], window=14).rsi()
            macd = ta.trend.MACD(close=df['Close'])
            df['macd'] = macd.macd()
            df['macd_signal'] = macd.macd_signal()
            df['ema_9'] = ta.trend.EMAIndicator(close=df['Close'], window=9).ema_indicator()
            df['ema_21'] = ta.trend.EMAIndicator(close=df['Close'], window=21).ema_indicator()

            # Dernières valeurs
            last = df.iloc[-1]

            # Analyse des signaux
            signals = []

            if last['rsi'] < 30:
                signals.append("RSI < 30 : Survente ✅")
            elif last['rsi'] > 70:
                signals.append("RSI > 70 : Surachat ❌")
            else:
                signals.append(f"RSI neutre ({last['rsi']:.1f})")

            if last['macd'] > last['macd_signal']:
                signals.append("MACD haussier ✅")
            else:
                signals.append("MACD baissier ❌")

            if last['ema_9'] > last['ema_21']:
                signals.append("EMA9 > EMA21 : Tendance haussière ✅")
            else:
                signals.append("EMA9 < EMA21 : Tendance baissière ❌")

            bullish = sum("✅" in s for s in signals)
            bearish = sum("❌" in s for s in signals)
            final_signal = "BUY ✅" if bullish > bearish else "SELL ❌"

            st.subheader("📈 Résultat de l'analyse technique :")
            for s in signals:
                st.write("- " + s)

            st.markdown(f"### 🚨 SIGNAL FINAL : **{final_signal}**")

            # Affichage graphique interactif avec Plotly
            fig = go.Figure()

            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='Bougies'
            ))

            fig.add_trace(go.Scatter(x=df.index, y=df['ema_9'], line=dict(color='orange', width=1), name='EMA 9'))
            fig.add_trace(go.Scatter(x=df.index, y=df['ema_21'], line=dict(color='blue', width=1), name='EMA 21'))
            fig.update_layout(
                title=f"{pair_name} - Graphique avec EMA9 & EMA21",
                xaxis_rangeslider_visible=False,
                height=600
            )
            st.plotly_chart(fig, use_container_width=True)

            # RSI & MACD plots en dessous
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("RSI")
                fig_rsi = go.Figure()
                fig_rsi.add_trace(go.Scatter(x=df.index, y=df['rsi'], name='RSI', line=dict(color='purple')))
                fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
                fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
                fig_rsi.update_layout(height=300)
                st.plotly_chart(fig_rsi, use_container_width=True)

            with col2:
                st.subheader("MACD")
                fig_macd = go.Figure()
                fig_macd.add_trace(go.Scatter(x=df.index, y=df['macd'], name='MACD', line=dict(color='green')))
                fig_macd.add_trace(go.Scatter(x=df.index, y=df['macd_signal'], name='Signal', line=dict(color='red')))
                fig_macd.update_layout(height=300)
                st.plotly_chart(fig_macd, use_container_width=True)

        except Exception as e:
            st.error("Erreur lors de la récupération ou analyse des données.")
            st.text(str(e))
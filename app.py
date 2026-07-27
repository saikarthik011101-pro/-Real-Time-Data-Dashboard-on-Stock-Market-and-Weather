# app.py
import streamlit as st
import plotly.express as px
from utils import fetch_alpha_intraday, parse_alpha_intraday_json, fetch_weather
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(page_title="Real-Time Dashboard", layout="wide")
st.title("📊 Real-Time Data Analytics Dashboard")

# Sidebar
with st.sidebar:
    st.header("Settings")
    symbols_input = st.text_input("Enter Stock Symbols (comma-separated)", "AAPL,MSFT")
    city = st.text_input("Enter City Name", "Hyderabad")
    interval = st.selectbox("Stock Interval", ["1min", "5min", "15min", "30min"], index=1)
    refresh = st.button("🔄 Refresh Now")

symbols = [s.strip().upper() for s in symbols_input.split(",") if s.strip()]

@st.cache_data(ttl=120)
def get_stock_df(symbol, interval):
    raw = fetch_alpha_intraday(symbol, interval)
    return parse_alpha_intraday_json(raw)

@st.cache_data(ttl=120)
def get_weather_data(city):
    return fetch_weather(city)

col1, col2 = st.columns([2, 1])

# --- Stock Section ---
with col1:
    st.subheader("📈 Stock Data")
    for s in symbols:
        try:
            df = get_stock_df(s, interval)
            if df is None:
                st.warning(f"No data for {s}")
                continue
            st.markdown(f"**{s}** — Last Update: {df.index[-1]}")
            fig = px.line(df, x=df.index, y="Close", title=f"{s} Close Price")
            st.plotly_chart(fig, use_container_width=True)
            st.metric(label=f"{s} Current Price", value=f"${df['Close'].iloc[-1]:.2f}")
        except Exception as e:
            st.error(f"Error for {s}: {e}")

# --- Weather Section ---
with col2:
    st.subheader("🌦 Weather Info")
    try:
        w = get_weather_data(city)
        if w.get("main"):
            st.metric("Temperature (°C)", w["main"]["temp"])
            st.metric("Humidity (%)", w["main"]["humidity"])
            st.metric("Wind (m/s)", w["wind"]["speed"])
            st.markdown(f"**Condition:** {w['weather'][0]['description'].title()}")
        else:
            st.warning("City not found.")
    except Exception as e:
        st.error("Weather fetch error: " + str(e))

if refresh:
    st.experimental_rerun()

st.markdown("---")
st.caption("Built with Streamlit, Alpha Vantage & OpenWeatherMap APIs.")

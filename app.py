import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time
from datetime import datetime
import pytz

# ---- CONFIG ----
st.set_page_config(
    page_title="Live Weather Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- STYLES ----
st.markdown("""
    <style>
    .main {background-color: #0E1117; color: white;}
    .css-1d391kg {color: white;}
    .block-container {padding: 2rem;}
    </style>
""", unsafe_allow_html=True)

# ---- HEADERS ----
st.title("⛅ Live Weather Dashboard")

# ---- CURRENT DATE ----
current_date = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%A, %d %B %Y")
st.markdown(f"📅 {current_date}")
st.markdown("#### Updated every 30 seconds")

# ---- SIDEBAR ----
with st.sidebar:
    st.header("Controls ⚙")
    city = st.text_input("City Name", "Bangalore")
    show_trend = st.toggle("Show Trendline", value=True)

# ---- API DETAILS ----
API_KEY = st.secrets["api_key"]  # Add this in .streamlit/secrets.toml
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# ---- DATA FETCHING ----
def fetch_weather_data(city):
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        return {
            "city": city,
            "description": data["weather"][0]["description"],
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "timestamp": datetime.now(pytz.timezone("Asia/Kolkata"))
        }
    else:
        return None

# ---- CACHING ----
@st.cache_data(ttl=30)
def get_weather_df(city):
    row = fetch_weather_data(city)
    if row:
        return pd.DataFrame([row])
    return pd.DataFrame()

# ---- FETCH ----
df = get_weather_df(city)

if df.empty:
    st.error("Failed to fetch weather data. Check city name or API key.")
    st.stop()

# ---- Emoji Mapping ----
def get_weather_emoji(description):
    d = description.lower()
    if "cloud" in d:
        return "☁"
    elif "sun" in d or "clear" in d:
        return "☀"
    elif "rain" in d:
        return "🌧"
    elif "storm" in d or "thunder" in d:
        return "⛈"
    elif "mist" in d or "fog" in d:
        return "🌫"
    else:
        return "🌡"

# ---- SUMMARY METRIC ----
emoji = get_weather_emoji(df['description'][0])
st.markdown("### 🌍 Live Weather Summary")
st.metric(
    label=f"{emoji} {city} ({df['timestamp'][0].strftime('%H:%M:%S')})",
    value=f"{df['temperature'][0]}°C",
    delta=df['description'][0].capitalize()
)

# ---- BEAUTIFUL SNAPSHOT ----
st.markdown("### 🌟 Snapshot Summary")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"<h4 style='color:white;'>🌡 <b>Temperature:</b> {df['temperature'][0]}°C</h4>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<h4 style='color:white;'>💧 <b>Humidity:</b> {df['humidity'][0]}%</h4>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<h4 style='color:white;'>🌬 <b>Wind Speed:</b> {df['wind_speed'][0]} km/h</h4>", unsafe_allow_html=True)

# ---- TABLE ----
df['summary'] = (
    df['description'] + ", " +
    df['temperature'].astype(str) + "°C, " +
    df['humidity'].astype(str) + "% humidity, " +
    df['wind_speed'].astype(str) + " km/h wind"
)
st.markdown("### 📋 Weather Info Table")
st.dataframe(df[['timestamp', 'summary']], use_container_width=True)

# ---- TREND SIMULATION ----
timestamps = pd.date_range(end=df['timestamp'][0], periods=10, freq='3T')
trend_df = pd.DataFrame({
    "timestamp": timestamps,
    "temperature": df['temperature'][0] + pd.Series(range(10)).apply(lambda x: x * 0.1),
    "humidity": df['humidity'][0] + pd.Series(range(10)).apply(lambda x: (x % 2) * 1),
    "wind_speed": df['wind_speed'][0] + pd.Series(range(10)).apply(lambda x: (-1)**x * 0.1)
})

chart_colors = {
    'temperature': 'orangered',
    'humidity': 'deepskyblue',
    'wind_speed': 'gold'
}

for metric in ['temperature', 'humidity', 'wind_speed']:
    fig = px.line(trend_df, x='timestamp', y=metric, title=f'{metric.capitalize()} Trend', markers=True)
    fig.update_traces(line_shape="spline" if show_trend else "linear", line_color=chart_colors[metric])
    fig.update_layout(
        xaxis_title='Time (IST)',
        yaxis_title=metric.capitalize(),
        template='plotly_dark',
        title_font_size=20,
        margin=dict(l=20, r=20, t=40, b=20),
        height=300
    )
    st.plotly_chart(fig, use_container_width=True)

# ---- AUTO REFRESH ----
st.markdown("⏱ Auto-refreshes every 30 seconds.")
time.sleep(30)
st.rerun()

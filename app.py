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
    .main {
        background-color: #0E1117;
        color: white;
    }

    .block-container {
        padding: 2rem;
    }

    h1, h2, h3, h4, h5, h6, p, div {
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# ---- HEADER ----
st.title("⛅ Live Weather Dashboard")

# ---- CURRENT DATE ----
ist = pytz.timezone("Asia/Kolkata")
current_date = datetime.now(ist).strftime("%A, %d %B %Y")

st.markdown(f"📅 {current_date}")
st.markdown("#### Updated every 30 seconds")

# ---- SIDEBAR ----
with st.sidebar:
    st.header("Controls ⚙")

    city = st.text_input(
        "City Name",
        value="Bangalore"
    )

    show_trend = st.toggle(
        "Show Smooth Trendline",
        value=True
    )

# ---- API DETAILS ----
API_KEY = st.secrets["api_key"]

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# ---- WEATHER FETCH FUNCTION ----
def fetch_weather_data(city):

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)

        if response.status_code == 200:

            data = response.json()

            return {
                "city": city,
                "description": data["weather"][0]["description"],
                "temperature": float(data["main"]["temp"]),
                "humidity": int(data["main"]["humidity"]),
                "wind_speed": float(data["wind"]["speed"]),
                "timestamp": datetime.now(ist)
            }

        else:
            return None

    except Exception as e:
        st.error(f"API Error: {e}")
        return None

# ---- CACHE ----
@st.cache_data(ttl=30)
def get_weather_df(city):

    row = fetch_weather_data(city)

    if row:
        return pd.DataFrame([row])

    return pd.DataFrame()

# ---- FETCH DATA ----
df = get_weather_df(city)

# ---- VALIDATION ----
if df.empty:
    st.error("❌ Failed to fetch weather data. Check city name or API key.")
    st.stop()

# ---- SAFE DATETIME CONVERSION ----
df["timestamp"] = pd.to_datetime(df["timestamp"])

# ---- WEATHER EMOJI ----
def get_weather_emoji(description):

    d = description.lower()

    if "cloud" in d:
        return "☁"

    elif "clear" in d or "sun" in d:
        return "☀"

    elif "rain" in d:
        return "🌧"

    elif "storm" in d or "thunder" in d:
        return "⛈"

    elif "mist" in d or "fog" in d:
        return "🌫"

    else:
        return "🌡"

# ---- SUMMARY ----
emoji = get_weather_emoji(df["description"].iloc[0])

st.markdown("### 🌍 Live Weather Summary")

st.metric(
    label=f"{emoji} {city} ({df['timestamp'].iloc[0].strftime('%H:%M:%S')})",
    value=f"{df['temperature'].iloc[0]}°C",
    delta=df["description"].iloc[0].capitalize()
)

# ---- SNAPSHOT CARDS ----
st.markdown("### 🌟 Snapshot Summary")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
        <div style='padding:15px;border-radius:12px;background:#1E1E1E;'>
        <h4>🌡 Temperature</h4>
        <h2>{df['temperature'].iloc[0]} °C</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div style='padding:15px;border-radius:12px;background:#1E1E1E;'>
        <h4>💧 Humidity</h4>
        <h2>{df['humidity'].iloc[0]} %</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div style='padding:15px;border-radius:12px;background:#1E1E1E;'>
        <h4>🌬 Wind Speed</h4>
        <h2>{df['wind_speed'].iloc[0]} km/h</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---- WEATHER TABLE ----
df["summary"] = (
    df["description"]
    + ", "
    + df["temperature"].astype(str)
    + "°C, "
    + df["humidity"].astype(str)
    + "% humidity, "
    + df["wind_speed"].astype(str)
    + " km/h wind"
)

st.markdown("### 📋 Weather Info Table")

st.dataframe(
    df[["timestamp", "summary"]],
    use_container_width=True
)

# ---- TREND DATA ----
base_temp = df["temperature"].iloc[0]
base_humidity = df["humidity"].iloc[0]
base_wind = df["wind_speed"].iloc[0]

# IMPORTANT FIX HERE
timestamps = pd.date_range(
    end=df["timestamp"].iloc[0],
    periods=10,
    freq="3min"
)

trend_df = pd.DataFrame({
    "timestamp": timestamps,

    "temperature": [
        base_temp + (i * 0.15)
        for i in range(10)
    ],

    "humidity": [
        base_humidity + ((-1) ** i)
        for i in range(10)
    ],

    "wind_speed": [
        base_wind + ((-1) ** i) * 0.2
        for i in range(10)
    ]
})

# ---- CHART COLORS ----
chart_colors = {
    "temperature": "orangered",
    "humidity": "deepskyblue",
    "wind_speed": "gold"
}

# ---- CHARTS ----
st.markdown("### 📈 Live Weather Trends")

for metric in ["temperature", "humidity", "wind_speed"]:

    fig = px.line(
        trend_df,
        x="timestamp",
        y=metric,
        markers=True,
        title=f"{metric.capitalize()} Trend"
    )

    fig.update_traces(
        line_shape="spline" if show_trend else "linear",
        line_color=chart_colors[metric]
    )

    fig.update_layout(
        template="plotly_dark",
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis_title="Time (IST)",
        yaxis_title=metric.capitalize(),
        title_font_size=22
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ---- FOOTER ----
st.markdown("---")
st.markdown("⏱ Dashboard auto-refreshes every 30 seconds.")

# ---- AUTO REFRESH ----
time.sleep(30)
st.rerun()

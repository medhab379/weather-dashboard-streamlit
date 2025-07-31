# 🌦 Real-Time Weather Monitoring Dashboard

A *real-time weather monitoring dashboard* built using *Streamlit, **Plotly, and **OpenWeather API* — designed for professional clarity, live updates, and a recruiter-friendly presentation.

---

## 🔍 Overview

This project visualizes *live weather conditions* (temperature, humidity, wind speed, and sky condition) in *Bangalore* and auto-refreshes every 30 seconds. It is styled with a dark theme and features trendlines, snapshot summaries, and geographic mapping.

---

## 🚀 Features

✅ Auto-refresh every 30 seconds  
✅ Toggle trendline ON/OFF  
✅ Animated live sky background  
✅ Real-time voice alerts for weather changes  
✅ Streamlit dark mode styling  
✅ Interactive weather map with location pin  
✅ Displays current sky condition with icon  
✅ Snapshot summary of all metrics  
✅ Clean, recruiter-friendly UI

---

## 📦 Tech Stack

- *Streamlit* (dashboard framework)  
- *Plotly Express* (dynamic trend charts)  
- *Pandas* (data handling)  
- *OpenWeatherMap API* (live weather data)  
- *pydeck* (interactive map)  
- *HTML/CSS* (for animations and style)

---

## 📊 Dashboard Snapshot

| Temperature | Humidity | Wind Speed |
|-------------|----------|------------|
| ✅ Trend chart | ✅ Trend chart | ✅ Trend chart |

Also shows:
- Current condition (e.g., ☁ Overcast Clouds)
- Latest readings and time
- Map view of Bangalore

---

## 🔐 API Key Setup (Required)

Add your OpenWeather API key to Streamlit Cloud:

**/.streamlit/secrets.toml**
```toml
[weather_api]
key = "your_openweather_api_key"

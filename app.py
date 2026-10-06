import html
from datetime import datetime

import streamlit as st

from services.weather_service import (
    get_weather,
    weather_code_to_description,
    weather_code_to_icon,
)
from utils.travel import build_travel_insights, answer_weather_question


st.set_page_config(
    page_title="SkyCast — Weather Chatbot",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

:root {
  --bg: #07111f;
  --panel: rgba(15, 31, 52, 0.82);
  --panel-2: rgba(19, 39, 64, 0.78);
  --text: #f4f8fc;
  --muted: #a8b8c9;
  --line: rgba(255,255,255,.10);
  --accent: #74c7ff;
  --accent-2: #9b8cff;
  --good: #7ee2b8;
  --warn: #ffd27d;
  --danger: #ff9c9c;
}

html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif;
}

.stApp {
  background:
    radial-gradient(circle at 10% 0%, rgba(116,199,255,.15), transparent 30%),
    radial-gradient(circle at 90% 10%, rgba(155,140,255,.13), transparent 28%),
    linear-gradient(145deg, #07111f 0%, #0b1728 55%, #07111f 100%);
  color: var(--text);
}

.block-container {
  max-width: 1180px;
  padding-top: 2.5rem;
  padding-bottom: 4rem;
}

.hero {
  padding: 1.2rem 0 1.5rem;
}

.eyebrow {
  color: var(--accent);
  font-size: .78rem;
  font-weight: 700;
  letter-spacing: .16em;
  text-transform: uppercase;
  margin-bottom: .5rem;
}

.hero h1 {
  font-family: 'Manrope', sans-serif;
  font-size: clamp(2.3rem, 5vw, 4.6rem);
  line-height: .98;
  letter-spacing: -.055em;
  margin: 0;
  color: var(--text);
}

.hero p {
  color: var(--muted);
  font-size: 1.05rem;
  max-width: 680px;
  margin-top: 1rem;
}

.search-wrap {
  background: rgba(12, 27, 46, .9);
  border: 1px solid var(--line);
  border-radius: 22px;
  padding: 1rem;
  box-shadow: 0 20px 60px rgba(0,0,0,.18);
}

.section-title {
  font-family: 'Manrope', sans-serif;
  font-size: 1.2rem;
  font-weight: 800;
  margin: 1.8rem 0 .8rem;
}

.card {
  background: linear-gradient(145deg, var(--panel), var(--panel-2));
  border: 1px solid var(--line);
  border-radius: 22px;
  padding: 1.25rem;
  height: 100%;
  box-shadow: 0 12px 40px rgba(0,0,0,.12);
  backdrop-filter: blur(12px);
}

.current-card {
  min-height: 265px;
}

.location {
  color: var(--muted);
  font-size: .92rem;
}

.temp {
  font-family: 'Manrope', sans-serif;
  font-size: 4.4rem;
  font-weight: 800;
  line-height: 1;
  letter-spacing: -.06em;
  margin: .55rem 0;
}

.condition {
  font-size: 1.05rem;
  color: var(--text);
}

.weather-icon {
  font-size: 4rem;
  line-height: 1;
}

.muted {
  color: var(--muted);
}

.metric-label {
  color: var(--muted);
  font-size: .78rem;
  margin-bottom: .2rem;
}

.metric-value {
  font-size: 1.02rem;
  font-weight: 700;
}

.forecast-card {
  text-align: center;
  padding: 1rem .75rem;
}

.forecast-day {
  font-weight: 700;
}

.forecast-icon {
  font-size: 2.1rem;
  margin: .45rem 0;
}

.forecast-temp {
  font-size: 1.15rem;
  font-weight: 700;
}

.insight {
  border-left: 3px solid var(--accent);
  padding: .2rem 0 .2rem .85rem;
  margin: .85rem 0;
}

.insight strong {
  display: block;
  margin-bottom: .15rem;
}

.chat-user {
  background: rgba(116,199,255,.13);
  border: 1px solid rgba(116,199,255,.18);
  border-radius: 18px 18px 4px 18px;
  padding: .8rem 1rem;
  margin: .55rem 0 .55rem 12%;
}

.chat-bot {
  background: rgba(255,255,255,.055);
  border: 1px solid var(--line);
  border-radius: 18px 18px 18px 4px;
  padding: .8rem 1rem;
  margin: .55rem 12% .55rem 0;
}

.footer {
  text-align: center;
  color: #75889d;
  font-size: .78rem;
  padding-top: 2.5rem;
}

div[data-testid="stTextInput"] input {
  background: rgba(255,255,255,.055) !important;
  color: var(--text) !important;
  border: 1px solid var(--line) !important;
  border-radius: 14px !important;
}

div[data-testid="stButton"] button {
  border-radius: 14px !important;
  border: 1px solid rgba(116,199,255,.25) !important;
  background: linear-gradient(135deg, #318dcc, #5961d8) !important;
  color: white !important;
  font-weight: 700 !important;
  min-height: 44px;
}

div[data-testid="stChatInput"] textarea {
  background: rgba(255,255,255,.055) !important;
  color: var(--text) !important;
}

@media (max-width: 720px) {
  .block-container { padding: 1.2rem .8rem 3rem; }
  .hero h1 { font-size: 2.7rem; }
  .temp { font-size: 3.5rem; }
  .chat-user { margin-left: 4%; }
  .chat-bot { margin-right: 4%; }
}
</style>
"""
st.html(CSS)

if "weather" not in st.session_state:
    st.session_state.weather = None
if "city" not in st.session_state:
    st.session_state.city = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">SKYCAST · WEATHER INTELLIGENCE</div>
      <h1>Know the weather.<br>Plan the day.</h1>
      <p>Search any city for live conditions, a five-day forecast, and practical travel guidance — without a paid API key.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.container(border=False):
    st.markdown('<div class="search-wrap">', unsafe_allow_html=True)
    c1, c2 = st.columns([5, 1], vertical_alignment="bottom")
    with c1:
        city_input = st.text_input(
            "Destination",
            value=st.session_state.city,
            placeholder="Try Dubai, London, Mumbai...",
            label_visibility="collapsed",
        )
    with c2:
        search = st.button("Search weather", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

if search:
    city = city_input.strip()
    if not city:
        st.warning("Enter a city name first.")
    else:
        with st.spinner("Finding the city and checking the latest forecast..."):
            try:
                st.session_state.weather = get_weather(city)
                st.session_state.city = city
                st.session_state.messages = [{
                    "role": "assistant",
                    "content": f"Weather loaded for {st.session_state.weather['location_name']}. Ask me anything about the forecast."
                }]
            except ValueError as exc:
                st.session_state.weather = None
                st.error(str(exc))
            except Exception:
                st.session_state.weather = None
                st.error("The weather service is temporarily unavailable. Please try again.")

weather = st.session_state.weather

if weather:
    current = weather["current"]
    daily = weather["daily"]

    st.markdown(
        f"""
        <div class="section-title">{html.escape(weather['location_name'])}, {html.escape(weather['country'])}</div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.35, 1], gap="medium")

    with left:
        icon = weather_code_to_icon(current["weather_code"])
        desc = weather_code_to_description(current["weather_code"])
        st.markdown(
            f"""
            <div class="card current-card">
              <div class="location">Current conditions · {html.escape(weather['timezone'])}</div>
              <div style="display:flex;justify-content:space-between;align-items:center;margin-top:.6rem;">
                <div>
                  <div class="temp">{current['temperature']:.0f}°</div>
                  <div class="condition">{html.escape(desc)} · feels like {current['apparent_temperature']:.0f}°</div>
                </div>
                <div class="weather-icon">{icon}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            f"""
            <div class="card current-card">
              <div class="metric-label">TODAY'S SNAPSHOT</div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-top:1rem;">
                <div><div class="metric-label">Humidity</div><div class="metric-value">{current['humidity']:.0f}%</div></div>
                <div><div class="metric-label">Wind</div><div class="metric-value">{current['wind_speed']:.0f} km/h</div></div>
                <div><div class="metric-label">Rain probability</div><div class="metric-value">{daily['precipitation_probability'][0]:.0f}%</div></div>
                <div><div class="metric-label">UV max</div><div class="metric-value">{daily['uv_index_max'][0]:.1f}</div></div>
                <div><div class="metric-label">Sunrise</div><div class="metric-value">{daily['sunrise'][0][11:16]}</div></div>
                <div><div class="metric-label">Sunset</div><div class="metric-value">{daily['sunset'][0][11:16]}</div></div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-title">5-day forecast</div>', unsafe_allow_html=True)
    forecast_cols = st.columns(5)
    for i, col in enumerate(forecast_cols):
        date = datetime.fromisoformat(daily["time"][i]).strftime("%a")
        icon = weather_code_to_icon(daily["weather_code"][i])
        desc = weather_code_to_description(daily["weather_code"][i])
        with col:
            st.markdown(
                f"""
                <div class="card forecast-card">
                  <div class="forecast-day">{date}</div>
                  <div class="forecast-icon">{icon}</div>
                  <div class="muted" style="font-size:.78rem;min-height:2.1rem;">{html.escape(desc)}</div>
                  <div class="forecast-temp">{daily['temperature_2m_max'][i]:.0f}° / {daily['temperature_2m_min'][i]:.0f}°</div>
                  <div class="muted" style="font-size:.75rem;margin-top:.3rem;">Rain {daily['precipitation_probability'][i]:.0f}%</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    insights = build_travel_insights(weather)
    st.markdown('<div class="section-title">Travel intelligence</div>', unsafe_allow_html=True)
    i1, i2 = st.columns(2)
    for idx, insight in enumerate(insights):
        with (i1 if idx % 2 == 0 else i2):
            st.markdown(
                f"""
                <div class="card" style="margin-bottom:1rem;">
                  <div class="insight">
                    <strong>{html.escape(insight['title'])}</strong>
                    <span class="muted">{html.escape(insight['text'])}</span>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown('<div class="section-title">Ask about the weather</div>', unsafe_allow_html=True)

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="chat-user">{html.escape(msg["content"])}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="chat-bot">{html.escape(msg["content"])}</div>',
                unsafe_allow_html=True,
            )

    question = st.chat_input(f"Ask about {weather['location_name']}...")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        answer = answer_weather_question(question, weather)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()

    st.markdown(
        '<div class="footer">Weather data: Open-Meteo · No paid API key required for non-commercial use</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <div class="card" style="margin-top:1.5rem;text-align:center;padding:3rem 1.5rem;">
          <div style="font-size:3rem;">☁️</div>
          <h3 style="font-family:'Manrope',sans-serif;">Search a destination</h3>
          <p class="muted">Get current conditions, a five-day forecast and weather-aware travel guidance.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

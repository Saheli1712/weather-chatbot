# SkyCast — Weather Chatbot

A polished Streamlit weather application using Open-Meteo's no-key weather and geocoding services.

## What it does

- Search any city
- Current weather
- Five-day forecast
- Rain probability
- Humidity
- Wind
- UV index
- Sunrise / sunset
- Weather-aware travel insights
- Simple conversational weather questions
- No paid API key
- Deployable to Streamlit-compatible hosting

## Important data-source note

Open-Meteo provides free weather access without an API key for non-commercial use. Review its current terms and attribution requirements before using the application commercially.

## 1. Create the environment

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 2. Run

```bash
streamlit run app.py
```

Streamlit will show the local URL, normally:

```text
http://localhost:8501
```

## 3. VS Code

Open this folder in VS Code.

Select the interpreter from:

```text
.venv/bin/python
```

on macOS/Linux, or:

```text
.venv\Scripts\python.exe
```

on Windows.

Do not install project packages globally.

## 4. Deploy

Push the complete project to GitHub.

Then create a new Streamlit app and select:

```text
app.py
```

No secret/API key is required for this implementation.

## Architecture

```text
Streamlit UI
    |
    +--> services/weather_service.py
    |       |
    |       +--> Open-Meteo Geocoding
    |       |
    |       +--> Open-Meteo Forecast
    |
    +--> utils/travel.py
            |
            +--> weather-derived travel insights
            +--> conversational weather responses
```

## Design decision

This implementation deliberately uses Streamlit's native rendering plus sanitized HTML/CSS rather than Tailwind. That avoids introducing a Node/Tailwind build pipeline and keeps local and hosted Streamlit deployments using the same code path.

## Limitations

The conversational layer is deterministic rather than LLM-powered. This keeps the application keyless and makes the demo predictable. An LLM can later be added behind the same UI without changing the weather service.

The travel suggestions are weather-derived recommendations, not live attraction recommendations.

Weather accuracy depends on the underlying Open-Meteo forecast models and location resolution.

## Test cities

Try:

- Dubai
- London
- Mumbai
- New York
- Singapore
- Tokyo
- Paris

Also test:

- an empty search
- a nonsense city
- loss of internet connectivity

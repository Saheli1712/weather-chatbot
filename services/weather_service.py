from functools import lru_cache

import requests


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


WEATHER_CODES = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "🌤️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Fog", "🌫️"),
    48: ("Rime fog", "🌫️"),
    51: ("Light drizzle", "🌦️"),
    53: ("Moderate drizzle", "🌦️"),
    55: ("Dense drizzle", "🌧️"),
    56: ("Freezing drizzle", "🌧️"),
    57: ("Dense freezing drizzle", "🌧️"),
    61: ("Slight rain", "🌦️"),
    63: ("Moderate rain", "🌧️"),
    65: ("Heavy rain", "🌧️"),
    66: ("Freezing rain", "🌧️"),
    67: ("Heavy freezing rain", "🌧️"),
    71: ("Slight snow", "🌨️"),
    73: ("Moderate snow", "🌨️"),
    75: ("Heavy snow", "❄️"),
    77: ("Snow grains", "❄️"),
    80: ("Slight rain showers", "🌦️"),
    81: ("Moderate rain showers", "🌧️"),
    82: ("Violent rain showers", "⛈️"),
    85: ("Slight snow showers", "🌨️"),
    86: ("Heavy snow showers", "❄️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm with hail", "⛈️"),
    99: ("Thunderstorm with heavy hail", "⛈️"),
}


def weather_code_to_description(code: int) -> str:
    return WEATHER_CODES.get(int(code), ("Unknown conditions", "🌡️"))[0]


def weather_code_to_icon(code: int) -> str:
    return WEATHER_CODES.get(int(code), ("Unknown conditions", "🌡️"))[1]


@lru_cache(maxsize=128)
def geocode_city(city: str) -> dict:
    response = requests.get(
        GEOCODING_URL,
        params={
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json",
        },
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    results = data.get("results", [])
    if not results:
        raise ValueError(f"I couldn't find a city matching “{city}”. Try a more specific city name.")
    return results[0]


@lru_cache(maxsize=128)
def fetch_forecast(latitude: float, longitude: float, timezone: str) -> dict:
    response = requests.get(
        FORECAST_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone,
            "forecast_days": 5,
            "current": ",".join([
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "weather_code",
                "wind_speed_10m",
            ]),
            "daily": ",".join([
                "weather_code",
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_probability_max",
                "precipitation_sum",
                "uv_index_max",
                "sunrise",
                "sunset",
            ]),
        },
        timeout=12,
    )
    response.raise_for_status()
    return response.json()


def get_weather(city: str) -> dict:
    place = geocode_city(city)
    timezone = place.get("timezone") or "auto"

    data = fetch_forecast(
        float(place["latitude"]),
        float(place["longitude"]),
        timezone,
    )

    current = data.get("current")
    daily = data.get("daily")

    if not current or not daily:
        raise ValueError("The weather service returned incomplete weather data. Please try again.")

    required_daily = [
        "time",
        "weather_code",
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_probability_max",
        "uv_index_max",
        "sunrise",
        "sunset",
    ]
    if any(key not in daily for key in required_daily):
        raise ValueError("The forecast response is missing required weather fields.")

    return {
        "location_name": place.get("name", city.title()),
        "country": place.get("country", ""),
        "timezone": timezone,
        "latitude": place["latitude"],
        "longitude": place["longitude"],
        "current": {
            "temperature": current["temperature_2m"],
            "humidity": current["relative_humidity_2m"],
            "apparent_temperature": current["apparent_temperature"],
            "weather_code": current["weather_code"],
            "wind_speed": current["wind_speed_10m"],
        },
        "daily": {
            "time": daily["time"],
            "weather_code": daily["weather_code"],
            "temperature_2m_max": daily["temperature_2m_max"],
            "temperature_2m_min": daily["temperature_2m_min"],
            "precipitation_probability": daily["precipitation_probability_max"],
            "precipitation_sum": daily["precipitation_sum"],
            "uv_index_max": daily["uv_index_max"],
            "sunrise": daily["sunrise"],
            "sunset": daily["sunset"],
        },
    }

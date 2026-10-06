def build_travel_insights(weather: dict) -> list[dict]:
    current = weather["current"]
    daily = weather["daily"]

    today_temp = current["temperature"]
    rain = daily["precipitation_probability"][0]
    uv = daily["uv_index_max"][0]
    wind = current["wind_speed"]
    code = int(current["weather_code"])

    insights = []

    if rain >= 60:
        insights.append({
            "title": "Carry rain protection",
            "text": f"Rain probability is {rain:.0f}% today. Keep outdoor plans flexible and carry an umbrella or rain jacket.",
        })
    elif rain >= 30:
        insights.append({
            "title": "Keep a backup plan",
            "text": f"There is a {rain:.0f}% chance of precipitation. Outdoor plans are possible, but an indoor alternative is sensible.",
        })
    else:
        insights.append({
            "title": "Outdoor-friendly window",
            "text": f"Rain probability is only {rain:.0f}% today, so outdoor sightseeing is broadly supported by the forecast.",
        })

    if today_temp >= 35:
        insights.append({
            "title": "Avoid peak heat",
            "text": "Temperatures are very high. Favor morning and evening activities and use air-conditioned venues during the hottest hours.",
        })
    elif today_temp >= 30:
        insights.append({
            "title": "Plan around the heat",
            "text": "It is warm today. Morning and late-afternoon sightseeing should be more comfortable than midday.",
        })
    else:
        insights.append({
            "title": "Comfortable temperatures",
            "text": "Current temperatures are relatively moderate, making outdoor sightseeing easier to schedule across the day.",
        })

    if uv >= 8:
        insights.append({
            "title": "High UV",
            "text": f"Maximum UV is forecast around {uv:.1f}. Use sunscreen, shade and appropriate sun protection during midday.",
        })
    elif uv >= 5:
        insights.append({
            "title": "Sun protection",
            "text": f"Maximum UV is around {uv:.1f}. Sun protection is advisable during prolonged outdoor exposure.",
        })
    else:
        insights.append({
            "title": "Lower UV",
            "text": f"Maximum UV is around {uv:.1f}, though normal sun protection is still appropriate outdoors.",
        })

    if wind >= 35:
        insights.append({
            "title": "Wind advisory for activities",
            "text": f"Wind speeds are around {wind:.0f} km/h. Check conditions before boating, kayaking or other wind-sensitive activities.",
        })
    elif code >= 95:
        insights.append({
            "title": "Thunderstorm caution",
            "text": "Thunderstorm conditions are indicated. Avoid exposed outdoor activities and check local alerts before travelling.",
        })
    else:
        insights.append({
            "title": "Activity planning",
            "text": "There is no major weather signal in the current forecast that would automatically rule out normal sightseeing.",
        })

    return insights[:4]


def answer_weather_question(question: str, weather: dict) -> str:
    q = question.lower().strip()
    current = weather["current"]
    daily = weather["daily"]
    city = weather["location_name"]

    if any(word in q for word in ["temperature", "hot", "cold", "degree"]):
        return (
            f"{city} is currently {current['temperature']:.0f}°C, with a feels-like temperature "
            f"of {current['apparent_temperature']:.0f}°C. Today's high is "
            f"{daily['temperature_2m_max'][0]:.0f}°C and low is {daily['temperature_2m_min'][0]:.0f}°C."
        )

    if any(word in q for word in ["rain", "umbrella", "wet"]):
        probability = daily["precipitation_probability"][0]
        return (
            f"Today's maximum precipitation probability is {probability:.0f}%. "
            + (
                "I'd keep an umbrella or rain jacket handy."
                if probability >= 40
                else "Rain does not look like a major constraint for today's plans."
            )
        )

    if any(word in q for word in ["sightseeing", "tour", "outside", "outdoor", "walk"]):
        probability = daily["precipitation_probability"][0]
        if current["temperature"] >= 35:
            return "Sightseeing is more comfortable in the morning or evening because of the high heat. Consider indoor activities around midday."
        if probability >= 60:
            return "Outdoor sightseeing may be interrupted by rain. Schedule flexible outdoor activities around clearer periods and keep an indoor backup."
        return "The current forecast is broadly suitable for sightseeing. Morning and late afternoon are sensible windows, especially if temperatures rise later."

    if any(word in q for word in ["tomorrow", "next day"]):
        return (
            f"Tomorrow's forecast is {weather_code_to_text(daily['weather_code'][1])}, "
            f"with a high around {daily['temperature_2m_max'][1]:.0f}°C, "
            f"a low around {daily['temperature_2m_min'][1]:.0f}°C, and "
            f"a maximum rain probability of {daily['precipitation_probability'][1]:.0f}%."
        )

    if any(word in q for word in ["forecast", "week", "five", "5 day", "5-day"]):
        parts = []
        for i in range(min(5, len(daily["time"]))):
            parts.append(
                f"{daily['time'][i]}: {weather_code_to_text(daily['weather_code'][i])}, "
                f"{daily['temperature_2m_min'][i]:.0f}–{daily['temperature_2m_max'][i]:.0f}°C, "
                f"rain {daily['precipitation_probability'][i]:.0f}%"
            )
        return "Here is the five-day outlook:\n" + "\n".join(parts)

    if any(word in q for word in ["wind", "windy"]):
        return f"Current wind speed is around {current['wind_speed']:.0f} km/h."

    if any(word in q for word in ["humidity", "humid"]):
        return f"Current relative humidity is around {current['humidity']:.0f}%."

    return (
        f"For {city}, it is currently {weather_code_to_text(current['weather_code'])} at "
        f"{current['temperature']:.0f}°C. You can ask me about temperature, rain, wind, "
        f"tomorrow, the five-day forecast, or sightseeing."
    )


def weather_code_to_text(code: int) -> str:
    mapping = {
        0: "clear skies",
        1: "mainly clear skies",
        2: "partly cloudy skies",
        3: "overcast skies",
        45: "fog",
        48: "rime fog",
        51: "light drizzle",
        53: "moderate drizzle",
        55: "dense drizzle",
        61: "light rain",
        63: "moderate rain",
        65: "heavy rain",
        80: "light rain showers",
        81: "moderate rain showers",
        82: "heavy rain showers",
        95: "thunderstorms",
        96: "thunderstorms with hail",
        99: "thunderstorms with heavy hail",
    }
    return mapping.get(int(code), "variable conditions")

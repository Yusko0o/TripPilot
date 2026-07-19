from datetime import datetime

import requests


class WeatherProviderError(RuntimeError):
    pass


CONDITIONS = {
    0: ("Ciel dégagé", "Clear sky"),
    1: ("Principalement dégagé", "Mainly clear"),
    2: ("Partiellement nuageux", "Partly cloudy"),
    3: ("Couvert", "Overcast"),
    45: ("Brouillard", "Fog"),
    48: ("Brouillard givrant", "Rime fog"),
    51: ("Bruine légère", "Light drizzle"),
    53: ("Bruine", "Drizzle"),
    55: ("Forte bruine", "Heavy drizzle"),
    61: ("Pluie légère", "Light rain"),
    63: ("Pluie", "Rain"),
    65: ("Forte pluie", "Heavy rain"),
    71: ("Neige légère", "Light snow"),
    73: ("Neige", "Snow"),
    75: ("Forte neige", "Heavy snow"),
    80: ("Averses légères", "Light showers"),
    81: ("Averses", "Showers"),
    82: ("Fortes averses", "Heavy showers"),
    95: ("Orage", "Thunderstorm"),
    96: ("Orage avec grêle", "Thunderstorm with hail"),
    99: ("Fort orage avec grêle", "Heavy thunderstorm with hail"),
}


class OpenMeteoWeatherProvider:
    endpoint = "https://api.open-meteo.com/v1/forecast"

    def get_weather(self, latitude, longitude, language="fr"):
        try:
            response = requests.get(
                self.endpoint,
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
                    "daily": "weather_code,temperature_2m_max,temperature_2m_min",
                    "forecast_days": 7,
                    "timezone": "auto",
                },
                timeout=12,
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as error:
            raise WeatherProviderError("La météo en temps réel est momentanément indisponible.") from error

        current = payload.get("current") or {}
        daily = payload.get("daily") or {}
        locale_index = 1 if language == "en" else 0
        code = int(current.get("weather_code", 0))
        dates = daily.get("time", [])
        maximums = daily.get("temperature_2m_max", [])
        weather_codes = daily.get("weather_code", [])
        forecast = []
        for index, day in enumerate(dates[:5]):
            day_code = int(weather_codes[index]) if index < len(weather_codes) else 0
            forecast.append(
                {
                    "day": datetime.fromisoformat(day).strftime("%a"),
                    "temperature": round(maximums[index]) if index < len(maximums) else None,
                    "condition": CONDITIONS.get(day_code, CONDITIONS[0])[locale_index],
                }
            )
        return {
            "temperature": round(float(current.get("temperature_2m", 0))),
            "condition": CONDITIONS.get(code, CONDITIONS[0])[locale_index],
            "humidity": round(float(current.get("relative_humidity_2m", 0))),
            "wind": round(float(current.get("wind_speed_10m", 0))),
            "observedAt": current.get("time"),
            "forecast": forecast,
            "source": "Open-Meteo",
            "live": True,
        }


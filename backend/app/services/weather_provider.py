from datetime import datetime

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


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

MET_CONDITIONS = {
    "clearsky": ("Ciel dégagé", "Clear sky"),
    "fair": ("Peu nuageux", "Fair"),
    "partlycloudy": ("Partiellement nuageux", "Partly cloudy"),
    "cloudy": ("Couvert", "Cloudy"),
    "fog": ("Brouillard", "Fog"),
    "lightrain": ("Pluie légère", "Light rain"),
    "rain": ("Pluie", "Rain"),
    "heavyrain": ("Forte pluie", "Heavy rain"),
    "lightsnow": ("Neige légère", "Light snow"),
    "snow": ("Neige", "Snow"),
    "heavysnow": ("Forte neige", "Heavy snow"),
    "rainshowers": ("Averses", "Rain showers"),
    "snowshowers": ("Averses de neige", "Snow showers"),
    "sleet": ("Neige fondue", "Sleet"),
    "thunderstorm": ("Orage", "Thunderstorm"),
}


def met_condition(symbol, language):
    normalized = str(symbol or "cloudy").replace("_day", "").replace("_night", "")
    normalized = normalized.replace("andthunder", "")
    locale_index = 1 if language == "en" else 0
    for key, labels in MET_CONDITIONS.items():
        if key in normalized:
            return labels[locale_index]
    return MET_CONDITIONS["cloudy"][locale_index]


def retry_session():
    retry_policy = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=0.4,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
    )
    session = requests.Session()
    session.headers.update(
        {
            "Accept": "application/json",
            "User-Agent": "TripPilot/1.2 (+https://github.com/Yusko0o/TripPilot)",
        }
    )
    session.mount("https://", HTTPAdapter(max_retries=retry_policy))
    return session


class OpenMeteoWeatherProvider:
    endpoint = "https://api.open-meteo.com/v1/forecast"

    def __init__(self):
        self.session = retry_session()

    def get_weather(self, latitude, longitude, language="fr"):
        try:
            response = self.session.get(
                self.endpoint,
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
                    "daily": "weather_code,temperature_2m_max,temperature_2m_min",
                    "forecast_days": 7,
                    "timezone": "auto",
                },
                timeout=(5, 15),
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as error:
            raise WeatherProviderError("La météo en temps réel est momentanément indisponible.") from error

        current = payload.get("current") or {}
        daily = payload.get("daily") or {}
        if current.get("temperature_2m") is None or current.get("weather_code") is None:
            raise WeatherProviderError("La météo en temps réel a renvoyé une réponse incomplète.")
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


class MetNoWeatherProvider:
    endpoint = "https://api.met.no/weatherapi/locationforecast/2.0/compact"

    def __init__(self):
        self.session = retry_session()

    def get_weather(self, latitude, longitude, language="fr"):
        try:
            response = self.session.get(
                self.endpoint,
                params={"lat": round(float(latitude), 4), "lon": round(float(longitude), 4)},
                timeout=(5, 15),
            )
            response.raise_for_status()
            timeseries = response.json()["properties"]["timeseries"]
            current_item = timeseries[0]
            current = current_item["data"]["instant"]["details"]
        except (requests.RequestException, ValueError, KeyError, IndexError, TypeError) as error:
            raise WeatherProviderError("Le fournisseur météo de secours est indisponible.") from error

        summary = current_item["data"].get("next_1_hours", {}).get("summary", {})
        symbol = summary.get("symbol_code", "cloudy")
        daily = {}
        for item in timeseries:
            day = item.get("time", "")[:10]
            details = item.get("data", {}).get("instant", {}).get("details", {})
            temperature = details.get("air_temperature")
            if not day or temperature is None:
                continue
            entry = daily.setdefault(day, {"temperatures": [], "symbol": None})
            entry["temperatures"].append(float(temperature))
            item_summary = item.get("data", {}).get("next_6_hours", {}).get("summary", {})
            if item_summary.get("symbol_code"):
                entry["symbol"] = item_summary["symbol_code"]

        forecast = []
        for day, values in list(daily.items())[:5]:
            forecast.append(
                {
                    "day": datetime.fromisoformat(day).strftime("%a"),
                    "temperature": round(max(values["temperatures"])),
                    "condition": met_condition(values["symbol"], language),
                }
            )

        return {
            "temperature": round(float(current["air_temperature"])),
            "condition": met_condition(symbol, language),
            "humidity": round(float(current.get("relative_humidity", 0))),
            "wind": round(float(current.get("wind_speed", 0)) * 3.6),
            "observedAt": current_item.get("time"),
            "forecast": forecast,
            "source": "MET Norway",
            "live": True,
        }


class FallbackWeatherProvider:
    def __init__(self, primary=None, fallback=None):
        self.primary = primary or OpenMeteoWeatherProvider()
        self.fallback = fallback or MetNoWeatherProvider()

    def get_weather(self, latitude, longitude, language="fr"):
        try:
            return self.primary.get_weather(latitude, longitude, language)
        except WeatherProviderError:
            return self.fallback.get_weather(latitude, longitude, language)

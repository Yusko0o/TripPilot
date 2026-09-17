from datetime import date
from urllib.parse import quote_plus

from flask import Blueprint, jsonify, request

from ..services.airport_provider import AirportProvider
from ..services.demo_provider import DemoTravelProvider
from ..services.nearest_airport import nearest_airport as find_nearest_airport
from ..services.weather_provider import OpenMeteoWeatherProvider, WeatherProviderError

travel_bp = Blueprint("travel", __name__)
content_provider = DemoTravelProvider()
weather_provider = OpenMeteoWeatherProvider()
airports = AirportProvider()

AIRLINE_LINKS = (
    {
        "provider": "Luxair",
        "code": "LG",
        "websiteUrl": "https://www.luxair.lu/",
    },
    {
        "provider": "Air France",
        "code": "AF",
        "websiteUrl": "https://www.airfrance.com/",
    },
    {
        "provider": "Ryanair",
        "code": "FR",
        "websiteUrl": "https://www.ryanair.com/",
    },
)


@travel_bp.get("/airports/search")
def search_airports():
    query = request.args.get("q", "").strip()
    if len(query) < 2:
        return {"airports": []}
    if len(query) > 80:
        return jsonify({"error": "La recherche est trop longue."}), 400
    return {"airports": airports.search(query)}


@travel_bp.get("/flights/search")
def search_flights():
    origin_query = request.args.get("origin", "LUX").strip()
    destination_query = request.args.get("destination", "").strip()
    departure_date = request.args.get("date", date.today().isoformat()).strip()
    try:
        adults = int(request.args.get("adults", "1"))
    except ValueError:
        adults = 0

    origin = airports.resolve(origin_query)
    destination = airports.resolve(destination_query)
    if not origin or not destination:
        return jsonify({"error": "Sélectionne un aéroport valide dans les suggestions."}), 400
    try:
        parsed_date = date.fromisoformat(departure_date)
    except ValueError:
        return jsonify({"error": "La date doit être au format AAAA-MM-JJ."}), 400
    if parsed_date < date.today():
        return jsonify({"error": "La date de départ ne peut pas être dans le passé."}), 400
    if not 1 <= adults <= 9:
        return jsonify({"error": "Le nombre de voyageurs doit être compris entre 1 et 9."}), 400

    links = [
        {
            **airline,
            "origin": origin["code"],
            "destination": destination["code"],
            "departureDate": departure_date,
            "adults": adults,
        }
        for airline in AIRLINE_LINKS
    ]
    google_query = quote_plus(
        f"Flights from {origin['code']} to {destination['code']} "
        f"on {departure_date} for {adults} adult{'s' if adults > 1 else ''}"
    )
    links.insert(
        0,
        {
            "provider": "Google Flights",
            "code": "GF",
            "websiteUrl": f"https://www.google.com/travel/flights?q={google_query}",
            "origin": origin["code"],
            "destination": destination["code"],
            "departureDate": departure_date,
            "adults": adults,
        },
    )
    return {
        "flights": [],
        "airlineLinks": links,
        "search": {
            "origin": airports.public(origin),
            "destination": airports.public(destination),
        },
        "dataMode": "external_redirect",
    }


@travel_bp.get("/destinations/<string:code>")
def destination_details(code):
    language = request.args.get("lang", "fr").lower()
    if language not in {"fr", "en"}:
        language = "fr"
    airport = airports.resolve(code)
    details = (
        content_provider.destination_details(airport["code"], airport, language)
        if airport
        else None
    )
    if not details:
        return jsonify({"error": "Cette destination n'est pas disponible."}), 404
    try:
        details["weather"] = weather_provider.get_weather(
            airport["latitude"], airport["longitude"], language
        )
        details["dataMode"]["weather"] = "live"
    except WeatherProviderError:
        details["weather"] = {
            "available": False,
            "live": False,
            "source": "Open-Meteo",
        }
        details["dataMode"]["weather"] = "temporarily_unavailable"
    return details


@travel_bp.post("/location/nearest-airport")
def nearest_airport():
    data = request.get_json(silent=True) or {}
    if data.get("consent") is not True:
        return jsonify({"error": "Ton autorisation est nécessaire."}), 400
    try:
        latitude = float(data["latitude"])
        longitude = float(data["longitude"])
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "Coordonnées invalides."}), 400
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        return jsonify({"error": "Coordonnées invalides."}), 400

    airport = find_nearest_airport(latitude, longitude)
    if airport is None:
        return jsonify({"error": "Aucun aéroport n'a été trouvé."}), 404
    return {
        "airport": airport,
        "privacy": {
            "storedByServer": False,
            "source": "browser_permission",
        },
    }

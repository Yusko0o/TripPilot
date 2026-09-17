from datetime import date, timedelta

import pytest

from app import create_app
from app.extensions import db
from app.routes.travel import weather_provider

FUTURE_DATE = (date.today() + timedelta(days=30)).isoformat()


@pytest.fixture(autouse=True)
def mock_weather_provider(monkeypatch):
    monkeypatch.setattr(
        weather_provider,
        "get_weather",
        lambda latitude, longitude, language="fr": {
            "temperature": 22,
            "condition": "Clear sky" if language == "en" else "Ciel dégagé",
            "humidity": 55,
            "wind": 10,
            "observedAt": "2026-07-19T20:00",
            "forecast": [],
            "source": "Open-Meteo",
            "live": True,
        },
    )


@pytest.fixture()
def client(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'test.db'}",
            "WTF_CSRF_ENABLED": False,
        }
    )
    with app.app_context():
        db.create_all()
    return app.test_client()


def test_health(client):
    assert client.get("/api/health").get_json()["status"] == "ok"


def test_register_login_and_favorite(client):
    response = client.post(
        "/api/auth/register",
        json={
            "username": "Kilian",
            "email": "kilian@example.com",
            "password": "Voyage2026!",
        },
    )
    assert response.status_code == 201
    favorite = client.post(
        "/api/favorites/destinations",
        json={"city": "Paris", "country": "France"},
    )
    assert favorite.status_code == 201
    assert client.get("/api/favorites").get_json()["destinations"][0]["city"] == "Paris"


def test_invalid_registration_and_protected_route(client):
    assert client.get("/api/favorites").status_code == 401
    response = client.post(
        "/api/auth/register",
        json={"username": "A", "email": "bad", "password": "short"},
    )
    assert response.status_code == 400


def test_external_airline_search_and_destination(client):
    response = client.get(
        f"/api/flights/search?origin=LUX&destination=CDG&date={FUTURE_DATE}"
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["flights"] == []
    assert payload["dataMode"] == "external_redirect"
    assert {item["code"] for item in payload["airlineLinks"]} == {"GF", "LG", "AF", "FR"}
    assert "LUX" in payload["airlineLinks"][0]["websiteUrl"]
    assert FUTURE_DATE in payload["airlineLinks"][0]["websiteUrl"]

    destination = client.get("/api/destinations/CDG").get_json()
    assert destination["weather"]["live"] is True
    assert len(destination["hotels"]) == 10
    assert len(destination["activities"]) == 5


def test_airport_autocomplete_and_city_resolution(client):
    suggestions = client.get("/api/airports/search?q=nyc").get_json()["airports"]
    assert {airport["code"] for airport in suggestions} >= {"JFK", "LGA"}
    suggestions = client.get("/api/airports/search?q=new%20y").get_json()["airports"]
    assert any(airport["city"] == "New York" for airport in suggestions)
    response = client.get(
        f"/api/flights/search?origin=Luxembourg&destination=Paris&date={FUTURE_DATE}"
    )
    assert response.status_code == 200
    assert response.get_json()["search"]["destination"]["code"] == "CDG"
    assert response.get_json()["search"]["destination"]["city"] == "Paris"


def test_english_destination_content(client):
    destination = client.get("/api/destinations/LIS?lang=en").get_json()
    assert destination["destination"]["city"] == "Lisbon"
    assert destination["activities"][0]["name"].startswith("Guided tour")
    assert destination["weather"]["condition"] == "Clear sky"


def test_destination_still_loads_when_weather_provider_is_down(client, monkeypatch):
    from app.services.weather_provider import WeatherProviderError

    def unavailable(*_args, **_kwargs):
        raise WeatherProviderError("provider down")

    monkeypatch.setattr(weather_provider, "get_weather", unavailable)
    response = client.get("/api/destinations/CDG")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["destination"]["city"] == "Paris"
    assert payload["weather"]["available"] is False
    assert payload["dataMode"]["weather"] == "temporarily_unavailable"


def test_flight_search_does_not_expose_internal_search_fields(client):
    response = client.get(
        f"/api/flights/search?origin=LUX&destination=CDG&date={FUTURE_DATE}"
    )
    destination = response.get_json()["search"]["destination"]
    assert set(destination) == {
        "code", "name", "city", "country", "latitude", "longitude"
    }


def test_nearest_airport_uses_browser_coordinates_without_storage(client):
    assert client.post("/api/location/nearest-airport", json={}).status_code == 400
    response = client.post(
        "/api/location/nearest-airport",
        json={"consent": True, "latitude": 49.6116, "longitude": 6.1319},
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["airport"]["code"] == "LUX"
    assert payload["privacy"]["storedByServer"] is False

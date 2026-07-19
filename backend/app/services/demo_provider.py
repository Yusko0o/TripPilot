from urllib.parse import quote_plus


DESTINATIONS = {
    "CDG": {
        "city": "Paris",
        "country": "France",
        "temperature": 22,
        "condition": "Éclaircies",
        "image": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=1600&q=80",
    },
    "ORY": {
        "city": "Paris",
        "country": "France",
        "temperature": 22,
        "condition": "Éclaircies",
        "image": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=1600&q=80",
    },
    "NCE": {
        "city": "Nice",
        "country": "France",
        "temperature": 27,
        "condition": "Ensoleillé",
        "image": "https://images.unsplash.com/photo-1533614767277-723c06e66954?auto=format&fit=crop&w=1600&q=80",
    },
    "LIS": {
        "city": "Lisbonne",
        "country": "Portugal",
        "temperature": 26,
        "condition": "Ensoleillé",
        "image": "https://images.unsplash.com/photo-1555881400-74d7acaacd8b?auto=format&fit=crop&w=1600&q=80",
    },
    "FCO": {
        "city": "Rome",
        "country": "Italie",
        "temperature": 29,
        "condition": "Grand soleil",
        "image": "https://images.unsplash.com/photo-1552832230-c0197dd311b5?auto=format&fit=crop&w=1600&q=80",
    },
    "BCN": {
        "city": "Barcelone",
        "country": "Espagne",
        "temperature": 28,
        "condition": "Peu nuageux",
        "image": "https://images.unsplash.com/photo-1539037116277-4db20889f2d4?auto=format&fit=crop&w=1600&q=80",
    },
}


class DemoTravelProvider:
    def destination_details(self, code, airport=None, language="fr"):
        destination = DESTINATIONS.get(code)
        if destination is None and airport:
            temperature = 17 + sum(ord(character) for character in code) % 13
            destination = {
                "city": airport.get("city") or airport.get("name") or code,
                "country": airport.get("country") or "",
                "temperature": temperature,
                "condition": "Partiellement nuageux",
                "image": "https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=1600&q=80",
            }
        if not destination:
            return None

        destination = dict(destination)
        if language == "en":
            english_cities = {"CDG": "Paris", "ORY": "Paris", "NCE": "Nice", "LIS": "Lisbon", "FCO": "Rome", "BCN": "Barcelona"}
            destination["city"] = english_cities.get(code, destination["city"])
            conditions = {"Éclaircies": "Sunny spells", "Ensoleillé": "Sunny", "Grand soleil": "Sunny", "Peu nuageux": "Partly cloudy", "Partiellement nuageux": "Partly cloudy"}
            destination["condition"] = conditions.get(destination["condition"], destination["condition"])

        city = destination["city"]
        hotel_names = [
            "Grand Central", "Maison Élégance", "The Riverside", "Horizon Suites",
            "Jardin Secret", "Urban Nest", "Bellevue", "Le Voyageur",
            "Palais Lumière", "City Garden",
        ]
        hotels = [
            {
                "id": index + 1,
                "name": f"{name} {city}",
                "rating": round(4.9 - index * 0.07, 1),
                "price": 95 + index * 17,
                "currency": "EUR",
                "websiteUrl": f"https://www.booking.com/searchresults.html?ss={quote_plus(f'{name} {city}')}",
            }
            for index, name in enumerate(hotel_names)
        ]
        if language == "en":
            activity_data = [
                (f"Guided tour of central {city}", "2 hr", "Culture"),
                ("Local food discovery tour", "3 hr", "Food"),
                ("Panoramic sunset walk", "2 hr 30", "Nature"),
                ("Must-see museum and heritage tour", "2 hr", "History"),
                ("Authentic markets and neighborhoods", "3 hr", "Local"),
            ]
        else:
            activity_data = [
                (f"Visite guidée du centre de {city}", "2 h", "Culture"),
                ("Découverte gastronomique locale", "3 h", "Gastronomie"),
                ("Balade panoramique au coucher du soleil", "2 h 30", "Nature"),
                ("Musée et patrimoine incontournable", "2 h", "Histoire"),
                ("Marché et quartiers authentiques", "3 h", "Local"),
            ]
        activities = [
            {
                "name": name,
                "duration": duration,
                "category": category,
                "websiteUrl": f"https://www.getyourguide.com/s/?q={quote_plus(f'{name} {city}')}",
            }
            for name, duration, category in activity_data
        ]
        return {
            "destination": {"code": code, **destination},
            "hotels": hotels,
            "activities": activities,
            "dataMode": {"hotels": "demo", "activities": "demo"},
        }

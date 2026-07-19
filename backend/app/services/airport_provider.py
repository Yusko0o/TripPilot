import re
import unicodedata
from functools import lru_cache

import airportsdata


METRO_ALIASES = {
    "nyc": "new york",
    "lon": "london",
    "par": "paris",
    "tyo": "tokyo",
    "rom": "rome",
    "mil": "milan",
    "was": "washington",
    "chi": "chicago",
    "sel": "seoul",
    "bjs": "beijing",
    "sao": "sao paulo",
    "bue": "buenos aires",
    "mow": "moscow",
    "osa": "osaka",
    "rio": "rio de janeiro",
    "sto": "stockholm",
}


def normalize(value):
    value = unicodedata.normalize("NFKD", str(value or ""))
    value = "".join(character for character in value if not unicodedata.combining(character))
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


@lru_cache(maxsize=1)
def airport_index():
    records = []
    for airport in airportsdata.load("IATA").values():
        if not airport.get("iata") or not airport.get("name"):
            continue
        item = {
            "code": airport["iata"],
            "name": airport["name"],
            "city": airport.get("city") or airport.get("subd") or "",
            "country": airport.get("country") or "",
            "latitude": airport.get("lat"),
            "longitude": airport.get("lon"),
        }
        item["search"] = normalize(
            f"{item['code']} {item['city']} {item['name']} {airport.get('subd', '')} {item['country']}"
        )
        item["city_search"] = normalize(item["city"])
        item["name_search"] = normalize(item["name"])
        records.append(item)
    return records


class AirportProvider:
    def search(self, query, limit=8):
        raw_query = normalize(query)[:80]
        if len(raw_query) < 2:
            return []
        expanded_query = METRO_ALIASES.get(raw_query, raw_query)
        query_code = raw_query.upper()
        matches = []

        for item in airport_index():
            code = item["code"]
            if code == query_code:
                score = 0
            elif code.startswith(query_code):
                score = 1
            elif item["city_search"] == expanded_query:
                score = 2
            elif item["city_search"].startswith(expanded_query):
                score = 3
            elif item["name_search"].startswith(expanded_query):
                score = 4
            elif expanded_query in item["search"]:
                score = 5
            else:
                continue
            matches.append((score, len(item["name"]), item))

        matches.sort(key=lambda match: (match[0], match[1], match[2]["code"]))
        return [
            {key: value for key, value in item.items() if not key.endswith("search")}
            for _score, _length, item in matches[:limit]
        ]

    def resolve(self, value):
        value = str(value or "").strip()
        if not value:
            return None
        direct_code = value.upper()
        for item in airport_index():
            if item["code"] == direct_code:
                return item
        results = self.search(value, limit=1)
        return results[0] if results else None


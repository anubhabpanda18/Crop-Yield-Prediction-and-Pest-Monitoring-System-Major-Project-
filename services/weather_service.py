import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from config import Config

WORLD_CITIES = {
    "India": [
        "Mumbai", "Delhi", "Kolkata", "Chennai", "Bangalore",
        "Hyderabad", "Ahmedabad", "Pune", "Jaipur", "Lucknow",
        "Bhopal", "Patna", "Bhubaneswar", "Guwahati", "Chandigarh"
    ],
    "Asia": [
        "Tokyo", "Beijing", "Shanghai", "Seoul", "Bangkok",
        "Singapore", "Kuala Lumpur", "Jakarta", "Manila", "Karachi",
        "Dhaka", "Colombo", "Kathmandu", "Islamabad", "Yangon"
    ],
    "Europe": [
        "London", "Paris", "Berlin", "Madrid", "Rome",
        "Amsterdam", "Vienna", "Stockholm", "Oslo", "Zurich",
        "Brussels", "Warsaw", "Prague", "Budapest", "Athens"
    ],
    "Americas": [
        "New York", "Los Angeles", "Chicago", "Toronto", "Vancouver",
        "Mexico City", "Sao Paulo", "Buenos Aires", "Lima", "Bogota",
        "Santiago", "Miami", "Houston", "Montreal", "Havana"
    ],
    "Middle East & Africa": [
        "Dubai", "Riyadh", "Tehran", "Istanbul", "Cairo",
        "Lagos", "Nairobi", "Johannesburg", "Casablanca", "Addis Ababa",
        "Accra", "Dakar", "Khartoum", "Beirut", "Baghdad"
    ],
    "Oceania": [
        "Sydney", "Melbourne", "Brisbane", "Auckland", "Perth"
    ]
}


class WeatherService:
    BASE_URL = "https://api.openweathermap.org/data/2.5"

    def get_current(self, city: str) -> dict:
        try:
            r = requests.get(
                f"{self.BASE_URL}/weather",
                params={
                    "q": city,
                    "appid": Config.OPENWEATHER_API_KEY,
                    "units": "metric"
                },
                timeout=8
            )
            r.raise_for_status()
            d = r.json()
            return {
                "city":        d["name"],
                "country":     d["sys"]["country"],
                "temperature": round(d["main"]["temp"], 1),
                "feels_like":  round(d["main"]["feels_like"], 1),
                "humidity":    d["main"]["humidity"],
                "pressure":    d["main"]["pressure"],
                "rainfall_mm": round(d.get("rain", {}).get("1h", 0) * 24, 1),
                "wind_speed":  d["wind"]["speed"],
                "wind_deg":    d["wind"].get("deg", 0),
                "description": d["weather"][0]["description"].title(),
                "icon":        d["weather"][0]["icon"],
                "icon_url":    f"https://openweathermap.org/img/wn/{d['weather'][0]['icon']}@2x.png",
                "visibility":  d.get("visibility", 0) // 1000,
                "clouds":      d["clouds"]["all"],
                "lat":         d["coord"]["lat"],
                "lon":         d["coord"]["lon"],
                "source":      "live"
            }
        except requests.exceptions.HTTPError as e:
            if r.status_code == 401:
                return {"error": "Invalid API key", "city": city, "source": "error"}
            if r.status_code == 404:
                return {"error": f"City '{city}' not found", "city": city, "source": "error"}
            return self._simulated(city)
        except Exception:
            return self._simulated(city)

    def get_forecast(self, city: str, days: int = 5) -> list:
        try:
            r = requests.get(
                f"{self.BASE_URL}/forecast",
                params={
                    "q": city,
                    "appid": Config.OPENWEATHER_API_KEY,
                    "units": "metric",
                    "cnt": days * 8
                },
                timeout=8
            )
            r.raise_for_status()
            items = r.json()["list"]
            seen, result = set(), []
            for item in items:
                date = item["dt_txt"].split(" ")[0]
                if date not in seen:
                    seen.add(date)
                    result.append({
                        "date":        date,
                        "temperature": round(item["main"]["temp"], 1),
                        "temp_min":    round(item["main"]["temp_min"], 1),
                        "temp_max":    round(item["main"]["temp_max"], 1),
                        "humidity":    item["main"]["humidity"],
                        "rainfall_mm": round(item.get("rain", {}).get("3h", 0), 1),
                        "wind_speed":  item["wind"]["speed"],
                        "description": item["weather"][0]["description"].title(),
                        "icon":        item["weather"][0]["icon"],
                        "icon_url":    f"https://openweathermap.org/img/wn/{item['weather'][0]['icon']}@2x.png"
                    })
            return result[:days]
        except Exception:
            return []

    def get_cities_by_region(self, region: str) -> list:
        cities = WORLD_CITIES.get(region, [])
        results = []
        for city in cities:
            data = self.get_current(city)
            if data.get("source") != "error":
                results.append(data)
        return results

    def _simulated(self, city: str) -> dict:
        return {
            "city":        city,
            "country":     "N/A",
            "temperature": 27.4,
            "feels_like":  29.1,
            "humidity":    71,
            "pressure":    1012,
            "rainfall_mm": 3.8,
            "wind_speed":  4.2,
            "wind_deg":    180,
            "description": "Partly Cloudy (Simulated)",
            "icon":        "02d",
            "icon_url":    "https://openweathermap.org/img/wn/02d@2x.png",
            "visibility":  10,
            "clouds":      40,
            "lat":         0,
            "lon":         0,
            "source":      "simulated"
        }


weather_service = WeatherService()
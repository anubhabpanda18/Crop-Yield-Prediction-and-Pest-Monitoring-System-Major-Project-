import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from flask import Blueprint, request, jsonify
from services.weather_service import weather_service, WORLD_CITIES
from utils.helpers import ok

monitor_bp = Blueprint("monitor", __name__, url_prefix="/api/monitor")


# ── Region route MUST come BEFORE single city route ──────────────────────────
@monitor_bp.route("/weather/region/<path:region>", methods=["GET"])
def weather_by_region(region):
    data = weather_service.get_cities_by_region(region)
    return jsonify(ok({"region": region, "count": len(data), "cities": data}))


@monitor_bp.route("/weather/<city>", methods=["GET"])
def get_weather(city):
    current  = weather_service.get_current(city)
    forecast = weather_service.get_forecast(city)
    return jsonify(ok({"current": current, "forecast": forecast}))
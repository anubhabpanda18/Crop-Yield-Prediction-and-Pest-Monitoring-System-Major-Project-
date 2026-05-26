import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from flask import Blueprint, request, jsonify
from models.crop_model import crop_model
from models.schemas import YieldInput, PestInput
from services.soil_service import soil_service
from utils.helpers import ok, err, profit_estimate

predict_bp = Blueprint("predict", __name__, url_prefix="/api/predict")


@predict_bp.route("/yield", methods=["POST"])
def predict_yield():
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"status": "error", "message": "No JSON body"}), 400
    try:
        inp = YieldInput(
            crop=body.get("crop", "rice"),
            N=float(body.get("N", 0)),
            P=float(body.get("P", 0)),
            K=float(body.get("K", 0)),
            temperature=float(body.get("temperature", 25)),
            humidity=float(body.get("humidity", 70)),
            ph=float(body.get("ph", 6.5)),
            rainfall=float(body.get("rainfall", 100)),
            area=float(body.get("area", 1)),
            season=body.get("season", "Kharif")
        )
        result = crop_model.predict_yield(vars(inp))
        result["profit_estimate"] = profit_estimate(
            result["total_estimated_yield_kg"], inp.area, inp.crop,
            body.get("price_per_kg"))
        result["soil_analysis"] = soil_service.analyze(inp.N, inp.P, inp.K, inp.ph)
        return jsonify(ok(result, "Yield prediction successful"))
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@predict_bp.route("/pest", methods=["POST"])
def predict_pest():
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"status": "error", "message": "No JSON body"}), 400
    try:
        inp = PestInput(
            crop=body.get("crop", "rice"),
            temperature=float(body.get("temperature", 25)),
            humidity=float(body.get("humidity", 70)),
            rainfall=float(body.get("rainfall", 50)),
            wind_speed=float(body.get("wind_speed", 5)),
            crop_age_days=int(body.get("crop_age_days", 30)),
            previous_infestation=int(body.get("previous_infestation", 0))
        )
        result = crop_model.predict_pest_risk(vars(inp))
        return jsonify(ok(result, "Pest risk prediction successful"))
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@predict_bp.route("/train", methods=["POST"])
def train():
    try:
        metrics = crop_model.train()
        return jsonify(ok(metrics, "All models trained successfully"))
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
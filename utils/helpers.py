from datetime import datetime


def ok(data: dict, message: str = "Success") -> dict:
    return {
        "status":    "success",
        "message":   message,
        "data":      data,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


def err(message: str, code: int = 400):
    return {
        "status":    "error",
        "message":   message,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }, code


GROWTH_ADVICE = {
    "germination": [
        "Keep soil moist but not waterlogged.",
        "Maintain soil temperature between 20-30°C.",
        "Protect seeds from birds and rodents."
    ],
    "vegetative": [
        "Apply top-dressing Nitrogen fertilizer now.",
        "Irrigate every 5-7 days based on rainfall.",
        "Scout weekly for pest eggs and early damage."
    ],
    "flowering": [
        "Avoid water stress — critical pollination period.",
        "Spray Boron micronutrient if symptoms appear.",
        "Reduce pesticide use to protect pollinators."
    ],
    "maturity": [
        "Reduce irrigation frequency gradually.",
        "Watch for fungal diseases in humid conditions.",
        "Plan harvest timing based on grain moisture content."
    ]
}


def growth_advice(stage: str) -> list:
    stage = stage.lower()
    for key in GROWTH_ADVICE:
        if key in stage:
            return GROWTH_ADVICE[key]
    return ["No specific advice available for this growth stage."]


CROP_PRICES_INR = {
    "rice": 21, "wheat": 22, "maize": 18, "sugarcane": 3.5,
    "cotton": 65, "groundnut": 55, "jute": 40, "coffee": 380,
    "banana": 25, "mango": 50, "grapes": 80, "default": 28
}

COST_PER_HA_INR = 38000


def profit_estimate(yield_kg: float, area_ha: float, crop: str,
                    price_per_kg: float = None) -> dict:
    price   = price_per_kg or CROP_PRICES_INR.get(crop.lower(), CROP_PRICES_INR["default"])
    revenue = yield_kg * price
    cost    = area_ha * COST_PER_HA_INR
    profit  = revenue - cost
    return {
        "price_per_kg_inr":       price,
        "gross_revenue_inr":      round(revenue, 2),
        "estimated_cost_inr":     round(cost, 2),
        "net_profit_inr":         round(profit, 2),
        "profit_per_hectare_inr": round(profit / area_ha if area_ha else 0, 2),
        "profitable":             profit > 0
    }
import os
class Config:
    DEBUG = os.getenv("DEBUG", "True") == "True"
    SECRET_KEY = os.getenv("SECRET_KEY", "crop-yield-pest-monitor-key")
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
    MODEL_PATH      = "models/saved/yield_model.pkl"
    SCALER_PATH     = "models/saved/scaler.pkl"
    ENCODER_PATH    = "models/saved/label_encoder.pkl"
    PEST_MODEL_PATH = "models/saved/pest_model.pkl"

    CROPS = [
        "rice", "wheat", "maize", "sugarcane", "cotton",
        "groundnut", "jute", "coffee", "chickpea", "kidneybeans",
        "pigeonpeas", "mothbeans", "mungbean", "blackgram",
        "lentil", "pomegranate", "banana", "mango", "grapes",
        "watermelon", "muskmelon", "apple", "orange", "papaya", "coconut"
    ]

    SEASONS = ["Kharif", "Rabi", "Zaid", "Whole Year"]

    YIELD_FEATURES = [
        "N", "P", "K", "temperature",
        "humidity", "ph", "rainfall",
        "area", "season_encoded"
    ]

    PEST_FEATURES = [
        "temperature", "humidity", "rainfall",
        "wind_speed", "crop_age_days", "previous_infestation"
    ]

    # Common pests per crop category
    PEST_MAP = {
        "rice":     ["Brown Planthopper", "Stem Borer", "Leaf Folder", "Blast Fungus"],
        "wheat":    ["Aphid", "Rust", "Termite", "Army Worm"],
        "maize":    ["Fall Army Worm", "Stem Borer", "Aphid", "Smut"],
        "cotton":   ["Bollworm", "Whitefly", "Thrips", "Jassid"],
        "default":  ["Aphid", "Whitefly", "Mites", "Fungal Blight"]
    }
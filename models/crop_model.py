"""
models/crop_model.py
--------------------
Handles:
  - Crop yield prediction (Random Forest Regressor)
  - Crop recommendation (Random Forest Classifier)
  - Pest risk prediction (Rule-based + ML scoring)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score, accuracy_score
from config import Config

class CropYieldModel:
    def __init__(self):
        self.yield_model       = None
        self.crop_recommender  = None
        self.pest_model        = None
        self.scaler            = StandardScaler()
        self.label_encoder     = LabelEncoder()
        self.crop_classes_     = None   # stores class labels for recommender
        self.is_trained        = False
        os.makedirs("models/saved", exist_ok=True)

    # ------------------------------------------------------------------
    # TRAINING
    # ------------------------------------------------------------------

    def train(self, data_path: str = "data/crop_data.csv") -> dict:
        """Train all models on the provided dataset."""
        df = pd.read_csv(data_path)

        # Encode season
        season_map = {"Kharif": 0, "Rabi": 1, "Zaid": 2, "Whole Year": 3}
        df["season_encoded"] = df["season"].map(season_map).fillna(0)

        # Encode crop labels
        df["crop_encoded"] = self.label_encoder.fit_transform(df["crop"])
        self.crop_classes_ = self.label_encoder.classes_

        # ---- 1. Yield Prediction ----
        X_yield = df[Config.YIELD_FEATURES].values
        y_yield = df["yield"].values

        Xtr, Xte, ytr, yte = train_test_split(
            X_yield, y_yield, test_size=0.2, random_state=42
        )
        Xtr_s = self.scaler.fit_transform(Xtr)
        Xte_s = self.scaler.transform(Xte)

        self.yield_model = RandomForestRegressor(
            n_estimators=200, max_depth=15,
            random_state=42, n_jobs=-1
        )
        self.yield_model.fit(Xtr_s, ytr)
        y_pred = self.yield_model.predict(Xte_s)
        mae = mean_absolute_error(yte, y_pred)
        r2  = r2_score(yte, y_pred)

        # ---- 2. Crop Recommender ----
        rec_feats = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
        X_rec = df[rec_feats].values
        y_rec = df["crop_encoded"].values

        Xtr2, Xte2, ytr2, yte2 = train_test_split(
            X_rec, y_rec, test_size=0.2, random_state=42
        )
        self.crop_recommender = RandomForestClassifier(
            n_estimators=150, random_state=42, n_jobs=-1
        )
        self.crop_recommender.fit(Xtr2, ytr2)
        acc = accuracy_score(yte2, self.crop_recommender.predict(Xte2))

        # ---- 3. Pest Risk Model (synthetic data since no dataset) ----
        self._train_pest_model()

        # Save everything
        joblib.dump(self.yield_model,      Config.MODEL_PATH)
        joblib.dump(self.scaler,           Config.SCALER_PATH)
        joblib.dump(self.label_encoder,    Config.ENCODER_PATH)
        joblib.dump(self.pest_model,       Config.PEST_MODEL_PATH)

        self.is_trained = True
        return {
            "yield_model": {
                "mae": round(float(mae), 2),
                "r2_score": round(float(r2), 3)
            },
            "crop_recommender": {
                "accuracy_pct": round(float(acc) * 100, 1)
            },
            "pest_model": {
                "status": "trained on synthetic risk data"
            }
        }

    def _train_pest_model(self):
        """Train pest risk classifier using synthetically generated data."""
        np.random.seed(42)
        n = 1000

        temperature        = np.random.uniform(15, 42, n)
        humidity           = np.random.uniform(20, 100, n)
        rainfall           = np.random.uniform(0, 300, n)
        wind_speed         = np.random.uniform(0, 25, n)
        crop_age_days      = np.random.uniform(0, 180, n)
        previous_infestation = np.random.randint(0, 2, n)

        # Risk logic: high humidity + warm temp + rain → higher risk
        risk_score = (
            (humidity / 100) * 0.35
            + (np.clip(temperature - 20, 0, 20) / 20) * 0.25
            + (rainfall / 300) * 0.15
            + previous_infestation * 0.20
            + (1 - wind_speed / 25) * 0.05
        )
        # 0=Low, 1=Moderate, 2=High
        y = np.where(risk_score < 0.35, 0, np.where(risk_score < 0.60, 1, 2))

        X = np.column_stack([
            temperature, humidity, rainfall,
            wind_speed, crop_age_days, previous_infestation
        ])

        Xtr, _, ytr, _ = train_test_split(X, y, test_size=0.2, random_state=42)

        self.pest_model = GradientBoostingClassifier(
            n_estimators=100, max_depth=4, random_state=42
        )
        self.pest_model.fit(Xtr, ytr)

    # ------------------------------------------------------------------
    # LOAD SAVED MODELS
    # ------------------------------------------------------------------

    def load(self) -> bool:
        """Load pre-trained models from disk."""
        try:
            self.yield_model      = joblib.load(Config.MODEL_PATH)
            self.scaler           = joblib.load(Config.SCALER_PATH)
            self.label_encoder    = joblib.load(Config.ENCODER_PATH)
            self.pest_model       = joblib.load(Config.PEST_MODEL_PATH)
            self.crop_classes_    = self.label_encoder.classes_
            self.is_trained       = True
            return True
        except FileNotFoundError:
            return False

    # ------------------------------------------------------------------
    # INFERENCE
    # ------------------------------------------------------------------

    def predict_yield(self, features: dict) -> dict:
        """Predict crop yield given soil, weather, and farm inputs."""
        self._require_trained()

        season_map  = {"Kharif": 0, "Rabi": 1, "Zaid": 2, "Whole Year": 3}
        season_enc  = season_map.get(features.get("season", "Kharif"), 0)

        vec = np.array([[
            features["N"],           features["P"],
            features["K"],           features["temperature"],
            features["humidity"],    features["ph"],
            features["rainfall"],    features["area"],
            season_enc
        ]])

        vec_s         = self.scaler.transform(vec)
        pred_yield    = float(self.yield_model.predict(vec_s)[0])
        total_yield   = pred_yield * features["area"]

        importances   = self.yield_model.feature_importances_
        impact        = dict(zip(Config.YIELD_FEATURES, importances.round(3).tolist()))

        return {
            "predicted_yield_kg_per_ha": round(pred_yield, 1),
            "total_estimated_yield_kg":  round(total_yield, 1),
            "feature_impact":            impact
        }

    def recommend_crop(self, soil_weather: dict) -> dict:
        """Recommend top 3 crops suited for given conditions."""
        self._require_trained()

        vec    = np.array([[
            soil_weather["N"],           soil_weather["P"],
            soil_weather["K"],           soil_weather["temperature"],
            soil_weather["humidity"],    soil_weather["ph"],
            soil_weather["rainfall"]
        ]])
        proba  = self.crop_recommender.predict_proba(vec)[0]
        top3   = np.argsort(proba)[-3:][::-1]

        recs = []
        for idx in top3:
            crop_label = self.label_encoder.inverse_transform(
                [self.crop_recommender.classes_[idx]]
            )[0]
            recs.append({
                "crop":       crop_label,
                "confidence": round(float(proba[idx]) * 100, 1)
            })
        return {"recommendations": recs}

    def predict_pest_risk(self, env: dict) -> dict:
        """Predict pest infestation risk level."""
        self._require_trained()

        vec    = np.array([[
            env.get("temperature", 25),
            env.get("humidity", 60),
            env.get("rainfall", 50),
            env.get("wind_speed", 5),
            env.get("crop_age_days", 30),
            int(env.get("previous_infestation", 0))
        ]])

        proba         = self.pest_model.predict_proba(vec)[0]
        level_idx     = int(np.argmax(proba))
        levels        = ["Low", "Moderate", "High"]
        level_colors  = ["green", "orange", "red"]

        # Identify likely pests based on crop
        crop      = env.get("crop", "default").lower()
        pest_list = Config.PEST_MAP.get(crop, Config.PEST_MAP["default"])

        # Filter pests based on risk level
        likely_pests = pest_list if level_idx >= 1 else []

        return {
            "risk_level":          levels[level_idx],
            "risk_color":          level_colors[level_idx],
            "risk_probabilities": {
                "Low":      round(float(proba[0]) * 100, 1),
                "Moderate": round(float(proba[1]) * 100, 1),
                "High":     round(float(proba[2]) * 100, 1)
            },
            "likely_pests":        likely_pests,
            "prevention_tips":     self._pest_prevention(level_idx, crop)
        }

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------

    def _require_trained(self):
        if not self.is_trained:
            raise RuntimeError("Model not trained. Call train() or load() first.")

    def _pest_prevention(self, level: int, crop: str) -> list:
        base = [
            "Inspect crops twice weekly for early pest signs.",
            "Maintain field hygiene — remove crop debris.",
            "Use yellow/blue sticky traps as monitoring tools."
        ]
        moderate = [
            "Apply neem-based biopesticides as a first line of defense.",
            "Introduce beneficial insects (ladybirds, parasitoid wasps).",
            "Increase scouting frequency to every 2–3 days."
        ]
        high = [
            "Apply recommended chemical pesticides at prescribed dosage.",
            "Consult local agricultural extension officer immediately.",
            "Consider protective netting or row covers for high-value crops.",
            "Document infestation and report to local Krishi Kendra."
        ]
        if level == 0:   return base
        if level == 1:   return base + moderate
        return base + moderate + high


# Singleton instance
crop_model = CropYieldModel()
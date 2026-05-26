"""
models/schemas.py
-----------------
Dataclasses for request validation.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class YieldInput:
    crop:        str
    N:           float    # Nitrogen  (kg/ha)
    P:           float    # Phosphorus (kg/ha)
    K:           float    # Potassium  (kg/ha)
    temperature: float    # °C
    humidity:    float    # %
    ph:          float    # 0–14
    rainfall:    float    # mm
    area:        float    # hectares
    season:      str      # Kharif | Rabi | Zaid | Whole Year

    def validate(self) -> list:
        errors = []
        if not (0 <= self.N <= 200):        errors.append("N must be 0–200 kg/ha")
        if not (0 <= self.P <= 150):        errors.append("P must be 0–150 kg/ha")
        if not (0 <= self.K <= 250):        errors.append("K must be 0–250 kg/ha")
        if not (-10 <= self.temperature <= 60): errors.append("temperature must be -10 to 60°C")
        if not (0 <= self.humidity <= 100): errors.append("humidity must be 0–100%")
        if not (0 <= self.ph <= 14):        errors.append("pH must be 0–14")
        if not (0 <= self.rainfall <= 5000): errors.append("rainfall must be 0–5000 mm")
        if self.area <= 0:                  errors.append("area must be > 0 hectares")
        if self.season not in ["Kharif", "Rabi", "Zaid", "Whole Year"]:
            errors.append(f"Invalid season: {self.season}")
        return errors


@dataclass
class PestInput:
    crop:                 str
    temperature:          float
    humidity:             float
    rainfall:             float
    wind_speed:           float = 5.0
    crop_age_days:        int   = 30
    previous_infestation: int   = 0   # 0=No, 1=Yes

    def validate(self) -> list:
        errors = []
        if not (-10 <= self.temperature <= 60): errors.append("temperature out of range")
        if not (0 <= self.humidity <= 100):     errors.append("humidity must be 0–100%")
        if not (0 <= self.rainfall <= 1000):    errors.append("rainfall must be 0–1000 mm")
        if not (0 <= self.wind_speed <= 100):   errors.append("wind_speed must be 0–100 km/h")
        if self.crop_age_days < 0:              errors.append("crop_age_days must be >= 0")
        if self.previous_infestation not in (0, 1): errors.append("previous_infestation must be 0 or 1")
        return errors


@dataclass
class FieldMonitor:
    field_id:     str
    crop:         str
    growth_stage: str     # germination | vegetative | flowering | maturity
    ndvi:         float   # -1 to 1 (Normalized Difference Vegetation Index)
    soil_moisture: float  # %
    temperature:  float
    humidity:     float
    lat:          Optional[float] = None
    lon:          Optional[float] = None

    def health_score(self) -> float:
        ndvi_score     = max(0, min(100, (self.ndvi + 1) / 2 * 100))
        moisture_score = max(0, min(100, self.soil_moisture))
        temp_score     = max(0, 100 - abs(self.temperature - 25) * 3)
        return round(ndvi_score * 0.4 + moisture_score * 0.35 + temp_score * 0.25, 1)
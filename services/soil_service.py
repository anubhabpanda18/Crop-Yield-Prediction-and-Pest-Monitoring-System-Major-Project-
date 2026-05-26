class SoilService:

    PH_CATEGORIES = [
        (0,   5.0, "Strongly Acidic"),
        (5.0, 6.0, "Moderately Acidic"),
        (6.0, 6.5, "Slightly Acidic"),
        (6.5, 7.0, "Neutral"),
        (7.0, 7.5, "Slightly Alkaline"),
        (7.5, 8.5, "Moderately Alkaline"),
        (8.5, 14,  "Strongly Alkaline"),
    ]

    NUTRIENT_THRESHOLDS = {
        "N": {"low": 30, "medium": 60},
        "P": {"low": 15, "medium": 30},
        "K": {"low": 40, "medium": 80},
    }

    FERTILIZER_MAP = {
        "N_low":  ("Urea (46% N) or Ammonium Nitrate", "Apply 50-80 kg/ha before sowing"),
        "P_low":  ("Single Super Phosphate (SSP)", "Apply 100 kg/ha as basal dose"),
        "K_low":  ("Muriate of Potash (MOP)", "Apply 40-60 kg/ha at transplanting"),
        "ph_low": ("Agricultural Lime (CaCO3)", "Apply 1-2 t/ha; incorporate 4 weeks before sowing"),
        "ph_high":("Gypsum or Elemental Sulfur", "Apply 200-500 kg/ha; mix into top 15 cm soil"),
    }

    def analyze(self, N, P, K, ph):
        nutrient_status = self._classify_nutrients(N, P, K)
        ph_cat          = self._classify_ph(ph)
        recs            = self._recommendations(N, P, K, ph)
        score           = self._health_score(N, P, K, ph)

        return {
            "ph_value":          ph,
            "ph_category":       ph_cat,
            "nutrient_status":   nutrient_status,
            "soil_health_score": score,
            "health_category":   self._score_label(score),
            "recommendations":   recs
        }

    def _classify_ph(self, ph):
        for lo, hi, label in self.PH_CATEGORIES:
            if lo <= ph < hi:
                return label
        return "Unknown"

    def _classify_nutrients(self, N, P, K):
        result = {}
        for nutrient, val in [("N", N), ("P", P), ("K", K)]:
            t = self.NUTRIENT_THRESHOLDS[nutrient]
            if val < t["low"]:
                result[nutrient] = "Low"
            elif val < t["medium"]:
                result[nutrient] = "Medium"
            else:
                result[nutrient] = "High"
        return result

    def _recommendations(self, N, P, K, ph):
        recs = []
        if N < self.NUTRIENT_THRESHOLDS["N"]["low"]:
            fert, method = self.FERTILIZER_MAP["N_low"]
            recs.append({"issue": "Low Nitrogen", "fertilizer": fert, "method": method})
        if P < self.NUTRIENT_THRESHOLDS["P"]["low"]:
            fert, method = self.FERTILIZER_MAP["P_low"]
            recs.append({"issue": "Low Phosphorus", "fertilizer": fert, "method": method})
        if K < self.NUTRIENT_THRESHOLDS["K"]["low"]:
            fert, method = self.FERTILIZER_MAP["K_low"]
            recs.append({"issue": "Low Potassium", "fertilizer": fert, "method": method})
        if ph < 6.0:
            fert, method = self.FERTILIZER_MAP["ph_low"]
            recs.append({"issue": f"Soil Too Acidic (pH {ph})", "fertilizer": fert, "method": method})
        if ph > 7.5:
            fert, method = self.FERTILIZER_MAP["ph_high"]
            recs.append({"issue": f"Soil Too Alkaline (pH {ph})", "fertilizer": fert, "method": method})
        if not recs:
            recs.append({"issue": "None", "fertilizer": "No amendment needed",
                         "method": "Soil is well-balanced. Continue current management."})
        return recs

    def _health_score(self, N, P, K, ph):
        n_score  = min(100, (N / 60) * 100)
        p_score  = min(100, (P / 30) * 100)
        k_score  = min(100, (K / 80) * 100)
        ph_score = max(0, 100 - abs(ph - 6.8) * 18)
        return round((n_score + p_score + k_score + ph_score) / 4, 1)

    def _score_label(self, score):
        if score >= 80: return "Excellent"
        if score >= 60: return "Good"
        if score >= 40: return "Fair"
        return "Poor"


soil_service = SoilService()
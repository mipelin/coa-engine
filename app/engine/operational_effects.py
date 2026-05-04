"""Operational effects model: environment, logistics, jamming, and second-order risks.

Applies deterministic modifiers to analysis outputs based on current operational
conditions. All effects are table-driven, explainable, and never call LLMs.

Effect categories:
- Environment: sea_state, visibility, weather, time_of_day, ice_cover
- Jamming: radio interference, sensor degradation
- Logistics: distance to operating area, asset readiness, fuel/endurance

Integration points (downstream consumers apply modifiers):
- Feature engineering: sensor confidence adjustments
- Anomaly detection: threshold adjustments
- Threat assessment: probability modifiers
- Simulation: success/time/risk adjustments
- Scoring: feasibility adjustments
- COA optimizer: variant parameter tuning
- Forecasting: effects propagated across horizon
- COP: effects exposed in UI
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("coa_engine.engine.operational_effects")

# ---------------------------------------------------------------------------
# Effect lookup tables — all deterministic
# ---------------------------------------------------------------------------

# Sea state (Beaufort 0-9): sensor_effectiveness multiplier, detection_penalty
SEA_STATE_EFFECTS: dict[int, dict[str, float]] = {
    0: {"sensor_effectiveness": 1.00, "detection_penalty": 0.00, "label": "Calm"},
    1: {"sensor_effectiveness": 0.98, "detection_penalty": 0.00, "label": "Light air"},
    2: {"sensor_effectiveness": 0.95, "detection_penalty": 0.02, "label": "Light breeze"},
    3: {"sensor_effectiveness": 0.90, "detection_penalty": 0.05, "label": "Gentle breeze"},
    4: {"sensor_effectiveness": 0.82, "detection_penalty": 0.10, "label": "Moderate breeze"},
    5: {"sensor_effectiveness": 0.72, "detection_penalty": 0.18, "label": "Fresh breeze"},
    6: {"sensor_effectiveness": 0.60, "detection_penalty": 0.28, "label": "Strong breeze"},
    7: {"sensor_effectiveness": 0.48, "detection_penalty": 0.38, "label": "Near gale"},
    8: {"sensor_effectiveness": 0.35, "detection_penalty": 0.50, "label": "Gale"},
    9: {"sensor_effectiveness": 0.25, "detection_penalty": 0.60, "label": "Strong gale"},
}

# Visibility: confidence modifier for visual/ISR
VISIBILITY_EFFECTS: dict[str, dict[str, float]] = {
    "excellent": {"confidence_modifier": 1.00, "isr_penalty": 0.00},
    "good": {"confidence_modifier": 0.95, "isr_penalty": 0.02},
    "moderate": {"confidence_modifier": 0.85, "isr_penalty": 0.08},
    "poor": {"confidence_modifier": 0.70, "isr_penalty": 0.20},
    "very_poor": {"confidence_modifier": 0.50, "isr_penalty": 0.35},
    "fog": {"confidence_modifier": 0.35, "isr_penalty": 0.45},
}

# Time of day: affects optical/visual ISR
TIME_OF_DAY_EFFECTS: dict[str, dict[str, float]] = {
    "dawn": {"optical_isr_modifier": 0.85, "detection_bonus": 0.00},
    "day": {"optical_isr_modifier": 1.00, "detection_bonus": 0.05},
    "dusk": {"optical_isr_modifier": 0.80, "detection_bonus": 0.00},
    "night": {"optical_isr_modifier": 0.50, "detection_bonus": -0.05},
    "midday": {"optical_isr_modifier": 1.00, "detection_bonus": 0.08},
}

# Ice cover: affects vessel movement and submarine detection
ICE_COVER_EFFECTS: dict[str, dict[str, float]] = {
    "none": {"vessel_speed_modifier": 1.00, "sub_detection_bonus": 0.00},
    "light": {"vessel_speed_modifier": 0.90, "sub_detection_bonus": 0.05},
    "partial": {"vessel_speed_modifier": 0.75, "sub_detection_bonus": 0.12},
    "heavy": {"vessel_speed_modifier": 0.55, "sub_detection_bonus": 0.20},
    "complete": {"vessel_speed_modifier": 0.30, "sub_detection_bonus": 0.25},
}

# Weather: general operational modifier
WEATHER_EFFECTS: dict[str, dict[str, float]] = {
    "clear": {"operation_modifier": 1.00, "sortie_rate": 1.00},
    "overcast": {"operation_modifier": 0.95, "sortie_rate": 0.95},
    "rain": {"operation_modifier": 0.85, "sortie_rate": 0.80},
    "storm": {"operation_modifier": 0.60, "sortie_rate": 0.50},
    "snow": {"operation_modifier": 0.70, "sortie_rate": 0.65},
    "fog": {"operation_modifier": 0.55, "sortie_rate": 0.40},
}

# Jamming intensity: sensor degradation
JAMMING_INTENSITY_EFFECTS: dict[str, dict[str, float]] = {
    "none": {"sensor_degradation": 0.00, "comm_reliability": 1.00},
    "low": {"sensor_degradation": 0.10, "comm_reliability": 0.92},
    "medium": {"sensor_degradation": 0.25, "comm_reliability": 0.78},
    "high": {"sensor_degradation": 0.45, "comm_reliability": 0.55},
    "severe": {"sensor_degradation": 0.65, "comm_reliability": 0.30},
}

# Logistics readiness levels
READINESS_EFFECTS: dict[str, dict[str, float]] = {
    "full": {"asset_availability": 1.00, "response_time_modifier": 1.00, "endurance_factor": 1.00},
    "high": {"asset_availability": 0.90, "response_time_modifier": 1.05, "endurance_factor": 0.95},
    "moderate": {"asset_availability": 0.75, "response_time_modifier": 1.15, "endurance_factor": 0.85},
    "low": {"asset_availability": 0.55, "response_time_modifier": 1.30, "endurance_factor": 0.70},
    "critical": {"asset_availability": 0.30, "response_time_modifier": 1.60, "endurance_factor": 0.50},
}

# Distance to operating area (nautical miles)
DISTANCE_EFFECTS: dict[str, dict[str, float]] = {
    "close": {"logistics_modifier": 1.00, "fuel_factor": 1.00, "response_delay_min": 0.0},
    "medium": {"logistics_modifier": 0.90, "fuel_factor": 0.90, "response_delay_min": 30.0},
    "far": {"logistics_modifier": 0.75, "fuel_factor": 0.75, "response_delay_min": 90.0},
    "distant": {"logistics_modifier": 0.55, "fuel_factor": 0.55, "response_delay_min": 180.0},
}


# ---------------------------------------------------------------------------
# OperationalEffects dataclass
# ---------------------------------------------------------------------------


@dataclass
class OperationalEffects:
    """Computed operational effects from current conditions.

    All values are deterministic modifiers in [0, 1] or additive deltas.
    """
    # Input conditions
    sea_state: int = 0
    visibility: str = "good"
    weather: str = "clear"
    time_of_day: str = "day"
    ice_cover: str = "none"
    jamming_intensity: str = "none"
    readiness: str = "full"
    distance: str = "close"
    fuel_endurance: float = 1.0  # 1.0 = full endurance, 0.0 = depleted

    # Computed effect modifiers
    sensor_effectiveness: float = 1.0
    detection_penalty: float = 0.0
    confidence_modifier: float = 1.0
    isr_penalty: float = 0.0
    optical_isr_modifier: float = 1.0
    vessel_speed_modifier: float = 1.0
    sub_detection_bonus: float = 0.0
    operation_modifier: float = 1.0
    sortie_rate: float = 1.0
    sensor_degradation: float = 0.0
    comm_reliability: float = 1.0
    asset_availability: float = 1.0
    response_time_modifier: float = 1.0
    endurance_factor: float = 1.0
    logistics_modifier: float = 1.0
    fuel_factor: float = 1.0
    response_delay_min: float = 0.0

    # Derived composite effects
    overall_effectiveness: float = 1.0
    coa_success_modifier: float = 1.0
    coa_time_modifier: float = 1.0
    coa_risk_modifier: float = 1.0
    threat_detection_modifier: float = 1.0
    feasibility_modifier: float = 1.0

    # Human-readable explanations
    active_effects: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "sea_state": self.sea_state,
            "visibility": self.visibility,
            "weather": self.weather,
            "time_of_day": self.time_of_day,
            "ice_cover": self.ice_cover,
            "jamming_intensity": self.jamming_intensity,
            "readiness": self.readiness,
            "distance": self.distance,
            "fuel_endurance": round(self.fuel_endurance, 3),
            "sensor_effectiveness": round(self.sensor_effectiveness, 3),
            "detection_penalty": round(self.detection_penalty, 3),
            "confidence_modifier": round(self.confidence_modifier, 3),
            "isr_penalty": round(self.isr_penalty, 3),
            "optical_isr_modifier": round(self.optical_isr_modifier, 3),
            "vessel_speed_modifier": round(self.vessel_speed_modifier, 3),
            "sub_detection_bonus": round(self.sub_detection_bonus, 3),
            "operation_modifier": round(self.operation_modifier, 3),
            "sortie_rate": round(self.sortie_rate, 3),
            "sensor_degradation": round(self.sensor_degradation, 3),
            "comm_reliability": round(self.comm_reliability, 3),
            "asset_availability": round(self.asset_availability, 3),
            "response_time_modifier": round(self.response_time_modifier, 3),
            "endurance_factor": round(self.endurance_factor, 3),
            "logistics_modifier": round(self.logistics_modifier, 3),
            "fuel_factor": round(self.fuel_factor, 3),
            "response_delay_min": round(self.response_delay_min, 1),
            "overall_effectiveness": round(self.overall_effectiveness, 3),
            "coa_success_modifier": round(self.coa_success_modifier, 3),
            "coa_time_modifier": round(self.coa_time_modifier, 3),
            "coa_risk_modifier": round(self.coa_risk_modifier, 3),
            "threat_detection_modifier": round(self.threat_detection_modifier, 3),
            "feasibility_modifier": round(self.feasibility_modifier, 3),
            "active_effects": self.active_effects,
        }


# ---------------------------------------------------------------------------
# Compute effects from environment dict
# ---------------------------------------------------------------------------


def compute_operational_effects(
    environment: dict[str, Any] | None = None,
    *,
    jamming_intensity: str | None = None,
    readiness: str | None = None,
    distance: str | None = None,
    fuel_endurance: float | None = None,
) -> OperationalEffects:
    """Compute operational effects from environment conditions.

    Environment dict keys: sea_state, visibility, weather, time_of_day, ice_cover.
    Explicit parameters override environment dict values.
    """
    env = environment or {}

    sea_state = int(env.get("sea_state", 0))
    visibility = str(env.get("visibility", "good")).lower()
    weather = str(env.get("weather", "clear")).lower()
    time_of_day = str(env.get("time_of_day", "day")).lower()
    ice_cover = str(env.get("ice_cover", "none")).lower()

    jamming = jamming_intensity or str(env.get("jamming_intensity", "none")).lower()
    ready = readiness or str(env.get("readiness", "full")).lower()
    dist = distance or str(env.get("distance", "close")).lower()
    fuel = fuel_endurance if fuel_endurance is not None else float(env.get("fuel_endurance", 1.0))

    effects = OperationalEffects(
        sea_state=sea_state,
        visibility=visibility,
        weather=weather,
        time_of_day=time_of_day,
        ice_cover=ice_cover,
        jamming_intensity=jamming,
        readiness=ready,
        distance=dist,
        fuel_endurance=max(0.0, min(1.0, fuel)),
    )
    explanations: list[str] = []

    # --- Environment effects ---
    sea = SEA_STATE_EFFECTS.get(sea_state, SEA_STATE_EFFECTS[0])
    effects.sensor_effectiveness = sea["sensor_effectiveness"]
    effects.detection_penalty = sea["detection_penalty"]
    if sea_state >= 5:
        explanations.append(f"Sea state {sea_state} ({sea['label']}): sensor effectiveness {sea['sensor_effectiveness']:.0%}")
    if sea_state >= 7:
        explanations.append(f"Heavy seas degrade ISR and increase response time")

    vis = VISIBILITY_EFFECTS.get(visibility, VISIBILITY_EFFECTS["good"])
    effects.confidence_modifier = vis["confidence_modifier"]
    effects.isr_penalty = vis["isr_penalty"]
    if visibility in ("poor", "very_poor", "fog"):
        explanations.append(f"Visibility {visibility}: confidence {vis['confidence_modifier']:.0%}, ISR penalty {vis['isr_penalty']:.0%}")

    tod = TIME_OF_DAY_EFFECTS.get(time_of_day, TIME_OF_DAY_EFFECTS["day"])
    effects.optical_isr_modifier = tod["optical_isr_modifier"]
    if time_of_day == "night":
        explanations.append(f"Night conditions: optical ISR at {tod['optical_isr_modifier']:.0%}")

    ice = ICE_COVER_EFFECTS.get(ice_cover, ICE_COVER_EFFECTS["none"])
    effects.vessel_speed_modifier = ice["vessel_speed_modifier"]
    effects.sub_detection_bonus = ice["sub_detection_bonus"]
    if ice_cover in ("partial", "heavy", "complete"):
        explanations.append(f"Ice cover {ice_cover}: vessel speed {ice['vessel_speed_modifier']:.0%}, sub detection +{ice['sub_detection_bonus']:.0%}")

    wx = WEATHER_EFFECTS.get(weather, WEATHER_EFFECTS["clear"])
    effects.operation_modifier = wx["operation_modifier"]
    effects.sortie_rate = wx["sortie_rate"]
    if weather in ("storm", "fog", "snow"):
        explanations.append(f"Weather {weather}: operations at {wx['operation_modifier']:.0%}, sortie rate {wx['sortie_rate']:.0%}")

    # --- Jamming effects ---
    jam = JAMMING_INTENSITY_EFFECTS.get(jamming, JAMMING_INTENSITY_EFFECTS["none"])
    effects.sensor_degradation = jam["sensor_degradation"]
    effects.comm_reliability = jam["comm_reliability"]
    if jamming in ("medium", "high", "severe"):
        explanations.append(f"Jamming {jamming}: sensor degradation {jam['sensor_degradation']:.0%}, comm reliability {jam['comm_reliability']:.0%}")

    # --- Logistics effects ---
    rd = READINESS_EFFECTS.get(ready, READINESS_EFFECTS["full"])
    effects.asset_availability = rd["asset_availability"]
    effects.response_time_modifier = rd["response_time_modifier"]
    effects.endurance_factor = rd["endurance_factor"]
    if ready in ("low", "critical"):
        explanations.append(f"Readiness {ready}: asset availability {rd['asset_availability']:.0%}, response time x{rd['response_time_modifier']:.2f}")

    de = DISTANCE_EFFECTS.get(dist, DISTANCE_EFFECTS["close"])
    effects.logistics_modifier = de["logistics_modifier"]
    effects.fuel_factor = de["fuel_factor"]
    effects.response_delay_min = de["response_delay_min"]
    if dist in ("far", "distant"):
        explanations.append(f"Distance {dist}: logistics {de['logistics_modifier']:.0%}, fuel {de['fuel_factor']:.0%}, delay {de['response_delay_min']:.0f} min")

    # Fuel endurance
    if fuel < 0.5:
        effects.fuel_factor *= fuel
        explanations.append(f"Low fuel endurance ({fuel:.0%}): further reduces fuel factor to {effects.fuel_factor:.2f}")

    # --- Composite effects ---
    # Overall effectiveness: geometric mean of key modifiers
    base_mods = [
        effects.sensor_effectiveness,
        effects.confidence_modifier,
        effects.operation_modifier,
        1.0 - effects.sensor_degradation,
        effects.asset_availability,
        effects.logistics_modifier,
    ]
    effects.overall_effectiveness = _geomean(base_mods)

    # COA success modifier: reduced by environment + jamming + logistics
    env_factor = effects.sensor_effectiveness * effects.confidence_modifier * effects.operation_modifier
    jam_factor = 1.0 - effects.sensor_degradation * 0.5
    log_factor = effects.asset_availability * effects.fuel_factor
    effects.coa_success_modifier = round(env_factor * jam_factor * log_factor, 3)

    # COA time modifier: worse conditions = slower response
    time_mod = 1.0 / max(effects.operation_modifier, 0.3)
    time_mod *= effects.response_time_modifier
    if effects.response_delay_min > 0:
        time_mod *= 1.0 + effects.response_delay_min / 120.0
    effects.coa_time_modifier = round(time_mod, 3)

    # COA risk modifier: worse conditions = higher risk
    risk_mod = 1.0 + effects.detection_penalty + effects.isr_penalty + effects.sensor_degradation * 0.3
    risk_mod *= 1.0 / max(effects.comm_reliability, 0.3)
    effects.coa_risk_modifier = round(risk_mod, 3)

    # Threat detection modifier: how well we can detect threats
    effects.threat_detection_modifier = round(
        effects.sensor_effectiveness * effects.confidence_modifier * (1.0 - effects.isr_penalty * 0.5),
        3,
    )

    # Feasibility modifier: logistics + readiness
    effects.feasibility_modifier = round(
        effects.asset_availability * effects.fuel_factor * effects.sortie_rate,
        3,
    )

    effects.active_effects = explanations

    if explanations:
        logger.info("Operational effects active: %d conditions, overall_effectiveness=%.2f",
                     len(explanations), effects.overall_effectiveness)

    return effects


def _geomean(values: list[float]) -> float:
    """Geometric mean, clamped to avoid log(0)."""
    clamped = [max(v, 0.01) for v in values]
    return round(math.exp(sum(math.log(v) for v in clamped) / len(clamped)), 3)


# ---------------------------------------------------------------------------
# Helper to extract jamming intensity from events
# ---------------------------------------------------------------------------


def infer_jamming_intensity(events: list[Any]) -> str:
    """Infer jamming intensity from operational events.

    Uses jamming_nearby feature scores or event attributes.
    """
    from ..core.constants import EventType

    max_jam_score = 0.0
    jam_event_count = 0
    for e in events:
        etype = getattr(e, "event_type", None)
        if etype == EventType.JAMMING_DETECTED:
            jam_event_count += 1
            attrs = getattr(e, "attributes", {})
            radius = attrs.get("radius_nm", 20)
            if radius > 40:
                max_jam_score = max(max_jam_score, 0.8)
            elif radius > 20:
                max_jam_score = max(max_jam_score, 0.5)
            else:
                max_jam_score = max(max_jam_score, 0.3)
        feat = getattr(e, "jamming_nearby", None)
        if feat is not None and feat > 0:
            max_jam_score = max(max_jam_score, feat)

    if max_jam_score > 0.7 or jam_event_count >= 3:
        return "high"
    if max_jam_score > 0.4 or jam_event_count >= 2:
        return "medium"
    if max_jam_score > 0.1 or jam_event_count >= 1:
        return "low"
    return "none"


# ---------------------------------------------------------------------------
# Integration helpers
# ---------------------------------------------------------------------------


def apply_effects_to_features(
    features: list[Any],
    effects: OperationalEffects,
) -> list[Any]:
    """Apply operational effects to feature vectors.

    Adjusts confidence and detection-related features based on conditions.
    Returns new FeatureVector instances.
    """
    if not features or effects.overall_effectiveness >= 0.99:
        return features

    modified = []
    for f in features:
        updates = {}
        # Source confidence weighted by sensor effectiveness
        if hasattr(f, "source_confidence_weight"):
            updates["source_confidence_weight"] = round(
                f.source_confidence_weight * effects.confidence_modifier, 3
            )
        # Jamming score enhanced by actual jamming conditions
        if hasattr(f, "jamming_nearby") and effects.sensor_degradation > 0:
            updates["jamming_nearby"] = round(
                min(1.0, f.jamming_nearby + effects.sensor_degradation * 0.2), 3
            )
        if updates:
            modified.append(f.model_copy(update=updates))
        else:
            modified.append(f)
    return modified



def apply_effects_to_feasibility(
    coa: Any,
    effects: OperationalEffects,
) -> Any:
    """Apply operational effects to COA feasibility score.

    Returns modified CourseOfAction.
    """
    if effects.feasibility_modifier >= 0.99:
        return coa

    new_feasibility = coa.feasibility_score * effects.feasibility_modifier
    new_feasibility = max(0.0, min(1.0, new_feasibility))

    # Adjust logistics burden
    new_logistics = coa.logistics_burden / max(effects.logistics_modifier, 0.1)
    new_logistics = max(0.0, min(1.0, new_logistics))

    return coa.model_copy(update={
        "feasibility_score": round(new_feasibility, 3),
        "logistics_burden": round(new_logistics, 3),
    })

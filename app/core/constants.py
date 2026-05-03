from enum import Enum


class EventType(str, Enum):
    VESSEL_POSITION = "vessel_position"
    VESSEL_COURSE_CHANGE = "vessel_course_change"
    CABLE_SEVERANCE = "cable_severance"
    UAV_DETECTION = "uav_detection"
    CONVOY_SIGHTING = "convoy_sighting"
    JAMMING_DETECTED = "jamming_detected"
    SATELLITE_DETECTION = "satellite_detection"
    SOCIAL_MEDIA_REPORT = "social_media_report"
    OPERATIONAL_REPORT = "operational_report"
    SUBMARINE_DETECTION = "submarine_detection"


class EntityType(str, Enum):
    SUSPICIOUS_VESSEL = "suspicious_vessel"
    ALLIED_VESSEL = "allied_vessel"
    UAV = "uav"
    CONVOY = "convoy"
    INFRASTRUCTURE = "infrastructure"
    NEUTRAL_VESSEL = "neutral_vessel"
    ISR_ASSET = "isr_asset"


class AnomalyLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ThreatLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


CRITICAL_INFRASTRUCTURE = [
    {"name": "Baltic Cable Alpha", "type": "subsea_cable", "lat": 57.50, "lon": 19.20},
    {"name": "Baltic Cable Beta", "type": "subsea_cable", "lat": 58.10, "lon": 20.00},
    {"name": "Visby Airport", "type": "airport", "lat": 57.66, "lon": 18.35},
    {"name": "Riga Airport", "type": "airport", "lat": 56.92, "lon": 23.97},
]

BALTIC_BOUNDS = {
    "lat_min": 55.0,
    "lat_max": 60.0,
    "lon_min": 17.0,
    "lon_max": 26.0,
}

ARCTIC_INFRASTRUCTURE = [
    {"name": "Svalbard Undersea Cable", "type": "subsea_cable", "lat": 78.0, "lon": 15.0},
    {"name": "Tromso Naval Station", "type": "military_installation", "lat": 69.65, "lon": 18.96},
    {"name": "Andoya Space Center", "type": "military_installation", "lat": 69.30, "lon": 16.00},
    {"name": "Kiruna Radar Station", "type": "military_installation", "lat": 67.85, "lon": 20.22},
]

ARCTIC_BOUNDS = {
    "lat_min": 68.0,
    "lat_max": 80.0,
    "lon_min": 10.0,
    "lon_max": 35.0,
}

MEDITERRANEAN_INFRASTRUCTURE = [
    {"name": "East Med Gas Pipeline", "type": "pipeline", "lat": 34.5, "lon": 32.0},
    {"name": "Souda Bay Naval Base", "type": "military_installation", "lat": 35.48, "lon": 24.15},
    {"name": "Haifa Offshore Platform", "type": "offshore_platform", "lat": 33.10, "lon": 34.80},
    {"name": "Cyprus Communication Node", "type": "subsea_cable", "lat": 35.17, "lon": 33.37},
]

MEDITERRANEAN_BOUNDS = {
    "lat_min": 33.0,
    "lat_max": 37.0,
    "lon_min": 22.0,
    "lon_max": 36.0,
}

BEHAVIOR_WEIGHTS: dict[str, dict] = {
    "hostile_probe_infrastructure": {
        "anomaly_add": 12.0,
        "threat_add": 0.08,
        "explanation_anomaly": "Hostile intent: probing infrastructure target '{target}' (+{pts} pts)",
        "explanation_threat": "Hostile probe behavior targeting {targets}",
    },
    "hostile_loiter_then_divert": {
        "anomaly_add": 8.0,
        "threat_add": 0.05,
        "anomaly_condition_intent": "divert",
        "explanation_anomaly": "Hostile vessel diverting after trigger (+{pts} pts)",
        "explanation_threat": "Hostile vessel diverted after stimulus trigger",
    },
    "friendly_patrol_monitor": {
        "anomaly_multiply": 0.5,
        "threat_subtract": 0.15,
        "explanation_anomaly": "Friendly patrol activity — reduced anomaly relevance",
        "explanation_threat": "Entity classified as friendly patrol — reduced threat",
    },
    "neutral_transit": {
        "anomaly_multiply": 0.3,
        "threat_subtract": 0.10,
        "explanation_anomaly": "Neutral transit — minimal anomaly relevance",
        "explanation_threat": "Entity classified as neutral transit — reduced threat",
    },
}

SCENARIO_BOUNDS = {
    "baltic_hybrid_001": BALTIC_BOUNDS,
    "arctic_submarine_001": ARCTIC_BOUNDS,
    "mediterranean_001": MEDITERRANEAN_BOUNDS,
}

SCENARIO_CABLE_ROUTES = {
    "baltic_hybrid_001": [
        {
            "name": "Baltic Cable Alpha",
            "status": "severed",
            "points": [
                {"lat": 56.18, "lon": 18.10},
                {"lat": 56.30, "lon": 18.20},
                {"lat": 56.50, "lon": 18.40},
                {"lat": 56.70, "lon": 18.60},
                {"lat": 56.90, "lon": 18.80},
                {"lat": 57.10, "lon": 19.00},
                {"lat": 57.30, "lon": 19.10},
                {"lat": 57.50, "lon": 19.20},
                {"lat": 57.70, "lon": 19.40},
                {"lat": 57.90, "lon": 19.60},
                {"lat": 58.10, "lon": 19.80},
                {"lat": 58.30, "lon": 20.00},
            ],
            "landing_points": [0, 11],
        },
        {
            "name": "Baltic Cable Beta",
            "status": "threatened",
            "points": [
                {"lat": 57.00, "lon": 18.30},
                {"lat": 57.20, "lon": 18.50},
                {"lat": 57.40, "lon": 18.80},
                {"lat": 57.60, "lon": 19.10},
                {"lat": 57.80, "lon": 19.40},
                {"lat": 58.00, "lon": 19.70},
                {"lat": 58.10, "lon": 20.00},
                {"lat": 58.30, "lon": 20.30},
                {"lat": 58.50, "lon": 20.60},
            ],
            "landing_points": [0, 8],
        },
    ],
    "arctic_submarine_001": [
        {
            "name": "Svalbard Undersea Cable",
            "status": "intact",
            "points": [
                {"lat": 69.58, "lon": 18.88},
                {"lat": 70.64, "lon": 17.26},
                {"lat": 71.82, "lon": 15.72},
                {"lat": 73.18, "lon": 14.46},
                {"lat": 74.74, "lon": 13.64},
                {"lat": 76.22, "lon": 12.96},
                {"lat": 77.48, "lon": 13.60},
                {"lat": 78.00, "lon": 15.00},
            ],
            "landing_points": [0, 7],
        },
    ],
    "mediterranean_001": [
        {
            "name": "Cyprus Communications Cable",
            "status": "intact",
            "points": [
                {"lat": 34.42, "lon": 27.18},
                {"lat": 34.60, "lon": 28.36},
                {"lat": 34.76, "lon": 29.54},
                {"lat": 34.92, "lon": 30.62},
                {"lat": 35.04, "lon": 31.82},
                {"lat": 35.17, "lon": 33.37},
            ],
            "landing_points": [0, 5],
        },
    ],
}

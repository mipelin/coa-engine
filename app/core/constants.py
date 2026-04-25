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


class EntityType(str, Enum):
    SUSPICIOUS_VESSEL = "suspicious_vessel"
    ALLIED_VESSEL = "allied_vessel"
    UAV = "uav"
    CONVOY = "convoy"
    SUBSEA_CABLE = "subsea_cable"
    AIRPORT = "airport"
    BORDER_CROSSING = "border_crossing"
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
    {"name": "Baltic Cable Alpha", "type": "subsea_cable", "lat": 57.5, "lon": 19.0},
    {"name": "Baltic Cable Beta", "type": "subsea_cable", "lat": 58.0, "lon": 20.0},
    {"name": "Visby Airport", "type": "airport", "lat": 57.66, "lon": 18.35},
    {"name": "Riga Airport", "type": "airport", "lat": 56.92, "lon": 23.97},
]

BALTIC_BOUNDS = {
    "lat_min": 55.0,
    "lat_max": 60.0,
    "lon_min": 17.0,
    "lon_max": 26.0,
}

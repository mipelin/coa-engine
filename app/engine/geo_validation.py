"""Lightweight geospatial domain validation for the Baltic Sea region.

Uses simplified polygon approximations for land masses and sea corridors.
No heavy GIS dependencies — all checks are point-in-polygon with hardcoded
coordinates derived from real Baltic geography.

Domains:
  - surface (vessels): must be on water
  - subsurface (submarines): must be on water, preferably offshore
  - air (aircraft/UAV): no restriction
  - ground (convoys): must be on land
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


# ---------------------------------------------------------------------------
# Baltic Sea simplified land polygons (approximate coastlines)
#
# These are rough convex-hull approximations of major land masses.
# A point inside any land polygon is considered "on land".
# Points not inside any land polygon within the Baltic bounds are "at sea".
# ---------------------------------------------------------------------------

# Swedish mainland east coast (approximate polygon, south to north)
_SWEDEN_EAST: list[tuple[float, float]] = [
    (55.50, 12.80), (55.80, 13.00), (56.00, 12.70), (56.20, 12.80),
    (56.40, 13.00), (56.50, 13.50), (56.60, 14.00), (56.70, 14.50),
    (56.80, 15.00), (56.90, 15.50), (57.00, 16.00), (57.10, 16.50),
    (57.20, 16.80), (57.40, 16.70), (57.50, 16.90), (57.60, 17.00),
    (57.80, 17.10), (58.00, 17.20), (58.20, 17.40), (58.40, 17.60),
    (58.60, 17.80), (58.80, 18.00), (59.00, 18.20), (59.20, 18.40),
    (59.40, 18.60), (59.60, 18.80), (59.80, 19.00), (60.00, 19.50),
    # Northern boundary
    (60.50, 19.00), (61.00, 18.50), (61.50, 17.50), (62.00, 17.50),
    # West boundary (far west, closing)
    (62.00, 12.00), (55.50, 12.00),
]

# Gotland island (approximate polygon — realistic narrow shape)
_GOTLAND: list[tuple[float, float]] = [
    (57.15, 18.10), (57.25, 18.25), (57.35, 18.40), (57.45, 18.55),
    (57.55, 18.60), (57.65, 18.50), (57.72, 18.40), (57.68, 18.25),
    (57.60, 18.15), (57.50, 18.10), (57.40, 18.08), (57.30, 18.05),
    (57.20, 18.08),
]

# Estonian mainland (approximate polygon)
_ESTONIA: list[tuple[float, float]] = [
    (57.90, 22.00), (58.00, 23.00), (58.10, 23.50), (58.30, 24.00),
    (58.50, 24.50), (58.80, 25.00), (59.00, 25.50), (59.30, 26.00),
    (59.60, 26.50), (60.00, 27.00),
    # North boundary
    (60.00, 28.00), (59.50, 28.00), (59.00, 28.00),
    # East boundary
    (58.00, 27.50), (57.80, 27.00), (57.70, 26.50), (57.60, 26.00),
    (57.50, 25.50), (57.50, 25.00), (57.60, 24.50), (57.70, 24.00),
    (57.80, 23.50), (57.85, 23.00), (57.90, 22.50),
]

# Latvian/Lithuanian coast (approximate)
_LATVIA_LITHUANIA: list[tuple[float, float]] = [
    (55.70, 21.00), (56.00, 21.00), (56.30, 21.20), (56.50, 21.50),
    (56.70, 21.80), (56.90, 22.00), (57.10, 22.20), (57.30, 22.50),
    (57.50, 22.80), (57.60, 23.00), (57.70, 23.50), (57.80, 24.00),
    # Inland boundary
    (57.80, 26.00), (57.60, 26.00), (57.30, 25.50), (57.00, 25.00),
    (56.80, 24.50), (56.60, 24.00), (56.40, 23.50), (56.20, 23.00),
    (56.00, 22.50), (55.80, 22.00), (55.70, 21.50),
]

# Polish coast + Kaliningrad (approximate)
_POLAND_KALININGRAD: list[tuple[float, float]] = [
    (54.00, 14.00), (54.20, 14.50), (54.40, 15.00), (54.50, 16.00),
    (54.50, 17.00), (54.50, 18.00), (54.50, 19.00), (54.60, 19.50),
    (54.80, 20.00), (55.00, 20.50), (55.20, 21.00), (55.40, 21.50),
    (55.50, 22.00), (55.70, 22.00),
    # Inland boundary
    (55.70, 21.50), (55.50, 21.00), (55.30, 20.50), (55.10, 20.00),
    (54.90, 19.50), (54.70, 19.00), (54.60, 18.00), (54.50, 17.00),
    (54.50, 16.00), (54.40, 15.00), (54.20, 14.50), (54.00, 14.00),
]

# Danish islands / Copenhagen area (approximate)
_DENMARK: list[tuple[float, float]] = [
    (54.50, 8.00), (55.00, 8.50), (55.50, 9.00), (55.80, 10.00),
    (56.00, 10.50), (56.20, 11.00), (56.40, 11.50), (56.50, 12.00),
    (56.50, 12.80),
    # Inland / west
    (56.50, 12.00), (56.40, 11.50), (56.20, 11.00), (56.00, 10.50),
    (55.80, 10.00), (55.50, 9.50), (55.00, 9.00), (54.80, 8.50),
    (54.50, 8.00),
]

# Finnish south coast (approximate)
_FINLAND_SOUTH: list[tuple[float, float]] = [
    (59.50, 19.00), (59.70, 20.00), (59.80, 21.00), (59.90, 22.00),
    (60.00, 23.00), (60.00, 24.00), (60.00, 25.00), (60.00, 26.00),
    # North
    (60.50, 26.00), (60.50, 25.00), (60.50, 24.00), (60.50, 23.00),
    (60.50, 22.00), (60.50, 21.00), (60.50, 20.00), (60.50, 19.50),
    (60.50, 19.00), (60.00, 19.00),
]

_BALTIC_LAND_POLYGONS: list[list[tuple[float, float]]] = [
    _SWEDEN_EAST,
    _GOTLAND,
    _ESTONIA,
    _LATVIA_LITHUANIA,
    _POLAND_KALININGRAD,
    _DENMARK,
    _FINLAND_SOUTH,
]

# Baltic Sea bounds
BALTIC_BOUNDS = {
    "lat_min": 54.0,
    "lat_max": 61.0,
    "lon_min": 10.0,
    "lon_max": 30.0,
}

# Coastal buffer in degrees — areas within this distance of a land polygon
# edge are considered "shallow/coastal" (submarines should avoid)
_COASTAL_BUFFER_DEG = 0.15


# ---------------------------------------------------------------------------
# Core geometry helpers
# ---------------------------------------------------------------------------

def _point_in_polygon(lat: float, lon: float, polygon: list[tuple[float, float]]) -> bool:
    """Ray-casting algorithm for point-in-polygon test."""
    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        yi, xi = polygon[i]
        yj, xj = polygon[j]
        if ((yi > lat) != (yj > lat)) and (
            lon < (xj - xi) * (lat - yi) / (yj - yi + 1e-15) + xi
        ):
            inside = not inside
        j = i
    return inside


def _point_in_any_polygon(lat: float, lon: float, polygons: list[list[tuple[float, float]]]) -> bool:
    return any(_point_in_polygon(lat, lon, p) for p in polygons)


def _haversine_deg_lat() -> float:
    """1 degree of latitude in km."""
    return 111.0


def _haversine_deg_lon(lat: float) -> float:
    """1 degree of longitude in km at given latitude."""
    return 111.0 * math.cos(math.radians(lat))


def _nearest_polygon_edge_distance(lat: float, lon: float, polygon: list[tuple[float, float]]) -> float:
    """Approximate minimum distance from a point to polygon edge in degrees."""
    min_dist_sq = float("inf")
    n = len(polygon)
    for i in range(n):
        j = (i + 1) % n
        # Simple: distance to each vertex
        dlat = polygon[i][0] - lat
        dlon = polygon[i][1] - lon
        dist_sq = dlat * dlat + dlon * dlon
        if dist_sq < min_dist_sq:
            min_dist_sq = dist_sq
    return math.sqrt(min_dist_sq)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DomainType:
    SURFACE = "surface"
    SUBSURFACE = "subsurface"
    AIR = "air"
    GROUND = "ground"
    INFRASTRUCTURE = "infrastructure"


def is_on_land(lat: float, lon: float) -> bool:
    """Check if a point is on land in the Baltic region."""
    return _point_in_any_polygon(lat, lon, _BALTIC_LAND_POLYGONS)


def is_at_sea(lat: float, lon: float) -> bool:
    """Check if a point is at sea (not on land) within Baltic bounds."""
    if not (BALTIC_BOUNDS["lat_min"] <= lat <= BALTIC_BOUNDS["lat_max"]):
        return False
    if not (BALTIC_BOUNDS["lon_min"] <= lon <= BALTIC_BOUNDS["lon_max"]):
        return False
    return not is_on_land(lat, lon)


def is_offshore(lat: float, lon: float) -> bool:
    """Check if a point is in deeper/offshore water (not near coast)."""
    if not is_at_sea(lat, lon):
        return False
    for polygon in _BALTIC_LAND_POLYGONS:
        dist = _nearest_polygon_edge_distance(lat, lon, polygon)
        if dist < _COASTAL_BUFFER_DEG:
            return False
    return True


def is_near_coast(lat: float, lon: float) -> bool:
    """Check if a point is at sea but near the coast."""
    if not is_at_sea(lat, lon):
        return False
    for polygon in _BALTIC_LAND_POLYGONS:
        dist = _nearest_polygon_edge_distance(lat, lon, polygon)
        if dist < _COASTAL_BUFFER_DEG:
            return True
    return False


@dataclass
class ValidationResult:
    valid: bool
    domain: str
    is_on_land: bool
    is_at_sea: bool
    warning: str | None = None
    snapped_lat: float | None = None
    snapped_lon: float | None = None


def validate_placement(lat: float, lon: float, entity_type: str) -> ValidationResult:
    """Validate that a position is appropriate for the entity type.

    entity_type can be: vessel, submarine, uav, aircraft, helicopter,
                        convoy, ground_unit, or a ContactType value.
    """
    domain = _infer_domain(entity_type)
    on_land = is_on_land(lat, lon)
    at_sea = is_at_sea(lat, lon)

    warning = None
    snapped_lat = None
    snapped_lon = None
    valid = True

    if domain == DomainType.SURFACE:
        if on_land:
            warning = "This contact type should be placed on water."
            valid = False
            snap = snap_to_water(lat, lon)
            if snap:
                snapped_lat, snapped_lon = snap

    elif domain == DomainType.SUBSURFACE:
        if on_land:
            warning = "Submarines must be placed on water."
            valid = False
            snap = snap_to_water(lat, lon)
            if snap:
                snapped_lat, snapped_lon = snap
        elif is_near_coast(lat, lon):
            warning = "Submarines operate best in deeper/offshore water."

    elif domain == DomainType.GROUND:
        if at_sea or (not on_land and _in_baltic_bounds(lat, lon)):
            warning = "Ground units must be placed on land."
            valid = False
            snap = snap_to_land(lat, lon)
            if snap:
                snapped_lat, snapped_lon = snap

    # AIR: always valid, no restriction

    return ValidationResult(
        valid=valid,
        domain=domain,
        is_on_land=on_land,
        is_at_sea=at_sea,
        warning=warning,
        snapped_lat=snapped_lat,
        snapped_lon=snapped_lon,
    )


def validate_movement(
    from_lat: float, from_lon: float,
    to_lat: float, to_lon: float,
    entity_type: str,
) -> tuple[float, float]:
    """Validate and adjust a movement step. Returns adjusted (lat, lon).

    For vessels/submarines: if target is on land, clamp to nearest water.
    For ground units: if target is at sea, clamp to nearest land.
    For air: pass through.
    """
    domain = _infer_domain(entity_type)

    if domain == DomainType.AIR:
        return to_lat, to_lon

    if domain in (DomainType.SURFACE, DomainType.SUBSURFACE):
        if is_on_land(to_lat, to_lon):
            snap = snap_to_water(to_lat, to_lon)
            if snap:
                return snap[0], snap[1]
            # Fallback: stay in place
            return from_lat, from_lon
        return to_lat, to_lon

    if domain == DomainType.GROUND:
        if is_at_sea(to_lat, to_lon) or (not is_on_land(to_lat, to_lon) and _in_baltic_bounds(to_lat, to_lon)):
            snap = snap_to_land(to_lat, to_lon)
            if snap:
                return snap[0], snap[1]
            return from_lat, from_lon
        return to_lat, to_lon

    return to_lat, to_lon


def snap_to_water(lat: float, lon: float) -> tuple[float, float] | None:
    """Find the nearest sea point from a land position.

    Searches radially outward from the given position.
    """
    if is_at_sea(lat, lon):
        return lat, lon

    # Search in expanding grid
    for step in range(1, 40):
        delta = step * 0.02
        candidates = [
            (lat + delta, lon),
            (lat - delta, lon),
            (lat, lon + delta),
            (lat, lon - delta),
            (lat + delta, lon + delta),
            (lat + delta, lon - delta),
            (lat - delta, lon + delta),
            (lat - delta, lon - delta),
        ]
        for c_lat, c_lon in candidates:
            if is_at_sea(c_lat, c_lon):
                return round(c_lat, 4), round(c_lon, 4)
    return None


def snap_to_land(lat: float, lon: float) -> tuple[float, float] | None:
    """Find the nearest land point from a sea position."""
    if is_on_land(lat, lon):
        return lat, lon

    for step in range(1, 80):
        delta = step * 0.02
        candidates = [
            (lat + delta, lon),
            (lat - delta, lon),
            (lat, lon + delta),
            (lat, lon - delta),
            (lat + delta, lon + delta),
            (lat + delta, lon - delta),
            (lat - delta, lon + delta),
            (lat - delta, lon - delta),
        ]
        for c_lat, c_lon in candidates:
            if is_on_land(c_lat, c_lon):
                return round(c_lat, 4), round(c_lon, 4)
    return None


def cable_crosses_land(points: list[tuple[float, float]], landing_points: list[int] | None = None) -> list[int]:
    """Check which segments of a cable polyline cross land.

    Args:
        points: list of (lat, lon) tuples forming the cable route.
        landing_points: indices that are shore landing points (allowed on land).

    Returns:
        List of point indices that are on land and NOT landing points.
    """
    landing_set = set(landing_points or [])
    violations = []
    for i, (lat, lon) in enumerate(points):
        if i in landing_set:
            continue
        if is_on_land(lat, lon):
            violations.append(i)
    return violations


# ---------------------------------------------------------------------------
# Baltic Sea validated corridors
# ---------------------------------------------------------------------------

# Maritime corridors: known safe water routes (lat, lon waypoints)
BALTIC_MARITIME_CORRIDORS: dict[str, list[tuple[float, float]]] = {
    "south_north_main": [
        (55.50, 18.00), (55.80, 18.30), (56.10, 18.50), (56.40, 18.60),
        (56.70, 18.70), (57.00, 18.80), (57.30, 19.00), (57.60, 19.20),
        (57.90, 19.50), (58.20, 19.80), (58.50, 20.10), (58.80, 20.40),
    ],
    "east_gotland_south": [
        (56.50, 18.00), (56.80, 18.30), (57.00, 18.50), (57.20, 18.70),
        (57.40, 19.00), (57.60, 19.30), (57.80, 19.60),
    ],
    "east_gotland_north": [
        (57.80, 19.60), (58.00, 19.90), (58.30, 20.20), (58.60, 20.50),
        (58.90, 20.80), (59.20, 21.00),
    ],
    "gotland_west_channel": [
        (56.80, 17.50), (57.00, 17.60), (57.20, 17.70), (57.40, 17.80),
        (57.60, 17.90),
    ],
    "cable_approach_alpha": [
        (57.20, 18.80), (57.30, 18.90), (57.40, 19.00), (57.50, 19.10),
    ],
    "cable_approach_beta": [
        (57.70, 19.60), (57.80, 19.80), (57.90, 20.00), (58.00, 20.10),
    ],
}

# Ground convoy routes: on-land waypoints near border areas
BALTIC_LAND_CORRIDORS: dict[str, list[tuple[float, float]]] = {
    "eastern_border_south": [
        (56.50, 22.50), (56.70, 23.00), (56.90, 23.50), (57.10, 24.00),
        (57.30, 24.50), (57.50, 25.00),
    ],
    "estonian_route": [
        (58.30, 24.00), (58.50, 24.50), (58.70, 25.00), (58.90, 25.50),
    ],
}

# Submarine patrol zones: deeper offshore water areas
BALTIC_SUBMARINE_ZONES: list[tuple[float, float, float, float]] = [
    # (lat_center, lon_center, lat_radius, lon_radius)
    (57.50, 19.50, 0.5, 0.8),   # Central Baltic deep
    (58.00, 20.00, 0.5, 0.8),   # North-central Baltic
    (57.00, 19.00, 0.4, 0.6),   # South of Gotland
]

# Air approach corridors (aircraft can go anywhere, these are common routes)
BALTIC_AIR_CORRIDORS: dict[str, list[tuple[float, float]]] = {
    "visby_approach": [
        (57.80, 17.50), (57.75, 17.80), (57.70, 18.00), (57.66, 18.35),
    ],
    "riga_approach": [
        (57.20, 23.00), (57.00, 23.50), (56.92, 23.97),
    ],
    "baltic_transit_east": [
        (57.50, 17.00), (57.50, 19.00), (57.50, 21.00), (57.50, 23.00),
    ],
}


def random_water_point(rng, bounds: dict[str, float] | None = None, max_attempts: int = 50) -> tuple[float, float]:
    """Generate a random point that is at sea."""
    b = bounds or BALTIC_BOUNDS
    for _ in range(max_attempts):
        lat = rng.uniform(b["lat_min"] + 0.5, b["lat_max"] - 0.5)
        lon = rng.uniform(b["lon_min"] + 0.5, b["lon_max"] - 0.5)
        if is_at_sea(lat, lon):
            return round(lat, 4), round(lon, 4)
    # Fallback to known water point in central Baltic
    return 57.50, 19.50


def random_land_point(rng, bounds: dict[str, float] | None = None, max_attempts: int = 50) -> tuple[float, float]:
    """Generate a random point that is on land."""
    b = bounds or BALTIC_BOUNDS
    for _ in range(max_attempts):
        lat = rng.uniform(b["lat_min"], b["lat_max"])
        lon = rng.uniform(b["lon_min"], b["lon_max"])
        if is_on_land(lat, lon):
            return round(lat, 4), round(lon, 4)
    # Fallback to known land point (Latvia)
    return 56.90, 24.00


def random_offshore_point(rng, bounds: dict[str, float] | None = None, max_attempts: int = 80) -> tuple[float, float]:
    """Generate a random point in offshore/deep water."""
    b = bounds or BALTIC_BOUNDS
    for _ in range(max_attempts):
        lat = rng.uniform(b["lat_min"] + 0.5, b["lat_max"] - 0.5)
        lon = rng.uniform(b["lon_min"] + 0.5, b["lon_max"] - 0.5)
        if is_offshore(lat, lon):
            return round(lat, 4), round(lon, 4)
    # Fallback
    return 57.50, 19.50


def nearest_corridor_point(lat: float, lon: float, corridor_name: str) -> tuple[float, float] | None:
    """Find nearest point on a named maritime corridor."""
    corridor = BALTIC_MARITIME_CORRIDORS.get(corridor_name)
    if not corridor:
        return None
    best = None
    best_d = float("inf")
    for p_lat, p_lon in corridor:
        d = (p_lat - lat) ** 2 + (p_lon - lon) ** 2
        if d < best_d:
            best_d = d
            best = (p_lat, p_lon)
    return best


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _infer_domain(entity_type: str) -> str:
    """Infer the operating domain from entity type string."""
    t = (entity_type or "").lower().strip()
    if t in ("vessel", "ship", "warship", "surface", "suspicious_vessel",
             "allied_vessel", "neutral_vessel", "cargo", "tanker", "ferry",
             "fishing_vessel", "patrol_ship", "fast_attack_craft"):
        return DomainType.SURFACE
    if t in ("submarine", "subsurface", "sub", "kilo-class"):
        return DomainType.SUBSURFACE
    if t in ("uav", "aircraft", "air", "helicopter", "uav", "plane",
             "commercial_airliner", "military_jet", "recon_uav", "drone"):
        return DomainType.AIR
    if t in ("convoy", "ground", "ground_unit", "truck", "armor", "infantry"):
        return DomainType.GROUND
    if t in ("infrastructure", "subsea_cable", "cable", "pipeline",
             "airport", "military_installation", "offshore_platform"):
        return DomainType.INFRASTRUCTURE
    return DomainType.SURFACE  # default to surface


def _in_baltic_bounds(lat: float, lon: float) -> bool:
    return (
        BALTIC_BOUNDS["lat_min"] <= lat <= BALTIC_BOUNDS["lat_max"]
        and BALTIC_BOUNDS["lon_min"] <= lon <= BALTIC_BOUNDS["lon_max"]
    )

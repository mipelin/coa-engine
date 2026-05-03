from __future__ import annotations

import math
from typing import Any

from ..core.schemas import Contact, ContactTrack

EARTH_RADIUS_KM = 6371.0


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    rlat1, rlon1, rlat2, rlon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = rlat2 - rlat1
    dlon = rlon2 - rlon1
    a = math.sin(dlat / 2) ** 2 + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2) ** 2
    return EARTH_RADIUS_KM * 2 * math.asin(math.sqrt(a))


def bearing_to(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Bearing in degrees from point 1 to point 2."""
    rlat1, rlon1, rlat2, rlon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlon = rlon2 - rlon1
    x = math.sin(dlon) * math.cos(rlat2)
    y = math.cos(rlat1) * math.sin(rlat2) - math.sin(rlat1) * math.cos(rlat2) * math.cos(dlon)
    return (math.degrees(math.atan2(x, y)) + 360) % 360


def heading_diff(h1: float, h2: float) -> float:
    d = abs(h1 - h2)
    return min(d, 360 - d)


def enrich_contact(
    contact: Contact,
    track: ContactTrack | None,
    infrastructure: list[dict[str, Any]],
) -> Contact:
    """Add derived fields to a contact: distances, bearings, loitering, heading-toward-infra."""
    attrs = dict(contact.attributes)

    # Distance to nearest infrastructure
    min_dist = float("inf")
    nearest_name = ""
    for infra in infrastructure:
        d = haversine_km(contact.lat, contact.lon, infra["lat"], infra["lon"])
        if d < min_dist:
            min_dist = d
            nearest_name = infra.get("name", "")

    attrs["distance_to_nearest_infra_km"] = round(min_dist, 2)
    attrs["nearest_infra_name"] = nearest_name

    # Heading toward nearest infrastructure
    heading_toward = False
    heading_score = 0.0
    if infrastructure and contact.heading is not None:
        for infra in infrastructure:
            d = haversine_km(contact.lat, contact.lon, infra["lat"], infra["lon"])
            if d > 200:
                continue
            brng = bearing_to(contact.lat, contact.lon, infra["lat"], infra["lon"])
            diff = heading_diff(contact.heading, brng)
            if diff < 30:
                score = 1.0 - diff / 30.0
                if score > heading_score:
                    heading_score = score
                    heading_toward = True

    attrs["heading_toward_infra"] = heading_toward
    attrs["heading_toward_infra_score"] = round(heading_score, 3)

    # Track-derived fields
    if track and len(track.speeds) >= 3:
        recent_speeds = track.speeds[-5:]
        attrs["is_loitering"] = sum(s <= 1.5 for s in recent_speeds) >= len(recent_speeds) * 0.5
        attrs["avg_recent_speed"] = round(sum(recent_speeds) / len(recent_speeds), 2)
    else:
        attrs["is_loitering"] = False

    return contact.model_copy(update={"attributes": attrs})

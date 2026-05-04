from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GeoLabel:
    label: str
    lat_min: float
    lat_max: float
    lon_min: float
    lon_max: float

    def matches(self, lat: float, lon: float) -> bool:
        return self.lat_min <= lat <= self.lat_max and self.lon_min <= lon <= self.lon_max


_GEO_LABELS: tuple[GeoLabel, ...] = (
    GeoLabel("Baltic Sea near Visby", 57.55, 57.75, 18.15, 18.45),
    GeoLabel("Baltic Sea near Gotland", 56.9, 58.1, 18.0, 19.9),
    GeoLabel("Gulf of Riga", 56.8, 58.4, 22.0, 25.3),
    GeoLabel("Baltic Sea south of Gotland", 56.4, 57.2, 18.0, 19.8),
    GeoLabel("Mediterranean Sea near Cyprus", 33.4, 35.8, 31.0, 34.6),
    GeoLabel("Eastern Mediterranean", 33.0, 36.5, 22.0, 36.5),
    GeoLabel("Arctic waters near Svalbard", 76.0, 80.5, 10.0, 24.0),
    GeoLabel("Arctic waters near northern Norway", 68.0, 75.5, 12.0, 30.0),
)


def describe_location(lat: float | None, lon: float | None) -> str:
    if lat is None or lon is None:
        return "Unknown location"
    for item in _GEO_LABELS:
        if item.matches(lat, lon):
            return item.label
    if 54.0 <= lat <= 61.5 and 10.0 <= lon <= 30.0:
        return "Baltic Sea region"
    if 33.0 <= lat <= 37.5 and 22.0 <= lon <= 36.5:
        return "Mediterranean region"
    if 68.0 <= lat <= 81.0 and 10.0 <= lon <= 35.0:
        return "Arctic region"
    return f"WGS84 {lat:.4f}, {lon:.4f}"

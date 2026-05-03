from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class Bounds:
    lat_min: float
    lat_max: float
    lon_min: float
    lon_max: float


SOURCE_REGIONS: dict[str, Bounds] = {
    "baltic_hybrid_001": Bounds(lat_min=32.70, lat_max=33.10, lon_min=-80.20, lon_max=-79.55),
    "arctic_submarine_001": Bounds(lat_min=33.55, lat_max=34.05, lon_min=-118.60, lon_max=-117.70),
    "mediterranean_001": Bounds(lat_min=33.55, lat_max=34.05, lon_min=-118.60, lon_max=-117.70),
}

TARGET_REGIONS: dict[str, Bounds] = {
    "baltic_hybrid_001": Bounds(lat_min=55.00, lat_max=60.00, lon_min=17.00, lon_max=26.00),
    "arctic_submarine_001": Bounds(lat_min=68.00, lat_max=80.00, lon_min=10.00, lon_max=35.00),
    "mediterranean_001": Bounds(lat_min=33.00, lat_max=37.00, lon_min=22.00, lon_max=36.00),
}

SOURCE_LABELS = {
    "baltic_hybrid_001": "NOAA Charleston coastal traffic replay, remapped to Baltic scenario",
    "arctic_submarine_001": "NOAA Southern California traffic replay, remapped to Arctic scenario",
    "mediterranean_001": "NOAA Southern California traffic replay, remapped to Mediterranean scenario",
}


def _within(bounds: Bounds, lat: float, lon: float) -> bool:
    return bounds.lat_min <= lat <= bounds.lat_max and bounds.lon_min <= lon <= bounds.lon_max


def _remap(value: float, src_min: float, src_max: float, dst_min: float, dst_max: float) -> float:
    if src_max == src_min:
        return dst_min
    ratio = (value - src_min) / (src_max - src_min)
    return dst_min + ratio * (dst_max - dst_min)


def _remap_point(lat: float, lon: float, src: Bounds, dst: Bounds) -> tuple[float, float]:
    return (
        round(_remap(lat, src.lat_min, src.lat_max, dst.lat_min, dst.lat_max), 5),
        round(_remap(lon, src.lon_min, src.lon_max, dst.lon_min, dst.lon_max), 5),
    )


def build_replay(csv_path: Path, out_dir: Path, max_tracks: int = 18, max_points_per_track: int = 24) -> None:
    scenario_tracks: dict[str, dict[str, list[dict[str, object]]]] = {
        scenario_id: defaultdict(list) for scenario_id in SOURCE_REGIONS
    }

    with csv_path.open() as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            try:
                lat = float(row["latitude"])
                lon = float(row["longitude"])
                sog = float(row["sog"] or 0.0)
                cog = float(row["cog"] or 0.0)
            except (KeyError, TypeError, ValueError):
                continue
            for scenario_id, bounds in SOURCE_REGIONS.items():
                if not _within(bounds, lat, lon):
                    continue
                track_id = row.get("mmsi") or "unknown"
                track_points = scenario_tracks[scenario_id][track_id]
                if len(scenario_tracks[scenario_id]) > max_tracks and track_id not in scenario_tracks[scenario_id]:
                    continue
                if len(track_points) >= max_points_per_track:
                    continue
                timestamp = row.get("base_date_time") or ""
                vessel_name = row.get("vessel_name") or f"NOAA {track_id}"
                track_points.append({
                    "timestamp": timestamp,
                    "source_lat": lat,
                    "source_lon": lon,
                    "speed": round(sog, 2),
                    "heading": round(cog, 1),
                    "name": vessel_name.strip() or f"NOAA {track_id}",
                    "mmsi": track_id,
                    "imo": (row.get("imo") or "").strip(),
                    "call_sign": (row.get("call_sign") or "").strip(),
                    "vessel_type": (row.get("vessel_type") or "").strip(),
                    "status": (row.get("status") or "").strip(),
                })

    out_dir.mkdir(parents=True, exist_ok=True)
    for scenario_id, tracks in scenario_tracks.items():
        src_bounds = SOURCE_REGIONS[scenario_id]
        dst_bounds = TARGET_REGIONS[scenario_id]
        normalized_tracks: list[dict[str, object]] = []
        for index, (mmsi, points) in enumerate(sorted(tracks.items())[:max_tracks], start=1):
            remapped_points = []
            for point in points:
                lat, lon = _remap_point(point["source_lat"], point["source_lon"], src_bounds, dst_bounds)
                remapped_points.append({
                    "timestamp": point["timestamp"],
                    "lat": lat,
                    "lon": lon,
                    "speed": point["speed"],
                    "heading": point["heading"],
                })
            if len(remapped_points) < 3:
                continue
            normalized_tracks.append({
                "entity_id": f"NOAA-{scenario_id[:3].upper()}-{index:03d}",
                "name": points[0]["name"],
                "mmsi": mmsi,
                "imo": points[0]["imo"],
                "call_sign": points[0]["call_sign"],
                "vessel_type": points[0]["vessel_type"],
                "status": points[0]["status"],
                "points": remapped_points,
            })

        payload = {
            "scenario_id": scenario_id,
            "source": SOURCE_LABELS[scenario_id],
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "tracks": normalized_tracks,
        }
        (out_dir / f"noaa_replay_{scenario_id}.json").write_text(json.dumps(payload, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: build_noaa_replay.py <source_csv> <output_dir>")
    build_replay(Path(sys.argv[1]), Path(sys.argv[2]))

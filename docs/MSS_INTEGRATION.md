# MSS-Compatible Prototype Interface

This repository exposes a prototype integration surface that is compatible with an MSS-style operational workflow.

It is **not** a deployed MSS NATO integration.

## Posture

- REST API with JSON payloads
- Canonical COP endpoint for commander-facing state
- Structured observation ingestion
- Structured event ingestion
- Deterministic analysis outputs
- Replay and after-action review export

Statement of scope:

> This is an MSS-compatible prototype interface, not a deployed MSS NATO integration.

## Architecture Fit

The current interface supports these integration patterns:

- `GET /v1/engine/cop`
  - unified Common Operating Picture for dashboard or external MSS consumer
- `POST /v1/engine/inject`
  - structured contact/observation injection
- `POST /v1/events/ingest`
  - structured operational event ingestion where used
- `GET /v1/engine/analysis`
  - full deterministic analysis snapshot
- `GET /v1/engine/recommendation`
  - advisory recommendation output
- `GET /v1/engine/replay/aar`
  - deterministic after-action review summary

## Data Contracts

Structured observation example:

```json
{
  "contact_id": "OBS-CMS-001",
  "timestamp": "2026-05-03T12:00:00Z",
  "source": "combat_system",
  "contact_type": "vessel",
  "lat": 57.5032,
  "lon": 19.2147,
  "speed": 11.8,
  "heading": 46.0,
  "confidence": 0.84,
  "entity_id": "CMS-VES-001",
  "is_hostile": true,
  "attributes": {
    "subtype": "warship",
    "track_quality": "medium",
    "provenance": "synthetic observation"
  }
}
```

Fused track example:

```json
{
  "track_id": "FUSED-001-AIS-123",
  "primary_entity_id": "AIS-123",
  "correlated_entities": ["AIS-123", "CMS-123"],
  "track_type": "vessel",
  "allegiance": "hostile",
  "fused_confidence": 0.91,
  "source_count": 3,
  "sources": ["aishub", "combat_system", "esm"],
  "position": {"lat": 57.50341, "lon": 19.21455},
  "heading": 45.8,
  "speed": 12.0,
  "rationale": "Track AIS-123 is supported by aishub, combat_system, esm across 3 independent sources.",
  "provenance": "synthetic multi-source observations with deterministic fusion"
}
```

Target example:

```json
{
  "entity_id": "VES-HOT",
  "type": "vessel",
  "priority_level": "HIGH",
  "priority_score": 68.4,
  "recommended_action": "shadow",
  "roe_status": "allowed",
  "sources": ["aishub", "combat_system", "fusion", "behavior"],
  "supporting_asset": {
    "target_id": "VES-HOT",
    "assigned_asset_id": "maritime_patrol_vessel",
    "asset_type": "maritime_patrol_vessel",
    "assignment_role": "shadow",
    "suitability_score": 79.5,
    "constraints": [],
    "rationale": "Maritime Patrol Vessel is the best available advisory support asset to shadow for a vessel target; response ETA 60 min; suitability 79.5",
    "roe_status": "allowed"
  }
}
```

Recommendation example:

```json
{
  "recommended": {
    "coa": {
      "coa_id": "COA-TPL-CABLE-PROTECT",
      "title": "Protect Remaining Subsea Cable",
      "roe_status": "allowed"
    },
    "total_score": 84.6
  },
  "rationale": "ROE-constrained recommendation favors infrastructure protection under elevated hostile intent.",
  "edge_cases": "Escalation risk increases if jamming expands."
}
```

AAR example:

```json
{
  "situation_summary": "Synthetic multi-source observations indicated escalation near Baltic cable infrastructure.",
  "major_events": ["Cable severance", "Jamming detected", "Recommendation changed"],
  "decisions_recommended": ["Protect remaining cable", "Increase ISR coverage"],
  "lessons_learned": ["Deterministic fusion improved confidence before recommendation shifts."]
}
```

## Practical Integration Notes

- COP-first consumption is recommended for dashboards and demo clients.
- Raw contacts and synthetic observations remain available for provenance inspection.
- LLM outputs are explanation-only and are not part of the authoritative decision path.

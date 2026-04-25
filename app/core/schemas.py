from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from .constants import AnomalyLevel, EntityType, EventType, ThreatLevel
from .weights import ScenarioWeights


class OperationalEvent(BaseModel):
    event_id: str
    timestamp: datetime
    event_type: EventType
    source: str
    confidence: float = Field(ge=0.0, le=1.0)
    lat: float
    lon: float
    entity_id: str
    entity_type: EntityType
    description: str
    attributes: dict[str, Any] = Field(default_factory=dict)


class CriticalInfrastructure(BaseModel):
    name: str
    type: str
    lat: float
    lon: float


class Scenario(BaseModel):
    scenario_id: str
    name: str
    description: str
    timeframe: str
    critical_infrastructure: list[CriticalInfrastructure] = Field(default_factory=list)
    events: list[OperationalEvent] = Field(default_factory=list)
    entities: dict[str, dict[str, Any]] = Field(default_factory=dict)
    bounds: dict[str, float] | None = None
    weights: ScenarioWeights | None = None


class EventBatch(BaseModel):
    events: list[OperationalEvent]


class FeatureVector(BaseModel):
    event_id: str
    entity_id: str
    distance_to_nearest_critical_infrastructure: float
    distance_to_second_cable: float
    course_change_count: int
    speed_anomaly_score: float
    proximity_to_recent_incident: float
    multi_source_correlation_score: float
    event_density_score: float
    source_confidence_weight: float
    jamming_nearby: float
    convoy_activity_nearby: float
    time_since_cable_severance: float
    heading_towards_critical_asset: float


class AnomalyResult(BaseModel):
    event_id: str
    entity_id: str
    anomaly_score: float = Field(ge=0.0, le=100.0)
    anomaly_level: AnomalyLevel
    explanations: list[str]


class ThreatResult(BaseModel):
    entity_id: str
    threat_probability: float = Field(ge=0.0, le=1.0)
    threat_level: ThreatLevel
    confidence: float
    main_drivers: list[str]


class CourseOfAction(BaseModel):
    coa_id: str
    title: str
    description: str
    required_assets: list[str]
    available_assets: list[str] = Field(default_factory=list)
    missing_assets: list[str] = Field(default_factory=list)
    feasibility_score: float = Field(default=1.0, ge=0.0, le=1.0)
    assumptions: list[str]
    estimated_time_minutes: int
    expected_effect: str
    risk_categories: list[str]
    escalation_risk: float = Field(ge=0.0, le=1.0)
    civilian_risk: float = Field(ge=0.0, le=1.0)
    logistics_burden: float = Field(ge=0.0, le=1.0)


class SimulationResult(BaseModel):
    coa_id: str
    success_probability: float
    expected_time_to_effect: float
    risk_to_second_cable: float
    escalation_probability: float
    missed_detection_probability: float
    confidence_interval: tuple[float, float]
    simulation_runs: int


class ScoredCOA(BaseModel):
    coa: CourseOfAction
    simulation: SimulationResult
    total_score: float = Field(ge=0.0, le=100.0)
    rank: int
    tradeoff_explanation: str


class Recommendation(BaseModel):
    recommended: ScoredCOA | None
    alternatives: list[ScoredCOA]
    rationale: str
    edge_cases: str
    threat_narrative: str | None = None


class Briefing(BaseModel):
    situation: str
    key_indicators: list[str]
    assessment: str
    coas_considered: list[str]
    recommended_coa: str
    risks: list[str]
    confidence: str
    assumptions: list[str]
    enriched_assessment: str | None = None
    entity_risk_narratives: dict[str, str] | None = None


class AnalysisRequest(BaseModel):
    scenario_id: str | None = None
    events: list[OperationalEvent] | None = None
    use_session: bool = True
    asset_inventory: dict[str, int] | None = None


class HealthResponse(BaseModel):
    status: str
    version: str


class TrackInfo(BaseModel):
    entity_id: str
    position_count: int
    total_distance_km: float
    avg_speed_knots: float | None
    is_loitering: bool
    velocity_bearing: float | None
    velocity_speed: float | None


class TemporalSummary(BaseModel):
    event_rate_per_hour: float
    escalation_rate: float
    severity_trend: str
    cluster_count: int
    mean_inter_event_minutes: float | None = None

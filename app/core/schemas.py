from __future__ import annotations

from datetime import datetime
from enum import Enum
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
    allegiance: str = ""
    is_threat_candidate: bool = True
    is_infrastructure: bool = False


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
    allied_proximity_score: float = 0.0


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
    template_id: str
    title: str
    description: str
    target_entities: list[str] = Field(default_factory=list)
    required_assets: list[str]
    assigned_assets: list[str] = Field(default_factory=list)
    available_assets: list[str] = Field(default_factory=list)
    missing_assets: list[str] = Field(default_factory=list)
    objective: str = ""
    rationale: str = ""
    feasibility_score: float = Field(default=1.0, ge=0.0, le=1.0)
    feasibility_status: str = "unknown"
    validation_warnings: list[str] = Field(default_factory=list)
    assumptions: list[str]
    estimated_time_minutes: int
    expected_effect: str
    risk_categories: list[str]
    escalation_risk: float = Field(ge=0.0, le=1.0)
    civilian_risk: float = Field(ge=0.0, le=1.0)
    logistics_burden: float = Field(ge=0.0, le=1.0)
    source: str = "template_engine"
    localized: dict[str, dict[str, Any]] | None = None
    roe_status: str = "allowed"
    roe_reason: str = ""
    roe_constraints_triggered: list[str] = Field(default_factory=list)


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


class PlanTask(BaseModel):
    task_id: str
    task_type: str
    title: str
    description: str
    target_entities: list[str] = Field(default_factory=list)
    assigned_assets: list[str] = Field(default_factory=list)
    required_capabilities: list[str] = Field(default_factory=list)
    start_offset_min: int = Field(default=0, ge=0)
    duration_min: int = Field(default=0, ge=0)
    preconditions: list[str] = Field(default_factory=list)
    expected_effect: str = ""
    localized: dict[str, dict[str, Any]] | None = None


class DependencyEdge(BaseModel):
    predecessor_task_id: str
    successor_task_id: str
    dependency_type: str = "finish_to_start"
    condition: str | None = None
    localized: dict[str, dict[str, Any]] | None = None


class PlanPackage(BaseModel):
    package_id: str
    title: str
    summary: str
    tasks: list[PlanTask] = Field(default_factory=list)
    dependencies: list[DependencyEdge] = Field(default_factory=list)
    reserved_assets: list[str] = Field(default_factory=list)
    planning_assumptions: list[str] = Field(default_factory=list)
    localized: dict[str, dict[str, Any]] | None = None


class ScoredCOAPackage(BaseModel):
    package_id: str
    coas: list[ScoredCOA]
    plan: PlanPackage | None = None
    combined_assets: list[str] = Field(default_factory=list)
    feasibility_score: float = Field(default=1.0, ge=0.0, le=1.0)
    total_score: float = Field(ge=0.0, le=100.0)
    rank: int
    tradeoff_explanation: str


class Recommendation(BaseModel):
    recommended: ScoredCOA | None
    alternatives: list[ScoredCOA]
    recommended_package: ScoredCOAPackage | None = None
    alternative_packages: list[ScoredCOAPackage] = Field(default_factory=list)
    rationale: str
    edge_cases: str
    threat_narrative: str | None = None


class Briefing(BaseModel):
    situation: str
    what_changed: list[str] = Field(default_factory=list)
    recent_developments: list[str] = Field(default_factory=list)
    key_indicators: list[str]
    assessment: str
    key_actors: list[str] = Field(default_factory=list)
    coas_considered: list[str]
    recommended_coa: str
    roe_status: str | None = None
    risks: list[str]
    confidence: str
    assumptions: list[str]
    language: str = "en"
    language_used: str = "en"
    enriched_assessment: str | None = None
    entity_risk_narratives: dict[str, str] | None = None
    llm_used: bool = False
    llm_enriched: bool = False
    fallback_reason: str | None = None


class AnalysisRequest(BaseModel):
    scenario_id: str | None = None
    events: list[OperationalEvent] | None = None
    use_session: bool = True
    asset_inventory: dict[str, int] | None = None
    asset_states: list["AssetState"] | None = None


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


# ---------------------------------------------------------------------------
# Contact ingestion — real-time contact model
# ---------------------------------------------------------------------------

class ContactType(str, Enum):
    VESSEL = "vessel"
    UAV = "uav"
    CONVOY = "convoy"
    INFRASTRUCTURE = "infrastructure"
    JAMMING = "jamming"
    CABLE_EVENT = "cable_event"
    SUBMARINE = "submarine"
    RADAR = "radar"
    SIGINT = "sigint"
    UNKNOWN = "unknown"


class Contact(BaseModel):
    contact_id: str
    timestamp: datetime
    source: str
    contact_type: ContactType
    lat: float
    lon: float
    speed: float = 0.0
    heading: float = 0.0
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    entity_id: str
    is_hostile: bool = False
    attributes: dict[str, Any] = Field(default_factory=dict)


class ContactBatch(BaseModel):
    contacts: list[Contact]


class ContactUpdateRequest(BaseModel):
    name: str | None = None
    contact_type: ContactType | None = None
    is_hostile: bool | None = None
    lat: float | None = None
    lon: float | None = None
    speed: float | None = None
    heading: float | None = None
    attributes: dict[str, Any] | None = None


class CombatContactToggleRequest(BaseModel):
    enabled: bool | None = None
    density: str | None = None
    scenario_type: str | None = None


class CombatContactInjectRequest(BaseModel):
    kind: str = "aircraft"
    subtype: str | None = None
    suspicious: bool = False
    allegiance: str | None = None
    lat: float | None = None
    lon: float | None = None
    heading: float | None = None
    speed: float | None = None
    altitude_ft: float | None = None
    depth_m: float | None = None
    sensor_source: str | None = None
    track_quality: str | None = None
    timestamp: datetime | None = None


class EngineActionRequest(BaseModel):
    entity_id: str | None = None
    action: str
    execute_tick: int | None = None
    lat: float | None = None
    lon: float | None = None
    new_heading: float | None = None
    new_speed: float | None = None
    radius_nm: float | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)


class ContactTrack(BaseModel):
    entity_id: str
    positions: list[tuple[datetime, float, float]] = Field(default_factory=list)
    speeds: list[float] = Field(default_factory=list)
    headings: list[float] = Field(default_factory=list)
    last_contact: datetime | None = None
    is_loitering: bool = False
    heading_toward_infra: bool = False


class AssetState(BaseModel):
    asset_id: str
    asset_type: str
    capabilities: list[str] = Field(default_factory=list)
    quantity_total: int = Field(ge=0)
    quantity_available: int = Field(ge=0)
    status: str = "available"
    domain: str | None = None
    display_name: str | None = None
    location_label: str | None = None
    home_base: str | None = None
    lat: float | None = None
    lon: float | None = None
    coverage_radius_km: float | None = Field(default=None, ge=0.0)
    transit_speed_kts: float | None = Field(default=None, ge=0.0)
    response_eta_min: int | None = Field(default=None, ge=0)
    endurance_hours: float | None = Field(default=None, ge=0.0)
    on_station_hours: float | None = Field(default=None, ge=0.0)
    concurrency_limit: int = Field(default=1, ge=1)
    notes: str | None = None


class ScenarioState(BaseModel):
    scenario_id: str | None = None
    scenario_name: str | None = None
    mode: str = "simulation"
    infrastructure_status: str = "nominal"
    active_incidents: list[str] = Field(default_factory=list)
    last_updated: datetime | None = None
    seed: int | None = None
    timing_jitter: int = 0
    position_jitter: float = 0.0
    environment: dict[str, Any] = Field(default_factory=dict)
    upcoming_stimuli_count: int = 0
    active_stimuli_count: int = 0
    fired_stimuli_count: int = 0
    combat_contacts_enabled: bool = False
    combat_contacts_density: str = "medium"
    combat_contacts_scenario_type: str = "mixed"
    combat_contacts_last_update: datetime | None = None


class EngineState(BaseModel):
    tick: int = 0
    active_contacts: int = 0
    active_tracks: int = 0
    current_threat_level: str = "LOW"
    top_threat_entity: str | None = None
    top_threat_probability: float = 0.0
    recommended_coa_id: str | None = None
    recommended_coa_score: float = 0.0
    last_analysis_tick: int = 0
    llm_calls_made: int = 0
    ui_language: str = "en"
    contacts_processed: int = 0
    active_asset_types: int = 0
    available_asset_units: int = 0
    scenario: ScenarioState = Field(default_factory=ScenarioState)


class EventSummary(BaseModel):
    tick: int = 0
    event_type: str = "none"
    summary_text: str = ""
    timestamp: datetime | None = None
    llm_used: bool = False
    language_used: str = "en"
    fallback_reason: str | None = None


class LLMStatus(BaseModel):
    busy: bool = False
    queue_length: int = 0
    current_task_type: str | None = None
    last_error: str | None = None
    last_summary: EventSummary | None = None

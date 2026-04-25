from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "COA Engine"
    app_version: str = "0.2.0"
    debug: bool = False
    simulation_runs: int = 1000

    # Anomaly thresholds
    anomaly_threshold_medium: float = 40.0
    anomaly_threshold_high: float = 65.0
    anomaly_threshold_critical: float = 85.0

    # Threat thresholds
    threat_threshold_medium: float = 0.3
    threat_threshold_high: float = 0.6
    threat_threshold_critical: float = 0.8

    # Threat assessment weights
    threat_weight_max_anomaly: float = 0.40
    threat_weight_avg_anomaly: float = 0.15
    threat_weight_event_type_boost: float = 0.30
    threat_weight_heading: float = 0.08
    threat_weight_jamming: float = 0.07
    threat_weight_convoy: float = 0.05
    threat_cable_severance_vessel_boost: float = 0.10
    threat_uav_heading_boost: float = 0.05

    # Scoring weights
    scoring_weight_success: float = 0.30
    scoring_weight_time: float = 0.10
    scoring_weight_cable_protect: float = 0.20
    scoring_weight_escalation: float = 0.15
    scoring_weight_civilian: float = 0.10
    scoring_weight_logistics: float = 0.05
    scoring_weight_missed_detection: float = 0.10

    # Anomaly rule weights
    anomaly_cable_severance_pts: float = 55.0
    anomaly_proximity_threshold_close: float = 5.0
    anomaly_proximity_pts_close: float = 20.0
    anomaly_proximity_threshold_mid: float = 20.0
    anomaly_proximity_pts_mid: float = 8.0
    anomaly_suspicious_vessel_near_cable_threshold: float = 10.0
    anomaly_suspicious_vessel_near_cable_pts: float = 15.0
    anomaly_course_change_multi_pts: float = 12.0
    anomaly_course_change_multi_min: int = 2
    anomaly_course_change_single_pts: float = 5.0
    anomaly_heading_strong_threshold: float = 0.7
    anomaly_heading_strong_pts: float = 10.0
    anomaly_heading_partial_threshold: float = 0.3
    anomaly_heading_partial_pts: float = 4.0
    anomaly_speed_anomaly_high_threshold: float = 0.5
    anomaly_speed_anomaly_high_pts: float = 10.0
    anomaly_speed_anomaly_mid_threshold: float = 0.2
    anomaly_speed_anomaly_mid_pts: float = 4.0
    anomaly_uav_detection_pts: float = 15.0
    anomaly_jamming_high_threshold: float = 0.5
    anomaly_jamming_high_pts: float = 12.0
    anomaly_jamming_edge_pts: float = 5.0
    anomaly_multisource_high_threshold: float = 0.75
    anomaly_multisource_high_pts: float = 10.0
    anomaly_multisource_mid_threshold: float = 0.5
    anomaly_multisource_mid_pts: float = 4.0
    anomaly_convoy_proximity_pts: float = 5.0
    anomaly_convoy_region_pts: float = 2.0
    anomaly_density_pts: float = 5.0
    anomaly_post_severance_window_min: float = 120.0
    anomaly_post_severance_pts: float = 5.0
    anomaly_low_confidence_dampener: float = 0.7

    # Simulation
    simulation_seed: int = 42
    simulation_base_success: float = 0.50
    simulation_monitor_boost: float = 0.15
    simulation_shadow_boost: float = 0.20
    simulation_cable_protect_boost: float = 0.25
    simulation_combined_boost: float = 0.30

    # LLM configuration
    llm_base_url: str = "http://192.168.4.13:8080/v1"
    llm_api_key: str = "sk-mi-ia-secreta"
    llm_model: str = "gemma4"
    llm_timeout_seconds: float = 300.0
    llm_enabled: bool = True
    llm_max_tokens: int = 2048

    # API Security
    api_key_auth_enabled: bool = False
    api_keys_csv: str = ""
    cors_origins_csv: str = "http://localhost:8501"
    rate_limit_per_minute: int = 60

    # Session
    session_max_events: int = 5000

    model_config = {"env_prefix": "COA_"}


settings = Settings()

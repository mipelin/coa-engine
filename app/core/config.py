from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "COA Engine"
    app_version: str = "0.1.0"
    debug: bool = False
    simulation_runs: int = 1000
    anomaly_threshold_medium: float = 40.0
    anomaly_threshold_high: float = 65.0
    anomaly_threshold_critical: float = 85.0
    threat_threshold_medium: float = 0.3
    threat_threshold_high: float = 0.6
    threat_threshold_critical: float = 0.8

    model_config = {"env_prefix": "COA_"}


settings = Settings()

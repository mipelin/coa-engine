import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.schemas import OperationalEvent
from app.core.session import reset_session
from app.engine.contact_engine import get_contact_engine
from app.engine.ais_feed import get_ais_feed
from app.engine.noaa_replay import get_noaa_replay_feed
from app.engine.event_bus import get_event_bus
from app.engine.event_ingestion import load_sample_scenario, load_scenario_events
from app.engine.event_loop import get_event_loop
from app.engine.state_store import get_state_store
from app.engine.llm_client import reset_llm_client
from app.engine.llm_orchestrator import reset_llm_orchestrator
from app.main import app

API_PREFIX = "/v1"


@pytest.fixture(autouse=True)
def clean_session():
    """Reset session state before each test."""
    settings.rate_limit_enabled = False
    reset_session()
    get_contact_engine().reset()
    get_state_store().clear()
    get_event_bus().clear()
    get_event_loop().reset_runtime_state()
    get_ais_feed().reset()
    get_noaa_replay_feed().reset()
    reset_llm_client()
    reset_llm_orchestrator()
    yield
    settings.rate_limit_enabled = True
    reset_session()
    get_contact_engine().reset()
    get_state_store().clear()
    get_event_bus().clear()
    get_event_loop().reset_runtime_state()
    get_ais_feed().reset()
    get_noaa_replay_feed().reset()
    reset_llm_client()
    reset_llm_orchestrator()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def baltic_events():
    return load_scenario_events()


@pytest.fixture
def baltic_scenario():
    return load_sample_scenario()


@pytest.fixture
def sample_event():
    return OperationalEvent(
        event_id="TEST-001",
        timestamp="2025-06-15T08:00:00Z",
        event_type="vessel_position",
        source="test",
        confidence=0.9,
        lat=57.5,
        lon=19.0,
        entity_id="VES-TEST",
        entity_type="suspicious_vessel",
        description="Test event",
        attributes={"speed_knots": 0.5, "heading": 90.0},
    )


@pytest.fixture
def sample_event_json():
    return {
        "event_id": "TEST-001",
        "timestamp": "2025-06-15T08:00:00Z",
        "event_type": "vessel_position",
        "source": "test",
        "confidence": 0.9,
        "lat": 57.5,
        "lon": 19.0,
        "entity_id": "VES-TEST",
        "entity_type": "suspicious_vessel",
        "description": "Test event",
        "attributes": {"speed_knots": 0.5, "heading": 90.0},
    }


@pytest.fixture
def unsafe_words():
    return [
        "target", "weapon", "strike", "engage", "kill", "lethal",
        "execute order", "fire", "destroy", "neutralize",
    ]

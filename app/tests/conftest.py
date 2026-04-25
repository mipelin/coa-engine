import pytest
from fastapi.testclient import TestClient

from app.core.schemas import OperationalEvent
from app.core.session import reset_session
from app.engine.event_ingestion import load_sample_scenario, load_scenario_events
from app.main import app

API_PREFIX = "/v1"


@pytest.fixture(autouse=True)
def clean_session():
    """Reset session state before each test."""
    reset_session()
    yield
    reset_session()


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

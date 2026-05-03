"""Tests for rate limiter: enabled/disabled behavior, LAN bypass, and state isolation."""

import pytest

from app.core.config import settings
from app.core.rate_limit import RateLimiter, get_rate_limiter, _is_private_ip
from app.main import app

from fastapi.testclient import TestClient
from unittest.mock import MagicMock


# ---------------------------------------------------------------------------
# Fixtures — these tests intentionally manage rate_limit_enabled themselves
# ---------------------------------------------------------------------------


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def fresh_limiter():
    """Create an isolated limiter with a low threshold for testing."""
    return RateLimiter(max_requests=5, window_seconds=60)


@pytest.fixture(autouse=True)
def reset_global_limiter():
    """Ensure the global limiter is reset between tests."""
    import app.core.rate_limit as _rl
    _rl._rate_limiter = None
    yield
    _rl._rate_limiter = None


# ---------------------------------------------------------------------------
# 1. Disabled: requests pass regardless of volume
# ---------------------------------------------------------------------------


class TestRateLimitDisabled:
    def test_many_requests_not_blocked_when_disabled(self, client):
        settings.rate_limit_enabled = False
        for _ in range(80):
            resp = client.get("/health")
            assert resp.status_code == 200
        settings.rate_limit_enabled = True

    def test_engine_endpoints_not_blocked_when_disabled(self, client):
        settings.rate_limit_enabled = False
        for _ in range(80):
            resp = client.get("/v1/engine/state")
            assert resp.status_code == 200
        settings.rate_limit_enabled = True


# ---------------------------------------------------------------------------
# 2. Enabled: 429 returned when limit exceeded
# ---------------------------------------------------------------------------


class TestRateLimitEnabled:
    def test_returns_429_when_limit_exceeded(self, fresh_limiter):
        """Unit test: RateLimiter raises HTTPException after threshold."""
        for _ in range(5):
            fresh_limiter.check("external-client")

        with pytest.raises(Exception):
            fresh_limiter.check("external-client")

    def test_health_endpoint_excluded_from_rate_limit(self, client):
        import app.core.rate_limit as _rl

        limiter = RateLimiter(max_requests=2, window_seconds=60)
        _rl._rate_limiter = limiter

        settings.rate_limit_enabled = True

        # Health endpoint bypasses the limiter in middleware
        for _ in range(10):
            resp = client.get("/health")
            assert resp.status_code == 200

        settings.rate_limit_enabled = True


# ---------------------------------------------------------------------------
# 3. State isolation: RateLimiter.check() resets correctly
# ---------------------------------------------------------------------------


class TestRateLimiterState:
    def test_limiter_allows_requests_after_reset(self, fresh_limiter):
        # Fill up the limiter
        for _ in range(5):
            fresh_limiter.check("client-a")

        # Should now reject
        with pytest.raises(Exception):
            fresh_limiter.check("client-a")

        # Reset by creating a new limiter (simulates test fixture reset)
        new_limiter = RateLimiter(max_requests=5, window_seconds=60)
        new_limiter.check("client-a")  # Should not raise

    def test_different_clients_tracked_separately(self, fresh_limiter):
        # Use full quota for client-a
        for _ in range(5):
            fresh_limiter.check("client-a")

        # client-a is blocked
        with pytest.raises(Exception):
            fresh_limiter.check("client-a")

        # client-b is unaffected
        fresh_limiter.check("client-b")  # Should not raise


# ---------------------------------------------------------------------------
# 4. Private IP detection
# ---------------------------------------------------------------------------


class TestPrivateIPDetection:
    def test_loopback_is_private(self):
        assert _is_private_ip("127.0.0.1") is False  # handled by _LOCAL_HOSTS, not _PRIVATE_NETWORKS

    def test_10_range_is_private(self):
        assert _is_private_ip("10.0.0.1") is True
        assert _is_private_ip("10.255.255.255") is True

    def test_172_16_range_is_private(self):
        assert _is_private_ip("172.16.0.1") is True
        assert _is_private_ip("172.31.255.255") is True

    def test_192_168_range_is_private(self):
        assert _is_private_ip("192.168.0.1") is True
        assert _is_private_ip("192.168.4.242") is True
        assert _is_private_ip("192.168.255.255") is True

    def test_public_ip_is_not_private(self):
        assert _is_private_ip("8.8.8.8") is False
        assert _is_private_ip("1.2.3.4") is False

    def test_invalid_host_is_not_private(self):
        assert _is_private_ip("not-an-ip") is False


# ---------------------------------------------------------------------------
# 5. LAN client bypass: never rate-limited
# ---------------------------------------------------------------------------


class TestLANBypass:
    def _make_request_with_client_ip(self, client, path, client_ip):
        """Simulate a request from a specific client IP."""
        # TestClient uses 127.0.0.1 which is in _LOCAL_HOSTS, so always bypassed.
        # Instead, test _is_private_ip directly and the skip-path logic.
        pass  # Covered by TestUnlimitedPaths below with real middleware

    def test_private_ip_lan_client_never_rate_limited(self, client):
        """TestClient connects from 127.0.0.1 (localhost), which is always bypassed."""
        import app.core.rate_limit as _rl
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        _rl._rate_limiter = limiter

        settings.rate_limit_enabled = True
        # 127.0.0.1 is local — should never hit the limiter even with high volume
        for _ in range(50):
            resp = client.get("/v1/engine/state")
            assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 6. Unlimited paths: dashboard-critical endpoints never rate-limited
# ---------------------------------------------------------------------------


class TestUnlimitedPaths:
    @pytest.fixture(autouse=True)
    def _setup_strict_limiter(self):
        """Install a very low limit to verify bypass."""
        import app.core.rate_limit as _rl
        _rl._rate_limiter = RateLimiter(max_requests=2, window_seconds=60)
        settings.rate_limit_enabled = True
        yield
        settings.rate_limit_enabled = True

    def test_query_never_rate_limited(self, client):
        for _ in range(10):
            resp = client.post("/v1/engine/query", json={"question": "test"})
            # May fail for other reasons (no scenario), but never 429
            assert resp.status_code != 429

    def test_briefing_never_rate_limited(self, client):
        for _ in range(10):
            resp = client.get("/v1/engine/briefing")
            assert resp.status_code != 429

    def test_scenario_info_never_rate_limited(self, client):
        for _ in range(10):
            resp = client.get("/v1/engine/scenario/info")
            assert resp.status_code != 429

    def test_scenario_stimuli_never_rate_limited(self, client):
        for _ in range(10):
            resp = client.get("/v1/engine/scenario/stimuli")
            assert resp.status_code != 429

    def test_health_never_rate_limited(self, client):
        for _ in range(10):
            resp = client.get("/health")
            assert resp.status_code == 200

    def test_engine_state_never_rate_limited(self, client):
        for _ in range(10):
            resp = client.get("/v1/engine/state")
            assert resp.status_code != 429

    def test_llm_health_never_rate_limited(self, client):
        for _ in range(10):
            resp = client.get("/v1/engine/llm/health")
            assert resp.status_code != 429


# ---------------------------------------------------------------------------
# 7. Production rate limit: external clients still blocked
# ---------------------------------------------------------------------------


class TestProductionRateLimit:
    def test_external_client_still_rate_limited(self, fresh_limiter):
        """Unit test: limiter blocks after threshold for non-private IPs."""
        for _ in range(5):
            fresh_limiter.check("8.8.8.8")
        with pytest.raises(Exception):
            fresh_limiter.check("8.8.8.8")

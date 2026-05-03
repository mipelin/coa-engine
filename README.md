# COA Engine — Decision Superiority Module

A working prototype of an AI-assisted Course of Action (COA) analysis engine for operational decision support. Built for the NATO DIANA innovation framework.

## What This System Does

- Loads synthetic maritime scenarios (Baltic, Arctic, Mediterranean) with hostile, friendly, and neutral entities
- Runs a tick-based simulation with behavior models (hostile probe, loiter-and-divert, friendly patrol, neutral transit)
- Produces synthetic multi-source observations and deterministic fusion for a unified operational picture
- Detects anomalies, assesses threats, and generates explainable threat probabilities per entity
- Generates advisory targeting support with deterministic supporting-asset suggestions
- Generates ROE-constrained recommendations, simulates outcomes with Monte Carlo methods, scores and ranks them
- Evaluates Rules of Engagement (ROE) per COA — restricted actions are flagged, rejected actions are excluded
- Produces commander-style briefings with LLM explanation-only enrichment
- Accepts natural-language queries about current state, with deterministic fallbacks when no LLM is available
- Provides "what-if" forecasting grounded in simulation — the LLM may rephrase forecasts but never invents them
- Serves an operational dashboard with live map, contact tracking, COA ranking, and NL query interface

## What This System Does NOT Do

- **No autonomous targeting or lethal engagement** — advisory outputs only
- **No command execution** — all recommendations require human approval
- **No classified data** — all data is synthetic and open-source
- **No real NATO integrations** — MSS-compatible prototype with clear API boundaries
- **No live data feeds in default mode** — runs on local synthetic data (AIS/NOAA replay available when configured)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest app/tests/ -v

# Start the engine (dashboard + API)
./run_ui.sh
```

Then open:
- **Dashboard**: http://localhost:8002/dashboard
- **API docs**: http://localhost:8002/docs

The FastAPI dashboard is the only supported operator UI for this prototype.

For LLM-enhanced briefings and narratives, create a `.env` file (see `.env.example`).

## LLM Configuration (llama.cpp)

The engine uses an OpenAI-compatible endpoint (llama.cpp server). Set these in `.env`:

```bash
COA_LLM_ENABLED=true
COA_LLM_BASE_URL=http://192.168.4.14:8080/v1    # your llama.cpp server
COA_LLM_API_KEY=                                 # optional — leave empty for llama.cpp (no auth)
COA_LLM_MODEL=local                              # model name the server expects
```

When `COA_LLM_ENABLED=false` (or when the server is unreachable), all features fall back to deterministic answers — the engine works fully without an LLM.

**Test the llama.cpp server with curl:**

```bash
curl http://192.168.4.14:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "local",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 32
  }'
```

A successful response returns JSON with `choices[0].message.content`. A connection error means the server is not running or the URL is wrong — the engine will log a warning and use deterministic fallbacks.

## Architecture

```
coa_engine/
  app/
    main.py                     # FastAPI application, CORS, rate limiting middleware
    api/                        # REST API route handlers
      routes_engine.py          # Real-time engine control (tick, inject, query, state)
      routes_analysis.py        # Legacy analysis pipeline
      routes_coa.py             # COA generation, simulation, recommendation, briefing
      routes_events.py          # Event ingestion
      routes_scenarios.py       # Scenario loading (legacy)
      routes_sse.py             # Server-Sent Events / WebSocket streaming
      routes_dashboard.py       # Dashboard HTML serving
    core/
      schemas.py                # Pydantic data models (all API contracts)
      config.py                 # Settings (env-prefixed, tunable weights)
      constants.py              # Event types, entity types, infrastructure, behavior weights
      weights.py                # Scenario-specific weight overrides
      rate_limit.py             # Configurable rate limiter (disabled in tests)
      api_client.py             # Python client for the REST API
    engine/                     # Analytic modules (independent of FastAPI)
      contact_engine.py         # Real-time contact ingestion (simulation/hybrid/live modes)
      scenario_generator.py     # Scenario templates (Baltic, Arctic, Mediterranean)
      behavior_models.py        # Deterministic behavior policies for entity movement
      isr_simulation.py         # Synthetic multi-source observation plugins
      behavior_features.py      # Behavior-mode feature extraction
      contact_enrichment.py     # Distance-to-infra, heading-toward, loitering detection
      event_engine.py           # External event processing (cable, jamming, course changes)
      roe_engine.py             # Rules of Engagement evaluation
      feature_engineering.py    # Spatial features (haversine distances, anomaly signals)
      anomaly_detection.py      # Rule-based anomaly scoring (0–100) with explanations
      threat_assessment.py      # Entity-level threat probability aggregation
      asset_assignment.py       # Advisory supporting-asset assignment for top targets
      coa_generation.py         # Template-based advisory COA generation
      coa_templates.py          # COA template definitions and selection logic
      coa_validation.py         # Asset feasibility and spatial validation
      simulation.py             # Monte Carlo simulation (seeded, deterministic)
      scoring.py                # Weighted multi-criteria COA scoring
      recommendation.py         # Top-COA selection with rationale and alternatives
      portfolio.py              # Multi-COA portfolio (combined packages)
      plan_packages.py          # Task-level plan generation for packages
      explanation.py            # Commander briefing generation
      query_engine.py           # Natural-language query with guardrails
      forecasting.py            # What-if forecasting (simulation-based, LLM-free)
      event_loop.py             # Reactive analysis loop (tick-driven + event-triggered)
      engine_scheduler.py       # Background tick scheduler with SSE subscriptions
      state_store.py            # Thread-safe in-memory state store
      event_bus.py              # Pub/sub event bus for real-time updates
      persistence.py            # SQLite state persistence with auto-save
      llm_client.py             # LLM integration (optional, explanation-only)
      llm_narrative.py          # Threat narrative and briefing enrichment
      entity_catalog.py         # Entity type registry
      entity_tracking.py        # Track management and position history
      asset_state.py            # Asset state management and catalog
      noaa_replay.py            # NOAA replay dataset feed
      ais_feed.py               # AIS feed integration (AISHub)
      time_series.py            # Temporal event analysis
    i18n/
      static_translations.py    # COA template translations
    ui/
      dashboard_build.py        # Dashboard HTML/JS/CSS builder for the FastAPI dashboard
    data/
      sample_scenario_baltic.json
      sample_scenario_arctic.json
      sample_scenario_mediterranean.json
      noaa_replay_baltic_hybrid_001.json
      noaa_replay_arctic_submarine_001.json
      noaa_replay_mediterranean_001.json
    tests/                      # automated engine, API, UI, and safety coverage
      test_phase1.py ... test_rate_limit.py
```

The engine layer is independent of FastAPI. All analysis modules use deterministic functions with Pydantic schemas.

MSS posture:
- This is an MSS-compatible prototype interface, not a deployed MSS NATO integration.
- See [docs/MSS_INTEGRATION.md](docs/MSS_INTEGRATION.md) for payload contracts and integration posture.

## Real-Time Engine API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/engine/scenario/load` | Load scenario by ID |
| POST | `/engine/scenario/{id}` | Load scenario (alt) |
| GET | `/engine/scenario/templates` | List available scenario templates |
| GET | `/engine/scenario/info` | Current scenario metadata |
| GET | `/engine/scenario/stimuli` | Upcoming/fired stimuli |
| POST | `/engine/tick` | Advance one tick (triggers reactive analysis) |
| POST | `/engine/start` | Start auto-tick scheduler |
| POST | `/engine/stop` | Stop scheduler |
| POST | `/engine/reset` | Reset engine state |
| GET | `/engine/state` | Current engine state (tick, threat level, contacts) |
| GET | `/engine/contacts` | Active contacts |
| GET | `/engine/contacts/history` | Contact history |
| GET | `/engine/tracks` | Contact tracks with positions |
| PATCH | `/engine/contacts/{id}` | Update a contact |
| GET | `/engine/threats` | Threat assessment results |
| GET | `/engine/coas` | Scored COAs |
| GET | `/engine/recommendation` | Current recommendation |
| GET | `/engine/analysis` | Full analysis snapshot |
| GET | `/engine/briefing` | Commander briefing |
| GET | `/engine/assets` | Asset inventory |
| POST | `/engine/assets` | Set asset inventory |
| POST | `/engine/inject` | Inject contacts (triggers re-analysis) |
| DELETE | `/engine/inject/{id}` | Remove injected contact |
| POST | `/engine/actions` | Schedule a future action |
| POST | `/engine/query` | Natural-language query |
| POST | `/engine/mode/{mode}` | Set engine mode (simulation/hybrid/live) |
| POST | `/engine/translate-ui` | Translate UI strings |
| GET | `/engine/ais/visible` | Visible AIS contacts |
| GET | `/stream/events` | Server-Sent Events stream |

## Legacy Pipeline API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/analysis/run` | Run full analysis pipeline on loaded events |
| POST | `/coa/generate` | Generate advisory COAs |
| POST | `/coa/simulation/run` | Monte Carlo simulation for each COA |
| POST | `/coa/recommendation/run` | Score and recommend top COA |
| POST | `/coa/briefing/generate` | Generate commander briefing |
| POST | `/coa/briefing/export/json` | Export briefing as JSON |
| POST | `/coa/briefing/export/pdf` | Export briefing as PDF |

## Safety Boundaries

- **Guardrails**: The query engine refuses questions about lethal targeting, engagement authorization, and ROE bypass. These are checked before any processing.
- **LLM is explanation-only**: The LLM may rephrase answers and enrich narratives, but it never generates forecasts, selects COAs, or modifies engine state.
- **Targeting is advisory-only**: Target prioritization and supporting-asset assignment never authorize engagement or weapon release.
- **Fusion is deterministic**: The system uses synthetic multi-source observations with deterministic fusion. It does not claim real raw ISR processing.
- **Forecasting is simulation-based**: What-if forecasts are produced by cloning and running the simulation forward. The LLM may rephrase the output but cannot invent outcomes.
- **ROE enforcement**: Every COA is evaluated against ROE rules. Restricted COAs are flagged with reasons; rejected COAs are excluded from recommendation.
- **No state mutation from queries**: Natural-language queries and forecasts never modify engine state.

## Known Limitations

- Rule-based anomaly detection only (no ML model trained on real data — by design)
- Simulation uses simplified probability models, not high-fidelity wargaming
- Single-user prototype; no authentication or multi-user support
- In-memory state store (SQLite persistence available but not enabled by default)
- No real external integrations in default configuration (AIS/NOAA replay available when configured)

## Test Status

**Current suite passes in local validation.** Coverage includes:

- Feature engineering, anomaly detection, threat assessment
- COA generation, simulation, scoring, recommendation
- ROE evaluation and event engine
- Behavior models and scenario generator
- Real-time engine: contacts, ticks, injection, scheduling
- Natural-language query engine with guardrails
- Forecasting module (baseline, event-based, COA-based)
- Persistence, rate limiting, API client
- End-to-end integration tests

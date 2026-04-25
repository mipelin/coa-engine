# COA Engine — Decision Superiority Module

A working MVP of an AI-assisted Course of Action (COA) analysis engine for operational decision support. Built for the NATO DIANA innovation framework.

## What This System Does

- Ingests synthetic operational events from a simulated Baltic Sea hybrid-threat scenario
- Extracts features, detects anomalies, and assesses threat probability using explainable rules
- Generates advisory courses of action, simulates outcomes with Monte Carlo methods, scores and ranks them
- Produces explainable, human-readable commander briefings
- Displays results on an interactive dashboard with operational map and charts

## What This System Does NOT Do

- **No autonomous targeting or lethal engagement** — this is decision-support only
- **No command execution** — all recommendations require human approval
- **No classified data** — all data is synthetic and open-source
- **No real NATO integrations** — designed only as a local prototype with clear API boundaries
- **No live data feeds** — runs entirely on local synthetic data

## Quick Start

```bash
# From the coa_engine/ directory

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest -v

# Run the backend API (Terminal 1)
./run_backend.sh
# API docs: http://localhost:8002/docs

# Run the Streamlit dashboard (Terminal 2)
./run_ui.sh
# Dashboard: http://localhost:8501
```

For a guided demonstration, see [DEMO_SCRIPT.md](DEMO_SCRIPT.md).

## Architecture

```
coa_engine/
  app/
    main.py                  # FastAPI application entry point
    api/                     # Route handlers
      routes_scenarios.py    # Scenario loading endpoints
      routes_events.py       # Event ingestion endpoints
      routes_analysis.py     # Analysis pipeline endpoint
      routes_coa.py          # COA/simulation/recommendation/briefing endpoints
    core/
      schemas.py             # Pydantic models (contracts)
      constants.py           # Enum types, infrastructure data
      config.py              # Settings
    data/
      sample_scenario_baltic.json  # Synthetic Baltic scenario (20 events)
    engine/                  # Analytic modules (independent of FastAPI)
      event_ingestion.py     # Scenario/event loading and validation
      feature_engineering.py # Feature extraction (haversine distances, anomaly signals)
      anomaly_detection.py   # Rule-based anomaly scoring with explanations
      threat_assessment.py   # Entity-level threat probability aggregation
      coa_generation.py      # Advisory COA generation
      simulation.py          # Monte Carlo simulation (seeded, deterministic)
      scoring.py             # Weighted multi-criteria COA scoring
      recommendation.py      # Top-COA selection with rationale and alternatives
      explanation.py         # Commander briefing generation
    ui/
      streamlit_app.py       # Streamlit dashboard with map, charts, briefing
    tests/
      test_phase1.py         # Foundation tests (schemas, endpoints)
      test_phase2_analysis.py # Analysis pipeline tests (features, anomalies, threats)
      test_phase3_coa.py     # COA/simulation/scoring/recommendation tests
      test_phase4_ui.py      # Dashboard data helper tests
      test_end_to_end.py     # Full pipeline integration tests
```

The engine layer is independent of FastAPI and Streamlit. All modules use simple deterministic functions with Pydantic schemas.

## Dashboard

The Streamlit dashboard (`./run_ui.sh`) provides seven tabs:

- **Scenario Overview** — event counts, entity distribution, event type chart
- **Map** — folium map with color-coded markers for vessels, UAVs, cables, convoys, and jamming zones
- **Timeline** — Plotly scatter timeline of events by entity and time, colored by anomaly level
- **Threat Assessment** — ranked threat table with probability, level, drivers, and anomaly details
- **COA Ranking** — scored COAs with bar chart, detail table, and recommendation highlight
- **Simulation Results** — grouped bar chart comparing success/escalation/cable risk/missed detection
- **Commander Briefing** — formatted situation, indicators, assessment, risks, confidence, assumptions

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/scenario/sample` | Load sample Baltic scenario |
| POST | `/events/ingest` | Ingest a batch of operational events |
| POST | `/analysis/run` | Run features, anomalies, threat assessment |
| POST | `/coa/generate` | Generate advisory COAs |
| POST | `/coa/simulation/run` | Monte Carlo simulation for each COA |
| POST | `/coa/recommendation/run` | Score and recommend top COA |
| POST | `/coa/briefing/generate` | Generate commander briefing |

API documentation is available at `http://localhost:8002/docs` when the backend is running.

## Analysis Pipeline

1. **Event ingestion** — Load and validate synthetic events via Pydantic schemas
2. **Feature engineering** — Compute distances (haversine), speed anomalies, course change counts, multi-source correlation, jamming/convoy proximity, heading-toward-asset signals
3. **Anomaly detection** — Rule-based scoring (0-100) with explainable per-rule breakdown; cable severance is CRITICAL
4. **Threat assessment** — Aggregate anomalies by entity with event-type weighting; exclude allied/ISR assets; sort by probability
5. **COA generation** — Context-aware advisory options (ISR, shadow, cable protection, airspace safety, border monitoring, combined)
6. **Simulation** — Seeded Monte Carlo (1000 runs) using beta distributions around COA-specific baselines
7. **Scoring** — Weighted formula: success 30%, cable protection 20%, escalation 15%, time 10%, detection 10%, civilian safety 10%, logistics 5%
8. **Recommendation** — Select rank-1 COA with rationale and alternative edge cases
9. **Briefing** — Formatted commander decision-support product

## Known Limitations

- Single synthetic scenario only; no scenario editor or multi-scenario loading
- Rule-based anomaly detection only (no ML model trained on real data, by design)
- Simulation uses simplified probability models, not high-fidelity wargaming
- No persistence layer; all data is in-memory
- No user authentication or multi-user support
- No real external integrations (AIS, SIGINT, satellite)
- Dashboard consumes engine functions directly, not the REST API

## Phase Status

**MVP complete.** All five phases delivered:

- **Phase 1**: Repo structure, schemas, sample scenario, FastAPI skeleton
- **Phase 2**: Feature engineering, anomaly detection, threat assessment
- **Phase 3**: COA generation, Monte Carlo simulation, scoring, recommendation, briefing
- **Phase 4**: Streamlit dashboard with map, charts, and briefing view
- **Phase 5**: End-to-end testing, documentation, demo script, repository cleanup

## Safety and Ethical Boundary

This system is a **human decision-support tool only**. It does not make autonomous decisions, assign targets, or execute military commands. All outputs are advisory and require human review before any action. The prototype uses only synthetic, publicly describable data. No component of this system should be interpreted as a weapon system, autonomous targeting system, or command execution system.

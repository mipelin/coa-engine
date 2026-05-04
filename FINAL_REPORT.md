# COA Engine — Final Readiness Report

## Verification Summary

Final verification completed from the `coa_engine/` directory.

Commands verified:

```bash
pytest -q
python -c "from app.main import app; print(app.title)"
python -m json.tool app/data/sample_scenario_baltic.json
```

Results:

- Test suite: `757 passed`
- FastAPI import: successful, app title `COA Engine`
- Sample scenario JSON validation: successful
- Primary operator UI: FastAPI dashboard at `/dashboard`
- Legacy UI status: `app/ui/streamlit_app.py` remains available as legacy/optional and is not used in the demo flow

## Demo Readiness

The prototype is ready for a local DIANA-style demonstration.

Primary demo commands:

```bash
pip install -r requirements.txt
pytest -q
./run_ui.sh
```

Expected local URLs:

- FastAPI dashboard: `http://localhost:8002/dashboard`
- Backend API docs: `http://localhost:8002/docs`

## Delivered Capabilities

- FastAPI dashboard as the primary operator UI
- Multiple scenarios: Baltic, Arctic, Mediterranean
- NOAA replay datasets for scenario-aligned synthetic maritime replay
- Canonical deterministic analysis pipeline
- COP (Common Operating Picture) assembled from a single source of truth in live engine state
- Synthetic multi-source observations with deterministic fusion and fused tracks
- Explainable anomaly detection and entity-level threat probability assessment
- Advisory targeting support with supporting asset assignment
- ROE-constrained recommendations
- COA generation, deterministic parametric estimation, scoring, ranking, and optimization
- Multi-step forecasting grounded in deterministic parametric estimation
- Operational effects modeling for weather, visibility, jamming, logistics, and readiness
- Replay timeline plus deterministic after-action review
- SQLite persistence enabled by default for state restore and replay snapshots
- LLM explanation-only layer for Ask, briefings, and summaries; never part of the decision path

## Safety Boundary

The system is a human decision-support prototype only.

It does not:

- perform autonomous decision-making for targeting
- authorize use of force
- execute commands
- claim live ISR ingestion or analysis
- use classified data
- integrate with real NATO systems
- issue operational orders

All bundled data is synthetic. Decision-support outputs remain deterministic, and the LLM is used only for explanation.

## Known Limitations

- Rule-based anomaly logic only; no trained operational ML model
- Simplified parametric estimation model rather than high-fidelity wargaming
- Single-user prototype; no authentication or multi-user workflow
- No real external integrations in default demo configuration
- Legacy Streamlit UI remains in the repository but is not the primary UI and is not used in the demo

## Final Assessment

The prototype is coherent, locally runnable, test-covered, and suitable for a DIANA submission demo as an explainable decision-support layer. It should be presented as a system built on synthetic multi-source observations, deterministic fusion, advisory targeting support, ROE-constrained recommendations, and an LLM explanation-only layer.

# COA Engine — Final Readiness Report

## Verification Summary

Final verification completed from the `coa_engine/` directory.

Commands verified:

```bash
pytest
python -c "from app.main import app; print(app.title)"
python -m py_compile app/ui/streamlit_app.py
python -m json.tool app/data/sample_scenario_baltic.json
```

Results:

- Test suite: `72 passed`
- FastAPI import: successful, app title `COA Engine`
- Streamlit dashboard compile check: successful
- Sample scenario JSON validation: successful
- Dashboard data helper: returns 20 events, 9 threat entities, 6 scored COAs, recommended COA `COA-006`

## Demo Readiness

The MVP is ready for a local demonstration.

Primary demo commands:

```bash
pip install -r requirements.txt
pytest -v
./run_backend.sh
./run_ui.sh
```

Expected local URLs:

- Backend API docs: `http://localhost:8002/docs`
- Streamlit dashboard: `http://localhost:8501`

## Delivered Capabilities

- Synthetic Baltic hybrid-threat scenario ingestion
- Explainable feature extraction
- Rule-based anomaly detection
- Entity-level threat probability assessment
- Advisory COA generation
- Seeded Monte Carlo-style outcome simulation
- Weighted COA scoring and ranking
- Advisory recommendation with rationale
- Commander-style briefing
- Streamlit dashboard with map, timeline, threat panel, COA ranking, simulation chart, and briefing
- End-to-end API and pipeline tests

## Safety Boundary

The system is a human decision-support prototype only.

It does not:

- perform autonomous targeting
- assign weapons
- execute commands
- connect to live ISR feeds
- use classified data
- integrate with real NATO systems
- issue operational orders

All bundled data is synthetic and all outputs are advisory.

## Known Limitations

- Single bundled scenario only
- No scenario editor
- No persistence layer
- No authentication or multi-user support
- No real external integrations
- Rule-based anomaly logic only
- Simplified simulation model, not high-fidelity operational modelling
- Dashboard consumes local engine functions directly rather than the REST API

## Final Assessment

The prototype is coherent, locally runnable, test-covered, and suitable for a NATO/DIANA-style MVP demonstration as an explainable decision-support layer. It should be presented as a quantitative COA analysis prototype, not as a C2 platform or autonomous operational system.

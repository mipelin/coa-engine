# COA Engine — Demo Script

## 3-5 Minute Demonstration Flow

### Setup (30 seconds)

Open two terminals in the `coa_engine/` directory.

```bash
# Terminal 1: Start the backend
pip install -r requirements.txt
./run_backend.sh

# Terminal 2: Start the dashboard
./run_ui.sh
```

The dashboard opens at `http://localhost:8501`.

### 1. Scenario Overview (30 seconds)

**Show:** Scenario Overview tab.

**Talk:**
- "This is the COA Engine, a decision-support prototype for operational analysis."
- "It loads a synthetic Baltic Sea hybrid-threat scenario with 20 events across multiple domains: maritime, air, ground, and electronic warfare."
- "All data is synthetic. This is a prototype, not connected to any live systems."

### 2. Operational Map (45 seconds)

**Show:** Map tab.

**Talk:**
- "Red markers show suspicious vessels near subsea cable corridors."
- "Blue markers are allied naval assets on patrol."
- "Orange is an unidentified UAV near Visby Airport."
- "Purple circles show GPS/VHF jamming zones — note the expanding radius."
- "Dark green stars mark critical infrastructure: two subsea internet cables, airports."
- "This is the same picture a commander would see, but the system goes further."

### 3. Analysis Pipeline (60 seconds)

**Show:** Timeline tab, then Threat Assessment tab.

**Talk:**
- "The engine computes features for every event: distances to infrastructure, speed anomalies, course changes, multi-source correlation."
- "Anomaly detection uses explainable rules — every score has a human-readable explanation."
- "Cable severance is flagged as CRITICAL. Suspicious vessels near cables get elevated scores."
- "Threat assessment aggregates by entity. Suspicious vessels rank highest. Allied vessels are excluded from threat ranking."
- "The system labels these as estimated probabilities, not certainties."

### 4. COA Ranking (60 seconds)

**Show:** COA Ranking tab.

**Talk:**
- "Based on the threat picture, the system generates advisory courses of action: increase ISR, shadow vessels, protect the second cable, manage airspace, monitor borders."
- "Each COA is simulated using Monte Carlo methods — 1000 runs per option."
- "The scoring formula balances success probability, cable protection, escalation risk, civilian safety, and logistics."
- "The recommended COA is highlighted. The rationale and tradeoffs are explained in plain language."
- "This is advisory only. The system recommends — a human decides."

### 5. Simulation Results (30 seconds)

**Show:** Simulation Results tab.

**Talk:**
- "The grouped chart shows how each COA compares across success, escalation, cable risk, and detection probability."
- "Confidence intervals come from the Monte Carlo distribution."
- "Combined approaches score higher on effectiveness but carry more logistics burden."

### 6. Commander Briefing (30 seconds)

**Show:** Commander Briefing tab.

**Talk:**
- "The system produces a formatted decision-support briefing: situation, indicators, assessment, COAs considered, recommendation, risks, confidence, and assumptions."
- "This is designed to look like what a staff officer would produce — but generated from the quantitative pipeline."

### 7. API Demo (15 seconds)

**Show:** Backend terminal or Swagger docs at `http://localhost:8002/docs`.

**Talk:**
- "All outputs are also available through REST API endpoints — designed to be modular and pluggable."
- "The architecture uses clear API boundaries, while this prototype runs entirely locally with synthetic data."

### Closing

**Emphasize:**
- "Everything you saw is synthetic data, explainable rules, and advisory outputs."
- "No autonomous targeting. No command execution. Human decision-support only."
- "The MVP demonstrates that a modular AI/software layer can augment operational decision-making."

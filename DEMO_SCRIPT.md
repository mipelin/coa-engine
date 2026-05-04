# COA Engine — Demo Script (5 Minutes)

## Setup (before demo)

```bash
pip install -r requirements.txt
./run_ui.sh
```

Open http://localhost:8002/dashboard in a browser.
Open http://localhost:8002/docs in a second tab.

Use only the FastAPI dashboard for the demo flow. Do not switch to any legacy UI.
The Streamlit UI is legacy/optional and is not used in the demo.

## Mandatory startup sequence

Before beginning the spoken demo:

1. Load **Baltic Sea**
2. Click **Start**
3. Wait until all of the following are visible:
   - fused tracks visible
   - targets populated
   - COAs generated
   - threat level visible
   - replay snapshots present
4. Click **Test LLM** and confirm the dashboard shows the LLM as `READY` or otherwise reachable
5. Only then begin the explanation

Do not present the system in an empty state.

## 1. Load Scenario (0:00 – 0:30)

In the top header bar, select **Baltic Sea** from the scenario dropdown, then click **Start**.

> "This is the COA Engine — a decision-support prototype for maritime threat analysis. I'm loading a synthetic Baltic Sea scenario with six entities: two hostile vessels, a UAV, convoy activity, allied patrol assets, and critical subsea internet cables."

Wait for a few ticks. The map should show red hostile markers, blue friendly markers, and green infrastructure icons. Do not continue until fused tracks, populated targets, generated COAs, visible threat level, and replay snapshots are present.

> "All data is synthetic. The observation layer uses synthetic multi-source observations with deterministic fusion. This is not connected to any live system."

## 2. Threat Evolution (0:30 – 1:30)

Point to the threat level indicator rising from LOW to MEDIUM to HIGH.

> "As the simulation advances, the hostile vessel probes toward the cable corridor. A course change triggers. The system detects increased proximity, jamming correlation, and heading-toward-infrastructure indicators. Each entity gets an explainable threat score — you can see the drivers in the Contacts tab."

Switch to the **Contacts** tab. Show the top threat entity with its probability and drivers.

> "Every score has a human-readable explanation: proximity to infrastructure, course changes, jamming correlation. This is not a black box."

## 3. COA Ranking and ROE (1:30 – 2:30)

Switch to the **COAs** tab. Show the ranked list of advisory courses of action.

> "Based on the threat picture, the system generates advisory courses of action: increase ISR coverage, shadow vessels, protect the cable, manage airspace, monitor borders, and a combined approach. Each COA is Monte Carlo simulated — 1000 runs per option."

Point to the ROE badge and reason strip on each COA card.

> "Each COA is evaluated against Rules of Engagement. You can see the colored badge at a glance — green for allowed, amber for restricted, orange pulsing if authorization is needed, red and struck through if rejected. The reason strip below the card title explains why. Restricted COAs are flagged with reasons; rejected ones are excluded from the recommendation."

Point to the recommended COA.

> "The recommended COA is highlighted with a rationale and tradeoffs. Targeting support and supporting-asset suggestions are advisory only, and the recommendation remains ROE-constrained. A human decides."

## 4. Natural-Language Query (2:30 – 3:15)

Switch to the **Ask** tab. Click the **Threat level** chip (or type the question).

Show the structured answer.

> "Operators can ask questions in plain language. The system builds context from live state and routes through guardrails. The system is fully deterministic. The LLM is used only for explanation and can be disabled without affecting decision support."

## 5. Forecasting and What-If (3:15 – 4:15)

Click the **Cable what-if** chip (or type "What if the cable is severed?").

Show the forecast output: threat trend, key risks, expected outcome.

> "This is where it gets interesting. The system clones the current simulation state and runs it forward with the hypothetical event injected. The forecast is produced by the simulation engine. The LLM may rephrase it but cannot invent outcomes."

Click the **COA outcome** chip (or type "What happens if we choose the recommended COA?").

Show the COA-specific forecast with different threat projection.

> "Different COAs produce different projected outcomes. The system shows the effectiveness score, escalation risk, and threat level change for each option. The operator can compare before deciding."

## 6. API and Closing (4:15 – 5:00)

Switch to the Swagger docs tab. Show the endpoint list.

> "Everything you saw is available through REST API — state queries, synthetic observation ingestion, deterministic fusion outputs, contact management, COA ranking, natural-language queries, and real-time event streaming. The engine layer is framework-agnostic."

> "To be clear: this is a human decision-support tool only. No autonomous decision-making for targeting, no force-approval authority, and no command execution. All outputs are advisory and require human review. The prototype uses only synthetic data and MSS-compatible interfaces."

> "The MVP demonstrates that a modular software layer can provide explainable, grounded decision support for operational scenarios without any autonomous action."

## LLM fallback note

If the LLM becomes slow or unavailable, continue the demo using deterministic outputs from the COP, targets, COAs, forecasting, replay, and after-action review. Decision support remains available because the LLM is explanation-only and non-critical.

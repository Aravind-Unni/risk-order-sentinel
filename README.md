# Risk Order Sentinel

An automated, local AI-driven batch processing system designed for **Kavya Textiles** to monitor production workflows, perform mathematical timeline risk assessments, and automatically dispatch alerts for critical disruptions.

Powered by a local reasoning LLM via Ollama and tracked transparently with MLflow, the Sentinel runs as a predictable, deterministic background agent execution pipeline.

---

## 🏗️ System Architecture & Workflow

The system is architected as a robust **ReAct (Reasoning + Action)** pattern utilizing Langchain. Instead of relying on open-ended agentic autonomy, the system operates on strict deterministic validation and reporting logic:

```
[Trigger Scan] ──> [Fetch Active Orders (SQLite)]
        │
        ▼
[Initiate Langchain Loop]
        │
        ├──> 1. fetch_order_status
        ├──> 2. calculate_timeline_risk
        │
        ▼
   {Is Order At Risk?}
      /          \
   YES            NO
    │              │
    ▼              ▼
[send_email_alert]  [Log Status: Viable]
```

1. **State Extraction:** Queries the tracking schema to pull production stages, current metrics, and commitment targets.
2. **Risk Analysis:** Computes actual vs. target date intervals to evaluate if the delivery schedule is mathematically viable.
3. **Alerting System:** If structural anomalies or missing data thresholds are crossed, an alert is triggered to notify production supervisors immediately.

---

## 🛠️ Technology Stack

* **Orchestration:** Langchain (ReAct compiler)
* **LLM:** Groq API (llama-3.3-70b-versatile)
* **Tracking & Observability:** MLflow (Local SQLite tracking backend)
* **Package Management:** `uv` (Fast, isolated Python environment management)
* **Database:** SQLite3

---

## 📁 Repository Structure

```text
├── .github/workflows/
│   └── daily_scan.yml         # GitHub Actions CI/CD daily execution schedule
├── src/
│   ├── database/
│   │   ├── kavya_textiles.db  # Production state tracking database
│   │   ├── schemas.py         # Database schema definitions
│   │   └── setup_db.py        # Script to initialize test scenarios
│   └── tools/
│       ├── __init__.py        # Bundled toolkit initialization
│       ├── email_alerts.py    # Communication alert layers
│       ├── order_status.py    # State extraction tools
│       └── risk_calculator.py # Mathematical timeline risk rules
├── .env                       # Local environment variables (Ignored by git)
├── .gitignore                 # Project ignore specifications
├── main.py                    # Core execution batch entrypoint
├── pyproject.toml             # Project dependencies managed by uv
├── requirements.txt           # Exported dependency constraints
└── uv.lock                    # Lockfile for reproducible environments
```

---

## 🚀 Setup & Installation

### Prerequisites

* Python 3.10+
* Ollama installed and running locally.
* `uv` installed via:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 1. Initialize the Environment

Clone the repository and install all locked dependencies within an isolated virtual environment using `uv`:

```bash
uv sync
```

### 2. Pull the AI Model

Ensure your local Ollama instance has the target reasoning model downloaded:

```bash
ollama pull ornith:35b
```

> **Note:** For environments restricted by standard CPU/RAM hardware configurations, you can substitute this for `ornith:9b` within `main.py`.

### 3. Environment Configuration

Create a `.env` file in the root directory:

```
MLFLOW_TRACKING_URI=sqlite:///mlflow.db
# Add any additional notification credentials here if required by tools
```

### 4. Seed the Local Test Scenarios

Generate the local mock relational schema with test profiles (Normal, At-Risk, Ambiguous, Stale states):

```bash
uv run src/database/setup_db.py
```

---

## 🏃 Execution & Observability

### Running the Scan Loop

To execute the scheduled execution batch run locally:

```powershell
# Activate the environment in PowerShell
.venv\Scripts\Activate.ps1

# Run the sentinel core application
uv run main.py
```

### Viewing Traces in MLflow

To visually track the agent's logic, tool executions, and step-by-step reasoning trajectories, launch the local MLflow dashboard:

```bash
uv run mlflow server --backend-store-uri sqlite:///mlflow.db
```

Once started, navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000) in your web browser.

---

## 🤖 CI/CD Automation

The project includes a GitHub Actions configuration workflow (`.github/workflows/daily_scan.yml`) configured to automatically execute the tracking scan daily at 5:00 PM IST (11:30 UTC), ensuring complete continuous monitoring of operational health.

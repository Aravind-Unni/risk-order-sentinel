# Risk Order Sentinel

An automated, local AI-driven batch processing system designed for **Kavya Textiles** to monitor production workflows, perform mathematical timeline risk assessments, and automatically dispatch alerts for critical disruptions.

Powered by Groq-hosted Llama 3.3 70B for reasoning and tracked transparently with MLflow, the Sentinel runs as a predictable, deterministic background agent execution pipeline.

---

## 🏗️ System Architecture & Workflow

The system is architected as a robust **ReAct (Reasoning + Action)** pattern utilizing LangChain. Instead of relying on open-ended agentic autonomy, the system operates on strict deterministic validation and reporting logic:

```
[Trigger Scan] ──> [Fetch Active Orders (SQLite)]
        │
        ▼
[Initiate LangChain Loop]
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

* **Orchestration:** LangChain (ReAct-style tool-calling agent)
* **LLM Inference:** Groq API (Llama 3.3 70B)
* **Email Alerts:** SendGrid
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
* `uv` installed via:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

* A [Groq](https://console.groq.com/) API key (used for LLM inference — Llama 3.3 70B)
* A [SendGrid](https://sendgrid.com/) API key (used for email alerts)

### 1. Initialize the Environment

Create and initialize the project environment, then install dependencies:

```bash
uv venv
uv init
uv sync
uv pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the root directory with the following variables:

```
GROQ_API_KEY="your-groq-api-key"
SENDGRID_API_KEY="your-sendgrid-api-key"
SENDER_EMAIL="your-sender-email"
RECEIVER_EMAIL="your-alert-recipient-email"
MLFLOW_TRACKING_URI=http://127.0.0.1:5000
```

### 3. Seed the Local Test Scenarios

Generate the local mock relational schema with test profiles (Normal, At-Risk, Ambiguous, Stale states):

```bash
uv run src/database/setup_db.py
```

---

## 🏃 Execution & Observability

Run these two steps **at the same time, in separate terminals**.

### Terminal 1 — Start MLflow

Launch the local MLflow dashboard to track the agent's logic, tool executions, and step-by-step reasoning trajectories:

```bash
uv run mlflow ui --backend-store-uri sqlite:///mlflow.db
```

Once started, navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000) in your web browser to view traces.

### Terminal 2 — Run the Sentinel

With MLflow already running, execute the core application:

```bash
uv run main.py
```

---

## 🤖 CI/CD Automation

The project includes a GitHub Actions configuration workflow (`.github/workflows/daily_scan.yml`) configured to automatically execute the tracking scan daily at 5:00 PM IST (11:30 UTC), ensuring complete continuous monitoring of operational health.

### Configuring Secrets

Since `.env` is git-ignored, the workflow cannot read your local environment variables — they must be added as **GitHub Actions secrets** so the CI run has access to them:

1. Go to your repository on GitHub.
2. Navigate to **Settings → Secrets and variables → Actions**.
3. Click **New repository secret** and add each of the following:

   * `GROQ_API_KEY`
   * `SENDGRID_API_KEY`
   * `SENDER_EMAIL`
   * `RECEIVER_EMAIL`
   * `MLFLOW_TRACKING_URI`

4. Reference these secrets in `daily_scan.yml` under the job's `env:` block so they're injected as environment variables at runtime.

> Without this step, the scheduled workflow run will fail to authenticate with Groq/SendGrid or locate the tracking URI.

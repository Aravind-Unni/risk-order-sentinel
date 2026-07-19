import os
import sqlite3
import mlflow
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama

# Import the tools bundled in src/tools/__init__.py
from src.tools import ALL_TOOLS

# 1. Load Environment Variables
load_dotenv()

# 2. Database Path for fetching active orders
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "src/database/kavya_textiles.db"))

# 3. Configure MLflow Tracing
tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
mlflow.set_tracking_uri(tracking_uri)
mlflow.set_experiment("Risk_Order_Sentinel")
mlflow.langchain.autolog()

# 4. Define the System Prompt
# Adjusted for a proactive, scheduled batch-processing context
SYSTEM_PROMPT = """
You are the "At-Risk Order Sentinel" for Kavya Textiles. You are running as an automated, scheduled background process.

You must follow this strict ReAct sequence for the provided order:
1. USE 'fetch_order_status' to get the current stage, target date, transport mode, and any tracking notes.
2. USE 'calculate_timeline_risk' to determine if the deadline is mathematically viable.
3. Read the tracking notes carefully, even if the math says 'Viable'. The math only knows
   stage durations -- it cannot see external blockers described in the notes (e.g. customs
   holds, vendor delays, contradictory updates). If the notes describe an unresolved blocker
   that the math wouldn't capture, treat the order as effectively at risk regardless of the
   math verdict.
4. USE 'send_email_alert' if EITHER of the following is true:
   - The order is mathematically 'AT RISK', OR
   - The order is 'Viable' by the math, but the notes reveal an unresolved external blocker
     the math can't see, OR
   - The tracking data is stale (no update in ~3+ days), missing, or contradictory -- in this
     case use risk_level "INSUFFICIENT_DATA" rather than guessing.
5. If the order is genuinely 'Viable' with no contradicting signal in the notes, do NOT send
   an email. Output a brief confirmation of its viability for the system logs.

When reasoning about urgency and recommended_action, distinguish between blockers that are
already being resolved (e.g. a vendor confirms a fix is in progress) versus blockers that are
open-ended or worsening (e.g. no ETA, ongoing staff shortage). Reflect that difference in the
tone and urgency of your alert -- do not treat every AT_RISK order identically.

Always explain your observations clearly in your reasoning trace, citing the specific numbers
and notes that drove your conclusion.
"""

def create_sentinel_agent():
    """Initializes the LangGraph ReAct agent."""
    llm = ChatOllama(
        model="ornith:35b",
        temperature=0.1, 
        max_tokens=1024
    )
    
    agent_executor = create_agent(
    model=llm,
    tools=ALL_TOOLS,
    system_prompt=SYSTEM_PROMPT,
)
    
    return agent_executor

def fetch_active_orders() -> list:
    """Queries the database for all orders currently in production."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Fetching orders that are in the production tracking table
        cursor.execute("SELECT DISTINCT order_id FROM production_tracking")
        orders = [row[0] for row in cursor.fetchall()]
        conn.close()
        return orders
    except Exception as e:
        print(f"❌ Failed to fetch orders from database: {str(e)}")
        return []

def evaluate_order(agent, order_id: str):
    """Executes the ReAct loop for a single order."""
    print(f"\n{'='*50}")
    print(f"🕵️  EVALUATING ORDER: {order_id}")
    print(f"{'='*50}\n")
    
    # Wrap in MLflow for full observability of the agent's trajectory
    with mlflow.start_run(run_name=f"Daily_Scan_{order_id}"):
        # Formulate as a system trigger rather than a conversational prompt
        trigger_message = f"SYSTEM INSTRUCTION: Execute scheduled risk assessment for order {order_id}."
        inputs = {"messages": [HumanMessage(content=trigger_message)]}
        
        for event in agent.stream(inputs, stream_mode="values"):
            message = event["messages"][-1]
            message.pretty_print()

def run_daily_scan():
    """
    Orchestrates the scheduled job (Pattern A). 
    Designed to be triggered daily at 8 AM via cron or task scheduler.
    """
    print("⏰ Initiating Scheduled Daily Sentinel Scan...")
    
    active_orders = fetch_active_orders()
    if not active_orders:
        print("No active orders found. Terminating scan.")
        return

    print(f"Found {len(active_orders)} active orders to evaluate.\n")
    
    agent = create_sentinel_agent()
    
    for order_id in active_orders:
        evaluate_order(agent, order_id)
        
    print("\n✅ Daily Sentinel Scan Complete.")

if __name__ == "__main__":
    if not os.getenv("GROQ_API_KEY"):
        print("❌ ERROR: GROQ_API_KEY is missing from your .env file.")
        exit(1)
        
    # Execute the batch job
    run_daily_scan()

import os
from langchain_core.tools import tool
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

@tool
def send_email_alert(order_id: str, risk_level: str, risk_reasoning: str, recommended_action: str) -> str:
    """
            Sends an alert email to the factory owner/supervisor via SendGrid.

            Use this tool when an order needs human attention -- either because it's
            genuinely at risk, OR because the tracking data is too stale/missing/
            contradictory to judge confidently. These need different labels so
            Kavya's team can tell "this needs a freight decision" apart from
            "someone needs to go check the whiteboard."

            Args:
                order_id: The ID of the order needing attention.
                risk_level: Exactly "AT_RISK" or "INSUFFICIENT_DATA".
                    Use INSUFFICIENT_DATA whenever the stage data hasn't been
                    updated recently (e.g. more than ~3 days), or is missing/
                    contradictory -- do NOT guess a risk level in that case,
                    escalate instead.
                risk_reasoning: Plain-language explanation citing the actual
                    numbers and/or notes that led to this conclusion.
                recommended_action: A specific, concrete next step -- not a vague
                    warning like "monitor closely." Derive it from what the tracking
                    notes actually say is blocking this order, not from a template.
                    Think about: who or what is the blocker (a vendor, an internal
                    team, a customs/logistics step, an unclear record)? Has it
                    already been addressed, or is it still open? Is the shortfall
                    recoverable with a fix, or does the deadline need to move?
                    Name the specific person, vendor, or step from the notes where
                    the order provides one, and let the urgency of the wording
                    reflect whether the blocker is resolved, in progress, or stuck.
    """
    sg_key = os.environ.get('SENDGRID_API_KEY')
    from_email = os.environ.get('SENDER_EMAIL', 'sentinel@kavyatextiles.com')
    to_email = os.environ.get('RECEIVER_EMAIL', 'owner@kavyatextiles.com')

    level = risk_level.upper().strip()
    subject = (
        f"⚠️ NEEDS CHECK: Order {order_id} — data unreliable"
        if level == "INSUFFICIENT_DATA"
        else f"🔴 URGENT: Order {order_id} At Risk"
    )

    if not sg_key:
        print(f"\n[MOCK SENDGRID EMAIL FIRED]")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Body: Status - {level} | Reason - {risk_reasoning} | Action - {recommended_action}\n")
        return f"Email alert mocked successfully (risk_level={level}, No SendGrid API Key found in env)."

    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        html_content=f"""
        <strong>Order ID:</strong> {order_id}<br><br>
        <strong>Status:</strong> {level}<br><br>
        <strong>Reasoning:</strong> {risk_reasoning}<br><br>
        <strong>Recommended Action:</strong> {recommended_action}
        """
    )

    try:
        sg = SendGridAPIClient(sg_key)
        response = sg.send(message)
        return f"Email successfully sent with status code {response.status_code} (risk_level={level})."
    except Exception as e:
        return f"Failed to send email via SendGrid: {str(e)}"
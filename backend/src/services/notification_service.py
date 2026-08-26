"""Email notification service for workflow transitions."""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "insightful-system@inukafoundation.org")
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"

WORKFLOW_LABELS = {
    "drafting": "Drafting",
    "tier_2_verification": "Tier 2 Verification",
    "tier_3_assembly": "Tier 3 Assembly",
    "tier_4_final_sign_off": "Tier 4 Final Sign-Off",
    "exported_sent": "Exported/Sent",
}

ACTION_LABELS = {
    "submit_for_review": "submitted for review",
    "approve": "approved",
    "reject": "rejected",
    "request_changes": "changes requested",
    "assemble_report": "assembled and submitted for final approval",
    "submit_for_final_approval": "submitted for final approval",
    "edit_content": "edited report content",
    "save_draft": "saved as draft",
}


def send_email(to_email: str, subject: str, html_body: str) -> bool:
    if not EMAIL_ENABLED or not SMTP_USER:
        logger.info(f"Email disabled - would send to {to_email}: {subject}")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = EMAIL_FROM
        msg["To"] = to_email
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, to_email, msg.as_string())

        logger.info(f"Email sent to {to_email}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


def notify_workflow_transition(
    report_title: str,
    report_id: int,
    action: str,
    old_state: str,
    new_state: str,
    actor_name: str,
    actor_email: str,
    recipient_emails: list[str],
    recipient_names: list[str],
    comments: Optional[str] = None,
) -> dict:
    action_label = ACTION_LABELS.get(action, action)
    old_label = WORKFLOW_LABELS.get(old_state, old_state)
    new_label = WORKFLOW_LABELS.get(new_state, new_state)

    subject = f"[Insightful System] Report '{report_title}' - {action_label.title()}"

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: 0 auto;">
        <div style="background: linear-gradient(135deg, #1a237e, #283593); padding: 20px; border-radius: 8px 8px 0 0;">
            <h2 style="color: white; margin: 0;">Insightful System</h2>
            <p style="color: #c5cae9; margin: 5px 0 0 0;">Workflow Notification</p>
        </div>
        <div style="padding: 20px; background: #f5f5f5; border: 1px solid #ddd;">
            <p><strong>{actor_name}</strong> has <strong>{action_label}</strong> the report:</p>

            <div style="background: white; padding: 15px; border-radius: 6px; border-left: 4px solid #1a237e; margin: 15px 0;">
                <h3 style="margin: 0 0 10px 0; color: #1a237e;">{report_title}</h3>
                <table style="width: 100%; font-size: 14px;">
                    <tr>
                        <td style="padding: 4px 0; color: #666;">Report ID:</td>
                        <td style="padding: 4px 0;">#{report_id}</td>
                    </tr>
                    <tr>
                        <td style="padding: 4px 0; color: #666;">Previous Status:</td>
                        <td style="padding: 4px 0;">{old_label}</td>
                    </tr>
                    <tr>
                        <td style="padding: 4px 0; color: #666;">New Status:</td>
                        <td style="padding: 4px 0;"><strong>{new_label}</strong></td>
                    </tr>
                    <tr>
                        <td style="padding: 4px 0; color: #666;">Date:</td>
                        <td style="padding: 4px 0;">{datetime.now(timezone.utc).strftime('%B %d, %Y at %H:%M UTC')}</td>
                    </tr>
                </table>
            </div>

            {f'<div style="background: white; padding: 10px 15px; border-radius: 6px; margin: 10px 0; font-style: italic; color: #555;">"{comments}"</div>' if comments else ''}

            <p style="color: #666; font-size: 13px;">This notification was sent by the Insightful System automated workflow engine.</p>
        </div>
        <div style="padding: 10px 20px; text-align: center; color: #999; font-size: 11px;">
            Inuka Foundation &copy; {datetime.now(timezone.utc).year}
        </div>
    </body>
    </html>
    """

    results = {}
    for email, name in zip(recipient_emails, recipient_names):
        personalized = html_body.replace(
            "<p><strong>{actor_name}</strong>",
            f"<p><strong>{actor_name}</strong>",
        )
        sent = send_email(email, subject, personalized)
        results[email] = {"sent": sent, "name": name}

    return {"subject": subject, "recipients": results, "action": action}

"""Email service for sending follow-up emails to customers."""

import logging
from flask import current_app
from flask_mail import Mail, Message

mail = Mail()
logger = logging.getLogger(__name__)

TEMPLATES = {
    "initial_followup": {
        "subject": "Follow-up on your recent SAP Support experience - Incident #{incident_id}",
        "body": """Dear {customer_name},

Thank you for your feedback on incident #{incident_id}. We noticed your satisfaction rating was {score}/5 and we take this seriously.

I'm {engineer_name}, and I'd like to understand your experience better so we can improve our service. Could we schedule a brief call to discuss?

Best regards,
{engineer_name}
SAP Product Support""",
    },
    "resolution_update": {
        "subject": "Update on your feedback - Incident #{incident_id}",
        "body": """Dear {customer_name},

Following our recent conversation about incident #{incident_id}, I wanted to let you know about the steps we've taken to address your concerns:

{notes}

We value your feedback and are committed to improving our support experience.

Best regards,
{engineer_name}
SAP Product Support""",
    },
}


def get_template_names():
    """Return list of available template names."""
    return list(TEMPLATES.keys())


def render_template(template_name, **kwargs):
    """Render an email template with the given variables.

    Returns:
        tuple: (subject, body) or (None, None) if template not found
    """
    tmpl = TEMPLATES.get(template_name)
    if not tmpl:
        return None, None

    subject = tmpl["subject"].format(**kwargs)
    body = tmpl["body"].format(**kwargs)
    return subject, body


def send_email(to_email, subject, body):
    """Send an email via Flask-Mail.

    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        msg = Message(subject=subject, recipients=[to_email], body=body)
        mail.send(msg)
        logger.info(f"Email sent to {to_email}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False
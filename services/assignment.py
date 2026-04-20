"""Auto-assignment logic for low-score surveys."""

from models import db, Followup, Survey, Incident
from services.analyzer import analyze_comment


def process_survey(survey):
    """Process a survey: run AI analysis and create followup if score < 3.

    Args:
        survey: Survey model instance (must have incident relationship loaded)

    Returns:
        Followup instance if created, None otherwise
    """
    # Run AI analysis on comment
    if survey.comment:
        category, confidence = analyze_comment(survey.comment)
        survey.ai_category = category
        survey.ai_confidence = confidence

    # Only create followup for low scores
    if survey.score >= 3:
        return None

    # Find the original incident engineer
    incident = Incident.query.get(survey.incident_id)
    if not incident:
        return None

    engineer_id = incident.engineer_id

    # Create followup record
    followup = Followup(
        survey_id=survey.id,
        assigned_engineer_id=engineer_id,
        status="pending" if engineer_id else "escalated",
    )
    db.session.add(followup)
    db.session.commit()

    return followup
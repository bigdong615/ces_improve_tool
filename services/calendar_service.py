"""Calendar service for generating .ics files for phone call reminders."""

from datetime import timedelta
from icalendar import Calendar, Event, Alarm


def generate_ics(survey_id, customer_name, incident_summary, comment, score,
                 scheduled_time, engineer_name):
    """Generate an .ics calendar file for a follow-up call.

    Args:
        survey_id: Survey ID
        customer_name: Customer company name
        incident_summary: Brief incident description
        comment: Customer's survey comment
        score: Survey score
        scheduled_time: datetime for the call
        engineer_name: Name of the assigned engineer

    Returns:
        bytes: The .ics file content
    """
    cal = Calendar()
    cal.add("prodid", "-//CES Improve Tool//SAP Support//EN")
    cal.add("version", "2.0")

    event = Event()
    event.add("summary", f"[CES Follow-up] {customer_name} - Survey #{survey_id}")
    event.add("dtstart", scheduled_time)
    event.add("dtend", scheduled_time + timedelta(minutes=30))
    event.add(
        "description",
        f"Follow-up call for low satisfaction survey\n\n"
        f"Customer: {customer_name}\n"
        f"Survey Score: {score}/5\n"
        f"Customer Comment: {comment or 'No comment'}\n\n"
        f"Incident Summary: {incident_summary}\n\n"
        f"Assigned to: {engineer_name}",
    )

    # 15-minute reminder
    alarm = Alarm()
    alarm.add("action", "DISPLAY")
    alarm.add("description", f"CES Follow-up call with {customer_name} in 15 minutes")
    alarm.add("trigger", timedelta(minutes=-15))
    event.add_component(alarm)

    cal.add_component(event)
    return cal.to_ical()
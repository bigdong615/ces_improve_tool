"""Followup management routes."""

from datetime import datetime
from flask import (
    Blueprint, render_template, session, redirect, url_for,
    request, flash, Response,
)
from models import db, Followup, Survey, Incident, Customer, Engineer, ReasonCategory
from services.email_service import render_template as render_email, send_email
from services.calendar_service import generate_ics

followups_bp = Blueprint("followups", __name__, url_prefix="/followups")


def login_required(f):
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        if "engineer_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated


@followups_bp.route("/")
@login_required
def followup_list():
    engineer_id = session["engineer_id"]
    followups = (
        Followup.query
        .filter_by(assigned_engineer_id=engineer_id)
        .join(Survey)
        .order_by(Survey.score.asc(), Followup.created_at.desc())
        .all()
    )
    return render_template("followup_list.html", followups=followups)


@followups_bp.route("/<int:followup_id>")
@login_required
def followup_detail(followup_id):
    followup = Followup.query.get_or_404(followup_id)
    categories = ReasonCategory.query.order_by(ReasonCategory.label).all()
    return render_template("followup_form.html", followup=followup, categories=categories)


@followups_bp.route("/<int:followup_id>/send-email", methods=["POST"])
@login_required
def send_followup_email(followup_id):
    followup = Followup.query.get_or_404(followup_id)
    survey = followup.survey
    incident = survey.incident
    customer = incident.customer
    engineer = Engineer.query.get(session["engineer_id"])

    template_name = request.form.get("template", "initial_followup")
    subject, body = render_email(
        template_name,
        customer_name=customer.contact_person,
        incident_id=incident.id,
        score=survey.score,
        engineer_name=engineer.name,
        notes=followup.notes or "",
    )

    if subject:
        success = send_email(customer.email, subject, body)
        if success:
            followup.email_sent_at = datetime.utcnow()
            followup.contact_method = "both" if followup.contact_method == "phone" else "email"
            if followup.status == "pending":
                followup.status = "in_progress"
            db.session.commit()
            flash("Email sent successfully", "success")
        else:
            flash("Failed to send email. Check SMTP configuration.", "danger")
    else:
        flash("Email template not found", "danger")

    return redirect(url_for("followups.followup_detail", followup_id=followup_id))


@followups_bp.route("/<int:followup_id>/schedule-call", methods=["POST"])
@login_required
def schedule_call(followup_id):
    followup = Followup.query.get_or_404(followup_id)
    survey = followup.survey
    incident = survey.incident
    customer = incident.customer
    engineer = Engineer.query.get(session["engineer_id"])

    call_date = request.form.get("call_date")
    call_time = request.form.get("call_time")

    if not call_date or not call_time:
        flash("Please select both date and time", "danger")
        return redirect(url_for("followups.followup_detail", followup_id=followup_id))

    scheduled = datetime.strptime(f"{call_date} {call_time}", "%Y-%m-%d %H:%M")
    followup.call_scheduled_at = scheduled
    followup.contact_method = "both" if followup.contact_method == "email" else "phone"
    if followup.status == "pending":
        followup.status = "in_progress"
    db.session.commit()

    ics_data = generate_ics(
        survey_id=survey.id,
        customer_name=customer.name,
        incident_summary=incident.summary,
        comment=survey.comment,
        score=survey.score,
        scheduled_time=scheduled,
        engineer_name=engineer.name,
    )

    return Response(
        ics_data,
        mimetype="text/calendar",
        headers={"Content-Disposition": f"attachment; filename=followup-{followup_id}.ics"},
    )


@followups_bp.route("/<int:followup_id>/complete", methods=["POST"])
@login_required
def complete_followup(followup_id):
    followup = Followup.query.get_or_404(followup_id)

    followup.engineer_category = request.form.get("category")
    followup.notes = request.form.get("notes", "")
    followup.status = "completed"
    followup.completed_at = datetime.utcnow()
    db.session.commit()

    flash("Follow-up completed successfully", "success")
    return redirect(url_for("followups.followup_list"))
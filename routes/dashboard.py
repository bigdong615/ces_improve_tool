"""Dashboard route - overview statistics."""

from flask import Blueprint, render_template, session, redirect, url_for
from sqlalchemy import func
from models import db, Survey, Followup, Engineer

dashboard_bp = Blueprint("dashboard", __name__)


def login_required(f):
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        if "engineer_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated


@dashboard_bp.route("/")
@login_required
def index():
    total_surveys = Survey.query.count()
    avg_score = db.session.query(func.avg(Survey.score)).scalar() or 0
    low_score_count = Survey.query.filter(Survey.score < 3).count()
    low_score_pct = round(low_score_count / total_surveys * 100, 1) if total_surveys else 0

    pending_followups = Followup.query.filter_by(status="pending").count()

    # Score distribution
    score_dist = []
    for s in range(1, 6):
        count = Survey.query.filter_by(score=s).count()
        score_dist.append({"score": s, "count": count})

    # Followup status distribution
    status_counts = {}
    for status in ["pending", "in_progress", "completed", "escalated"]:
        status_counts[status] = Followup.query.filter_by(status=status).count()

    # Reason category distribution (from engineer-confirmed categories)
    category_rows = (
        db.session.query(Followup.engineer_category, func.count(Followup.id))
        .filter(Followup.engineer_category.isnot(None))
        .group_by(Followup.engineer_category)
        .all()
    )
    category_dist = [{"category": r[0], "count": r[1]} for r in category_rows]

    # Monthly average score trend
    monthly_rows = (
        db.session.query(
            func.strftime("%Y-%m", Survey.submitted_at).label("month"),
            func.avg(Survey.score).label("avg_score"),
        )
        .group_by("month")
        .order_by("month")
        .all()
    )
    monthly_trend = [{"month": r[0], "avg_score": round(r[1], 2)} for r in monthly_rows]

    # Team leaderboard
    engineers = Engineer.query.all()
    team_stats = []
    for eng in engineers:
        total = Followup.query.filter_by(assigned_engineer_id=eng.id).count()
        completed = Followup.query.filter_by(
            assigned_engineer_id=eng.id, status="completed"
        ).count()
        rate = round(completed / total * 100, 1) if total else 0
        team_stats.append({
            "name": eng.name,
            "total": total,
            "completed": completed,
            "rate": rate,
        })
    team_stats.sort(key=lambda x: x["rate"], reverse=True)

    return render_template(
        "dashboard.html",
        total_surveys=total_surveys,
        avg_score=round(avg_score, 2),
        low_score_pct=low_score_pct,
        pending_followups=pending_followups,
        score_dist=score_dist,
        status_counts=status_counts,
        category_dist=category_dist,
        monthly_trend=monthly_trend,
        team_stats=team_stats,
    )
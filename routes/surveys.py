"""Survey list and detail routes."""

from flask import Blueprint, render_template, session, redirect, url_for, request
from models import Survey, Incident, Customer, ReasonCategory

surveys_bp = Blueprint("surveys", __name__, url_prefix="/surveys")


def login_required(f):
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        if "engineer_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated


@surveys_bp.route("/")
@login_required
def survey_list():
    score_filter = request.args.get("score", type=int)
    query = Survey.query.join(Incident).join(Customer).order_by(Survey.submitted_at.desc())

    if score_filter:
        query = query.filter(Survey.score == score_filter)

    surveys = query.all()
    return render_template("survey_list.html", surveys=surveys, score_filter=score_filter)


@surveys_bp.route("/<int:survey_id>")
@login_required
def survey_detail(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    categories = ReasonCategory.query.order_by(ReasonCategory.label).all()
    return render_template("survey_detail.html", survey=survey, categories=categories)
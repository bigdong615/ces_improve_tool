"""Authentication routes."""

from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from werkzeug.security import check_password_hash
from models import Engineer

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        engineer = Engineer.query.filter_by(email=email).first()
        if engineer and check_password_hash(engineer.password_hash, password):
            session["engineer_id"] = engineer.id
            session["engineer_name"] = engineer.name
            return redirect(url_for("dashboard.index"))

        flash("Invalid email or password", "danger")

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
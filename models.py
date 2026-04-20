from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    region = db.Column(db.Text, nullable=False)  # APAC / EMEA / Americas
    contact_person = db.Column(db.Text, nullable=False)

    incidents = db.relationship("Incident", backref="customer", lazy=True)

    def __repr__(self):
        return f"<Customer {self.name}>"


class Engineer(db.Model):
    __tablename__ = "engineers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    password_hash = db.Column(db.Text, nullable=False)
    product_area = db.Column(db.Text, nullable=False)

    incidents = db.relationship("Incident", backref="engineer", lazy=True)
    followups = db.relationship("Followup", backref="assigned_engineer", lazy=True)

    def __repr__(self):
        return f"<Engineer {self.name}>"


class Incident(db.Model):
    __tablename__ = "incidents"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    engineer_id = db.Column(db.Integer, db.ForeignKey("engineers.id"), nullable=False)
    product_component = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)

    survey = db.relationship("Survey", backref="incident", uselist=False, lazy=True)

    def __repr__(self):
        return f"<Incident {self.id}: {self.summary[:30]}>"


class Survey(db.Model):
    __tablename__ = "surveys"

    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(
        db.Integer, db.ForeignKey("incidents.id"), nullable=False, unique=True
    )
    score = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ai_category = db.Column(db.Text)
    ai_confidence = db.Column(db.Float)

    followup = db.relationship("Followup", backref="survey", uselist=False, lazy=True)

    def __repr__(self):
        return f"<Survey {self.id}: score={self.score}>"


class Followup(db.Model):
    __tablename__ = "followups"

    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(
        db.Integer, db.ForeignKey("surveys.id"), nullable=False, unique=True
    )
    assigned_engineer_id = db.Column(
        db.Integer, db.ForeignKey("engineers.id"), nullable=False
    )
    status = db.Column(db.Text, nullable=False, default="pending")
    contact_method = db.Column(db.Text)  # email / phone / both
    engineer_category = db.Column(db.Text)
    notes = db.Column(db.Text)
    email_sent_at = db.Column(db.DateTime)
    call_scheduled_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Followup {self.id}: status={self.status}>"


class ReasonCategory(db.Model):
    __tablename__ = "reason_categories"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Text, nullable=False, unique=True)
    label = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<ReasonCategory {self.code}>"
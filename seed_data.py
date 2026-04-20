"""Seed the database with realistic mock data for demo purposes."""

import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app import create_app
from models import db, Customer, Engineer, Incident, Survey, Followup, ReasonCategory
from services.assignment import process_survey

app = create_app()

# --- Reference data ---
REASON_CATEGORIES = [
    ("slow_response", "Slow Response Time"),
    ("unresolved", "Issue Not Resolved"),
    ("poor_communication", "Poor Communication"),
    ("lack_expertise", "Lack of Technical Expertise"),
    ("process_issue", "Process / Escalation Issue"),
    ("expectation_mismatch", "Expectation Mismatch"),
    ("other", "Other"),
]

CUSTOMERS = [
    ("Siemens AG", "siemens@example.com", "EMEA", "Hans Mueller"),
    ("Toyota Motor Corp", "toyota@example.com", "APAC", "Kenji Tanaka"),
    ("Walmart Inc", "walmart@example.com", "Americas", "Sarah Johnson"),
    ("Samsung Electronics", "samsung@example.com", "APAC", "Min-jun Park"),
    ("Nestle SA", "nestle@example.com", "EMEA", "Pierre Dupont"),
    ("Petrobras", "petrobras@example.com", "Americas", "Carlos Silva"),
    ("Tata Consultancy", "tata@example.com", "APAC", "Raj Patel"),
    ("BMW Group", "bmw@example.com", "EMEA", "Klaus Weber"),
    ("Procter & Gamble", "pg@example.com", "Americas", "Emily Davis"),
    ("Infosys Limited", "infosys@example.com", "APAC", "Ananya Sharma"),
]

ENGINEERS = [
    ("Zhang Wei", "zhang.wei@sap.demo", "ERP/FI"),
    ("Li Ming", "li.ming@sap.demo", "ERP/MM"),
    ("Wang Fang", "wang.fang@sap.demo", "S/4HANA"),
    ("Chen Jie", "chen.jie@sap.demo", "BTP"),
    ("Liu Yang", "liu.yang@sap.demo", "SuccessFactors"),
]

PRODUCTS = [
    "SAP ERP/FI-GL", "SAP ERP/FI-AR", "SAP ERP/FI-AP",
    "SAP ERP/MM-PO", "SAP ERP/MM-IM",
    "SAP S/4HANA Migration Cockpit", "SAP S/4HANA Fiori Launchpad",
    "SAP BTP Cloud Foundry", "SAP BTP Integration Suite",
    "SAP SuccessFactors Employee Central", "SAP SuccessFactors Recruiting",
]

# Comments mapped by score range
LOW_COMMENTS = [
    "I waited over 2 weeks for a response. The delay was unacceptable and the issue is still not resolved.",
    "The engineer didn't understand our configuration. Wrong solution was applied and we had to revert.",
    "No update for days. I had to chase the support team multiple times. Very disappointed.",
    "Our ticket was transferred between 3 different teams. Bounced around with no clear ownership.",
    "The issue is still broken after the proposed fix. Same error still occurs in production.",
    "Expected a workaround within 24 hours as promised by our account manager. Very misleading.",
    "Response was slow and the engineer seemed inexperienced with our S/4HANA landscape.",
    "We never heard back after the initial response. No follow-up, no resolution. Ignored completely.",
    "The escalation process took too long. Multiple teams involved but nobody took ownership.",
    "Incorrect solution was suggested. The engineer didn't understand the root cause at all.",
    "We had to wait a month for a patch. The delay caused significant business impact.",
    "Communication was unclear throughout. Didn't explain the technical details properly.",
    "Promised a call back that never happened. No response to follow-up emails either.",
    "The fix didn't work and the same issue reappeared. Still open after 3 weeks.",
    "Was told the issue would be fixed in the next patch but it wasn't. Very disappointed.",
]

MID_COMMENTS = [
    "Issue was resolved but took longer than expected. Communication could be better.",
    "Adequate support but the initial response time was a bit slow.",
    "Solution worked but documentation provided was not very clear.",
]

HIGH_COMMENTS = [
    "Excellent support! The engineer resolved our issue quickly and explained everything clearly.",
    "Very professional and knowledgeable. Issue was fixed within hours.",
    "Great communication throughout. Kept us updated at every step. Highly satisfied.",
    "Outstanding technical expertise. The root cause analysis was thorough and the fix was permanent.",
    "Quick turnaround and the engineer went above and beyond to help us.",
]


def seed():
    with app.app_context():
        # Drop and recreate
        db.drop_all()
        db.create_all()
        print("Database tables created.")

        # Reason categories
        for code, label in REASON_CATEGORIES:
            db.session.add(ReasonCategory(code=code, label=label))
        db.session.commit()
        print(f"  {len(REASON_CATEGORIES)} reason categories inserted.")

        # Customers
        customers = []
        for name, email, region, contact in CUSTOMERS:
            c = Customer(name=name, email=email, region=region, contact_person=contact)
            db.session.add(c)
            customers.append(c)
        db.session.commit()
        print(f"  {len(customers)} customers inserted.")

        # Engineers (password: demo123)
        pwd_hash = generate_password_hash("demo123")
        engineers = []
        for name, email, area in ENGINEERS:
            e = Engineer(name=name, email=email, password_hash=pwd_hash, product_area=area)
            db.session.add(e)
            engineers.append(e)
        db.session.commit()
        print(f"  {len(engineers)} engineers inserted.")

        # Generate incidents and surveys over 6 months
        base_date = datetime(2025, 11, 1)
        incidents_created = 0
        surveys_created = 0

        for month_offset in range(6):
            month_start = base_date + timedelta(days=30 * month_offset)
            count = random.randint(8, 15)

            for _ in range(count):
                customer = random.choice(customers)
                engineer = random.choice(engineers)
                product = random.choice(PRODUCTS)

                created = month_start + timedelta(
                    days=random.randint(0, 28),
                    hours=random.randint(8, 17),
                )
                resolved = created + timedelta(
                    days=random.randint(1, 14),
                    hours=random.randint(1, 8),
                )

                incident = Incident(
                    customer_id=customer.id,
                    engineer_id=engineer.id,
                    product_component=product,
                    summary=f"{product} issue reported by {customer.name}",
                    created_at=created,
                    resolved_at=resolved,
                )
                db.session.add(incident)
                db.session.flush()
                incidents_created += 1

                # Generate score with realistic distribution
                # ~25% score 1-2, ~15% score 3, ~60% score 4-5
                r = random.random()
                if r < 0.12:
                    score = 1
                elif r < 0.25:
                    score = 2
                elif r < 0.40:
                    score = 3
                elif r < 0.70:
                    score = 4
                else:
                    score = 5

                if score <= 2:
                    comment = random.choice(LOW_COMMENTS)
                elif score == 3:
                    comment = random.choice(MID_COMMENTS)
                else:
                    comment = random.choice(HIGH_COMMENTS)

                survey = Survey(
                    incident_id=incident.id,
                    score=score,
                    comment=comment,
                    submitted_at=resolved + timedelta(days=random.randint(0, 3)),
                )
                db.session.add(survey)
                db.session.flush()
                surveys_created += 1

                # Process survey (AI analysis + auto-create followup for low scores)
                process_survey(survey)

        db.session.commit()
        print(f"  {incidents_created} incidents created.")
        print(f"  {surveys_created} surveys created.")

        followup_count = Followup.query.count()
        print(f"  {followup_count} follow-ups auto-generated for low-score surveys.")

        # Mark some followups as completed for demo variety
        followups = Followup.query.all()
        completed_count = 0
        for f in followups:
            r = random.random()
            if r < 0.3:
                f.status = "completed"
                f.engineer_category = random.choice([c[0] for c in REASON_CATEGORIES[:6]])
                f.notes = "Discussed with customer, root cause identified and addressed."
                f.contact_method = random.choice(["email", "phone", "both"])
                f.completed_at = f.created_at + timedelta(days=random.randint(1, 7))
                completed_count += 1
            elif r < 0.5:
                f.status = "in_progress"
                f.contact_method = random.choice(["email", "phone"])
                f.email_sent_at = f.created_at + timedelta(hours=random.randint(1, 48))

        db.session.commit()
        print(f"  {completed_count} follow-ups marked as completed for demo.")
        print("\nDone! Run 'python app.py' to start the server.")
        print("Login with any engineer email (e.g. zhang.wei@sap.demo) and password: demo123")


if __name__ == "__main__":
    seed()
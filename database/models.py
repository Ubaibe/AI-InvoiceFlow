from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta

db = SQLAlchemy()


class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))

    email = db.Column(db.String(100), unique=True)

    password = db.Column(db.String(255))


class Invoice(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    amount = db.Column(db.Float)

    buyer = db.Column(db.String(200))

    due_date = db.Column(db.Date)

    risk_score = db.Column(db.Integer)

    status = db.Column(db.String(50))

    auction_end = db.Column(db.DateTime)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    invoice_number = db.Column(db.String(100))

    industry = db.Column(db.String(100))

    ai_summary = db.Column(db.Text)

    invoice_number = db.Column(db.String(100))

    industry = db.Column(db.String(100))

    file_path = db.Column(db.String(255))

    grade = db.Column(db.String(5))

    apr = db.Column(db.Float)

    fraud_probability = db.Column(db.Float)

    funding_progress = db.Column(db.Float)

    auction_status = db.Column(
        db.String(20),
        default="Open"
    )

    private_ledger_id = db.Column(
        db.String(100),
        unique=True
    )

    auction_id = db.Column(
        db.String(100)
    )

    privacy_status = db.Column(
        db.String(30),
        default="Protected"
    )

    visibility = db.Column(
        db.String(30),
        default="Authorized Only"
    )

    auction_end = datetime.utcnow() + timedelta(hours=24)

class Bid(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    invoice_id = db.Column(
        db.Integer,
        db.ForeignKey("invoice.id")
    )

    lender_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    apr = db.Column(db.Float)

    amount = db.Column(db.Float)

class Investment(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    invoice_id = db.Column(
        db.Integer,
        db.ForeignKey("invoice.id")
    )

    investor_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    returns = db.Column(db.Float)

class PrivateLedger(db.Model):

    id = db.Column(
        db.String(100),
        primary_key=True
    )

    invoice_number = db.Column(
        db.String(100)
    )

    buyer = db.Column(
        db.String(200)
    )

    amount = db.Column(
        db.Float
    )

    due_date = db.Column(
        db.Date
    )

    industry = db.Column(
        db.String(100)
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

class PrivateAuction(db.Model):

    id = db.Column(
        db.String(100),
        primary_key=True
    )

    private_ledger_id = db.Column(
        db.String(100),
        db.ForeignKey("private_ledger.id")
    )

    status = db.Column(
        db.String(30),
        default="OPEN"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

class PrivateBid(db.Model):

    id = db.Column(
        db.String(100),
        primary_key=True
    )

    auction_id = db.Column(
        db.String(100),
        db.ForeignKey("private_auction.id")
    )

    lender_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    amount = db.Column(
        db.Float
    )

    apr = db.Column(
        db.Float
    )

    submitted_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
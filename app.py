from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid
from openai import OpenAI
from datetime import datetime
from services.underwriting import generate_credit_memo
from agents.auction_ai import generate_ai_bids
from agents.auction_agent import select_winning_bid
from agents.portfolio_dashboard import build_portfolio_dashboard
from agents.credit_agent import calculate_credit_score
from werkzeug.utils import secure_filename
from agents.portfolio_engine import allocate_portfolio
from agents.portfolio_ai import generate_portfolio_commentary
from agents.llm_underwriter import generate_ai_credit_memo
from agents.extractor_agent import process_invoice
from agents.matching_agents import choose_best_bid
from agents.privacy_agent import anonymize_buyer
from agents.underwriting_agent import generate_underwriting_report
from services.canton_service import CantonService
from services.underwriting import generate_credit_memo
from datetime import datetime
from services.underwriter import calculate_underwriting
from services.pdf_to_image import pdf_first_page
from flask import Response
from services.openrouter_service import stream_credit_memo
from database.models import db, User, Invoice, Investment, Bid, Investment, PrivateLedger, PrivateAuction, PrivateBid
import json
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(

    base_url="https://openrouter.ai/api/v1",

    api_key=os.getenv("OPENROUTER_API_KEY")

)

app = Flask(__name__)

canton = CantonService()

app.config["SECRET_KEY"] = "supersecretkey"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///invoiceflow.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(
    app.config["UPLOAD_FOLDER"],
    exist_ok=True
)

db.init_app(app)

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(
        User,
        int(user_id)
    )

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        user = User(
            name=name,
            email=email,
            password=password
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            login_user(user)

            return redirect(
                url_for("command_center")
            )

    return render_template("login.html")

@app.route("/command_center")
@login_required
def command_center():

    invoices = Invoice.query.all()

    total_volume = sum(i.amount for i in invoices)

    average_apr = (
        round(sum(i.apr for i in invoices) / len(invoices), 2)
        if invoices else 0
    )

    pending = len(
        [i for i in invoices if i.status == "Pending"]
    )

    active = len(
        [i for i in invoices if i.status != "Funded"]
    )

    return render_template(

        "command_center.html",

        total_invoices=len(invoices),

        total_volume=total_volume,

        average_apr=average_apr,

        pending=pending,

        active=active

    )

@app.route("/wallet_login")
def wallet_login():

    return jsonify({

        "address":

        "wallet-demo-" +

        str(uuid.uuid4())[:8]

    })

@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect("/")

@app.route("/borrower_dashboard")
@login_required
def borrower_dashboard():
    invoices = Invoice.query.filter_by(
        user_id=current_user.id
    ).all()

    outstanding_amount = sum(
        invoice.amount
        for invoice in invoices
        if invoice.status != "Funded"
    )

    active_invoices = len(invoices)

    if invoices:
        average_apr = round(
            sum(invoice.apr for invoice in invoices) / len(invoices),
            1
        )
    else:
        average_apr = 0

    return render_template("borrower_dashboard.html",
        invoices=invoices,
        outstanding_amount=outstanding_amount,
        active_invoices=active_invoices,
        average_apr=average_apr)

@app.route("/lender_dashboard")
@login_required
def lender_dashboard():
    investments = Investment.query.filter_by(
        investor_id=current_user.id
    ).all()

    return render_template("lender_dashboard.html",
        investments=investments)

@app.route("/upload_invoice", methods=["GET", "POST"])
@login_required
def upload_invoice():

    if request.method == "POST":

        # -----------------------------
        # Save uploaded PDF
        # -----------------------------

        file = request.files["invoice_file"]

        filename = secure_filename(file.filename)

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(filepath)

        # -----------------------------
        # Manual invoice details
        # -----------------------------

        invoice_number = request.form["invoice_number"]

        buyer = request.form["buyer"]

        amount = float(request.form["amount"])

        industry = request.form["industry"]

        due_date = datetime.strptime(
            request.form["due_date"],
            "%Y-%m-%d"
        ).date()

        # -----------------------------
        # AI Underwriting
        # -----------------------------

        credit = calculate_credit_score(amount)

        memo = generate_credit_memo(
            invoice_number,
            buyer,
            amount,
            industry,
            due_date
        )

        # -----------------------------
        # Store privately on Canton
        # -----------------------------

        private_payload = {

            "invoice_number": invoice_number,

            "buyer": buyer,

            "amount": amount,

            "industry": industry,

            "due_date": due_date.strftime("%Y-%m-%d")

        }

        private_ledger_id = canton.store_private_invoice(
            private_payload
        )

        auction = canton.create_private_auction(
            private_ledger_id
        )

        auction_id = auction["auction_id"]

        # -----------------------------
        # Save Invoice
        # -----------------------------

        invoice = Invoice(

            user_id=current_user.id,

            invoice_number=invoice_number,

            buyer=buyer,

            amount=amount,

            due_date=due_date,

            industry=industry,

            risk_score=credit["risk_score"],

            grade=credit["grade"],

            apr=credit["apr"],

            fraud_probability=0,

            funding_progress=0,

            status="Pending",

            file_path=filepath,

            ai_summary=memo,

            auction_status="Open",

            private_ledger_id=private_ledger_id,

            auction_id=auction_id,

            privacy_status="Protected",

            visibility="Authorized Only"

        )

        db.session.add(invoice)

        db.session.commit()

        return redirect(
            url_for("borrower_dashboard")
        )

    return render_template(
        "upload_invoice.html"
    )

@app.route("/invoice/<int:invoice_id>")
@login_required
def invoice_details(invoice_id):

    invoice = Invoice.query.get_or_404(
        invoice_id
    )

    can_view = canton.authorize_viewer(

        invoice,

        current_user

    )

    if can_view:

        buyer = invoice.buyer

        amount = invoice.amount

        privacy_message = "Full access granted."

    else:

        buyer = anonymize_buyer(

            invoice.buyer,

            invoice.industry

        )

        amount = "Confidential"

        privacy_message = (

            "Confidential data is protected "

            "until funding is completed."

        )
    try:

        credit_memo = generate_ai_credit_memo(
            invoice
        )

    except Exception:

        credit_memo = generate_underwriting_report(
            invoice
        )
    return render_template(

        "invoice_details.html",

        invoice=invoice,

        buyer=buyer,

        amount=amount,

        can_view=can_view,

        privacy_message=privacy_message,

        credit_memo=credit_memo

    )

@app.route("/marketplace")
def marketplace():
    invoices = Invoice.query.all()

    for invoice in invoices:
        invoice.display_buyer = anonymize_buyer(
            invoice.buyer,
            invoice.industry
        )

    return render_template(
        "marketplace.html",
        invoices=invoices
    )

@app.route("/fund/<int:invoice_id>",
methods=["POST"])
@login_required
def fund_invoice(invoice_id):

    invoice = Invoice.query.get_or_404(
        invoice_id
    )

    investment = Investment(

        invoice_id=invoice.id,

        investor_id=current_user.id,

        returns=invoice.amount * (
            invoice.apr / 100
        )
    )

    invoice.status = "Funded"

    invoice.funding_progress = 100

    db.session.add(investment)

    db.session.commit()

    return redirect(
        url_for("lender_dashboard")
    )

@app.route("/about")
def about():
    return render_template("about.html")

@app.route(
    "/bid/<int:invoice_id>",
    methods=["GET", "POST"]
)
@login_required
def bid_invoice(invoice_id):

    invoice = Invoice.query.get_or_404(
        invoice_id
    )

    if request.method == "POST":
        amount = float(request.form["amount"])

        apr = float(request.form["apr"])

        # ----------------------------------
        # Send bid through Canton first
        # ----------------------------------

        canton.submit_private_bid(

            invoice.auction_id,

            current_user.id,

            amount,

            apr

        )

        # ----------------------------------
        # Save application record
        # ----------------------------------

        bid = Bid(

            invoice_id=invoice.id,

            lender_id=current_user.id,

            amount=amount,

            apr=apr

        )

        db.session.add(bid)

        db.session.commit()

        return redirect(url_for("marketplace"))

    return render_template(

        "bid.html",

        invoice=invoice,

        bids=invoice.bids

    )

@app.route(
    "/select_bid/<int:invoice_id>"
)
@login_required
def select_bid(invoice_id):

    invoice = Invoice.query.get_or_404(invoice_id)

    bids = Bid.query.filter_by(
        invoice_id=invoice_id
    ).all()

    winner = choose_best_bid(bids)

    if winner:

        investment = Investment(

            invoice_id=winner.invoice_id,

            investor_id=winner.lender_id,

            returns=winner.amount * (
                winner.apr / 100
            )

        )

        invoice.status = "Funded"

        invoice.funding_progress = 100

        db.session.add(investment)

        db.session.commit()

    return redirect(
        url_for(
            "invoice_details",
            invoice_id=invoice_id
        )
    )

@app.route("/stream_memo/<int:invoice_id>")
@login_required
def stream_memo(invoice_id):

    invoice = Invoice.query.get_or_404(invoice_id)

    prompt = f"""
    You are the Chair of the Investment Committee at a global institutional private credit fund.

    Your responsibility is to prepare the final underwriting memorandum that will be presented to institutional investors considering financing this invoice.

    Write exactly like an experienced investment committee member at BlackRock, Apollo, Ares, Goldman Sachs Asset Management or JPMorgan Private Credit.

    Return ONLY Markdown.

    Do NOT use code blocks.

    Do NOT mention AI.

    Use professional formatting.

    Use proper markdown tables.

    Use bullet points.

    The memorandum MUST follow this structure.

    # Institutional Credit Memorandum

    Prepared for: Investment Committee

    ---

    ## Executive Summary

    Provide a concise institutional overview.

    ---

    ## Invoice Overview

    | Item | Value |
    |------|------|
    | Invoice Number | {invoice.invoice_number} |
    | Buyer | {invoice.buyer} |
    | Industry | {invoice.industry} |
    | Amount | {invoice.amount} |
    | Due Date | {invoice.due_date} |

    ---

    ## Credit Assessment

    | Metric | Value |
    |------|------|
    | Risk Score | {invoice.risk_score} |
    | Credit Grade | {invoice.grade} |
    | APR | {invoice.apr}% |
    | Fraud Probability | {invoice.fraud_probability}% |

    Explain what these metrics imply.

    ---

    ## Buyer Assessment

    Evaluate the buyer's repayment capacity.

    ---

    ## Industry Outlook

    Discuss macroeconomic outlook.

    ---

    ## Cash Flow Analysis

    Assess payment certainty.

    ---

    ## Key Strengths

    Provide 4–6 bullets.

    ---

    ## Key Risks

    Provide 4–6 bullets.

    ---

    ## Fraud Assessment

    Evaluate fraud indicators.

    ---

    # Investment Committee Decision

    Determine ONE of the following:

    **APPROVE**

    **APPROVE WITH CONDITIONS**

    **DECLINE**

    Then provide a professional table exactly like this:

    | Decision Metric | Value |
    |------|------|
    | Recommended Investment | (recommend an amount to finance based on the invoice value and risk) |
    | Expected Annual Yield | (estimated annual yield) |
    | Maximum Portfolio Exposure | (recommended concentration limit) |
    | Portfolio Bucket | (e.g. Trade Receivables, Manufacturing Receivables, Energy, Healthcare, etc.) |
    | Risk Grade | {invoice.grade} |
    | AI Confidence | (confidence percentage) |

    Finally write a section titled:

    ## Committee Notes

    Write 2–3 professional paragraphs explaining why the committee reached its decision and any conditions or monitoring requirements.

    End with one sentence that would appear in official investment committee minutes.
    """

    return Response(
        stream_credit_memo(prompt),
        mimetype="text/plain"
    )

@app.route("/committee_decision/<int:invoice_id>")
@login_required
def committee_decision(invoice_id):

    invoice = Invoice.query.get_or_404(invoice_id)

    prompt = f"""
You are the Investment Committee Chair of a global private credit fund.

Review the following invoice and return ONLY valid JSON.

Invoice

Number: {invoice.invoice_number}

Buyer: {invoice.buyer}

Industry: {invoice.industry}

Amount: {invoice.amount}

Due Date: {invoice.due_date}

Risk Score: {invoice.risk_score}

Grade: {invoice.grade}

APR: {invoice.apr}

Fraud Probability: {invoice.fraud_probability}

Return EXACTLY this JSON.

{{
    "decision":"",
    "investment":"",
    "yield":"",
    "exposure":"",
    "bucket":"",
    "confidence":"",
    "notes":""
}}

Do not include markdown.

Return only JSON.
"""

    response = client.chat.completions.create(

        model="openrouter/free",

        messages=[

            {

                "role":"user",

                "content":prompt

            }

        ],

        temperature=0.2

    )

    return jsonify(

        json.loads(

            response.choices[0].message.content

        )

    )

@app.route("/portfolio_allocation/<int:invoice_id>")

@login_required

def portfolio_allocation(invoice_id):

    invoice = Invoice.query.get_or_404(invoice_id)

    allocation = allocate_portfolio(invoice)

    commentary = generate_portfolio_commentary(

        invoice,

        allocation

    )

    allocation["commentary"] = commentary

    return jsonify(allocation)

@app.route("/portfolio_dashboard/<int:invoice_id>")

@login_required

def portfolio_dashboard(invoice_id):

    invoice = Invoice.query.get_or_404(invoice_id)

    return jsonify(

        build_portfolio_dashboard(invoice)

    )

@app.route("/auction_room/<int:invoice_id>")
@login_required
def auction_room(invoice_id):

    invoice = Invoice.query.get_or_404(invoice_id)

    bids = generate_ai_bids(invoice)

    winner = select_winning_bid(bids)

    return jsonify({

        "bids": winner["ranked"],

        "winner": winner["winner"],

        "reason": winner["reason"]

    })

@app.route("/auction/finalize", methods=["POST"])
@login_required
def finalize_auction():

    data = request.get_json()

    bids = data["bids"]

    class Bid:

        def __init__(self, data):

            self.institution = data["institution"]

            self.amount = float(data["amount"])

            self.apr = float(data["apr"])

            self.confidence = data["confidence"]

    bid_objects = [

        Bid(b)

        for b in bids

    ]

    result = select_winning_bid(

        bid_objects

    )

    winner = result["winner"]

    return jsonify({

        "institution": winner.institution,

        "amount": winner.amount,

        "apr": winner.apr,

        "confidence": winner.confidence,

        "reason": result["reason"]

    })

@app.route(

    "/settle/<int:invoice_id>",

    methods=["POST"]

)

@login_required

def settle_invoice(invoice_id):

    invoice = Invoice.query.get_or_404(invoice_id)

    winner = Bid.query.filter_by(

        invoice_id=invoice.id

    ).order_by(

        Bid.apr.asc()

    ).first()

    if not winner:

        return jsonify({

            "error":"No winning bid"

        }),400

    result = canton.settle_invoice(

        invoice,

        winner

    )

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
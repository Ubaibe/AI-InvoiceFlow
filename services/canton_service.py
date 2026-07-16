import uuid
from datetime import datetime
from database.models import (

    db,

    Investment,

    PrivateLedger,

    PrivateAuction,

    PrivateBid

)

class CantonService:
    """
    Simulated Canton privacy layer.

    All confidential invoice data is stored here before
    being referenced inside the application database.

    Later, this class can be replaced with the official
    Canton SDK/API implementation without changing
    the Flask routes.
    """

    def __init__(self):
        self.private_ledger = {}
        self.private_auctions = {}

    # -----------------------------------------
    # Invoice Privacy
    # -----------------------------------------

    def store_private_invoice(self, invoice_data):
        ledger = PrivateLedger(

            id=str(uuid.uuid4()),

            invoice_number=invoice_data["invoice_number"],

            buyer=invoice_data["buyer"],

            amount=invoice_data["amount"],

            due_date=datetime.strptime(

                invoice_data["due_date"],

                "%Y-%m-%d"

            ).date(),

            industry=invoice_data["industry"]

        )

        db.session.add(ledger)

        db.session.commit()

        return ledger.id

    def reveal_invoice(

            self,

            private_ledger_id

    ):
        return PrivateLedger.query.get(

            private_ledger_id

        )

    # -----------------------------------------
    # Permissions
    # -----------------------------------------

    def authorize_viewer(

            self,

            invoice,

            user

    ):

        # Borrower always has access

        if invoice.user_id == user.id:
            return True

        # Winning lender has access

        investment = Investment.query.filter_by(

            invoice_id=invoice.id,

            investor_id=user.id

        ).first()

        if investment:
            return True

        return False

    # -----------------------------------------
    # Blind Auction
    # -----------------------------------------

    def create_private_auction(

            self,

            private_ledger_id

    ):
        auction = PrivateAuction(

            id=str(uuid.uuid4()),

            private_ledger_id=private_ledger_id,

            status="OPEN"

        )

        db.session.add(auction)

        db.session.commit()

        return {

            "auction_id": auction.id

        }

    def submit_private_bid(

            self,

            auction_id,

            lender_id,

            amount,

            apr

    ):
        bid = PrivateBid(

            id=str(uuid.uuid4()),

            auction_id=auction_id,

            lender_id=lender_id,

            amount=amount,

            apr=apr

        )

        db.session.add(bid)

        db.session.commit()

        return bid

    def get_private_bids(self, auction_id):

        return self.private_auctions[auction_id]["bids"]

    # -----------------------------------------
    # Auction Settlement
    # -----------------------------------------

    def choose_best_bid(

            self,

            auction_id

    ):
        bids = PrivateBid.query.filter_by(

            auction_id=auction_id

        ).all()

        if not bids:
            return None

        return min(

            bids,

            key=lambda bid: bid.apr

        )

    def settle_invoice(

            self,

            invoice,

            winning_bid

    ):

        ledger_id = str(uuid.uuid4())

        settlement_hash = str(uuid.uuid4())

        ownership_token = str(uuid.uuid4())

        timestamp = datetime.utcnow().isoformat()

        invoice.status = "Funded"

        invoice.funding_progress = 100

        db.session.commit()

        return {

            "ledger_id": ledger_id,

            "settlement_hash": settlement_hash,

            "ownership_token": ownership_token,

            "timestamp": timestamp

        }
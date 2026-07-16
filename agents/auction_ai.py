import random


INSTITUTIONS = [

    "Apollo Private Credit",

    "BlackRock Private Debt",

    "Goldman Sachs Asset Management",

    "Ares Management",

    "KKR Credit",

    "Blue Owl Capital",

    "Brookfield Credit",

    "Carlyle Private Credit"

]


def generate_ai_bids(invoice):

    bids = []

    base_apr = invoice.apr

    amount = invoice.amount

    score = invoice.risk_score

    grade = invoice.grade

    industry = invoice.industry

    # Better invoices receive tighter pricing

    if score >= 90:

        spread = 0.20

    elif score >= 80:

        spread = 0.40

    elif score >= 70:

        spread = 0.80

    else:

        spread = 1.50

    selected = random.sample(INSTITUTIONS, 4)

    for institution in selected:

        adjustment = round(

            random.uniform(

                -spread,

                spread

            ),

            2

        )

        bids.append({

            "institution": institution,

            "amount": amount,

            "apr": round(

                base_apr + adjustment,

                2

            ),

            "grade": grade,

            "industry": industry,

            "confidence": random.randint(88,99)

        })

    bids.sort(

        key=lambda x: x["apr"]

    )

    return bids
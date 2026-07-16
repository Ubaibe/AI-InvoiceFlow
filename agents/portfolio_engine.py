from random import randint


def allocate_portfolio(invoice):

    score = invoice.risk_score
    amount = invoice.amount
    industry = invoice.industry
    apr = invoice.apr

    # ------------------------
    # Portfolio Selection
    # ------------------------

    if score >= 90:

        portfolio = "Senior Direct Lending Fund"

        weight = "3.5%"

        risk_bucket = "Tier I"

    elif score >= 80:

        portfolio = "Corporate Credit Opportunities Fund"

        weight = "5.2%"

        risk_bucket = "Tier II"

    else:

        portfolio = "Special Situations Fund"

        weight = "2.4%"

        risk_bucket = "Tier III"

    # ------------------------

    investment = amount

    expected_return = round(amount * (apr / 100), 2)

    remaining_capacity = f"${randint(45,95)}M"

    diversification = "Positive"

    sector_weight = f"{randint(6,18)}%"

    return {

        "portfolio": portfolio,

        "investment": f"${amount:,.0f}",

        "weight": weight,

        "yield": f"{apr}%",

        "capacity": remaining_capacity,

        "sector_weight": sector_weight,

        "diversification": diversification,

        "risk_bucket": risk_bucket,

        "expected_return": f"${expected_return:,.0f}"

    }
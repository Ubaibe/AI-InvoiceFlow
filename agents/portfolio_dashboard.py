def build_portfolio_dashboard(invoice):

    aum = 250000000

    deployed = 182000000 + invoice.amount

    deployment = round(
        deployed / aum * 100,
        1
    )

    avg_yield = round(
        (8.4 + invoice.apr) / 2,
        2
    )

    avg_risk = round(
        (81 + invoice.risk_score) / 2,
        1
    )

    return {

        "aum": f"${aum/1000000:.0f}M",

        "deployment": f"{deployment}%",

        "yield": f"{avg_yield}%",

        "risk": avg_risk

    }
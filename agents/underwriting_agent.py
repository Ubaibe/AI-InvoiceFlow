def generate_underwriting_report(invoice):

    score = invoice.risk_score

    grade = invoice.grade

    apr = invoice.apr

    amount = invoice.amount

    industry = invoice.industry

    fraud = invoice.fraud_probability

    if score >= 85:

        executive = (
            "This invoice demonstrates a strong "
            "credit profile with low expected "
            "default risk."
        )

        recommendation = "APPROVE FUNDING"

        confidence = 94

        concerns = [
            "No major concerns detected."
        ]

    elif score >= 70:

        executive = (
            "This invoice presents moderate "
            "risk and should undergo "
            "additional review."
        )

        recommendation = "REVIEW"

        confidence = 81

        concerns = [
            "Industry volatility",
            "Moderate repayment uncertainty"
        ]

    else:

        executive = (
            "This invoice presents elevated "
            "credit risk."
        )

        recommendation = "DECLINE"

        confidence = 76

        concerns = [
            "High default probability",
            "Weak repayment profile"
        ]

    strengths = []

    if score >= 80:

        strengths.append("Strong credit score")

    if amount >= 30000:

        strengths.append("Commercial invoice value")

    strengths.append("Private settlement via Canton")

    return {

        "executive": executive,

        "risk_score": score,

        "grade": grade,

        "confidence": confidence,

        "fraud": fraud,

        "industry": industry,

        "strengths": strengths,

        "concerns": concerns,

        "recommendation": recommendation,

        "apr": apr

    }
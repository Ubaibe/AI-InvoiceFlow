def anonymize_buyer(buyer_name, industry):
    """
    Returns an anonymized buyer label based on industry.
    """

    industry = (industry or "").lower()

    if industry == "retail":
        prefix = "Retail Enterprise"

    elif industry == "manufacturing":
        prefix = "Manufacturing Company"

    elif industry == "healthcare":
        prefix = "Healthcare Organization"

    elif industry == "technology":
        prefix = "Technology Firm"

    elif industry == "logistics":
        prefix = "Logistics Provider"

    else:
        prefix = "Private Buyer"

    number = abs(hash(buyer_name)) % 1000

    return f"{prefix} #{number}"
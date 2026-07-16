def calculate_credit_score(amount):

    if amount <= 10000:

        return {
            "risk_score": 95,
            "grade": "A",
            "apr": 6
        }

    elif amount <= 50000:

        return {
            "risk_score": 85,
            "grade": "A",
            "apr": 8
        }

    elif amount <= 100000:

        return {
            "risk_score": 75,
            "grade": "B",
            "apr": 10
        }

    else:

        return {
            "risk_score": 60,
            "grade": "C",
            "apr": 15
        }
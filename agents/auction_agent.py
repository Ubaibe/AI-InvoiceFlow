def select_winning_bid(bids):

    ranked = sorted(

        bids,

        key=lambda bid: (

            bid.apr,

            -bid.confidence

            - bid.amount

        )

    )

    winner = ranked[0]

    return {

        "winner": winner,

        "ranked": ranked,

        "reason":

        (

            "Selected based on the lowest financing cost, "

            "highest execution confidence, and full capital availability."

        )

    }
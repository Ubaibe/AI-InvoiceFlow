def choose_best_bid(bids):

    if not bids:

        return None

    return min(
        bids,
        key=lambda bid: bid.apr
    )
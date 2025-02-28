import norgatedata


def get_stocks_in_watchlist(universe):
    return norgatedata.watchlist_symbols(universe)


def get_overlapping_stocks(universe1, universe2):
    stocks1 = get_stocks_in_watchlist(universe1)
    stocks2 = get_stocks_in_watchlist(universe2)
    return set(stocks1).intersection(stocks2)


def get_overlap_with_universe(this_universe, that_universe):
    ov = get_overlapping_stocks(this_universe, that_universe)
    pcnt_overlapping = len(ov) / len(get_stocks_in_watchlist(this_universe)) * 100
    return pcnt_overlapping


if __name__ == "__main__":
    overlap_results = []
    # compare_to_watchlist = "Russell 1000"
    compare_to_watchlist = "S&P 500"
    for watchlist in norgatedata.watchlists():
        if watchlist == compare_to_watchlist:
            continue
        if "Current & Past" in watchlist:
            continue
        pcnt_overlap = get_overlap_with_universe(watchlist, compare_to_watchlist)
        overlap_results.append((pcnt_overlap, watchlist))

    overlap_results.sort()

    for pcnt, universe in overlap_results:
        print(f"{pcnt:6.2f}% - {universe}")
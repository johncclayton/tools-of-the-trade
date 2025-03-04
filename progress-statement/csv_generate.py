from trade_details import TradeDetails


class TradeDetailsCSVGenerator:
    @staticmethod
    def get_header_row():
        return [
            "Side",
            "Symbol",
            "Shares",

            "DateIn",
            "QtyIn",
            "PriceIn",
            "FeesIn",

            "Currency",

            "DateOut",
            "QtyOut",
            "PriceOut",
            "FeesOut",

            "ProfitLoss"
            "Strategy",
            "IsRealized"
        ]

    @staticmethod
    def get_data_row(trade):
        return [
            str(trade.Side),
            trade.Symbol,
            trade.Shares,

            trade.DateIn,
            f"{trade.QtyIn}",
            f"{trade.PriceIn}",
            f"{trade.FeesIn}",

            trade.Currency,

            trade.DateOut,
            f"{trade.QtyOut}",
            f"{trade.PriceOut}",
            f"{trade.FeesOut}",

            f"{trade.calculate_profit_loss()}",
            trade.Strategy,

            str(trade.is_realized())
        ]

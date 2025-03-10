from data.trade_details import TradeDetails


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

            "M2MPrice",
            "UsedCapital",

            "TotalFees",
            "GrossProfitLoss",
            "NetProfitLoss",
            "Strategy",
            "IsRealized"
        ]

    @staticmethod
    def get_data_row(trade):
        date_out = "" if trade.DateOut == "0001-01-01 00:00:00" else trade.DateOut

        row = [
            str(trade.Side),
            trade.Symbol,
            str(trade.Shares),

            trade.DateIn,
            f"{trade.QtyIn}",
            f"{trade.PriceIn}",
            f"{trade.FeesIn}",

            trade.Currency,

            date_out,
            f"{trade.QtyOut}",
            f"{trade.PriceOut}",
            f"{trade.FeesOut}",

            f"{trade.M2MPrice}",
            f"{trade.calculate_used_capital()}",

            f"{trade.calculate_total_fees()}",
            f"{trade.calculate_gross_profit_loss()}",
            f"{trade.calculate_net_profit_loss()}",

            trade.Strategy,
            str(trade.is_realized())
        ]
        return row


import unittest
from data.trade_details import TradeDetails
from trade_details_csv import TradeDetailsCSVGenerator


class TestTradeDetails(unittest.TestCase):

    def setUp(self):
        self.realized_trade = TradeDetails(
            Side=1,
            Symbol="AAPL",
            Shares=100,
            DateIn="2023-01-01",
            PriceIn=150.0,
            QtyIn=100,
            DateOut="2023-01-10",
            PriceOut=155.0,
            QtyOut=100,
            FeesIn=10.0,
            FeesOut=10.0,
            M2MPrice=0.0,
            Currency="USD",
            Strategy="Long"
        )

        self.unrealized_trade = TradeDetails(
            Side=1,
            Symbol="GOOGL",
            Shares=50,
            DateIn="2023-01-01",
            PriceIn=2000.0,
            QtyIn=50,
            DateOut="0001-01-01 00:00:00",
            PriceOut=0.0,
            QtyOut=0,
            FeesIn=5.0,
            FeesOut=0.0,
            M2MPrice=0.0,
            Currency="USD",
            Strategy="Long"
        )

    def test_is_realized(self):
        self.assertTrue(self.realized_trade.is_realized())
        self.assertFalse(self.unrealized_trade.is_realized())

    def test_calculate_used_capital(self):
        self.assertEqual(self.realized_trade.calculate_used_capital(), 15000.0)
        self.assertEqual(self.unrealized_trade.calculate_used_capital(), 100000.0)

    def test_calculate_total_fees(self):
        self.assertEqual(self.realized_trade.calculate_total_fees(), 20.0)
        self.assertEqual(self.unrealized_trade.calculate_total_fees(), 5.0)

    def test_calculate_gross_profit_loss(self):
        self.assertEqual(self.realized_trade.calculate_gross_profit_loss(), 500.0)
        self.assertEqual(self.unrealized_trade.calculate_gross_profit_loss(), 0.0)

    def test_calculate_net_profit_loss(self):
        self.assertEqual(self.realized_trade.calculate_net_profit_loss(), 480.0)
        self.assertEqual(self.unrealized_trade.calculate_net_profit_loss(), 0.0)

    def test_csv_output(self):
        header = TradeDetailsCSVGenerator.get_header_row()
        realized_data_row = TradeDetailsCSVGenerator.get_data_row(self.realized_trade)
        unrealized_data_row = TradeDetailsCSVGenerator.get_data_row(self.unrealized_trade)

        expected_header = [
            "Side", "Symbol", "Shares", "DateIn", "QtyIn", "PriceIn", "FeesIn",
            "Currency", "DateOut", "QtyOut", "PriceOut", "FeesOut", "M2MPrice",
            "UsedCapital", "TotalFees", "GrossProfitLoss", "NetProfitLoss",
            "Strategy", "IsRealized"
        ]

        expected_realized_data_row = [
            "1", "AAPL", "100", "2023-01-01", "100", "150.0", "10.0", "USD",
            "2023-01-10", "100", "155.0", "10.0", "0.0", "15000.0", "20.0",
            "500.0", "480.0", "Long", "True"
        ]

        expected_unrealized_data_row = [
            "1", "GOOGL", "50", "2023-01-01", "50", "2000.0", "5.0", "USD",
            "", "0", "0.0", "0.0", "0.0", "100000.0", "5.0",
            "0.0", "0.0", "Long", "False"
        ]

        self.assertEqual(header, expected_header)
        self.assertEqual(realized_data_row, expected_realized_data_row)
        self.assertEqual(unrealized_data_row, expected_unrealized_data_row)


if __name__ == '__main__':
    unittest.main()

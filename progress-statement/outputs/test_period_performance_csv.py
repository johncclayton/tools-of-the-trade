import unittest
from datetime import datetime
from data.trade_details import TradeDetails
from outputs.period_performance_csv import PerformanceCSVGenerator, PeriodType


class TestPerformanceCSVGenerator(unittest.TestCase):

    def setUp(self):
        # month 1 - first symbol, across multiple weeks

        self.realized_trade1 = TradeDetails(Side=1, Symbol="AAPL", Shares=100, DateIn="2023-01-01", PriceIn=150.0,
                                            QtyIn=100, DateOut="2023-01-10", PriceOut=155.0, QtyOut=100, FeesIn=10.0,
                                            FeesOut=10.0, M2MPrice=0.0, Currency="USD", Strategy="Apple")
        self.realized_trade2 = TradeDetails(Side=1, Symbol="AAPL", Shares=25, DateIn="2023-01-01", PriceIn=150.0,
                                            QtyIn=25, DateOut="2023-02-10", PriceOut=160.0, QtyOut=25, FeesIn=10.0,
                                            FeesOut=1.5, M2MPrice=0.0, Currency="USD", Strategy="Apple")
        self.realized_trade2 = TradeDetails(Side=1, Symbol="AAPL", Shares=25, DateIn="2023-01-01", PriceIn=150.0,
                                            QtyIn=25, DateOut="2023-02-22", PriceOut=160.0, QtyOut=25, FeesIn=10.0,
                                            FeesOut=1.5, M2MPrice=0.0, Currency="USD", Strategy="Apple")

        # month 1, second symbol

        self.realized_trade3 = TradeDetails(Side=1, Symbol="GOOGL", Shares=100, DateIn="2023-01-01", PriceIn=2000.0,
                                            QtyIn=100, DateOut="2023-01-15", PriceOut=2100.0, QtyOut=100, FeesIn=5.0,
                                            FeesOut=5.0, M2MPrice=0.0, Currency="USD", Strategy="Google")

        self.unrealized_trade = TradeDetails(Side=1, Symbol="MSFT", Shares=75, DateIn="2023-01-01", PriceIn=999.0,
                                             QtyIn=75, DateOut="0001-01-01 00:00:00", PriceOut=0.0, QtyOut=0,
                                             FeesIn=7.5, FeesOut=0.0, M2MPrice=0.0, Currency="USD", Strategy="Long")

        self.profit_loss_data = type('ProfitLossData', (object,), {
            'trades': [self.realized_trade1, self.realized_trade2, self.realized_trade3, self.unrealized_trade]
        })()

        self.expected_stats_monthly = {
            "2023-01": {
                "Apple": {"NetPnL": 480.0, "PeriodType": "Month", "UsedCapital": 15000.0},
                "Google": {"NetPnL": 9990.0, "PeriodType": "Month", "UsedCapital": 200000.0}
            },
            "2023-02": {
                "Apple": {"NetPnL": 238.50, "PeriodType": "Month", "UsedCapital": 3750.0},
            }
        }

        self.expected_stats_weekly = {
            "2023-W2": {
                "Apple": {"NetPnL": 480.0, "PeriodType": "Week", "UsedCapital": 15000.0},
                "Google": {"NetPnL": 9990.0, "PeriodType": "Week", "UsedCapital": 200000.0}
            },
            "2023-W8": {
                "Apple": {"NetPnL": 238.50, "PeriodType": "Week", "UsedCapital": 3750.0},
            }
        }

        self.expected_stats_daily = {
            "2023-01-10": {
                "Apple": {"NetPnL": 480.0, "PeriodType": "Day", "UsedCapital": 15000.0},
            },
            "2023-01-15": {
                "Google": {"NetPnL": 9990.0, "PeriodType": "Day", "UsedCapital": 200000.0}
            },
            "2023-02-22": {
                "Apple": {"NetPnL": 238.50, "PeriodType": "Day", "UsedCapital": 3750.0},
            }
        }

    def test_calculate_period_stats_monthly(self):
        generator = PerformanceCSVGenerator(self.profit_loss_data, PeriodType.MONTH)
        period_stats = generator._calculate_period_stats()
        self.assertEqual(period_stats, self.expected_stats_monthly)

    def test_calculate_period_stats_weekly(self):
        generator = PerformanceCSVGenerator(self.profit_loss_data, PeriodType.WEEK)
        period_stats = generator._calculate_period_stats()
        self.assertEqual(period_stats, self.expected_stats_weekly)

    def test_calculate_period_stats_daily(self):
        generator = PerformanceCSVGenerator(self.profit_loss_data, PeriodType.DAY)
        period_stats = generator._calculate_period_stats()
        self.assertEqual(period_stats, self.expected_stats_daily)

    def test_get_header_row(self):
        generator = PerformanceCSVGenerator(self.profit_loss_data, PeriodType.MONTH)
        header = generator.get_header_row()
        expected_header = ["Date", "Strategy", "PeriodType", "NetPnL", "UsedCapital"]
        self.assertEqual(header, expected_header)


if __name__ == '__main__':
    unittest.main()

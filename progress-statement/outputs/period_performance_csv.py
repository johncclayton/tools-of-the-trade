from datetime import datetime
from enum import Enum
from typing import List
from data.performance_row import PerformanceRow
from data.trade_details import TradeDetails


class PeriodType(Enum):
    DAY = "Day"
    WEEK = "Week"
    MONTH = "Month"


class PerformanceCSVGenerator:
    def __init__(self, profit_loss_data, period_type: PeriodType = PeriodType.MONTH):
        self.profit_loss_data = profit_loss_data
        self.period_type = period_type
        self.period_stats = self._calculate_period_stats()

    def _calculate_period_stats(self):
        grouped = {}
        for trade in self.profit_loss_data.trades:
            if not trade.is_realized():
                continue
            dt_out = datetime.fromisoformat(trade.DateOut)
            period_key = self._get_period_key(dt_out)
            if period_key not in grouped:
                grouped[period_key] = {}
            if trade.Strategy not in grouped[period_key]:
                grouped[period_key][trade.Strategy] = {
                    "NetPnL": 0.0,
                    "UsedCapital": 0.0,
                    "PeriodType": self.period_type.value
                }
            net_pnl = trade.calculate_net_profit_loss()
            used_capital = trade.calculate_used_capital()
            grouped[period_key][trade.Strategy]["UsedCapital"] += used_capital
            grouped[period_key][trade.Strategy]["NetPnL"] += net_pnl

        sorted_grouped = {}
        for date_key in sorted(grouped.keys()):
            sub_dict = grouped[date_key]
            sorted_sub_dict = {k: sub_dict[k] for k in sorted(sub_dict.keys())}
            sorted_grouped[date_key] = sorted_sub_dict
        return sorted_grouped

    def _get_period_key(self, dt_out: datetime) -> str:
        if self.period_type == PeriodType.DAY:
            return dt_out.strftime("%Y-%m-%d")
        elif self.period_type == PeriodType.WEEK:
            year, week, _ = dt_out.isocalendar()
            return f"{year}-W{week}"
        return dt_out.strftime("%Y-%m")

    def get_performance_rows(self) -> List[PerformanceRow]:
        rows = []
        for date_key, strategies in self.period_stats.items():
            for strategy, info in strategies.items():
                rows.append(PerformanceRow(
                    Date=date_key,
                    Strategy=strategy,
                    PeriodType=info["PeriodType"],
                    NetPnL=info["NetPnL"],
                    UsedCapital=info["UsedCapital"],
                ))
        return rows

    @staticmethod
    def get_header_row():
        return ["Date", "Strategy", "PeriodType", "NetPnL", "UsedCapital"]

    def get_data_rows(self):
        data = []
        for row in self.get_performance_rows():
            data.append([
                row.Date,
                row.Strategy,
                row.PeriodType,
                str(row.NetPnL),
                str(row.UsedCapital)
            ])
        return data

from dataclasses import dataclass, field
from typing import List


@dataclass
class TradeDetails:
    Side: int
    Symbol: str
    Shares: float
    DateIn: str
    PriceIn: float
    QtyIn: float
    DateOut: str
    QtyOut: float
    PriceOut: float
    FeesIn: float
    FeesOut: float
    M2MPrice: float
    Currency: str
    Strategy: str

    def is_long(self) -> bool:
        return self.Side == 1

    def is_short(self) -> bool:
        return self.Side == -1

    def is_realized(self) -> bool:
        return self.QtyIn > 0 and self.QtyOut > 0

    def calculate_used_capital(self) -> float:
        return self.QtyIn * self.PriceIn

    def calculate_total_fees(self) -> float:
        return self.FeesIn + self.FeesOut

    def calculate_gross_profit_loss(self) -> float:
        if not self.is_realized():
            return 0.0
        return self.Side * ((self.QtyOut * self.PriceOut) - (self.QtyIn * self.PriceIn))

    def calculate_net_profit_loss(self) -> float:
        if not self.is_realized():
            return 0.0
        return self.calculate_gross_profit_loss() - (self.FeesIn + self.FeesOut)


@dataclass
class ProfitLossData:
    trades: List[TradeDetails] = field(default_factory=list)

    def realized_trades(self) -> List[TradeDetails]:
        return [trade for trade in self.trades if trade.is_realized()]

    def unrealized_trades(self) -> List[TradeDetails]:
        return [trade for trade in self.trades if not trade.is_realized()]

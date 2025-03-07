from dataclasses import dataclass, field
from typing import List


@dataclass
class PerformanceRow:
    Date: str
    Strategy: str
    PeriodType: str
    NetPnL: float
    UsedCapital: float

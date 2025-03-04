from typing import Dict, List, Any



def print_realized_trades_table(trades: List[Dict[str, Any]]) -> None:
    """Prints a formatted table of realized trades."""
    table_data: List[List[str]] = [
        ["Symbol", "DateIn", "PriceIn", "SharesIn", "DateOut", "PriceOut", "SharesOut", "FeesIn", "FeesOut",
         "Capital Used", "Profit", "Currency"]]
    for trade in trades:
        used_capital = (trade['PriceIn'] * trade['SharesIn']) + trade['FeesIn']
        table_data.append([
            trade['Symbol'],
            trade['DateIn'],
            f"{trade['PriceIn']:,.2f}",
            f"{trade['SharesIn']:,.0f}",
            trade['DateOut'],
            f"{trade['PriceOut']:,.2f}",
            f"{trade['SharesOut']:,.0f}",
            f"{trade['FeesIn']:,.2f}",
            f"{trade['FeesOut']:,.2f}",
            f"${used_capital:,.2f}",
            f"${trade['Profit']:,.2f}",
            trade['Currency']
        ])

    column_widths: List[int] = [max(len(item[i]) for item in table_data) for i in range(len(table_data[0]))]

    for i, header in enumerate(table_data[0]):
        print(header.ljust(column_widths[i]) + "  ", end="")
    print()

    for row in table_data[1:]:
        for i, cell in enumerate(row):
            if i in [2, 3, 5, 6, 7, 8, 9]:  # Indices of numeric columns
                print(cell.rjust(column_widths[i]) + "  ", end="")
            else:
                print(cell.ljust(column_widths[i]) + "  ", end="")
        print()


def print_unrealized_trades_table(capital_data: Dict[str, Dict[str, float]], profit_data: Dict[str, float]) -> None:
    table_data: List[List[str]] = [["Strategy", "Symbol", "Profit/Loss", "  Cost Basis", "MTM Profit %"]]
    total_profit: float = 0
    total_capital: float = 0

    for strategy, symbol_data in capital_data.items():
        for symbol, capital in symbol_data.items():
            profit: float = profit_data[(strategy, symbol)]
            profit_percentage: float = (profit / capital) * 100 if capital != 0 else 0
            table_data.append([
                strategy,
                symbol,
                f"${profit:,.2f}",
                f"${capital:,.2f}",
                f"{profit_percentage:.2f}%"
            ])
            total_profit += profit
            total_capital += capital

    table_data.append([
        "Totals",
        "",
        f"${total_profit:,.2f}",
        f"${total_capital:,.2f}",
        ""
    ])

    column_widths: List[int] = [max(len(row[i]) for row in table_data) for i in range(len(table_data[0]))]

    for i, header in enumerate(table_data[0]):
        print(header.ljust(column_widths[i]) + "  ", end="")
    print()

    for row in table_data[1:]:
        for i, cell in enumerate(row):
            if i in [2, 3, 4]:  # numeric columns
                print(cell.rjust(column_widths[i]) + "  ", end="")
            else:
                print(cell.ljust(column_widths[i]) + "  ", end="")
        print()


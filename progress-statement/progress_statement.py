import csv, os
from collections import defaultdict
from typing import Dict, List, Any

from config import get_config
from pdf_reporting import generate_pdf_report
from price_extraction import get_closing_price_from_norgate
from trade_extraction import extract_year
from console_reporting import print_realized_trades_table, print_unrealized_trades_table


def calculate_profit_loss() -> dict[int, dict[str, dict[str, Any]]] | None:
    """
    Calculates and summarizes profit/loss, used capital, and profit percentage from trades in a CSV file.
    Skips trades with no strategy name. For unrealized P/L, it displays the symbol and capital used.
    """
    config = get_config()
    input_dir = config.get('paths', 'input_dir', fallback='.')
    filename = os.path.join(input_dir, 'OrderClerkTrades.csv')
    print(f"Reading CSV from: {filename}")

    # Data structure to store profits/losses and used capital, grouped by year and strategy
    GroupedDataType = Dict[int, Dict[str, Dict[str, Any]]]
    grouped_data: GroupedDataType = defaultdict(lambda: {
        "realized": {"trades": defaultdict(list), "profit": defaultdict(float), "capital": defaultdict(float)},
        "unrealized": {"profit": defaultdict(float), "capital": defaultdict(lambda: defaultdict(float))}
    })

    try:
        with open(filename, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            if reader.fieldnames is None:
                print("CSV file is empty or has no header.")
                return None

            for row in reader:
                try:
                    # Extract relevant data, handling potential missing values
                    symbol: str = row['Symbol']
                    strategy: str = row['Strategy'].strip()  # Get strategy and remove leading/trailing whitespace
                    if not strategy:  # Skip if strategy is empty
                        trade_id = row['TradeID']
                        date_in = row['DateIn']
                        print(f"Skipping trade {trade_id} for symbol {symbol} on {date_in} due to missing strategy.")
                        continue

                    side: int = int(row['Side'])  # 1 for buy, -1 for sale (if shorting is involved)
                    shares: float = float(row['Shares'])
                    date_in_str: str = row['DateIn']
                    price_in: float = float(row['PriceIn'])
                    fees_in: float = float(row['FeesIn'])
                    currency: str = row['Currency']
                    date_out_str: str = row['DateOut']
                    price_out: float = float(row['PriceOut'])
                    fees_out: float = float(row['FeesOut'])

                    # Extract year from DateOut
                    year: int = extract_year(date_out_str)

                    # Calculate used capital for the trade
                    used_capital: float = shares * price_in + fees_in

                    # Calculate gross profit/loss for the trade - by using the price data from Norgate
                    if date_out_str == '0001-01-01 00:00:00':
                        # Fetch price_out from Norgate for unrealized trades
                        price_out: float = get_closing_price_from_norgate(symbol, currency)
                        profit_loss: float = side * shares * (price_out - price_in) - fees_in  # mark to market
                        grouped_data[year]["unrealized"]["profit"][(strategy, symbol)] += profit_loss
                        grouped_data[year]["unrealized"]["capital"][strategy][symbol] += used_capital

                    else:
                        # Realized profit/loss
                        profit_loss: float = side * shares * (price_out - price_in) - (fees_in + fees_out)
                        trade_details: Dict[str, Any] = {
                            'Symbol': symbol,
                            'DateIn': date_in_str,
                            'PriceIn': price_in,
                            'SharesIn': shares,
                            'DateOut': date_out_str,
                            'PriceOut': price_out,
                            'SharesOut': shares,
                            'FeesIn': fees_in,
                            'FeesOut': fees_out,
                            'Profit': profit_loss,
                            'Currency': currency
                        }
                        grouped_data[year]["realized"]["trades"][strategy].append(trade_details)
                        grouped_data[year]["realized"]["profit"][strategy] += profit_loss
                        grouped_data[year]["realized"]["capital"][strategy] += used_capital

                except ValueError as e:
                    print(f"Error processing row: {row}. Error: {e}")
                    continue  # Skip to the next row
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

    # Output the results
    for year, data in sorted(grouped_data.items()):
        print(f"\n--- Year: {year} ---")
        total_profit_loss: float = 0
        total_used_capital: float = 0

        print("\nRealized Profit/Loss and Used Capital:")
        for strategy, trades in data["realized"]["trades"].items():
            capital: float = data["realized"]["capital"][strategy]
            profit: float = data["realized"]["profit"][strategy]
            profit_percentage: float = (profit / capital) * 100 if capital != 0 else 0  # Calculate profit percentage

            print(f"  - Strategy: {strategy}:")
            print_realized_trades_table(trades)

            print(
                f"    Total Profit = ${profit:,.2f}, Capital Used = ${capital:,.2f}, Profit % = {profit_percentage:.2f}%")
            total_profit_loss += profit
            total_used_capital += capital

        print("\nUnrealized Profit/Loss and Used Capital:")
        print_unrealized_trades_table(data["unrealized"]["capital"], data["unrealized"]["profit"])

        print(f"\n  **Total Profit/Loss for {year}: ${total_profit_loss:,.2f}**")

        total_profit_percentage = (
                                              total_profit_loss / total_used_capital) * 100 if total_used_capital != 0 else 0  # Calculate total profit percentage
        print(f"  **Total Capital Used for {year}: ${total_used_capital:,.2f}**")
        print(f"  **Total Profit % for {year}: {total_profit_percentage:.2f}%**")

    return grouped_data


print_pdf = False
if __name__ == "__main__":
    gd = calculate_profit_loss()
    if gd and print_pdf:
        pdf_filename = generate_pdf_report(gd)
        os.startfile(pdf_filename)

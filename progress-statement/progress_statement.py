import csv, os
import norgatedata
import pandas as pd
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Any

from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch

import configparser


def load_config(file_name='config.ini'):
    config = configparser.ConfigParser()
    search_paths = [os.getcwd(), os.path.expanduser('~')]
    ini_path = None

    for path in search_paths:
        potential_path = os.path.join(path, file_name)
        if os.path.exists(potential_path):
            ini_path = potential_path
            config.read(ini_path)
            break

    if ini_path is None:
        config.add_section('paths')
        config.set('paths', 'input_dir', '.')
        config.set('paths', 'output_dir', '.')
    else:
        if not config.has_section('paths'):
            raise ValueError(f"Missing 'paths' section in configuration file '{ini_path}'.")

    if not config.has_option('paths', 'input_dir'):
        raise ValueError(f"Missing 'input_dir' option in 'paths' section of configuration file '{ini_path}'.")

    if not config.has_option('paths', 'output_dir'):
        raise ValueError(f"Missing 'output_dir' option in 'paths' section of configuration file '{ini_path}'.")

    return config


def generate_pdf_report(grouped_data):
    config = load_config()
    output_dir = config.get('paths', 'output_dir', fallback='.')
    pdf_filename = os.path.join(output_dir, 'MyModernReport.pdf')
    print(f"Writing PDF to: {pdf_filename}")

    doc = SimpleDocTemplate(pdf_filename, pagesize=landscape(letter))
    styles = getSampleStyleSheet()
    modern_style = ParagraphStyle('Modern', parent=styles['Normal'],
                                  fontName='Helvetica', fontSize=10,
                                  leading=12, textColor=colors.black)
    no_unrealized_style = ParagraphStyle('NoUnrealized', parent=styles['Normal'],
                                         fontName='Helvetica-Bold', fontSize=36,
                                         textColor=colors.Color(0.4, 0.4, 0.4),
                                         alignment=1)
    story = []

    for year, data in sorted(grouped_data.items()):
        story.append(Paragraph(f"Year: {year}", modern_style))
        story.append(Paragraph("Realized Profit/Loss:", modern_style))

        realized_table_data = [
            ["Symbol", "DateIn", "PriceIn", "SharesIn", "DateOut", "PriceOut",
             "SharesOut", "FeesIn", "FeesOut", "Profit", "Currency"]
        ]
        for strategy, trades in data["realized"]["trades"].items():
            for trade in trades:
                realized_table_data.append([
                    trade['Symbol'], trade['DateIn'],
                    f"{trade['PriceIn']:.2f}", f"{trade['SharesIn']:.0f}",
                    trade['DateOut'], f"{trade['PriceOut']:.2f}",
                    f"{trade['SharesOut']:.0f}", f"{trade['FeesIn']:.2f}",
                    f"{trade['FeesOut']:.2f}", f"${trade['Profit']:.2f}", trade['Currency']
                ])

        col_widths = [
            1.2 * inch, 1.5 * inch, 0.8 * inch, 0.8 * inch,
            1.5 * inch, 0.8 * inch, 0.8 * inch, 0.8 * inch,
            0.8 * inch, 1.0 * inch, 0.8 * inch
        ]
        t = Table(realized_table_data, colWidths=col_widths)
        t.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue)
        ]))
        story.append(t)

        # Calculate yearly totals
        total_profit_loss = 0
        total_used_capital = 0
        for strategy in data["realized"]["profit"]:
            total_profit_loss += data["realized"]["profit"][strategy]
            total_used_capital += data["realized"]["capital"][strategy]
        total_profit_perc = (total_profit_loss / total_used_capital) * 100 if total_used_capital else 0

        # Add yearly totals table
        yearly_totals_data = [
            ["Total Profit/Loss:", f"${total_profit_loss:.2f}"],
            ["Capital Used:", f"${total_used_capital:.2f}"],
            ["Profit %:", f"{total_profit_perc:.2f}%"]
        ]
        totals_table = Table(yearly_totals_data, colWidths=[2.0 * inch, 2.0 * inch])
        totals_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue)
        ]))
        story.append(PageBreak())
        story.append(Paragraph(f"Year: {year}", modern_style))
        story.append(Paragraph("Year Totals:", modern_style))
        story.append(totals_table)

        story.append(PageBreak())
        story.append(Paragraph(f"Year: {year}", modern_style))
        story.append(Paragraph("Unrealized Profit/Loss and Used Capital:", modern_style))

        if not data["unrealized"]["capital"]:
            story.append(Paragraph("No Unrealized Trades Listed", no_unrealized_style))
        else:
            unrealized_table_data = [["Strategy", "Symbol", "Profit/Loss", "Cost Basis", "Profit %"]]
            for strategy, symbol_data in data["unrealized"]["capital"].items():
                for symbol, cap in symbol_data.items():
                    pf = data["unrealized"]["profit"][(strategy, symbol)]
                    pf_perc = (pf / cap) * 100 if cap else 0
                    unrealized_table_data.append([
                        strategy, symbol, f"${pf:.2f}", f"${cap:.2f}", f"{pf_perc:.2f}%"
                    ])
            col_count = len(unrealized_table_data[0])
            col_width = doc.width / col_count
            t_unreal = Table(unrealized_table_data, colWidths=[col_width] * col_count)
            t_unreal.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue)
            ]))
            story.append(t_unreal)

        story.append(PageBreak())

    doc.build(story)


def calculate_profit_loss() -> dict[int, dict[str, dict[str, Any]]] | None:
    """
    Calculates and summarizes profit/loss, used capital, and profit percentage from trades in a CSV file.
    Skips trades with no strategy name. For unrealized P/L, it displays the symbol and capital used.
    """
    config = load_config()
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
                        price_out: float = get_price_from_norgate(symbol, currency)
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


def extract_year(date_str: str) -> int:
    """Extracts the year from a date string.
    For unrealized trades, uses the current year.
    """
    if date_str != '0001-01-01 00:00:00':
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').year
    return datetime.now().year


def get_price_from_norgate(symbol: str, currency: str) -> float:
    """Fetches the closing price from Norgate for a given symbol and currency."""
    prior_business_day: datetime = datetime.today() - pd.offsets.BDay(1)
    try:
        price_recarray = norgatedata.price_timeseries(
            (symbol + ".au") if currency == "AUD" else symbol,
            start_date=prior_business_day,
            end_date=prior_business_day
        )
        price_dataframe = pd.DataFrame(price_recarray)
        return price_dataframe.iloc[0]['Close']
    except Exception as e:
        print(f"Error fetching price from Norgate for {symbol}: {e}")
        return 0.0  # Return a default value in case of an error


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


# Example usage (assuming the file is in the same directory)
print_pdf = False
if __name__ == "__main__":
    gd = calculate_profit_loss()
    if gd and print_pdf:
        generate_pdf_report(gd, 'MyModernReport.pdf')

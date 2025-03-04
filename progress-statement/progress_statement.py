import csv, os

from flask import Flask, Response
from config import get_config
from price_extraction import get_closing_price_from_norgate
from trade_details import TradeDetails, ProfitLossData
from csv_generate import TradeDetailsCSVGenerator

app = Flask(__name__)


def calculate_profit_loss() -> ProfitLossData | None:
    config = get_config()
    input_dir = config.get('paths', 'input_dir', fallback='.')
    filename = os.path.join(input_dir, 'OrderClerkTrades.csv')
    print(f"Reading CSV from: {filename}")

    grouped_data = ProfitLossData()

    try:
        with open(filename, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            if reader.fieldnames is None:
                print("CSV file is empty or has no header.")
                return None

            for row in reader:
                try:
                    symbol: str = row['Symbol']
                    strategy: str = row['Strategy'].strip()
                    if not strategy:
                        trade_id = row['TradeID']
                        date_in = row['DateIn']
                        print(f"Skipping trade {trade_id} for symbol {symbol} on {date_in} due to missing strategy.")
                        continue

                    side: int = int(row['Side'])
                    shares: float = float(row['Shares'])
                    date_in_str: str = row['DateIn']
                    qty_in: float = float(row['QtyIn']) # zero if not filled.
                    price_in: float = float(row['PriceIn'])
                    fees_in: float = float(row['FeesIn'])
                    currency: str = row['Currency']
                    date_out_str: str = row['DateOut']
                    qty_out: float = float(row['QtyOut']) # zero if no exit
                    price_out: float = float(row['PriceOut'])
                    fees_out: float = float(row['FeesOut'])

                    if date_out_str == '0001-01-01 00:00:00':
                        price_out = get_closing_price_from_norgate(symbol, currency)

                    trade_details = TradeDetails(
                        Side=side,
                        Symbol=symbol,
                        Shares=shares,
                        DateIn=date_in_str,
                        PriceIn=price_in,
                        QtyIn=qty_in,
                        DateOut=date_out_str,
                        PriceOut=price_out,
                        QtyOut=qty_out,
                        FeesIn=fees_in,
                        FeesOut=fees_out,
                        Currency=currency,
                        Strategy=strategy  # Added strategy attribute
                    )
                    grouped_data.trades.append(trade_details)

                except ValueError as e:
                    print(f"Error processing row: {row}. Error: {e}")
                    continue
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

    return grouped_data


@app.route('/profit_loss_data.csv')
def serve_profit_loss_data():
    profit_loss_data = calculate_profit_loss()
    if profit_loss_data is None:
        return "No data available", 404

    def generate():
        header = TradeDetailsCSVGenerator.get_header_row()
        yield ','.join(header) + '\n'
        for trade in profit_loss_data.trades:
            row = TradeDetailsCSVGenerator.get_header_row()
            yield ','.join(row) + '\n'

    return Response(generate(), mimetype='text/csv')


if __name__ == "__main__":
    app.run(debug=True)

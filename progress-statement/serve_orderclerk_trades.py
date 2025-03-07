import csv
import os

from flask import Flask, Response

from config import get_config
from outputs.trade_details_csv import TradeDetailsCSVGenerator
from outputs.period_performance_csv import PerformanceCSVGenerator
from price_extraction import get_closing_price_from_norgate
from data.trade_details import TradeDetails, ProfitLossData

app = Flask(__name__)


def read_trade_csv_list() -> ProfitLossData | None:
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
                    m2m_price: float = 0

                    if date_out_str == '0001-01-01 00:00:00' and qty_out == 0:
                        m2m_price = get_closing_price_from_norgate(symbol, currency)

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
                        M2MPrice=m2m_price,
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


# I would like to see the %age return on Used Capital for a time unit (day/week/month).
#
# output:
# - daily/weekly/monthly/yearly used capital, per strategy as well as corresponding profit/loss and %age return.
#
# so that:
# - I can import this into Excel and create graphs / reports etc to see how my strategies are performing.
# - I can create a total (all strategy) performance graph, grouped by period.
# - I can break that down by strategy.
# - I can do histograms of %age return over time periods, per strategy.
#
# actually the time roll up should be a parameter, so that the user can choose daily/weekly/monthly/yearly.
@app.route('/PeriodPerformance.csv')
def serve_period_performance_data():
    profit_loss_data = read_trade_csv_list()
    if profit_loss_data is None:
        return "No data available", 404

    # Instantiate PerformanceCSVGenerator with the full trade data
    performance_gen = PerformanceCSVGenerator(profit_loss_data)

    def generate():
        header = performance_gen.get_header_row()
        yield ','.join(header) + '\n'
        for row in performance_gen.get_data_rows():
            yield ','.join(row) + '\n'

    return Response(generate(), mimetype='text/csv')


# Return the total list of order clerk trades, including additional data - as a CSV file.
@app.route('/OrderClerkTrades.csv')
def serve_order_clerk_trades_data():
    profit_loss_data = read_trade_csv_list()
    if profit_loss_data is None:
        return "No data available", 404

    def generate():
        header = TradeDetailsCSVGenerator.get_header_row()
        yield ','.join(header) + '\n'
        for trade in profit_loss_data.trades:
            row = TradeDetailsCSVGenerator.get_data_row(trade)
            yield ','.join(row) + '\n'

    return Response(generate(), mimetype='text/csv')


if __name__ == "__main__":
    app.run(debug=True, port=os.environ.get('FLASK_RUN_PORT', 5000), host=os.environ.get('FLASK_RUN_HOST', '127.0.0.1'))

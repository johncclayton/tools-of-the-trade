import csv
import sys
import glob
from argparse import ArgumentParser, RawTextHelpFormatter
from datetime import datetime
from binance.client import Client
from binance.enums import HistoricalKlinesType
from tqdm import tqdm
from utils import read_symbols, create_path

INTERVALS = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w']
DATE_FORMAT = '%d/%m/%Y'

# calculate start time for a year
def get_start_time(year):
    return str(datetime(year, 1, 1).timestamp() * 1000)


def get_parser():
    parser = ArgumentParser(description="This is a script to download historical klines data", formatter_class=RawTextHelpFormatter)
    parser.add_argument('-i', dest='interval', default='1d', help='KLINE interval')
    parser.add_argument('-y', dest='year', default='2024', help='The year to obtain data for')
    # add a simple 'combine' flag to combine all the data into one file
    parser.add_argument('-c', dest='combine', action='store_true', help='Combine all data into one file')  
    return parser



def download_kline(symbol, klines_type, interval, start_year=2017):
    """Download spot/futures klines for selected symbol, and save the data into csv files.

    Args:
        symbol (str): e.g., 'BTCUSDT'
        klines_type (str): 'spot' or 'futures'
        interval ([type]): e.g., '5m' for 5 minutes interval
        start_year: the year you wish to obtain data for
    """
    the_start_time = get_start_time(start_year)
    if klines_type == 'spot':
        klines_enum = HistoricalKlinesType.SPOT
    elif klines_type == 'futures':
        klines_enum = HistoricalKlinesType.FUTURES
    try:
        klines = client.get_historical_klines(
            symbol=symbol,
            klines_type=klines_enum,
            interval=interval,
            start_str=the_start_time,
            limit=300
        )
    except Exception:
        print(f'No {klines_type} data for {symbol}')
        return
    # write into csv
    with open(f'./data/{klines_type}/{interval}/{start_year}_{symbol}.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(
            ['Symbol',
             'Open time',
             'Open',
             'High',
             'Low',
             'Close',
             'Volume',
             'Close time',
             'Quote asset volume',
             'Number of trades',
             'Taker buy base asset volume',
             'Taker buy quote asset volume',
             'Ignore']
        )

        for kline in klines:
            kline[0] = datetime.utcfromtimestamp(int(kline[0]) / 1000).strftime(DATE_FORMAT)
            # get the year fom the kline[0] datetime, only export if within range (year is at the end)
            if int(kline[0][-4:]) == start_year:
                kline.insert(0, symbol)
                writer.writerow(kline)


def combine_csv_files(symbol, klines_type, interval, output_file):
    all_data = []
    file_pattern = f'./data/{klines_type}/{interval}/*_{symbol}.csv'
    files = glob.glob(file_pattern)

    header = None
    for file in files:
        with open(file, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)  # Skip the header
            for row in reader:
                all_data.append(row)

    # Sort data by the 'Open time' column (assuming it's the first column)
    all_data.sort(key=lambda x: datetime.strptime(x[1], DATE_FORMAT))

    if header is not None and len(all_data) > 0:
        # Write combined and sorted data to the output file
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)  # Write the header
            writer.writerows(all_data)


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args(sys.argv[1:])

    if args.interval not in INTERVALS:
        raise NameError('Invalid interval')

    client = Client()
    symbols = read_symbols()

    for symbol in tqdm(symbols):
        create_path('spot', args.interval)
        download_kline(symbol, 'spot', args.interval, int(args.year))
        if args.combine:
            combine_csv_files(symbol, 'spot', args.interval, f'./data/spot/{args.interval}/combined/{symbol}.csv')

        # create_path('futures', args.interval)
        # klines = download_kline(symbol, 'futures', args.interval)

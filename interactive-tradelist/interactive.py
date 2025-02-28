import datetime
import os.path
import sys
import pandas as pd
import norgatedata
import configparser
import plotly.graph_objects as go

priceadjust = norgatedata.StockPriceAdjustmentType.CAPITAL
padding_setting = norgatedata.PaddingType.NONE
timeseriesformat = 'pandas-dataframe'


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
        config.set('paths', 'input_name', 'OrderClerkTrades.csv')
    else:
        if not config.has_section('paths'):
            raise ValueError(f"Missing 'paths' section in configuration file '{ini_path}'.")

    if not config.has_option('paths', 'input_dir'):
        raise ValueError(f"Missing 'input_dir' option in 'paths' section of configuration file '{ini_path}'.")

    return config


config = load_config(file_name='config.ini')


# Get the trade list pathname from the config file, or use the first command line argument
input_dir = config.get('paths', 'input_dir')
input_name = config.get('paths', 'input_name')

pathname = sys.argv[1] if len(sys.argv) > 1 else os.path.join(input_dir, input_name)

if not os.path.exists(pathname):
    print(f"File {pathname} does not exist.")
    sys.exit(1)

data = pd.read_csv(pathname)
dateformat = '%Y-%m-%d %H:%M:%S'

# print("Got columns: ", data.columns)

# get the header, this can tell us if its a trade list exported from RT, or a order list from OrderClerk
# check if these columns exist:Trade,Strategy,Symbol,Side,DateIn,TimeIn,QtyIn,PriceIn,DateOut,TimeOut,QtyOut,PriceOut,Reason,Bars,PctGain,Profit,PctMFE,PctMAE,Fraction,Size,Dividends
mode = None
if 'Trade' in data.columns and 'Strategy' in data.columns and 'Symbol' in data.columns and 'Side' in data.columns and 'DateIn' in data.columns and 'TimeIn' in data.columns and 'QtyIn' in data.columns and 'PriceIn' in data.columns and 'DateOut' in data.columns and 'TimeOut' in data.columns and 'QtyOut' in data.columns and 'PriceOut' in data.columns and 'Reason' in data.columns and 'Bars' in data.columns and 'PctGain' in data.columns and 'Profit' in data.columns and 'PctMFE' in data.columns and 'PctMAE' in data.columns and 'Fraction' in data.columns and 'Size' in data.columns and 'Dividends' in data.columns:
    mode = "tradelist"
    dateformat = '%d/%m/%y'
elif 'Symbol' in data.columns and 'DateIn' in data.columns and 'DateOut' in data.columns and 'PriceIn' in data.columns and 'PriceOut' in data.columns:
    mode = "orderclerk"

# print(f"Mode: {mode}")

# Strip out the header
data = data[1:]

# Filter out rows with invalid DateIn
valid_rows = []
for index, row in data.iterrows():
    try:
        the_date = row['DateIn']
        row['DateIn'] = pd.to_datetime(the_date, format=dateformat)
        valid_rows.append(row)
    except (ValueError, pd.errors.OutOfBoundsDatetime):
        continue

data = pd.DataFrame(valid_rows)

valid_rows = []
for index, row in data.iterrows():
    try:
        row['DateOut'] = pd.to_datetime(row['DateOut'], format=dateformat)
        valid_rows.append(row)
    except (ValueError, pd.errors.OutOfBoundsDatetime):
        row['DateOut'] = pd.to_datetime(datetime.datetime.today())
        valid_rows.append(row)

data = pd.DataFrame(valid_rows)

# if the value of PriceOut is zero, then replace it with the prior business days close price
rows_to_drop = []
for index, row in data.iterrows():
    if row['PriceOut'] == 0:
        prior_business_day = row['DateOut'] - pd.offsets.BDay(1)
        try:
            price_dataframe = norgatedata.price_timeseries(
                row['Symbol'],
                stock_price_adjustment_setting=priceadjust,
                padding_setting=padding_setting,
                start_date=prior_business_day,
                timeseriesformat=timeseriesformat)
        except ValueError:
            print(f"Skipping {row['Symbol']} on {prior_business_day} due to missing price data.")
            continue

        if not price_dataframe.empty:
            closing_price = price_dataframe.iloc[0]['Close']
            data.at[index, 'PriceOut'] = closing_price

            # while iterating a row if the row does not contain a pcnt gain value
            if 'PctGain' not in row or pd.isna(row['PctGain']):
                data['PctGain'] = ((data['PriceOut'].astype(float) - data['PriceIn'].astype(float)) / data[
                    'PriceIn'].astype(float)) * 100
            else:
                # PcntGain is 12.57% and I want to convert it to 12.57 - make sure the result is of float type
                data['PctGain'] = data['PctGain'].astype(str).str.rstrip('%').astype('float')
            data['UsesClosingPrice'] = True
        else:
            print(f"No price data available for {row['Symbol']} on {prior_business_day}")
            rows_to_drop.append(index)

data.drop(rows_to_drop, inplace=True)

# Validate that all DateOut and DateIn columns are datetime objects
data['DateIn'] = pd.to_datetime(data['DateIn'])
data['DateOut'] = pd.to_datetime(data['DateOut'])

# Calculate trade duration
data['Duration'] = (data['DateOut'] - data['DateIn']).dt.days

# Find the earliest and latest date in the whole trading range
earliest_date = data['DateIn'].min()
latest_date = data['DateOut'].max()

spx_pricedata_pd_dataframe = norgatedata.price_timeseries(
    "$SPX",
    stock_price_adjustment_setting=priceadjust,
    padding_setting=padding_setting,
    start_date=earliest_date,
    timeseriesformat=timeseriesformat,
)

spx_pricedata_pd_dataframe = spx_pricedata_pd_dataframe[spx_pricedata_pd_dataframe.index <= latest_date]

min_price = spx_pricedata_pd_dataframe['Close'].min()
max_price = spx_pricedata_pd_dataframe['Close'].max()

# Scale SPX prices to range [-50, 50]
spx_pricedata_pd_dataframe['Scaled_Close'] = -80 + ((spx_pricedata_pd_dataframe['Close'] - min_price) * (50 - (-50)) / (max_price - min_price))

scaling_factor = 2.5  # Adjust this value as needed
data['Scaled_PctGain'] = data['PctGain'] * scaling_factor

# Create a new figure
fig = go.Figure()

# Draw a horizontal dotted line for the 30% mark - for the regime filter.
fig.add_hline(y=30, line_width=1, line_dash="dot", line_color="grey")

# Add traces for each trade
circle_radius = 5  # Configurable circle radius
box_size = 10  # Configurable box size

for _, trade in data.iterrows():
    dates = pd.date_range(start=trade['DateIn'], end=trade['DateOut'])
    gains = [trade['Scaled_PctGain'] * (i / len(dates)) for i in range(len(dates))]
    fig.add_trace(go.Scatter(x=dates, y=gains, mode='lines', name=f"{trade['Symbol']} )",))

    # Check if PriceOut is missing
    if trade['UsesClosingPrice']:
        # Draw a circle around the end of the line
        fig.add_trace(go.Scatter(x=[trade['DateOut']], y=[gains[-1]], mode='markers',
                                 marker=dict(symbol='circle', size=circle_radius, color='blue'),
                                 showlegend=False))
    else:
        # Draw a box around the end of the line
        is_positive_gain = trade['PctGain'] > 0
        symbol = 'triangle-up' if is_positive_gain else 'triangle-down'
        color = 'green' if is_positive_gain else 'red'
        fig.add_trace(go.Scatter(x=[trade['DateOut']], y=[gains[-1]], mode='markers',
                                 marker=dict(symbol=symbol, size=box_size, color=color),
                                 showlegend=False))

# Monthly markers
monthly_markers = pd.date_range(start=earliest_date, end=latest_date, freq='MS')

# Add vertical lines for each month
for date in monthly_markers:
    month_name = date.strftime('%b')  # Short month name
    fig.add_vline(x=date, line_width=1, line_dash="dot", line_color="grey")
    fig.add_annotation(x=date, y=-150,  # Adjust y position as needed
                       text=month_name,
                       showarrow=False,
                       xshift=-5,  # Adjust x shift for alignment
                       textangle=-90,  # Rotate text to vertical
                       font=dict(size=10, color="white"))  # Adjust font size and color as needed

col = 'rgba(0.1,0.1,0.1,0.9)'
col_white = 'rgba(1,1,1,1)'
fig.update_layout(plot_bgcolor=col_white)
fig.update_layout(paper_bgcolor=col_white)
fig.update_layout(title_font_color='white', xaxis_title_font_color="white", yaxis_title_font_color='white')

# Customize the layout
fig.update_layout(
    title='Trade Performance Over Time',
    xaxis_title='Date',
    yaxis_title='Percentage Gain',
    yaxis=dict(range=[-150, 150]),
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))

# Last output line
print(f"Last date in the data set is {latest_date}")

fig.show(config={'displayModeBar': True})
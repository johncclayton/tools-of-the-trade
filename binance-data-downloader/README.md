# binance-data-downloader
Scripts for downloading binance public data by python-binance.

# Scripts
- symbol_sel.py - select TRADING/USDT/PERPETUAL futures symbols, export them to symbols.txt
- klines_downloader.py - download spot and futures klines data for symbols in symbols.txt, save as csv format
- refresh_this_year.ps1 - download all data for 2025
- download_all_history.ps1 - get everything available from binance, back to 2017

# RealTest

In Real Test - I use the data like this.

```rts
Import:
	DataSource:	CSV
	DataPath:	.. full path to the data folder...\data\spot\1d\combined
	CSVDateFmt:	DMY
	CSVFields: 	symbol, date, open, high, low, close, volume
	IncludeList:	BTCUSDT {"assets"}
	SaveAs:	data_file_name_to_use.rtd
	
Settings:
	DataFile:	data_file_name_to_use.rtd
	
	StartDate:	Earliest
	EndDate:	Latest
	
	AccountSize:	200000
	BarSize:	Daily
	
TestSettings:
	StartDate:	2000/1/1
```
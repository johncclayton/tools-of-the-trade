# Progress

Using the trade list output from OrderClerk, this program will generate a progress statement
for years/months and per strategy.

To calculate % profit, only the capital deployed is used - what you might have had available is irrelevant.  Therefore, interest
earned via IBKR is not included in the calculation and must be added separately.

# Configuration

Write a config.ini file so that the program knows where your OrderClerk trades are being stored, and
where to throw the output - something like this:

```ini
[paths]
input_dir=C:\Users\johnc\OneDrive - Effective Flow\Trading\RT\Env_LiveTrading\OrderClerk
output_dir=C:\Users\johnc\OneDrive - Effective Flow\Trading\RT\Env_LiveTrading
```


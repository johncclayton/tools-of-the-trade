# Progress

Using the trade list output from OrderClerk, this program will generate embellished CSV 
files as well as serve them via an HTTP server, for use by excel for example.

No data is ever stored - the program is stateless.

To calculate % profit, only the capital deployed is used - what you might have had available is irrelevant.  Interest
earned via IBKR is not included in the calculation and must be added separately.

# Configuration

Write a config.ini file so that the program knows where your OrderClerk trades are being stored, and
where to throw the output - something like this:

```ini
[paths]
input_dir=C:\Users\johnc\OneDrive - Effective Flow\Trading\RT\Env_LiveTrading\OrderClerk
output_dir=C:\Users\johnc\OneDrive - Effective Flow\Trading\RT\Env_LiveTrading\Reporting
```

# Deployment

Is locally, depending also on this .venv - this is because the code requires access to the norgate data service, which
is in fact running on this machine.

deploy-production.ps1 is a script that will copy the code to the production machine, and also take care of the service (which I created by hand)

# Service

I used nssm to install the service by hand.  

* OrderClerkService, uses the start_flask.bat file as the service app.


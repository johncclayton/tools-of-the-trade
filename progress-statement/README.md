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
deployment_dir=C:\Users\johnc\OneDrive - Effective Flow\Trading\RT\Env_LiveTrading\Reporting
service_name=OrderClerkService
```

## Default Values

| Config Key       | Description                                            | Default Value   |
|------------------|--------------------------------------------------------|-----------------|
| `input_dir`      | The directory to find the OrderClerkTrades.csv file in | None            |
| `deployment_dir` | A directory - where to deploy the Flask application    | None            |
| `service_name`   | The name of the service (manually added)               | ServeOrderClerk |

# Deployment

Deployment is to the local machine into another directory, as specified by the ``deployment_dir`` param in the 
config.ini. 

This also relies on a correctly set up python environment.  This can be created using the ``requirements.txt`` file.

The reason that this is a local deployment is that the system relies on Norgate data, which is only available on the
local machine.

# Service Installation (Manual Steps)

I used nssm to install the service by hand.  

* OrderClerkService, uses the start_flask.bat file as the service app.


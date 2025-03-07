# deploy manually to the production environment - which is to say, copy the files and restart the service.

# stop the live service
$SERVICE_NAME = "ServeOrderClerk"
$s = Get-Service $SERVICE_NAME
if($s.Status -eq "Running") {
    Write-Error "The service is running, stop it first before performing deployment"
}

# copy the .py files to the live area
$DEPLOYMENT_DIR = "D:\trading-deployment\order-clerk-trades"

# Ensure the deployment directory exists
if (-Not (Test-Path -Path $DEPLOYMENT_DIR)) {
    New-Item -ItemType Directory -Path $DEPLOYMENT_DIR
}

# Copy all .py files and maintain subdirectory structure
Get-ChildItem -Path . -Filter *.py -Recurse | ForEach-Object {
    $destination = Join-Path -Path $DEPLOYMENT_DIR -ChildPath $_.DirectoryName.Substring($PWD.Path.Length)
    if (-Not (Test-Path -Path $destination)) {
        New-Item -ItemType Directory -Path $destination
    }
    Copy-Item -Path $_.FullName -Destination $destination
}

Copy-Item -Path config.ini -Destination $DEPLOYMENT_DIR
Copy-Item -Path start_flask.bat -Destination $DEPLOYMENT_DIR
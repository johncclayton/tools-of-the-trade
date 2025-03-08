# deploy manually to the production environment - which is to say, copy the files and restart the service.

$ErrorActionPreference = "Stop"

# stop the live service
$sn = (Get-Content .\config.ini | Select-String -Pattern '^service_name=')
if (-not $sn) {
    $SERVICE_NAME = "ServeOrderClerk"
} else {
    $SERVICE_NAME = $sn.ToString().Split('=')[1].Trim()
}

$s = Get-Service $SERVICE_NAME
if($s.Status -eq "Running") {
    Write-Error "The service is running, stop it first before performing deployment"
} else {
    Write-Host "Service ${SERVICE_NAME} is stopped"
}

$DEPLOYMENT_DIR = (Get-Content .\config.ini | Select-String -Pattern '^deployment_dir=').ToString().Split('=')[1].Trim()
if (-not $DEPLOYMENT_DIR) {
    Write-Error "Deployment directory is not specified in the config.ini file via deployment_dir=<some value>"
    exit 1
}

# Ensure the deployment directory exists
if (-Not (Test-Path -Path $DEPLOYMENT_DIR)) {
    New-Item -ItemType Directory -Path $DEPLOYMENT_DIR
}

# Remove all files and directories in the deployment directory, except config.ini
Get-ChildItem -Path $DEPLOYMENT_DIR -Recurse -Exclude config.ini | Remove-Item -Recurse -Force

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

Write-Host "Upgrade complete - you can start the service now"
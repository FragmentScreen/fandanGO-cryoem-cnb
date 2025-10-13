# Invoke: $scriptPath = "$(Get-Location)\irods_fetch_win.ps1"; (Invoke-WebRequest -UseBasicParsing "https://raw.githubusercontent.com/FragmentScreen/fandanGO-cryoem-cnb/refs/heads/main/cryoemcnb/utils/irods_fetch_win.ps1").Content | Out-File $scriptPath -Encoding UTF8; & powershell -ExecutionPolicy Bypass -File $scriptPath --host "{host}" --ticket "{ticket}" --collection "{collection_path}" --output_dir "{output_dir}"; Remove-Item $scriptPath

# Define path to Python
$PYTHON = "python"

$REQUIRED_VERSION = "3.0.0"
$DOWNLOAD=$false

# Ensure irods module is installed

try {
    $VERSION = & $PYTHON -c "import irods; print(irods.__version__)" 2>$null
} catch {
    $VERSION = $null
}

if ($VERSION) {
    $VERSION = $VERSION.Trim()
    if ($VERSION -eq $REQUIRED_VERSION) {
        Write-Host "iRODS module found (version $VERSION)."
        $DOWNLOAD=$true
    } else {
        Write-Host "iRODS version $VERSION found, but $REQUIRED_VERSION is required. Change it by executing: $PYTHON -m pip install --upgrade python-irodsclient==$REQUIRED_VERSION"
    }
} else {
    Write-Host "python-irodsclient is not installed or could not get the version. Get it by executing: $PYTHON -m pip install python-irodsclient==$REQUIRED_VERSION"
}

if ($DOWNLOAD) {
    # Execute downloader from url
    $python_script_url="https://raw.githubusercontent.com/FragmentScreen/fandanGO-cryoem-cnb/main/cryoemcnb/utils/irods_fetch.py"
    $scriptContent = Invoke-WebRequest -Uri $python_script_url -UseBasicParsing | Select-Object -ExpandProperty Content
    $scriptContent | & $PYTHON - @args
} else {
    Write-Host "No data will be downloaded."
}
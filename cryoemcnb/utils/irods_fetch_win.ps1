# Define path to Python
$PYTHON = "python"

# Ensure irods module is installed
function Version-Ge {
    param (
        [string]$version1,
        [string]$version2
    )
    return ([Version]$version1 -ge [Version]$version2)
}

try {
    $VERSION = & $PYTHON -c "import irods; print(irods.__version__)" 2>$null
} catch {
    $VERSION = $null
}

$REQUIRED_VERSION = "3.0.0"

if ($VERSION) {
    $VERSION = $VERSION.Trim()
    if (Version-Ge $VERSION $REQUIRED_VERSION) {
        Write-Host "iRODS module found (version $VERSION)."
    } else {
        Write-Host "iRODS version $VERSION found, but at least $REQUIRED_VERSION is required. Upgrading..."
        & $PYTHON -m pip install --upgrade "python-irodsclient>=$REQUIRED_VERSION"
    }
} else {
    Write-Host "python-irodsclient is not installed. Installing..."
    & $PYTHON -m pip install "python-irodsclient>=3.0.0"
}


# Execute downloader from url
$python_script_url="https://raw.githubusercontent.com/FragmentScreen/fandanGO-cryoem-cnb/main/cryoemcnb/utils/irods_fetch.py"
$scriptContent = Invoke-WebRequest -Uri $python_script_url -UseBasicParsing | Select-Object -ExpandProperty Content
$scriptContent | & $PYTHON - @args
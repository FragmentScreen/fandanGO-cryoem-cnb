# The following code was from https://github.com/cemcof/cemcof.github.io/blob/main/irods_fetch_unix.sh

# Invoke: curl -sSfL "https://raw.githubusercontent.com/FragmentScreen/fandanGO-cryoem-cnb/main/cryoemcnb/utils/irods_fetch_unix.sh" | bash -s -- --host "{host}" --ticket "{ticket}" --collection "{collection_path}" --output_dir "{output_dir}"

# Define path to Python
PYTHON="python3"

REQUIRED_VERSION="3.0.0"
DOWNLOAD=false

# Ensure irods module is installed

if $PYTHON -c "import irods; print(irods.__version__)" >/dev/null 2>&1; then
    VERSION=$($PYTHON -c "import irods; print(irods.__version__)")

    if [ "$VERSION" = "$REQUIRED_VERSION" ]; then
        echo "iRODS module found (version $VERSION)."
        DOWNLOAD=true

    else
        echo "iRODS version $VERSION found, but $REQUIRED_VERSION is required. Change it by executing: $PYTHON -m pip install --upgrade python-irodsclient==$REQUIRED_VERSION"
    fi
else
    echo "python-irodsclient is not installed or could not get the version. Get it by executing: $PYTHON -m pip install python-irodsclient==$REQUIRED_VERSION"
fi

if [ "$DOWNLOAD" = true ]; then
    # Execute downloader from url
    python_script_url="https://raw.githubusercontent.com/FragmentScreen/fandanGO-cryoem-cnb/main/cryoemcnb/utils/irods_fetch.py"
    curl -fL $python_script_url | $PYTHON - $@
else
    echo "No data will be downloaded."
fi
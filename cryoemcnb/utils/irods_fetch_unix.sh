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
        read -p "iRODS version $VERSION found, but $REQUIRED_VERSION is required. Do you want to change to it? [y/n]" UPGRADE
        UPGRADE=${UPGRADE,,}  # to lowercase
        if [[ "$UPGRADE" == "y" || "$UPGRADE" == "yes" ]]; then
            echo "Changing python-irodsclient version..."
            $PYTHON -m pip install --upgrade "python-irodsclient==$REQUIRED_VERSION"
            DOWNLOAD=true
        else
            echo "Not changing python-irodsclient version"
        fi
    fi
else
    read -p "python-irodsclient is not installed or could not get the version. Do you want to install it (version $REQUIRED_VERSION)? [y/n]" INSTALL
    INSTALL=${INSTALL,,}  # to lowercase
    if [[ "$INSTALL" == "y" || "$INSTALL" == "yes" ]]; then
        echo "Installing python-irodsclient..."
        $PYTHON -m pip install "python-irodsclient==$REQUIRED_VERSION"
        DOWNLOAD=true
    else
        echo "Not installing python-irodsclient"
    fi
fi

if [ "$DOWNLOAD" = true ]; then
    # Execute downloader from url
    python_script_url="https://raw.githubusercontent.com/FragmentScreen/fandanGO-cryoem-cnb/main/cryoemcnb/utils/irods_fetch.py"
    curl -fL $python_script_url | $PYTHON - $@
else
    echo "No data will be downloaded."
fi
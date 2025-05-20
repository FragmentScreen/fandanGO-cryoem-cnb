# The following code was from https://github.com/cemcof/cemcof.github.io/blob/main/irods_fetch_unix.sh

# Invoke: curl -sSfL "https://raw.githubusercontent.com/FragmentScreen/fandanGO-cryoem-cnb/main/cryoemcnb/utils/irods_fetch_unix.sh" | bash -s -- --host "{host}" --ticket "{ticket}" --collection "{colleciton_path}"

# Define path to Python
PYTHON="python3"

# Ensure irods module is installed
version_ge() {
    printf '%s\n%s\n' "$2" "$1" | sort -V | head -n 1 | grep -qx "$2"
}

if $PYTHON -c "import irods; print(irods.__version__)" >/dev/null 2>&1; then
    VERSION=$($PYTHON -c "import irods; print(irods.__version__)")
    REQUIRED_VERSION="3.0.0"

    if version_ge "$VERSION" "$REQUIRED_VERSION"; then
        echo "iRODS module found (version $VERSION)."
    else
        echo "iRODS version $VERSION found, but at least $REQUIRED_VERSION is required. Upgrading..."
        $PYTHON -m pip install --upgrade "python-irodsclient>=$REQUIRED_VERSION"
    fi
else
    echo "python-irodsclient is not installed. Installing..."
    $PYTHON -m pip install "python-irodsclient>=3.0.0"
fi


# Execute downloader from url
python_script_url="https://raw.githubusercontent.com/FragmentScreen/fandanGO-cryoem-cnb/main/cryoemcnb/utils/irods_fetch.py"
curl -fL $python_script_url | $PYTHON - $@

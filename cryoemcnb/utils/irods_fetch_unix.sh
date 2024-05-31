# The following code was from https://github.com/cemcof/cemcof.github.io/blob/main/irods_fetch_unix.sh

# Invoke: curl -sSfL "https://raw.githubusercontent.com/FragmentScreen/fandanGO-cryoem-cnb/main/cryoemcnb/utils/irods_fetch.py" | bash -s -- --host "{host}" -t "{ticket}" -c "{colleciton_path}"

# Ensure irods module is installed
if python3 -c "import irods" >/dev/null 2>&1; then
    echo "iRODS module found."
else
    echo "python-iordsclient is not installed. Installing..."
    python3 -m pip install python-irodsclient
fi


# Execute downloader from url
python_script_url="https://raw.githubusercontent.com/FragmentScreen/fandanGO-cryoem-cnb/main/cryoemcnb/utils/irods_fetch.py"
curl -fL $python_script_url | python3 - $@

# Alternative:
# temp_file=$(mktemp)
# curl -sSfL -o "$temp_file" "$python_script_url"
# python3 "$temp_file" $@
# rm "$temp_file"

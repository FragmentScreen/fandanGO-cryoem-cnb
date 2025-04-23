# The following code was taken from https://github.com/cemcof/cemcof.github.io/blob/main/irods_fetch.py

# iRODS collection downloader

import argparse, pathlib

from irods.collection import iRODSCollection
from irods.session import iRODSSession
from irods.ticket import Ticket

import time

# Utility to convert file size to huma readable format
def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


aparser = argparse.ArgumentParser(
    prog = 'irods-fetch',
    description = 'LIMS utility for downloading collection of files from iRODS cloud'
)

aparser.add_argument("--ticket", "-t", dest="ticket", help="Access ticket")

aparser.add_argument("--host", required=True, dest="host", help="iRODS host")
aparser.add_argument("--port", "-p", dest="port", type=int, default="1247", help="iRODS port, defaults to 1247")
aparser.add_argument("--user", "-u", dest="user", default="anonymous", help="iRODS user, defaults to 'anonymous'")
aparser.add_argument("--password", "-P", dest="password", default="", help="iRODS user password, defaults to empty password")

aparser.add_argument("--collection", "-c", required=True, dest="collection_path", type=str, help="Collection path")
aparser.add_argument("--output_dir", "-o", dest="output_dir", type=pathlib.Path, default=pathlib.Path("."))

arguments = aparser.parse_args()

# Extract zone from the collection argument (first path part)
arguments.zone = arguments.collection_path.split("/")[1]

def download_completed(port, host, user, password, zone, collection_path, ticket, output_dir):
    # Open iRODS session
    with iRODSSession(port=port, host=host, user=user, password=password, zone=zone) as irods_session:

        # -------- grent ticket
        # new_t = Ticket(irods_session)
        # new_t.issue("read", collection_path)
        # print(new_t.string)
        # exit()
        # -------

        # Supply the access ticket, if any
        if ticket:
            Ticket(irods_session, ticket).supply()
            # collection = iRODSCollection(irods_session.collections, irods_session.query(Collection).one())
        #else:
        #    collection = irods_session.collections.get(collection_path)


        #irods_session.query()
        collection = irods_session.collections.get(str(collection_path))
        print(f"Connected to iRODS, starting file downloads from the collection {collection.path}...")

        def walk_collection(collection: iRODSCollection):
            for subcol in collection.subcollections:
                yield from walk_collection(subcol) # Recurse into subcollections

            for dobj in collection.data_objects:
                yield dobj

        data_objects = list(walk_collection(collection))
        total_files = len(data_objects)
        current_file = 0

        try:
            # Download collection files
            for data_obj in data_objects:
                target_path: pathlib.Path = output_dir / pathlib.Path(data_obj.path).relative_to(collection_path)

                # Check if file already exists and has same size as collection file
                # In that case, skip it
                if target_path.exists():
                    # File already there - does it have the same size?
                    if target_path.stat().st_size == data_obj.size:
                        # Skip - it is already downloaded
                        print(f"[{current_file+1}/{total_files}] Skipped file {target_path} - already downloaded")
                        current_file = current_file + 1
                        continue
                    else:
                        target_path.unlink(missing_ok=True)

                # Ensure directory exists for the target file
                if not target_path.parent.is_dir():
                    target_path.parent.mkdir(parents=True, exist_ok=True)

                # Download the file
                print(f"[{current_file+1}/{total_files}] Downloading file {str(target_path)}...", end='', flush=True)
                start = time.time()
                irods_session.data_objects.get(data_obj.path, str(target_path))
                duration_sec = time.time() - start
                size = sizeof_fmt(target_path.stat().st_size)
                print(f" done, {duration_sec:.2f} sec, {size}")
                current_file = current_file + 1

        except Exception as e:
            print(f"Something bad happened while trying to get {data_obj.path}: {e}")

    return total_files == current_file

while True:
    try:
        is_complete = download_completed(arguments.port, arguments.host, arguments.user, arguments.password, arguments.zone, arguments.collection_path, arguments.ticket, arguments.output_dir)
        if is_complete:
            break
    except Exception as e:
        print(f"Something bad happened: {e}")
        pass

# iRODS session closed
print(f"Successfully downloaded collection: {arguments.collection_path}")

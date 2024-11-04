import os
from irods.session import iRODSSession
from irods.ticket import Ticket
from irods.exception import CollectionDoesNotExist, NetworkException
from irods.access import iRODSAccess
from dotenv import load_dotenv
import time
from cryoemcnb.db.sqlite_db import update_project

load_dotenv()

irods_zone = os.getenv('IRODS_ZONE_NAME')
irods_host = os.getenv('IRODS_ZONE_HOST')
irods_user = os.getenv('IRODS_ZONE_USER')
irods_port = os.getenv('IRODS_ZONE_PORT')
irods_pass = os.getenv('IRODS_ZONE_PASS')
irods_parent_collection = os.getenv('IRODS_ZONE_COLLECTION')

def is_broken_symlink(path):
    return os.path.islink(path) and not os.path.exists(path)


def find_collection_physical_path(session, virtual_path):
    collection = session.collections.get(virtual_path)

    for obj in collection.data_objects:
        for replica in obj.replicas:
            physical_path = replica.path
            return physical_path

    for subcollection in collection.subcollections:
        sub_physical_path = find_collection_physical_path(subcollection.path)
        if sub_physical_path:
            return sub_physical_path


def ensure_collection_exists(session, irods_subdir, max_retries=15):
    for attempt in range(max_retries):
        try:
            session.collections.get(irods_subdir)
            return True
        except CollectionDoesNotExist:
            session.collections.create(irods_subdir)
            return True
        except (NetworkException, KeyError) as e:
            print(f"Network or connection error {e}. . Trying to reconnect... (Try {attempt + 1}/{max_retries})")
            session.cleanup()
            session.__init__(host=irods_host, port=irods_port, user=irods_user, password=irods_pass, zone=irods_zone)
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False
    print(f"The connection to iRODS Zone was not successful after {max_retries} tries.")
    return False


def upload_file_with_reconnect(session, local_file, irods_file, max_retries=15):
    for attempt in range(max_retries):
        try:
            session.data_objects.put(local_file, irods_file)
            return True
        except (NetworkException, KeyError):
            print(f"Error while transfer {local_file}. Trying to reconnect... (Try {attempt + 1}/{max_retries})")
            session.cleanup()
            session.__init__(host=irods_host, port=irods_port, user=irods_user, password=irods_pass, zone=irods_zone)
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False
    print(f"The transfer of {local_file} was not successful after {max_retries} tries.")
    return False


def copy_data(project_name, raw_data_path):
    """
    Function that creates an iRODS collection from data provided

    Args:
        project_name (str): FandanGO project name
        raw_data_path (str): path of the origin data

    Returns:
        success (bool): if everything went ok or not
        info (dict): irods collection info (path, ticket id, etc.)
    """

    print(f'FandanGO will create an iRODS collection for project {project_name} with raw data located at {raw_data_path}...')
    success = False
    info = None

    with iRODSSession(host=irods_host, port=irods_port, user=irods_user, password=irods_pass, zone=irods_zone) as session:
        try:
            # create new collection and put the data onto it
            new_collection = irods_parent_collection + project_name

            # upload recursively
            for root, dirs, files in os.walk(raw_data_path):
                for name in dirs:
                    local_subdir = os.path.join(root, name)
                    if is_broken_symlink(local_subdir):
                        print(f'Skipping broken symlink: {local_subdir}')
                        continue
                    irods_subdir = os.path.join(new_collection, os.path.relpath(local_subdir, raw_data_path)).replace("\\", "/")
                    ensure_collection_exists(session, irods_subdir)

                for name in files:
                    local_file = os.path.join(root, name)
                    if is_broken_symlink(local_file):
                        print(f'Skipping broken symlink: {local_file}')
                        continue
                    irods_file = os.path.join(new_collection, os.path.relpath(local_file, raw_data_path)).replace("\\", "/")
                    print(f"Copying {local_file} into {irods_file} ...")
                    if upload_file_with_reconnect(session, local_file, irods_file):
                        print("... copied!")
                    else:
                        print(f"... failed to upload {local_file}. Skipping...")

            # avoid 'anonymous' or 'public' user access to collection without having ticket id
            session.acls.set(iRODSAccess('null', new_collection, 'anonymous'), recursive=True)
            session.acls.set(iRODSAccess('null', new_collection, 'public'), recursive=True)

            # create ticket for retrieving the data back
            print(f'Creating ticket for project {project_name}...')
            new_ticket = Ticket(session)
            ticket_id = new_ticket.issue(target=new_collection, permission='read').string
            print(f'... ticket generated with id {ticket_id}...')

            # get collection physical location
            first_file_physical_path = find_collection_physical_path(session, new_collection)
            collection_physical_path = os.path.join(first_file_physical_path.split(project_name)[0], project_name)
            success = True

        except Exception as e:
            info = f'... collection could not be created for project {project_name} because of: {e}'

    if success:
        # update ddbb
        update_project(project_name, 'data_retrieval_command', f'curl -sSfL "https://raw.githubusercontent.com/FragmentScreen/fandanGO-cryoem-cnb/main/cryoemcnb/utils/irods_fetch_unix.sh" | bash -s -- --host "{irods_host}" --collection "{new_collection}" --ticket "{ticket_id}"')
        update_project(project_name, 'data_physical_location', collection_physical_path)

        info = {'irods_host': irods_host,
                'irods_location': new_collection,
                'irods_ticket_id': ticket_id,
                'irods_retrieval_script': 'https://raw.githubusercontent.com/FragmentScreen/fandanGO-cryoem-cnb/main/cryoemcnb/utils/irods_fetch_unix.sh'}

    return success, info


def perform_action(args):
    success, info = copy_data(args['name'], args['raw_data_path'])
    results = {'success': success, 'info': info}
    return results

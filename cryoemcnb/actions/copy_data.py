import os
from irods.session import iRODSSession
from irods.ticket import Ticket
from dotenv import load_dotenv
from cryoemcnb.db.sqlite_db import update_project

load_dotenv()

irods_zone = os.getenv('IRODS_ZONE_NAME')
irods_host = os.getenv('IRODS_ZONE_HOST')
irods_user = os.getenv('IRODS_ZONE_USER')
irods_port = os.getenv('IRODS_ZONE_PORT')
irods_pass = os.getenv('IRODS_ZONE_PASS')
irods_parent_collection = os.getenv('IRODS_ZONE_COLLECTION')

def copy_data(project_name, raw_data_path):
    """
    Function that creates an iRODS collection from data provided

    Args:
        project_name (str): FandanGO project name
        raw_data_path (str): path of the origin data

    Returns:
        success (bool): if everything went ok or not
    """

    print(f'FandanGO will create an iRODS collection for project {project_name} with raw data located at {raw_data_path}...')
    success = False
    info = None

    with iRODSSession(host=irods_host, port=irods_port, user=irods_user, password=irods_pass, zone=irods_zone) as session:
        try:
            # create new collection and put the data onto it
            new_collection = irods_parent_collection + project_name
            session.collections.create(new_collection)
            for file_name in os.listdir(raw_data_path):
                local_file_path = os.path.join(raw_data_path, file_name)
                session.data_objects.put(local_file_path, new_collection + '/' + file_name)

            # create ticket for retrieving the data back
            print(f'Creating ticket for project {project_name}...')
            new_ticket = Ticket(session)
            ticket_id = new_ticket.issue(target=new_collection, permission='read').string
            print(f'... ticket generated with id {ticket_id}...')

            # update ddbb
            update_project(project_name, 'data_manager', 'irods')
            update_project(project_name, 'irods_location', new_collection)
            update_project(project_name, 'irods_ticket_id', ticket_id)
            info = {'irods_location': new_collection, 'irods_ticket_id': ticket_id}
            success = True

        except Exception as e:
            info = f'... collection could not be created for project {project_name} because of: {e}'
            print(info)
    return success, info


def perform_action(args):
    success, info = copy_data(args['name'], args['raw_data_path'])
    results = {'success': success, 'info': info}
    return results

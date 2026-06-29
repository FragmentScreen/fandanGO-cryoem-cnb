from dotenv import load_dotenv
from cryoemcnb.db.sqlite_db import update_project, get_project_info

load_dotenv()



def provide_raw_data(project_name, raw_data_links):
    print(f'The ticket to download the raw_data will be asociated to the project {project_name} ...')
    success = False
    if raw_data_links:
        success = True
        column_names, project_info = get_project_info(project_name)
        exists = any(key == "raw_data_ticket_linux" for _, key, _ in project_info)
        print('exist a raw_data_ticket_linux on the project, associating the new...') if exists else print('raw_data_ticket_linux does not exist on the project, associating...')
        update_project(project_name, 'raw_data_ticket_linux', raw_data_links)
        info = {'raw_data_ticket_linux': raw_data_links}
        update_project(project_name, 'raw_data_ticket_linux', raw_data_links)

    else:
        info = (f'... raw_data_ticket_linux could not be retrieved)')
    return success, info


def perform_action(args):
    success, info = provide_raw_data(args['name'], args['irods_ticket'])
    results = {'success': success, 'info': info}
    return results

#fandanGO execute --action provide-raw-data-linux --name test3 --irods-ticket ticketSimulatedLinux

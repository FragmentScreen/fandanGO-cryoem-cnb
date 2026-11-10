from cryoemcnb.db.sqlite_db import get_project_metadata, get_project_data_retrieval_info
from datetime import datetime
from dotenv import load_dotenv
import yaml
from fGOaria import AriaClient, Bucket, Field, pretty_print
from ..constants import EMBARGO_YEARS
import os
load_dotenv()

def send_metadata(project_name, visit_id):
    """
    Function that sends FandanGO project info to ARIA

    Args:
        project_name (str): FandanGO project name
        visit_id (int): ARIA visit ID

    Returns:
        success (bool): if everything went ok or not
        info (dict): bucket, record and field ARIA data
    """

    print(f'FandanGO will send metadata for {project_name} project to ARIA...')
    success = True
    info = None

    try:
        project_metadata = get_project_metadata(project_name)
        project_retrieval_info_linux = get_project_data_retrieval_info(project_name, operating_system='linux')
        project_retrieval_info_windows = get_project_data_retrieval_info(project_name, operating_system='windows')

        aria = AriaClient(True)
        aria.login()
        today = datetime.today()
        visit = aria.new_data_manager(int(visit_id), 'visit', True)
        embargo_date = datetime(today.year + EMBARGO_YEARS, today.month, today.day).strftime('%Y-%m-%d')
        bucket = Bucket(visit.entity_id, visit.entity_type, embargo_date)
        visit.push_safe_cli(bucket)

        # project metadata
        record_oscem = visit.create_record(bucket.id, 'OSCEM')
        for yaml_path in project_metadata:
            if os.path.isfile(yaml_path):
                with open(yaml_path, 'r') as file:
                    data = yaml.safe_load(file)
                    field = Field(record_oscem.id, 'YAML', data)
                    visit.push_safe_cli(field)
                    if not isinstance(field, Field):
                        success = False
        # data retrieval info
        record_retrieval_info_linux = visit.create_record(bucket.id, 'Generic')
        raw_data_download_commands_linux = Field(record_retrieval_info_linux.id, 'COMMAND', project_retrieval_info_linux)
        visit.push_safe_cli(raw_data_download_commands_linux)
        if not isinstance(raw_data_download_commands_linux, Field):
            success = False

        record_retrieval_info_windows = visit.create_record(bucket.id, 'Generic')
        raw_data_download_commands_windows = Field(record_retrieval_info_windows.id, 'COMMAND', project_retrieval_info_windows)
        visit.push_safe_cli(raw_data_download_commands_windows)
        if not isinstance(raw_data_download_commands_windows, Field):
            success = False 

    except Exception as e:
        success = False
        info = e
        print(f'Error send_metadata: {e}')


    if success:
        print(f'Successfully sent metadata for project {project_name} to ARIA!')
        info = {'bucket': bucket.__dict__,
                'record_oscem': record_oscem.__dict__,
                'record_retrieval_info_linux': record_retrieval_info_linux.__dict__,
                'record_retrieval_info_windows': record_retrieval_info_windows.__dict__,
                'raw_data_download_commands_linux': raw_data_download_commands_linux.__dict__,
                'raw_data_download_commands_windows': raw_data_download_commands_windows.__dict__}
        print(f'FandanGO record_id Linux: {record_retrieval_info_linux._id}')
        print(f'FandanGO record_id Windows: {record_retrieval_info_windows._id}')
        print(f'FandanGO record_id oscem: {record_oscem._id}')



    return success, info


def perform_action(args):
    success, info = send_metadata(args['name'], args['visit_id'])
    results = {'success': success, 'info': info}
    return results

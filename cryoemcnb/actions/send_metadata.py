from cryoemcnb.db.sqlite_db import get_project_metadata, get_project_data_retrieval_info
from datetime import datetime
from dotenv import load_dotenv
import json
import os
from fGOaria import AriaClient, Bucket, Field, pretty_print

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
        project_retrieval_info = get_project_data_retrieval_info(project_name)

        aria = AriaClient(True)
        aria.login()
        today = datetime.today()
        visit = aria.new_data_manager(int(visit_id), 'visit', True)
        embargo_date = datetime(today.year + 3, today.month, today.day).strftime('%Y-%m-%d')
        bucket = Bucket(visit.entity_id, visit.entity_type, embargo_date)
        visit.push(bucket)

        # project metadata
        record_oscem = visit.create_record(bucket.id, 'OSCEM')
        for json_path in project_metadata:
            with open(json_path, 'r') as file:
                data = json.load(file)
                field = Field(record_oscem.id, 'JSON', data)
                visit.push(field)
                if not isinstance(field, Field):
                    success = False

        # data retrieval info
        record_retrieval_info = visit.create_record(bucket.id, 'Generic')
        field = Field(record_retrieval_info.id, 'COMMAND', project_retrieval_info)
        visit.push(field)
        if not isinstance(field, Field):
            success = False

    except Exception as e:
        success = False
        info = e

    if success:
        print(f'Successfully sent metadata for project {project_name} to ARIA!')
        info = {'bucket': bucket.__dict__,
                'record_oscem': record_oscem.__dict__,
                'record_retrieval_info': record_retrieval_info.__dict__,
                'field': field.__dict__}

    return success, info


def perform_action(args):
    success, info = send_metadata(args['name'], args['visit_id'])
    results = {'success': success, 'info': info}
    return results

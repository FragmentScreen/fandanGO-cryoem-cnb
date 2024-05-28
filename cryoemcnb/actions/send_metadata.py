from cryoemcnb.db.sqlite_db import get_project_metadata
from datetime import datetime
from dotenv import load_dotenv
import json
import os
from fGOaria import AriaClient, Bucket, Field, pretty_print

load_dotenv()

def send_metadata(project_name):
    """
    Function that prints info for a FandanGO project

    Args:
        project_name (str): FandanGO project name

    Returns:
        success (bool): if everything went ok or not
        info (dict): bucket, record and field ARIA data
    """

    print(f'FandanGO will send metadata for {project_name} project to ARIA...')
    success = True
    info = None

    try:
        project_metadata = get_project_metadata(project_name)

        aria = AriaClient(True)
        today = datetime.today()
        visit_id = today.strftime('%Y%m%d')
        visit = aria.new_data_manager(visit_id, 'visit', True)
        embargo_date = datetime(today.year + 3, today.month, today.day).strftime('%Y-%m-%d')
        bucket = Bucket(visit.entity_id, visit.entity_type, embargo_date)
        visit.push(bucket)
        record = visit.create_record(bucket.id, 'TestSchema')

        for json_path in project_metadata:
            if os.path.exists(json_path):
                with open(json_path, 'r') as file:
                    data = json.load(file)
                    field = Field(record.id, 'TestFieldType', data)
                    visit.push(field)
                    if not isinstance(field, Field):
                        success = False
            else:
                info += f'Metadata file {json_path} not found\n'

    except Exception as e:
        success = False
        info = e

    if success:
        print(f'Successfully sent metadata for project {project_name} to ARIA!')
        info = {'bucket': bucket.__dict__,
                'record': record.__dict__,
                'field': field.__dict__}

    return success, info


def perform_action(args):
    success, info = send_metadata(args['name'])
    results = {'success': success, 'info': info}
    return results

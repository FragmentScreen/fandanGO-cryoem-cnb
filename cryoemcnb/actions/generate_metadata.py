import configparser
import os
import subprocess
from cryoemcnb.db.sqlite_db import update_project
from sqlite3 import dbapi2 as sqlite
import json

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.yaml'))
scipion_launcher = config['SCIPION'].get('SCIPION_LAUNCHER')
scipion_projects_path = config['SCIPION'].get('SCIPION_PROJECTS_PATH')
emadmin_ddbb_path = config['EMADMIN'].get('EMADMIN_DDBB_PATH')

def generate_metadata_data(project_name, metadata_path):
    """
    Function that generates metadata for a FandanGO project

    Args:
        project_name (str): FandanGO project name
        metadata_path (str): Path of metadata generated with the OSCEM_json protocol
    Returns:
        success (bool): if everything went ok or not
        info (dict): info metadata path
    """

    print(f'FandanGO will retrieve generated metadata for project {project_name}...')
    success = False
    info = None
    if os.path.exists(metadata_path):
        success = True
        update_project(project_name, 'metadata_path', metadata_path)
        info = {'metadata_path': metadata_path}

    else:
        info = (f'... metadata could not be retrieved from this path ({metadata_path}). Create it with OSCEM_json protocol.')


    return success, info


def perform_action(args):
    success, info = generate_metadata_data(args['name'], args['metadata_path'])
    results = {'success': success, 'info': info}
    return results

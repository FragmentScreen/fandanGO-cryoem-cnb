from cryoemcnb.db.sqlite_db import get_project_info
from tabulate import tabulate

def print_project(project_name):
    """
    Function that prints info for a FandanGO project

    Args:
        project_name (str): FandanGO project name

    Returns:
        success (bool): if everything went ok or not
        info (list): project related rows
    """

    print('FandanGO project info:\n')
    success = False
    info = None

    try:
        column_names, project_info = get_project_info(project_name)
        print(tabulate(project_info, headers=column_names, tablefmt="pretty"))
        success = True
        info = project_info
    except Exception as e:
        info = e
    return success, info


def perform_action(args):
    success, info = print_project(args['name'])
    results = {'success': success, 'info': info}
    return results

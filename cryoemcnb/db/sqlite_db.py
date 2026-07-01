import os
from typing import Tuple, List, Optional
from cryoemcnb.constants import DBNAME
from fGOdb import SQLiteDB, ProjectInfo

def _db_conn() -> ProjectInfo:
    """Return a connection to the plugin's local project SQLite database."""
    config_path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    config_file = os.path.join(config_path, "plugin.cfg")
    return ProjectInfo(SQLiteDB(config_file, DBNAME))

def update_project(project_name: str, key: str, value: str) -> None:
    """Update a metadata field for a given project."""
    _db_conn().set(project_name, key, value)

def get_project_info(project_name: str) -> Tuple[List[str], List[Tuple]]:
    """Return list of metadata fields for a given project.
    Returns:
        Tuple[List[str], List[Tuple]]: Column names and list of metadata fields.
    """
    return ["key", "value"], _db_conn().list_by_project(project_name)

def get_project_metadata(project_name: str) -> List[Tuple[str, str]]:
    """Return list of metadata files for a given project.
    Returns:
        List[Tuple[str, str]]: Column names and list of metadata files.
    """
    return _db_conn().get(
        project_name,
        "metadata_path",
        all=True
    )

def get_project_value(project_name: str, key: str, default: Optional[str] = None) -> Optional[str]:
    return _db_conn().get(project_name, key) or default

def get_project_data_retrieval_info(project_name: str, operating_system: str):
    if operating_system.lower() == 'linux':
        key = "raw_data_ticket_linux"
    elif operating_system.lower() == 'windows':
        key = "raw_data_ticket_windows"
    else:
        raise ValueError(f"Invalid operating system: {operating_system}. Please use 'linux' or 'windows'.")
    return _db_conn().get(project_name, key)

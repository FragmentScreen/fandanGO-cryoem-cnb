from cryoemcnb.db.sqlite import connect_to_ddbb, close_connection_to_ddbb


def update_project(project_name, key, value):
    connection = None
    try:
        connection = connect_to_ddbb()
        cursor = connection.cursor()
        cursor.execute('INSERT INTO project_info VALUES (?, ?, ?)', (project_name, key, value))
        connection.commit()
        print(f'... project {project_name} updated: "{key}" = "{value}"')
    except Exception as e:
        print(f'... project could not be updated because of: {e}')
    finally:
        if connection:
            close_connection_to_ddbb(connection)


def get_project_info(project_name):
    connection = None
    try:
        connection = connect_to_ddbb()
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM project_info WHERE project_name = ?', (project_name,))
        project_info = cursor.fetchall()
        column_names = [columns[0] for columns in cursor.description]
        return column_names, project_info
    except Exception as e:
        print(f'... could not check projects because of: {e}')
    finally:
        if connection:
            close_connection_to_ddbb(connection)

def get_project_metadata(project_name):
    connection = None
    try:
        connection = connect_to_ddbb()
        cursor = connection.cursor()
        cursor.execute('SELECT value FROM project_info WHERE project_name = ? AND (key = "scipion_metadata_path" OR key = "acquisition_metadata_path")', (project_name,))
        project_metadata = cursor.fetchall()
        project_metadata = [metadata_file[0] for metadata_file in project_metadata]
        return project_metadata
    except Exception as e:
        print(f'... could not check projects because of: {e}')
    finally:
        if connection:
            close_connection_to_ddbb(connection)

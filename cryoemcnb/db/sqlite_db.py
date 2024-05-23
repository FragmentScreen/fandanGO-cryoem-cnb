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

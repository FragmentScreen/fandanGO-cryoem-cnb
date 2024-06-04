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

def generate_metadata_data(project_name, acquisition_name, source, output_dir):
    """
    Function that generates metadata for a FandanGO project

    Args:
        project_name (str): FandanGO project name
        acquisition_name (str): Scipion or EMadmin project name
        source (str): which is the metadata source? (scipion/emadmin)
        output_dir (str): folder for saving the metadata json
    Returns:
        success (bool): if everything went ok or not
        info (dict): Scipion or EMadmin metadata paths
    """

    print(f'FandanGO will create generate metadata for {source} project {project_name}...')
    success = False
    info = None

    # Scipion project metadata
    if source == 'scipion':
        try:
            scipion_script = f"""from pyworkflow.project import Manager
project_path = '{scipion_projects_path}/{acquisition_name}'
manager = Manager()
project = manager.loadProject(project_path)
protocols = [p for p in project.getRuns()]
project.exportProtocols(protocols, '{output_dir}/{project_name}_scipion.json')
"""

            with open('/tmp/fandanGO_scipion_script.py', 'w', encoding='utf-8') as file:
                file.write(scipion_script)

            subprocess.run([scipion_launcher, 'python', '/tmp/fandanGO_scipion_script.py'])

            if os.path.exists(f'{output_dir}/{project_name}_scipion.json'):
                success = True
                update_project(project_name, 'scipion_metadata_path', f'{output_dir}/{project_name}_scipion.json')
                info = {'scipion_metadata_path': f'{output_dir}/{project_name}_scipion.json'}

        except Exception as e:
            info = f'... metadata could not be generated for Scipion project {project_name} because of: {e}'

    # EMadmin acquistion metadata
    elif source == 'emadmin':
        connection = None
        try:
            connection = sqlite.connect(database=emadmin_ddbb_path)
            cursor = connection.cursor()
            # microscope data
            cursor.execute('SELECT microscope_id, id FROM create_proj_acquisition WHERE projname = ?', (acquisition_name,))
            microscope_id, acquisition_id = cursor.fetchone()
            cursor.execute('SELECT name, model, detector, detectorPixelSize, cs from create_proj_microscope WHERE id = ?', (microscope_id,))
            microscope_columns = ['microscope_name', 'microscope_model', 'microscope_detector', 'pixel_size', 'spherical_aberration']
            microscope_values = cursor.fetchone()
            microscope_units = [None, None, None, 'Å/px', 'mm']
            # acquisition data
            cursor.execute('SELECT voltage FROM create_proj_acquisition WHERE projname = ?', (acquisition_name,))
            voltage = cursor.fetchone()[0]
            cursor.execute('SELECT nominal_magnification, (dose_per_fraction/frames_in_fraction) as dose_per_frame, nominal_defocus_range FROM create_proj_acquisition2 WHERE id = ?', (acquisition_id,))
            nominal_magnification, dose_per_frame, nominal_defocus_range = cursor.fetchone()
            defocus_min, defocus_max, defocus_step = str(nominal_defocus_range).split(' ')
            defocus_min = float(defocus_min.replace(',', '.'))
            defocus_max = float(defocus_max.replace(',', '.'))
            acquisition_columns = ['voltage', 'nominal_magnification', 'dose_per_frame', 'defocus_min', 'defocus_max']
            acquisition_values = (voltage,) + (nominal_magnification,) + (dose_per_frame,) + (defocus_min,) + (defocus_max,)
            acquisition_units = ['kV', None, 'e/Å²', 'µm', 'µm']

            acquisition_info = {
                column: {
                    'value': value,
                    'units': unit
                } for column, value, unit in zip(microscope_columns + acquisition_columns,
                                                 microscope_values + acquisition_values,
                                                 microscope_units + acquisition_units)
            }

            with open(f'{output_dir}/{project_name}_emadmin.json', 'w', encoding='utf-8') as file:
                json.dump(acquisition_info, file, indent=4)

            if os.path.exists(f'{output_dir}/{project_name}_emadmin.json'):
                success = True
                update_project(project_name, 'acquisition_metadata_path', f'{output_dir}/{project_name}_emadmin.json')
                info = {'acquisition_metadata_path': f'{output_dir}/{project_name}_emadmin.json'}

        except Exception as e:
            info = f'... metadata could not be generated for EMadmin project {project_name} because of: {e}'

        finally:
            if connection:
                connection.close()

    return success, info


def perform_action(args):
    print(args)
    success, info = generate_metadata_data(args['name'], args['acquisition_name'], args['source'], args['output_dir'])
    results = {'success': success, 'info': info}
    return results

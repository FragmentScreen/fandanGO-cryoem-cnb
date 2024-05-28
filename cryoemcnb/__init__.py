import core
from cryoemcnb.constants import ACTION_COPY_DATA, ACTION_GENERATE_METADATA, ACTION_SEND_METADATA, ACTION_PRINT_PROJECT
from cryoemcnb.actions import copy_data, generate_metadata, send_metadata, print_project

class Plugin(core.Plugin):

    @classmethod
    def define_args(cls):
        cls.define_arg(ACTION_COPY_DATA, {
            'help': {'usage': '--raw-data-path RAW_DATA_PATH',
                     'epilog': '--raw-data-path /data/Talos/projectx'},
            'args': {
                'raw-data-path': {'help': 'path of the raw data',
                                  'required': True
                                  }
            }
        })
        cls.define_arg(ACTION_GENERATE_METADATA, {
            'help': {'usage': '--acquisition-name ACQUSITION_NAME --source {scipion, emadmin} --output-dir OUTPUT_DIR',
                     'epilog': '--acquisition-name 2024_05_24_username_000001 --source emadmin --output-dir /home/user/Desktop'},
            'args': {
                'acquisition-name': {'help': 'Scipion or EMadmin project name',
                                     'required': True
                                     },
                'source': {'help': 'Choose between Scipion or EMadmin metadata',
                           'required': True,
                           'choices': ['scipion', 'emadmin']
                           },
                'output-dir': {'help': 'folder for saving the Scipion workflow',
                               'required': True
                               }
            }
        })


    @classmethod
    def define_methods(cls):
        cls.define_method(ACTION_COPY_DATA, copy_data.perform_action)
        cls.define_method(ACTION_GENERATE_METADATA, generate_metadata.perform_action)
        cls.define_method(ACTION_SEND_METADATA, send_metadata.perform_action)
        cls.define_method(ACTION_PRINT_PROJECT, print_project.perform_action)

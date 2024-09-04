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
            'help': {'usage': '--metadata-path METADATA_PATH',
                     'epilog': '--metadata-path /home/user/ScipionUserData/projects/Project_scipion/Runs/003083_ProtOSCEM/extra'},
            'args': {
                'metadata-path': {'help': 'path of the metadata generated with the OSCEM_json protocol',
                                  'required': True
                                  }
            }
        })

        cls.define_arg(ACTION_SEND_METADATA, {
            'help': {'usage': '--visit-id VISIT_ID',
                     'epilog': '--visit-id 2'},
            'args': {
                'visit-id': {'help': 'ARIA visit id',
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

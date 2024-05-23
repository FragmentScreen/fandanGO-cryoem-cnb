import core
from cryoemcnb.constants import ACTION_COPY_DATA
from cryoemcnb.actions import copy_data


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

    @classmethod
    def define_methods(cls):
        cls.define_method(ACTION_COPY_DATA, copy_data.perform_action)

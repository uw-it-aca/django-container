import os
import sys
import importlib


class SettingLoader:
    def __init__(self, setting_file_path, **enviroment_variables):
        self.setting_file_path = setting_file_path
        self.enviroment_variables = enviroment_variables

    def __enter__(self):
        for variable_name in self.enviroment_variables:
            os.environ[variable_name] = self.enviroment_variables[variable_name]

        self.loaded_setting = importlib.import_module(self.setting_file_path)
        return self.loaded_setting

    def __exit__(self, exc_type, exc_value, tb):
        for variable_name in self.enviroment_variables:
            del os.environ[variable_name]

        modules_to_unload = []
        for module in sys.modules:
            if module.startswith(self.setting_file_path):
                modules_to_unload.append(module)

        for module in modules_to_unload:
            del sys.modules[module]

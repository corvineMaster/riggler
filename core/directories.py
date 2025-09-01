import json
from importlib import import_module, reload
from pathlib import Path
from riggler import modules


MOUDLES_RELATIVE_PATH = 'riggler.modules'
MODULES_ABSOLUTE_PATH = modules.__path__[0].replace('\\', '/')


def importModule(self, module_name, file):
    return import_module(file, module_name)


def importComponent(category, name):
    return import_module(f'{MOUDLES_RELATIVE_PATH}.{category}', name)


def importGuide(category, name):
    return import_module(f'{MOUDLES_RELATIVE_PATH}.{category}.{name}', 'guide')


def importBuild(category, name):
    import_module(f'{MOUDLES_RELATIVE_PATH}.{category}.{name}', 'build')


def getSettings(category, name):
    json_path = f'{MODULES_ABSOLUTE_PATH}/{category}/{name}/settings.json'
    data = json.load(open(json_path))
    return data
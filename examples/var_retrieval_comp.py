import builtins
from types import ModuleType

import importlib


class DummyModule(ModuleType):
    def __getattr__(self, key):
        return None
    __all__ = []   # support wildcard imports

def tryimport(namex, globals={}, locals={}, fromlist=[], level=0):
    try:
        print(f"Name: {namex}")
        return realimport(namex, globals, locals, fromlist, 0)
    except (ImportError):
        return DummyModule(namex)

realimport, builtins.__import__ = builtins.__import__, tryimport


import os.path
import sys

from src.stork_main import Stork
from src.ast.assign_visitor import AssignVisitor
from src.log_modules.util import getAst
import importlib.util

switcheroo = Stork(config_path="db_playgrounds/config.ini")
pipeline = "../src/log_modules/variable_path_reading.py"
# pipeline = "../examples/argus_eyes.py"
switcheroo.setup(pipeline=pipeline, new_pipeline="../src/log_modules/variable_path_reading_var_retrieval.py")



switcheroo.assignVisitor = AssignVisitor()
tree = getAst(pipeline=pipeline)
switcheroo.assignVisitor.setPipeline(pipeline=pipeline)
switcheroo.assignVisitor.visit(tree)
# stork.assignVisitor.filter_Assignments()

assignments = switcheroo.assignVisitor.assignments

for assignment in assignments:
    sources = assignment["data_source"]
    for source in sources:
        if isinstance(source, dict):
            try:
                data_file = source["data_file"]
            except KeyError as e:
                continue
            # print(data_file)
    try:
        pipeline_name = os.path.split(pipeline)[1]
        spec = importlib.util.spec_from_file_location(pipeline_name, pipeline)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module.__name__] = module
        # module = importlib.import_module(module.__name__)
        # spec.loader.load_module(module.__name__)
        spec.loader.exec_module(module)
        var_value = getattr(module, data_file[0])
        print(var_value)
    except (NameError, AttributeError, ImportError, ModuleNotFoundError) as e:
        print(e)
        # pass
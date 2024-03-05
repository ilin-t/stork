import ast
from pprint import pprint


class ImportVisitor(ast.NodeVisitor):
    def __init__(self):
        self.stats = {"import": [], "from": []}
        self.imports = []

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append({"import_library" : alias.name, "asname": alias.asname})
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        temp = {"from": node.module, "import_method": []}
        for alias in node.names:
            temp["import_method"].append(alias.name)
        self.imports.append(temp)
        self.generic_visit(node)

    def report(self):
        pprint(self.stats)

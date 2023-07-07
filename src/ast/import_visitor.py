import ast
from pprint import pprint


class ImportVisitor(ast.NodeVisitor):
    def __init__(self):
        self.stats = {"import": [], "from": []}

    def visit_Import(self, node):
        for alias in node.names:
            self.stats["import"].append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        temp = {"from": node.module, "import": []}
        for alias in node.names:
            temp["import"].append(alias.name)
        self.stats["from"].append(temp)
        self.generic_visit(node)

    def report(self):
        pprint(self.stats)

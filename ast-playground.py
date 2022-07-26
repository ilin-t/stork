import ast
from ast import Index, Name, Load, Subscript
from pprint import pprint
import pandas as pd


def main():
    with open("examples/paper-example.py", "r") as source:
        tree = ast.parse(source.read())

    analyzer = Analyzer()
    analyzer.visit(tree)
    analyzer.report()

    # transformer = RewriteName()
    # transformer.visit(tree)
    # # transformer.report()


class Analyzer(ast.NodeVisitor):
    def __init__(self):
        self.stats = {"import": [], "from": []}

    def visit_Import(self, node):
        for alias in node.names:
            self.stats["import"].append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        # temp = {"from" : "", "import" : []}
        temp = {"from" : node.module, "import": []}
        for alias in node.names:
            temp["import"].append(alias.name)
        self.stats["from"].append(temp)
        self.generic_visit(node)

    def report(self):
        pprint(self.stats)


class RewriteName(ast.NodeTransformer):
    def __init__(self):
        self.changed = {"changed-nodes": []}

    def visit_Name(self, node):
        return ast.copy_location(ast.Subscript(
            value=Name(id='data', ctx=Load()),
            slice=Index(value=ast.Str(s=node.id)),
            ctx=node.ctx
        ), node)



if __name__ == "__main__":

    main()

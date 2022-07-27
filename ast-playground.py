import ast
from ast import Index, Name, Load, Subscript
from pprint import pprint
import argparse

parser = argparse.ArgumentParser(description="AST Analyzer of Data Imports")
parser.add_argument("--input", required=True, help="Python script to be parsed")


def main(args):
    with open(args.input, "r") as source:
        tree = ast.parse(source.read())

    imports = ImportVisitor()
    imports.visit(tree)
    imports.report()

    assignments = AssignVisitor()
    assignments.visit(tree)
    assignments.report()

    # transformer = RewriteName()
    # transformer.visit(tree)
    # # transformer.report()


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


class AssignVisitor(ast.NodeVisitor):
    def __init__(self):
        self.assignments = []

    def visit_Assign(self, node):
        assignment = {"variable": [], "data_source": []}
        for target in node.targets:
            assignment["variable"].append(direct_visit(self, node, target))
            assignment["data_source"].append(direct_visit(self, node, node.value))
        self.assignments.append(assignment)
        # self.generic_visit(node)

    #
    def visit_Call(self, node):
        func_call = direct_visit(self, node, node.func)
        args_names = []
        for arg in node.args:
            args_names.append(direct_visit(self, node, arg))
        # self.generic_visit(node)

        return {"func_call": func_call, "data_file": args_names}

    def visit_Attribute(self, node):
        package = direct_visit(self, node, node.value)
        method = node.attr
        # self.generic_visit(node)

        return str(package) + "." + method


    def visit_BinOp(self, node):
        left = direct_visit(self, node, node.left)
        print(node.op)
        right = direct_visit(self, node,node.right)
        print(node.left._fields[0] + "  ", type(node.op).__name__ +
              " " + node.right._fields[1])
        # self.generic_visit(node)
        return [left, right]

    def visit_Subscript(self, node):
        load_var = direct_visit(self, node, node.value)
        filter_criteria = direct_visit(self, node, node.slice)

        return [load_var, filter_criteria]

    # TODO Check other AST nodes and what properties they carry.
    # TODO Adapt for subscripts,
    #  they are most commonly used for data filtering

    def visit_Name(self, node):
        # direct_visit()
        # self.generic_visit(node)
        return node.id

    def visit_Constant(self, node):
        # self.generic_visit(node)
        return node.value

    def report(self):
        pprint(self.assignments)


# class RewriteName(ast.NodeTransformer):
#     def __init__(self):
#         self.changed = {"changed-nodes": []}
#
#     def visit_Name(self, node):
#         return ast.copy_location(ast.Subscript(
#             value=Name(id='data', ctx=Load()),
#             slice=Index(value=ast.Str(s=node.id)),
#             ctx=node.ctx
#         ), node)

class TransformPipeline(ast.NodeTransformer):
    def __init__(self):
        self.changedNodes = []



def direct_visit(object, node, towards):
    try:
        func_name = "visit_" + type(towards).__name__
        func = getattr(object, func_name)
        print("Method %s will be called from node type %s from object %s.\n" % (func_name, type(node), type(object)))
        output = func(towards)
        return output
    except AttributeError:
        print("visit_" + type(towards).__name__ + " accessed from node type " + type(node).__name__ + " is not defined.")


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)

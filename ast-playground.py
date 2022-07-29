import ast
from ast import Index, Name, Load, Subscript
from pprint import pprint
import argparse

parser = argparse.ArgumentParser(description="AST Analyzer of Data Imports")
parser.add_argument("--pipeline", required=True, help="Python script to be parsed")
parser.add_argument("--input", default="0", help="new input dataset(s), should be the same number as existing "
                                                    "pipeline inputs. If more than 1, provide it in a list format."
                                                    " When providing a list, the inputs will "
                                                    "be mapped in the order of appearance. If not sure of the "
                                                    "ordering or naming, leave the field empty the system will "
                                                    "ask you for your input.")


def main(args):
    with open(args.pipeline, "r") as source:
        tree = ast.parse(source.read())

    # imports = ImportVisitor()
    # imports.visit(tree)
    # imports.report()
    assigner = AssignVisitor()
    assigner.visit(tree)
    reportAssign(assigner.assignments, "full")
    assigner.filter_Assignments()
    assigner.filter_datasets()
    reportAssign(assigner.datasets, "datasets")
    if len(args.input.split(",")) > len(assigner.datasets):
        print("New input size larger than the number of the datasets in the original pipeline. Please map your "
              "inputs.\n")
        for dataset in assigner.datasets:
            print("Current value for %s is: %s" % (dataset["variable"], dataset["data_source"]["data_file"]))
            assigner.new_inputs[assigner.datasets.index(dataset)] = input("New value for %s: \n" % dataset["variable"])
        print(assigner.new_inputs)
    elif int(args.input) == len(assigner.datasets):
        assigner.new_inputs = args.input.split(",")
    else:
        print("No new inputs provided. Please add the new inputs for: \n")
        for dataset in assigner.datasets:
            print("Current value for %s is: %s" % (dataset["variable"], dataset["data_source"]["data_file"]))
            assigner.new_inputs[assigner.datasets.index(dataset)] = input("New value for %s: \n" % dataset["variable"])
        print(assigner.new_inputs)


    # print(assigner.datasets)
    # print(trimmed)
    # reportAssign(trimmed, "clean")
    # report(assignments.assignments)

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


def reportAssign(assignments, full):
    path = str.split(args.input, "/")
    filename = str.split(path[len(path) - 1], ".")

    with open("assignments-" + filename[0] + "-" + full + ".txt", "w") as output:
        for assignment in assignments:
            output.write(str(assignment) + "\n")
        output.close()
    # pprint(assignments)


class AssignVisitor(ast.NodeVisitor):
    def __init__(self):
        self.inputs = []
        self.assignments = []
        self.datasets = []
        self.imports = []
        self.new_inputs=[]

    def visit_Assign(self, node):
        assignment = {"variable": str, "data_source": str}
        for target in node.targets:
            assignment["variable"] = direct_visit(self, node, target)
            assignment["data_source"] = direct_visit(self, node, node.value)
        self.assignments.append(assignment)
        # self.generic_visit(node)

    #
    def visit_Call(self, node):
        func_call = direct_visit(self, node, node.func)
        args_names = []
        params = []
        for arg in node.args:
            args_names.append(direct_visit(self, node, arg))
        # self.generic_visit(node)
        for keyword in node.keywords:
            params.append(direct_visit(self, node, keyword))

        return {"func_call": func_call, "data_file": args_names, "params": params}

    def visit_Attribute(self, node):
        package = direct_visit(self, node, node.value)
        method = node.attr
        # self.generic_visit(node)

        return {"from": package, "method": method}

    def visit_BinOp(self, node):
        left = direct_visit(self, node, node.left)
        print(node.op)
        right = direct_visit(self, node, node.right)
        print(node.left._fields[0] + "  ", type(node.op).__name__ +
              " " + node.right._fields[1])

        if type(node.op).__name__ == "Add":
            if type(left) == str and type(right) == str:
                return str(left + right)
        # self.generic_visit(node)
        # else:
        return [left, right]

    def visit_Subscript(self, node):
        load_var = direct_visit(self, node, node.value)
        filter_criteria = direct_visit(self, node, node.slice)

        return [load_var, filter_criteria]

    # TODO Check other AST nodes and what properties they carry.
    # TODO Adapt for subscripts,
    #  they are most commonly used for data filtering

    def visit_Name(self, node):
        return node.id

    def visit_Constant(self, node):
        return node.value

    def visit_keyword(self, node):
        return {node.arg: direct_visit(self, node, node.value)}

    # The methods below are necessary for parsing the filter operators and preprocessing operations

    #  TODO
    # def visit_Compare(self, node: Compare) -> Any:

    # TODO
    # def visit_List(self, node: List) -> Any:

    # TODO
    # def visit_Tuple(self, node: Tuple) -> Any:

    def filter_Assignments(self):
        removed = []
        for assignment in self.assignments:
            print(assignment)
            print("Type of the above assignment: %s" % type(assignment["data_source"]))
            if type(assignment["data_source"]) is not dict:
                removed.append(assignment)
                print("removed\n")
            elif "data_file" not in assignment["data_source"].keys():
                removed.append(assignment)
                print("removed\n")
            elif len(assignment["data_source"]["data_file"]) == 0:
                removed.append(assignment)
                print("removed\n")
            elif type(assignment["data_source"]["data_file"][0]) is not str:
                removed.append(assignment)
                print("Type of the above data_file: %s" % type(assignment["data_source"]["data_file"][0]))
                print("removed\n")
            elif type(assignment["data_source"]["data_file"][0][0]) is not str:
                removed.append(assignment)
                print("Type of the above data_file: %s" % type(assignment["data_source"]["data_file"][0][0]))
                print("removed\n")
            else:
                print("didn't remove\n")

        self.inputs = [assignment for assignment in self.assignments if assignment not in removed]

        return self.inputs

    def filter_datasets(self):
        processing_steps = []
        for assignment in self.inputs:
            for i in range(self.inputs.index(assignment) + 1, len(self.inputs)):
                if assignment["variable"] in self.inputs[i]["data_source"]["data_file"]:
                    processing_steps.append(self.inputs[i])
                    print("%s is a preprocessing step\n" % assignment)
                elif assignment["variable"] == self.inputs[i]["variable"]:
                    processing_steps.append(self.inputs[i])
                    print("%s alters a previous data input\n" % assignment)
                else:
                    print("%s is a data input\n" % assignment)
        self.datasets = [assignment for assignment in self.inputs if assignment not in processing_steps]
        print(self.datasets)


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


def direct_visit(parent_object, node, towards):
    try:
        func_name = "visit_" + type(towards).__name__
        func = getattr(parent_object, func_name)
        # print("Method %s will be called from node "
        #       "type %s from object %s.\n" % (func_name, type(node), type(parent_object)))
        output = func(towards)
        return output
    except AttributeError:
        print(
            "visit_" + type(towards).__name__ +
            " accessed from node type " + type(node).__name__ + " is not defined.")


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)

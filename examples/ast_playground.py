import ast
import argparse

from src.ast.assign_visitor import AssignVisitor
from src.ast.import_visitor import ImportVisitor
from src.util.util import getAst

parser = argparse.ArgumentParser(description="AST Analyzer of Data Imports")
parser.add_argument("--pipeline", required=True, help="Python script to be parsed")
parser.add_argument("--input", default="0", help="new input dataset(s), should be the same number as existing "
                                                 "pipeline inputs. If more than 1, provide it in a list format."
                                                 " When providing a list, the inputs will "
                                                 "be mapped in the order of appearance. If not sure of the "
                                                 "ordering or naming, leave the field empty the system will "
                                                 "ask you for your input.")


def main(args):
    # Generate this into a method / return tree
    # with open(args.pipeline, "r") as source:
    #     tree = ast.parse(source.read())
    #     # print(tree.body)

    # printAst(args.pipeline)
    tree = getAst(args.pipeline)
    assigner = AssignVisitor()

    assigner.visit(tree)

    imports = ImportVisitor()
    imports.visit(tree)
    imports.report()
    #
    # reportAssign(assigner.assignments, "full")
    # assigner.filter_Assignments()
    # assigner.filter_datasets()
    # reportAssign(assigner.datasets, "datasets")
    # if len(args.input.split(",")) > len(assigner.datasets):
    #     print("New input size larger than the number of the datasets in the original pipeline. Please map your "
    #           "inputs.\n")
    #     for dataset in assigner.datasets:
    #         print("Current value for %s is: %s. If no change to the input is required or the input variable is not "
    #               "suitable, press ENTER." % (dataset["variable"], dataset["data_source"]["data_file"]))
    #         assigner.new_inputs.append({"old_input": dataset["data_source"]["data_file"],
    #                                     "new_input": [input("New value for %s: \n" % dataset["variable"])]})
    # elif int(args.input) == len(assigner.datasets):
    #     assigner.new_inputs = args.input.split(",")
    # else:
    #     print("No new inputs provided. Please add the new inputs for: \n")
    #     for dataset in assigner.datasets:
    #         print("Current value for %s is: %s. If no change to the input is required or the input variable is not "
    #               "suitable, press ENTER." % (dataset["variable"], dataset["data_source"]["data_file"]))
    #         assigner.new_inputs.append({"old_input": dataset["data_source"]["data_file"],
    #                                     "new_input": [input("New value for %s: \n" % dataset["variable"])]})
    # assigner.parseNewInputs()
    #
    # pipeline_name = args.pipeline.split(".")
    # assigner.transformScript(args.pipeline, pipeline_name[0] + "-new." + pipeline_name[1])
    # #
    # # # print(assigner.datasets)
    # # # print(trimmed)
    # # # reportAssign(trimmed, "clean")
    # # # report(assignments.assignments)
    # #
    # # # transformer = RewriteName()
    # # # transformer.visit(tree)
    # # # # transformer.report()
    #


def printAst(source):
    with open(source, "r") as source:
        tree = ast.parse(source.read() + "\n")
        print(ast.dump(tree) + "\n")


def reportAssign(assignments, full):
    path = str.split(args.input, "/")
    filename = str.split(path[len(path) - 1], ".")

    with open("assignments-" + filename[0] + "-" + full + ".txt", "w") as output:
        for assignment in assignments:
            output.write(str(assignment) + "\n")
        output.close()





if __name__ == "__main__":
    args = parser.parse_args()
    main(args)

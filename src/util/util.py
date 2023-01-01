import ast


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
            " accessed from node type " + type(node).__name__ + " is not defined.\n")


def getAst(pipeline):
    with open(pipeline, "r") as source:
        return ast.parse(source.read() + "\n")

def checkDataFile(data_file):
    for item in data_file:
        return checkFileExtension(item)


def checkFileExtension(data_file):
    if type(data_file) is not str:
        return False
    file = data_file.split(".")
    if len(file) < 2:
        return False
    # Data files and compression support for numpy and pandas
    elif file[-1] in ["csv", "txt", "zip", "parquet", "gz", "tar", "bz2", "zstd", "npy"]:
        return True


def reportAssign(pipeline, assignments, full):
    path = str.split(pipeline, "/")
    filename = str.split(path[len(path) - 1], ".")

    with open("assignments-" + filename[0] + "-" + full + ".txt", "w") as output:
        for assignment in assignments:
            output.write(str(assignment) + "\n")
        output.close()

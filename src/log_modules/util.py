import ast

def getAst(pipeline):
    with open(pipeline, "r") as source:
        return ast.parse(source.read() + "\n")


# def checkDataFile(data_file):
#     for item in data_file:
#         print(f"Item: {item}")
#         if type(item) is not str:
#             return False
#         file = item.split(".")
#         if len(file) < 2:
#             return False
#         # Data files and compression support for pandas from_csv method
#         elif file[-1] in ["csv", "txt", "zip", "parquet", "gz", "tar", "bz2", "zstd"]:
#             return True

def checkDataFile(data_file):
    if isinstance(data_file, list):
        for item in data_file:
            return checkFileExtension(item)
    else:
        return checkFileExtension(data_file)

def checkFileExtension(data_file):
    if type(data_file) is not str:
        return False
    file = data_file.split(".")
    if len(file) < 2:
        return False
    # Data files and compression support for numpy and pandas
    elif file[-1] in ["csv", "txt", "zip", "parquet", "gz", "tar", "bz2", "zstd", "npy", "py"]:
        return True


def reportAssign(pipeline, assignments, full):
    path = str.split(pipeline, "/")
    filename = str.split(path[len(path) - 1], ".")

    with open("assignments-" + filename[0] + "-" + full + ".txt", "w") as output:
        for assignment in assignments:
            output.write(str(assignment) + "\n")
        output.close()

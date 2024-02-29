import ast
import os
import os.path
from os.path import basename, normpath


def getFileExtensions():
    return ["csv", "txt", "zip", "pkl", "parquet", "gz", "tar", "bz2", "zstd", "npy", "py"]

def list_folder_names(path):
    return [f.name for f in os.scandir(path) if f.is_dir()]


def list_files_paths(path):
    return [f.path for f in os.scandir(path) if f.is_file()]


def list_files_names(path):
    return [f.name for f in os.scandir(path) if f.is_file()]


def filter_python_files(files):
    return [file for file in files if file.lower().endswith('.py')]


def filter_folders(project_path):
    folder_paths = list_folder_paths(project_path)
    folders = []
    ignore = False
    to_ignore = ['bin/*', 'www', 'js', 'virtual', '*virtual*', 'dist-packages', 'site-packages',
                 '*env*', 'env', 'etc/*', 'include/*', 'lib/*', 'lib64/*', '.venv/*', '*/venv/*']
    for folder in folder_paths:
        for name in to_ignore:
            if name in basename(normpath(folder)).lower():
                ignore = True
                break
        if ignore:
            continue
        # if "env" in basename(normpath(folder)).lower() or "lib" in basename(normpath(folder)).lower():
        #     continue
        elif basename(normpath(folder)).startswith((".", "_")):
            continue
        else:
            folders.append(folder)
    return folders


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
    elif file[-1] in ["csv", "txt", "zip", "pkl", "parquet", "gz", "tar", "bz2", "zstd", "npy", "py"]:
        return True


def fileExists(data_file):
    return os.path.isfile(data_file)


def reportAssign(pipeline, assignments, full):
    path = str.split(pipeline, "/")
    filename = str.split(path[len(path) - 1], ".")

    with open("assignments-" + filename[0] + "-" + full + ".txt", "w") as output:
        for assignment in assignments:
            output.write(str(assignment) + "\n")
        output.close()


def compareTwoFiles(file1, file2):
    lines1 = []
    lines2 = []
    with open(file1) as f:
        lines1 = f.readlines()
    f.close()

    with open(file2) as f:
        lines2 = f.readlines()
    f.close()

    set_lines1 = set(lines1)
    diff = [x for x in lines2 if x not in set_lines1]
    # diff = [i for i in lines1 + lines2 if i not in lines1 or i not in lines2]

    return diff

def addToList(list, diff):
    print(len(diff))
    print(diff)
    with open(list, "a") as f:
        for el in diff:
            f.write(el)
    f.close()

def addToNewList(input_file, diff, output):
    lines1=[]
    with open(input_file) as f:
        lines1 = f.readlines()
    f.close()

    with open(output, "a") as f:
        f.writelines(lines1)
        f.write("\n")
        f.writelines(diff)
    f.close()



if __name__ == '__main__':
    # compareTwoFiles("../../analysis_results/stork-coverage/aggregated_results_local.txt",
    #                 "../../analysis_results/stork-coverage/aggregated_results_local_shorter.txt",
    #                 "../../analysis_results/stork-coverage/difference.txt")
    # compareTwoFiles("../../examples/repo_lists/aggregated_results_libs.txt",
    #                 "../../examples/repo_lists/aggregated_results_py.txt",
    #                 "../../analysis_results/stork-coverage/difference_lib.txt")
    # compareTwoFiles("../../examples/repo_lists/aggregated_results_py.txt",
    #                 "../../examples/repo_lists/aggregated_results_libs.txt",
    #                 "../../analysis_results/stork-coverage/difference_py.txt")

    diff = compareTwoFiles("../../analysis_results/repository_list/shortened_list_repositories_1.txt",
                    "../../analysis_results/repository_list/shortened_list_repositories_2.txt")

    addToNewList(input_file="../../analysis_results/repository_list/shortened_list_repositories_1.txt",
                 diff=diff,
                 output="../../analysis_results/repository_list/diff_short.txt")


def list_folder_paths(path):
    return [f.path for f in os.scandir(path) if f.is_dir()]

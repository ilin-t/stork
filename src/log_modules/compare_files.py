

def compare_files(f1_lines, f2_lines, method):
    if method == "intersection":
        return list(set(f1_lines) & set(f2_lines))
    elif method == "diff_left":
        return [x for x in f1_lines if x not in f2_lines]
    elif method == "diff_right":
        return [x for x in f2_lines if x not in f1_lines]
    elif method == "union":
        return list(set(f1_lines) | set(f2_lines))

def write_files(lines, output_file):
    with (open(output_file, "w") as f):
        for line in lines:
            f.write(line.strip())
            f.write("\n")
    f.close()
def generate_files(file1, file2, path, year):
    with open(file1) as f:
        f1_lines = f.readlines()
    f.close()
    with open(file2) as f:
        f2_lines = f.readlines()
    f.close()

    intersection = compare_files(f1_lines=f1_lines, f2_lines=f2_lines, method="intersection")
    diff_left = compare_files(f1_lines=f1_lines, f2_lines=f2_lines, method="diff_left")
    diff_right = compare_files(f1_lines=f1_lines, f2_lines=f2_lines, method="diff_right")
    union = compare_files(f1_lines=f1_lines, f2_lines=f2_lines, method="union")

    write_files(intersection, f"{path}/{year}/intersection_{year}.txt")
    write_files(diff_left, f"{path}/{year}/py_only_{year}.txt")
    write_files(diff_right, f"{path}/{year}/lib_only_{year}.txt")
    write_files(union, f"{path}/{year}/union_{year}.txt")

if __name__ == "__main__":
    # generate_files("../../analysis_results/repository_list/shortened_list_repositories_1.txt",
    #               "../../analysis_results/repository_list/shortened_list_repositories_2.txt",
    #                path="../../analysis_results/pipeline_distribution/", year="test")
    PATH_ROOT = "/home/ilint/HPI/Stork/pipeline-lists/"
    for year in range(2018, 2024):
        generate_files(f"{PATH_ROOT}python_reads/aggregated_results_{year}.txt",
                       f"{PATH_ROOT}library_reads/aggregated_results_{year}.txt",
                       path="../../analysis_results/pipeline_distribution/", year=year)




import os

from parse_repos import collect_resources


def get_packages(filepath):
    packages_per_file = []
    with open(f"{filepath}", "r") as file:
        for line in file.readlines():
            package = line.split("==")[0]
            package = package.split("<")[0]
            package = package.split(">")[0]
            package = package.strip()
            packages_per_file.append(package)
    # print(f"{requirements_file}: {packages_per_file}")
    file.close()

    return packages_per_file


def parse_requirement(packages_list, package_count, packages_path, num_threads, thread_id, package_totals):
    packages_per_thread = package_count // num_threads
    start_index = thread_id * packages_per_thread
    end_index = start_index + packages_per_thread
    parsed_packages = []
    total_packages = {}

    if (thread_id == num_threads - 1):
        end_index = package_count - 1

    for i in range(start_index, end_index):
        requirements_file = get_filename(packages_list[i])

        parsed_packages.append(packages_list[i])
        total_packages[requirements_file] = get_packages(packages_list[i])


def get_parent_dir(filepath):
    return os.path.dirname(filepath)


def get_filename(filepath):
    return os.path.basename(filepath)

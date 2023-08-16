import os
import pandas as pd

from os.path import isfile, join
from collections import Counter

from matplotlib import pyplot as plt

# sc = SparkContext("local", "Requirements file parser")
# rdd = pyspark.SparkContext.
OUTPUTS_ROOT = "/mnt/fs00/rabl/ilin.tolovski/stork/outputs/"
REPOS_ROOT = "/mnt/fs00/rabl/ilin.tolovski/stork/repositories-test/"
PACKAGES_ROOT = "/mnt/fs00/rabl/ilin.tolovski/stork/packages/"


# packages_path = "\\store-01.hpi.uni-potsdam.de\\fg\\rabl\\ilin.tolovski\\stork\\packages"
# packages_path = r"//store-01.hpi.uni-potsdam.de/fg/rabl/ilin.tolovski/stork/packages/"

def traverse_requirements(packages_root):
    total_packages = {}
    years = [f.name for f in os.scandir(packages_root) if f.is_dir()]
    for year in years:
        months = [f.name for f in os.scandir(f"{packages_root}{year}") if f.is_dir()]
        for month in months:
            days = [f.name for f in os.scandir(f"{packages_root}{year}/{month}") if f.is_dir()]
            for day in days:
                pages = [f.name for f in os.scandir(f"{packages_root}{year}/{month}/{day}") if f.is_dir()]
                for page in pages:
                    packages_path = f"{packages_root}{year}/{month}/{day}/{page}/"
                    requirements_list = [f.name for f in os.scandir(packages_path) if f.is_file()]
                    print(requirements_list)
                    for requirements_file in requirements_list:
                        packages_per_file = []
                        with open(f"{packages_path}{requirements_file}", "r") as file:
                            for line in file.readlines():
                                package = line.split("==")[0]
                                package = package.split("<")[0]
                                package = package.split(">")[0]
                                package = package.strip()
                                packages_per_file.append(package)
                        # print(f"{requirements_file}: {packages_per_file}")
                        file.close()
                        total_packages[requirements_file] = packages_per_file
                        # total_packages.append({requirements_file:packages_per_file})

    print(total_packages)
    return total_packages


# extract packages
def count_packages(total_packages, packages_root):
    complete_list = []

    for single_list in total_packages.values():
        for value in single_list:
            complete_list.append(value)

    # count occurences:
    occurences = Counter(complete_list)
    with open(f"{packages_root}occurences.csv", "w") as file:
        file.write("library,count\n")
        for library, count in occurences.items():
            if library == "":
                continue
            file.write('{},{}\n'.format(str(library), str(count)))
    file.close()


packages_list = traverse_requirements(packages_root=PACKAGES_ROOT)
count_packages(total_packages=packages_list, packages_root=PACKAGES_ROOT)

import logging
import os

from log_modules.log_results import createLoggerPlain

OUTPUTS_ROOT = "/mnt/fs00/rabl/ilin.tolovski/stork/outputs/"
REPOS_ROOT = "/mnt/fs00/rabl/ilin.tolovski/stork/repositories-test/"
PACKAGES_ROOT = "/mnt/fs00/rabl/ilin.tolovski/stork/packages/"


# repositories = [f.name for f in os.scandir(repos_path) if f.is_dir()]
# repositories_sorted = sorted(repositories, key=str.lower)
# print(len(repositories_sorted))
# print(repositories_sorted)

def generate_requirements(repos_root, packages_root):
    missing_repositories = createLoggerPlain(filename=f"{OUTPUTS_ROOT}missing_repositories.log",
                                             project_name="missing_repositories", level=logging.INFO)
    years = [f.name for f in os.scandir(repos_root) if f.is_dir()]
    for year in years:
        months = [f.name for f in os.scandir(f"{repos_root}{year}") if f.is_dir()]
        for month in months:
            days = [f.name for f in os.scandir(f"{repos_root}{year}/{month}") if f.is_dir()]
            for day in days:
                pages = [f.name for f in os.scandir(f"{repos_root}{year}/{month}/{day}") if f.is_dir()]
                for page in pages:

                    repos_path = f"{repos_root}{year}/{month}/{day}/{page}/"
                    packages_path = f"{packages_root}{year}/{month}/{day}/{page}/"
                    repos = [f.name for f in os.scandir(repos_path) if f.is_dir()]
                    print(repos)
                    for repo in repos:
                        os.makedirs(f"{packages_path}", exist_ok=True)
                        sysreturn = os.system(f"python3 -m pipreqs.pipreqs {repos_path}{repo}/ "
                                              f"--ignore bin,etc,include,lib,lib64,.venv --encoding=utf-8 "
                                              f"--savepath {packages_path}{repo}")
                        print(sysreturn)
                        if sysreturn != 0:
                            if os.path.exists(f"{repos_path}{repo}/requirements.txt"):
                                os.system(f"cp {repos_path}{repo}/requirements.txt {packages_path}{repo}")
                            else:
                                print(
                                    f"No requirements file found or generated for repository: {repo}. "
                                    f"Perform manual inspection.")
                                missing_repositories.info(msg=f"{repos_path}/{repo}")


generate_requirements(repos_root=REPOS_ROOT, packages_root=PACKAGES_ROOT)

import logging
import os

from log_results import createLoggerPlain

OUTPUTS_ROOT = "/mnt/fs00/rabl/ilin.tolovski/stork/outputs/"
REPOS_ROOT = "/mnt/fs00/rabl/ilin.tolovski/stork/repositories-test/"
PACKAGES_ROOT = "/mnt/fs00/rabl/ilin.tolovski/stork/packages/"


# repositories = [f.name for f in os.scandir(repos_path) if f.is_dir()]
# repositories_sorted = sorted(repositories, key=str.lower)
# print(len(repositories_sorted))
# print(repositories_sorted)

def generate_requirements(repos_root, packages_root, outputs_root, total_size, thread_id, num_threads):
    missing_repositories = createLoggerPlain(filename=f"{outputs_root}missing_repositories-{thread_id}.log",
                                             project_name=f"missing_repositories-{thread_id}", level=logging.INFO)
    repositories_totals = createLoggerPlain(filename=f"{outputs_root}repo_stats/stats-{thread_id}.log",
                                            project_name=f"stats-{thread_id}", level=logging.INFO)
    years = [f.name for f in os.scandir(repos_root) if f.is_dir()]

    # total_size = getSize(repos_root)
    per_thread = total_size // num_threads

    start_pos = per_thread * thread_id
    end_pos = start_pos + per_thread

    if thread_id == num_threads - 1:
        end_pos = total_size

    months, days, pages, repos = [], [], [], []
    month_count, day_count, page_count, repo_count, missing_repo_count = 0, 0, 0, 0, 0
    repositories_totals.info(f"year_count\t{len(years)}")
    for year in years:
        for i in range(start_pos, end_pos):
            months = [f.name for f in os.scandir(f"{repos_root}{year}") if f.is_dir()]
            month = months[i % len(months)]

            days = [f.name for f in os.scandir(f"{repos_root}{year}/{month}") if f.is_dir()]
            day_count += len(days)
            for day in days:
                pages = [f.name for f in os.scandir(f"{repos_root}{year}/{month}/{day}") if f.is_dir()]
                page_count += len(pages)
                for page in pages:
                    repos_path = f"{repos_root}{year}/{month}/{day}/{page}/"
                    packages_path = f"{packages_root}{year}/{month}/{day}/{page}/"
                    repos = [f.name for f in os.scandir(repos_path) if f.is_dir()]
                    repo_count += len(repos)
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
                                missing_repo_count += 1
        repositories_totals.info(f"month_count\t{month_count}")
        repositories_totals.info(f"day_count\t{day_count}")
        repositories_totals.info(f"page_count\t{page_count}")
        repositories_totals.info(f"repo_count\t{repo_count}")
        repositories_totals.info(f"missing_repo_count\t{missing_repo_count}")
        repositories_totals.info(f"missing_repo_ratio\t{missing_repo_count / repo_count}")

    # for year in years:
    #     months = [f.name for f in os.scandir(f"{repos_root}{year}") if f.is_dir()]
    #     month_count += len(months)
    #     for month in months:
    #         days = [f.name for f in os.scandir(f"{repos_root}{year}/{month}") if f.is_dir()]
    #         day_count += len(days)
    #         for day in days:
    #             pages = [f.name for f in os.scandir(f"{repos_root}{year}/{month}/{day}") if f.is_dir()]
    #             page_count += len(pages)
    #             for page in pages:
    #                 repos_path = f"{repos_root}{year}/{month}/{day}/{page}/"
    #                 packages_path = f"{packages_root}{year}/{month}/{day}/{page}/"
    #                 repos = [f.name for f in os.scandir(repos_path) if f.is_dir()]
    #                 repo_count += len(repos)
    #                 for repo in repos:
    #                     os.makedirs(f"{packages_path}", exist_ok=True)
    #                     sysreturn = os.system(f"python3 -m pipreqs.pipreqs {repos_path}{repo}/ "
    #                                           f"--ignore bin,etc,include,lib,lib64,.venv --encoding=utf-8 "
    #                                           f"--savepath {packages_path}{repo}")
    #                     print(sysreturn)
    #                     if sysreturn != 0:
    #                         if os.path.exists(f"{repos_path}{repo}/requirements.txt"):
    #                             os.system(f"cp {repos_path}{repo}/requirements.txt {packages_path}{repo}")
    #                         else:
    #                             print(
    #                                 f"No requirements file found or generated for repository: {repo}. "
    #                                 f"Perform manual inspection.")
    #                             missing_repositories.info(msg=f"{repos_path}/{repo}")
    #                             missing_repo_count += 1
    #
    # repositories_totals.info(f"month_count\t{month_count}")
    # repositories_totals.info(f"day_count\t{day_count}")
    # repositories_totals.info(f"page_count\t{page_count}")
    # repositories_totals.info(f"repo_count\t{repo_count}")
    # repositories_totals.info(f"missing_repo_count\t{missing_repo_count}")
    # repositories_totals.info(f"missing_repo_ratio\t{missing_repo_count/repo_count}")


# generate_requirements(repos_root=REPOS_ROOT, packages_root=PACKAGES_ROOT, outputs_root=OUTPUTS_ROOT)


def getTotalSize(repos_root):
    years = getYears(repos_root)
    month_len = 0
    years_len = len(years)
    for year in years:
        months = [f.name for f in os.scandir(f"{repos_root}{year}") if f.is_dir()]
        month_len += len(months)

    return years_len * month_len


def getMonthsForYear(repos_root, year):
    return [f.name for f in os.scandir(f"{repos_root}{year}") if f.is_dir()]


def getYears(repos_root):
    return [f.name for f in os.scandir(repos_root) if f.is_dir()]


def getYearMonthPairing(repos_root):
    years = getYears(repos_root)
    pairings = {}
    for year in years:
        months = getMonthsForYear(repos_root, year)
        pairings[year] = len(months)

    return pairings

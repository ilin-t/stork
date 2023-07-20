import json
import logging
import os
import sys
import time
from pathlib import Path

import requests
from log_results import createLogger

# query = "read_csv+language:python"
# query = "read_csv+language:python"
# query = "read_csv+extension%3Apy+extension%3Aipynb+language%3APython"
# languages = ["python", "Jupyter Notebook"]
# pages = range(1)
# per_page = 30
# storage_path = "/mnt/fs00/rabl/ilin.tolovski/stork-test/repositories-test/"
# output_path_local = "/home/ilint/HPI/repos/stork-test/outputs/"
# output_path_mnt = "/mnt/fs00/rabl/ilin.tolovski/stork-test/outputs/"
# # new token
# token = "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"

# years = [2018, 2019, 2020, 2021, 2022, 2023]
# years = [2021, 2022, 2023]
# months = [str(i).zfill(2) for i in range(1, 13)]
# days = [str(i).zfill(2) for i in range(1, 32)]
#
# # years = [2018, 2019]
# # days = range(30, 32)
# # months = ['03', '04']
#
#
# # pages = range(1,101)
# pages = range(1, 30)


def get_repos(years, months, days, pages, token):
    per_page = 30
    storage_path = "/mnt/fs00/rabl/ilin.tolovski/stork-test/repositories-test/"
    output_path_local = "/home/ilint/HPI/repos/stork-test/outputs/"
    output_path_mnt = "/mnt/fs00/rabl/ilin.tolovski/stork-test/outputs/"
    eom = False
    log = None
    licenses = ['mit']
    for year in years:
        for month in months:
            for day in days:
                for page in pages:

                    os.makedirs(f"{output_path_mnt}repo_stats/{day}-{month}-{year}", exist_ok=True)
                    log = createLogger(
                        filename=f"{output_path_mnt}repo_stats/{day}-{month}-{year}/repositories-{day}-{month}-{year}-page-{page}.log",
                        project_name=f"repo_stats-{day}-{month}-{year}-page-{page}", level=logging.INFO)

                    if (page > 1) and (page % 30 == 1):
                        time.sleep(60)
                    else:
                        query = f"q=license:mit+created:{year}-{month}-{day}+language:Python&type=repositories"
                        url = f"https://api.github.com/search/repositories?{query}&page={page}"
                        print(url)
                        headers = {
                            "Authorization": f"Bearer {token}",
                            "Accept": "application/vnd.github+json"
                        }
                        response = requests.request("GET", url, headers=headers)
                        json_response = response.json()
                        # print(json_response)
                        os.makedirs(f"{output_path_mnt}repo_lists/{day}-{month}-{year}", exist_ok=True)
                        with open(
                                f"{output_path_mnt}repo_lists/{day}-{month}-{year}/repos-read-csv-{day}-{month}-{year}-page-{page}.json",
                                mode="w") as file:
                            json.dump(json_response, file)

                        repositories = {}
                        if "items" not in json_response.keys():
                            print(f"Number of pages: {page}.")
                            eom = True
                            break
                        if not json_response["items"]:
                            time.sleep(60)
                            break
                        else:

                            for item in json_response["items"]:
                                repositories[item["name"]] = item["html_url"]

                            for repository in repositories:
                                print(f"Repository: {repository}, url: {repositories[repository]}")
                                log.info(f"Repository: {repository}, url: {repositories[repository]}, "
                                         f"date (yyyy-mm-dd):{year}-{month}-{day}")
                                response = requests.request("GET", repositories[repository], headers=headers)
                                os.system(f"git clone --depth 1 --single-branch --shallow-submodules "
                                          f"{repositories[repository]} "
                                          f"{storage_path}year-{year}/month-{month}/day-{day}/page-{page}/{repository}")

                        file.close()
                if eom:
                    eom = False
                    break
                log.info(f"Total count for {year}-{month}-{day}: {json_response['total_count']}")

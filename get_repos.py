import json
import os

import requests

query = "read_csv+language:python"
# query = "read_csv+extension%3Apy+extension%3Aipynb+language%3APython"
languages = ["python", "Jupyter Notebook"]
pages = range(1,101)
per_page = 30
token = "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"

for page in pages:
    url = f"https://api.github.com/search/code?q={query}&page={page}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    response = requests.request("GET", url, headers=headers)
    json_response = response.json()
    with open(f"repos_{page}_{per_page}.json", mode="w") as file:
        json.dump(json_response, file)

    repositories = {}

    for item in json_response["items"]:
        repositories[item["repository"]["name"]] = item["repository"]["html_url"]

    for repository in repositories:
        print(f"Repository: {repository}, url: {repositories[repository]}")
        # response = requests.request("GET", repositories[repository], headers=headers)
        os.system(f"git clone {repositories[repository]} github_repos_3000/{repository}")

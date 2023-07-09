import os

repos_path = "/home/ilint/HPI/fs00/rabl/ilin.tolovski/stork/repositories-test/"
packages_path = "/home/ilint/HPI/fs00/rabl/ilin.tolovski/stork/packages/"

repositories = [f.name for f in os.scandir(repos_path) if f.is_dir()]
repositories_sorted = sorted(repositories, key=str.lower)
print(len(repositories_sorted))

for repo in repositories_sorted:

    sysreturn = os.system(f"python3 -m pipreqs.pipreqs {repos_path}{repo} --ignore bin,etc,include,lib,lib64,.venv --encoding=utf-8 --savepath {packages_path}{repo}")
    print(sysreturn)
    if sysreturn!=0:
        if os.path.exists(f"{repos_path}{repo}/requirements.txt"):
            os.system(f"cp {repos_path}{repo}/requirements.txt {packages_path}{repo}")
        else:
            print(f"No requirements file found or generated for repository: {repo}. Perform manual inspection.")

packages = [f.name for f in os.scandir(packages_path) if f.is_file()]
packages_sorted = sorted(packages, key=str.lower)
print(len(packages_sorted))
diff = set(repositories_sorted).symmetric_difference(set(packages_sorted))
missing = list(diff)
print(missing)



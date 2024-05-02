import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

plt.rcParams["font.size"] = '11'
plt.rcParams["figure.figsize"] = (4.5,2)
plt.rcParams["legend.fontsize"] = '11'

plt.rcParams.update({'text.usetex' : True,
                     'pgf.rcfonts': False,
                     'text.latex.preamble':
                         r"""
                            \usepackage{iftex}
                            \ifxetex
                                \usepackage[libertine]{newtxmath}
                                \usepackage[tt=false]{libertine}
                                \setmonofont[StylisticSet=3]{inconsolata}
                            \else
                                \RequirePackage[tt=false, type1=true]{libertine}
                            \fi""",
                     'ytick.labelsize' : 'xx-small',
                     'xtick.labelsize' : 'xx-small'
                    })

plt.rcParams["ytick.labelsize"] = '14'
plt.rcParams["xtick.labelsize"] = '14'

HATCHES = ['//', 'oo', '++', 'xx', '|||', '--']
COLORS = ['#d73027', '#fc8d59', '#fee090', '#018571', '#af8dc3', '#4575b4']



WEB_ROOTS = ['requests', 'django', 'flask', 'fastapi', 'responses', 'beautifulsoup','cherrypy', 'werkzeug', 'network', 'fastapi', 'http', 'url', 'form', 'login', 'oauth', 'jwt']
DB_ROOTS = ['mongo', 'sqlalchemy', 'mysql', 'postgres', 'redis', 'etcd', 'db', 'sqlite', 'pg', 'elasticsearch']
DM_ROOTS = ['numpy', 'pandas', 'cudf', 'pyspark', 'spark', 'dask', 'arrow', 'duckdb', 'scipy', 'memcached', 'xml',
            'pydantic', 'modin', 'polars', 'dplyr','clickhouse', 'datatable', 'h5py', 'protobuf', 'marshmallow', 'pickle']
ML_ROOTS = ['nltk', 'onnx', 'scikit_learn', "xgboost", "lightgbm", "torch", "torchvision", "torchaudio",
            "tensorflow", "tensorboard", "keras", 'theano', 'transformers', 'openai']
VISUAL_ROOTS = ['matplotlib', 'seaborn', 'image', 'plotly', 'colorama', 'click', 'ggplot', 'skimage', 'pillow', 'color', 'tesseract', 'opengl', 'pyqt', 'cuda', 'opencl']
CLOUD_ROOTS = ['boto', 'odbc', 'google', 'azure', 'cloud', 'aws']
SETUP_ROOTS = ['cache',  'setuptools', 'pytest', 'tqdm', 'pyyaml', 'psutil', 'date', 'pytz'
               'dotenv', 'click', 'selenium', 'pip', 'cython', 'config', 'json', 'stream', 'ssl', 'ssh', 'qr', 'regex']

def count_group(group_root, file_root):
    occurrences = pd.read_csv(file_root)
    counts = {}
    libraries = occurrences["library"].to_list()
    for root in group_root:
        count=0
        for lib in libraries:
            if root.lower() in lib.lower():
                # print(f"{root} found in {lib}.")
                # print(f"{lib} has count of {occurrences.loc[occurrences['library'] == lib, 'count'].values[0]}")
                count = count + occurrences.loc[occurrences["library"] == lib, "count"].values[0]
        print(f"{root} has count of {count}.")
        counts[root] = count
    print(counts)
    return counts

def generate_db_counts(file_root):
    counts_db = count_group(DB_ROOTS, file_root)
    counts_db['postgres'] = counts_db['pg'] + counts_db['postgres']
    counts_db_agg = counts_db
    del counts_db_agg['pg']
    print(counts_db_agg)
    return counts_db_agg

def get_df_percentile(topx, file_root):
    occurrences = pd.read_csv(file_root)
    total = occurrences['count'].sum()
    print(f"Total imports: {total}")

    subset = occurrences.iloc[:topx][:]
    subset_imports = subset["count"].sum()

    print(f"Subset imports: {subset_imports}")

    print(f"Coverage: {subset_imports/total*100:.2f}%")
    return subset

def shorten_yaxis(value, pos):
    thousands = value / 1e3
    return f'{thousands:.1f}k'

def plot_bar_chart(in_dict, ylabel, fig_name):
    plt.subplots(layout="constrained")
    percentages = ["{:.2f}\%".format(x/sum(in_dict.values())*100) for x in in_dict.values()]
    bars = plt.bar(x = in_dict.keys(), height = in_dict.values(), width = 0.4, align = 'center',
            fill=False, edgecolor=COLORS, label=in_dict.keys(), hatch=HATCHES)
    plt.ylabel(ylabel)
    plt.legend(loc='upper right', ncols=len(in_dict.keys())/3, handletextpad=0.5, columnspacing=0.5, handlelength=1, borderpad=0.3, labelspacing=0)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(shorten_yaxis))
    plt.ylim(0, max(in_dict.values()) + 0.2*(max(in_dict.values())))
    plt.tick_params(axis='both', which='major', labelsize=11)
    plt.bar_label(bars, labels=percentages, padding=2)


    plt.savefig(f"../plots/{fig_name}.svg", transparent=True)


def merge_counts():
    occ434 = pd.read_csv("../../../analysis_results/yearly_splits/occurrences-434k.csv")
    occ20 = pd.read_csv("../../../analysis_results/yearly_splits/occurrences-20k.csv")

    new = occ434.merge(occ20, how='outer', on=['library'])
    new['count_x'].fillna(0, inplace=True)
    new['count_y'].fillna(0, inplace=True)
    new['count'] = new['count_x'] + new['count_y']

    new.drop(columns=['Unnamed: 0_x', 'Unnamed: 0_y', 'count_x', 'count_y'], inplace=True)
    print(new.head())
    print(len(new))
    new.to_csv("../../analysis_results/yearly_splits/occurrences_aggregated.csv", index=False)

if __name__ == '__main__':

    db_counts = generate_db_counts(file_root="../raw-data/occurrences_aggregated.csv")

    perc95 = get_df_percentile(30, "../raw-data/occurrences_aggregated.csv")

    subset_keys = ['mongo','sqlalchemy', 'mysql', 'postgres',  'redis', 'elasticsearch']

    subset_dict = {key: db_counts[key] for key in subset_keys if key in db_counts}

    plot_bar_chart(in_dict=subset_dict, ylabel="\# of Imports", fig_name="db_sys_dist")


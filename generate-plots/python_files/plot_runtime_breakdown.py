import matplotlib.pyplot as plt
import numpy as np

from matplotlib.ticker import FuncFormatter, LogLocator


# colors = [‘#BAE4BC’, ‘#7BCCC4’, ‘#43A2CA’, ‘#0868AC’]

# plt.rcParams["axes.prop_cycle"] = plt.cycler('color', ['#d7191c', '#fdae61', '#018571', '#abd9e9', '#2c7bb6'])



def custom_scale(value, pos):
    # Adjust these values to control the unevenness of the scale
    if value < 10:
        return value**10
    else:
        return value


plt.rcParams["font.size"] = '11'
plt.rcParams["figure.figsize"] = (5,2)
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
                     'ytick.labelsize' : 'xx-small'
                    })

plt.rcParams.update({
        'font.size': 11,
        'svg.fonttype': 'none',
    })

plt.rcParams["ytick.labelsize"] = '10'
plt.rcParams["xtick.labelsize"] = '10'

read_types = ("string path", "variable path", "external path")

pipeline_dists = {'dbms-1000': {'translation_time': 2.485255, 'schema_gen': 5.194627, 'table_insertion': 412175.389484},
                  'dbms-100': {'translation_time': 3.328946, 'schema_gen': 5.369288, 'table_insertion': 41095.120895},
                  'dbms-10': {'translation_time': 1.994515, 'schema_gen': 7.827708, 'table_insertion': 4106.353397},


                  's3-10':  {'translation_time': 2.859814, 'schema_gen': 403.693394, 'table_insertion': 8291.398719},
                  's3-1000':  {'translation_time': 9.593349, 'schema_gen': 376.316705, 'table_insertion':  758066.7316},
                  's3-100': {'translation_time': 4.122656, 'schema_gen': 443.112031, 'table_insertion': 77426.244862},


                  'lfs-10':{'translation_time': 1.847849, 'schema_gen': 0, 'table_insertion': 24.362831},
                  'lfs-100': {'translation_time': 3.657666, 'schema_gen': 0, 'table_insertion':  500.574081},
                  'lfs-1000': {'translation_time': 3.903186, 'schema_gen': 0, 'table_insertion': 3454.95699}
                  }




HATCHES = ['//', 'oo', '++', 'xx', '|||', '--']
COLORS = ['#018571', '#af8dc3', '#4575b4', '#d73027', '#fc8d59', '#fee090']

years = list(pipeline_dists.keys())
categories = list(pipeline_dists['s3-10'].keys())

bar_width = 0.45
bar_positions = np.arange(len(years))

fig, ax = plt.subplots(layout='constrained')

bottom = np.zeros(len(years))
width = 0.45  # the width of the bars
multiplier = 0

for i, category in enumerate(categories):
    offset = width * multiplier
    values = [pipeline_dists[year][category] for year in years]
    values = [x/1000 for x in values]
    ax.bar(bar_positions + offset, values, bar_width, label=category, edgecolor=COLORS[i % len(HATCHES)], fill=False, hatch=HATCHES[i % len(HATCHES)], bottom=bottom)
    bottom = bottom + values
    multiplier += 1



 # Log-like scaling
ax.get_yaxis().set_minor_formatter(FuncFormatter(custom_scale))
ax.set_yscale('log', base=10)
ax.set_ylabel('Time')
ax.set_xticks(bar_positions)
ax.set_xticklabels(years)
ax.legend(loc='upper left', ncols=1, handletextpad=0.5,
           columnspacing=0.5, handlelength=1, borderpad=0.3, labelspacing=0)

plt.show()
# fig.savefig("../../../analysis_results/plots/distributions/runtime-breakdown.svg", transparent=True)
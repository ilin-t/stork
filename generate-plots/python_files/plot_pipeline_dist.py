import os

import matplotlib.pyplot as plt
import numpy as np

from matplotlib.ticker import FuncFormatter

def shorten_yaxis(value, pos):
    thousands = value / 1e3
    return f'{thousands:.1f}k'


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

pipeline_dists = {'2018': {'Library': 12057, 'File Handler': 32340, 'Combined': 1851},
                  '2019': {'Library': 14083, 'File Handler': 35291, 'Combined': 2325},
                  '2020': {'Library': 16330, 'File Handler': 35042, 'Combined': 2564},
                  '2021': {'Library': 32100, 'File Handler': 70633, 'Combined': 5439},
                  '2022': {'Library': 30006, 'File Handler': 63362, 'Combined': 6208},
                  '2023': {'Library': 25246, 'File Handler': 77179, 'Combined': 4889}
                  }

HATCHES = ['//', 'oo', '++', 'xx', '|||', '--']
COLORS = ['#018571', '#af8dc3', '#4575b4', '#d73027', '#fc8d59', '#fee090']

years = list(pipeline_dists.keys())
categories = list(pipeline_dists['2018'].keys())

bar_width = 0.45
bar_positions = np.arange(len(years))

fig, ax = plt.subplots(layout='constrained')

bottom = np.zeros(len(years))

for i, category in enumerate(categories):
    values = [pipeline_dists[year][category] for year in years]
    ax.bar(bar_positions, values, bar_width, label=category, edgecolor=COLORS[i % len(HATCHES)], fill=False, hatch=HATCHES[i % len(HATCHES)], bottom=bottom)
    bottom += values

ax.set_ylabel('\# Pipelines')
ax.yaxis.set_major_formatter(FuncFormatter(shorten_yaxis))
ax.set_xticks(bar_positions)
ax.set_xticklabels(years)
ax.legend(loc='upper left', ncols=1, handletextpad=0.5,
           columnspacing=0.5, handlelength=1, borderpad=0.3, labelspacing=0)

# plt.show()
fig.savefig("../plots/pipeline_distribution.svg", transparent=True)
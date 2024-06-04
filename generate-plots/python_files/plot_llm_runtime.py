import os

import matplotlib.pyplot as plt
import numpy as np


plt.rcParams["axes.prop_cycle"] = plt.cycler('color', ['#d7191c', '#fdae61', '#018571', '#abd9e9', '#2c7bb6'])


plt.rcParams["font.size"] = '22'
plt.rcParams["figure.figsize"] = (8,3)
plt.rcParams["legend.fontsize"] = '22'
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
                     # 'ytick.labelsize' : 'xx-small'
                    })

plt.rcParams["ytick.labelsize"] = '22'
plt.rcParams["xtick.labelsize"] = '22'

read_types = ("string path", "variable path", "external path")
outputs = {
    'LLaMa3-8B': (3870.12688048, 7609.39898471429, 9026.344949),
    'GPT-3.5-Turbo': (924.6881815, 1503.958855, 2271.0174975),
    'Stork': (11.31526452, 19.21832142857143, 15.6969292)
    # 'Other': (6, 2, 1),
    # 'OOM': (0, 11, 4)
}

x = np.arange(3)  # the label locations
width = 0.18  # the width of the bars
multiplier = 0

fig, ax = plt.subplots(layout='constrained')
hatches = ['/', 'o', '+', 'x', '|']
COLORS = ['#018571', '#af8dc3', '#4575b4', '#d73027', '#fc8d59', '#fee090']

for attribute, measurement in outputs.items():
    offset = width * multiplier
    print(measurement)
    rects = ax.bar(x + offset, measurement, width, fill=False, edgecolor=COLORS[multiplier], label=attribute, hatch=hatches[multiplier])
    # pcts = [int(pct) for pct in measurement]
    # pcts[0] = "{:.1f}".format(pcts[0]/25*100)
    # pcts[1] = "{:.1f}".format(pcts[1]/25*100)
    # pcts[2] = "{:.1f}".format(pcts[2]/14*100)
    # ax.bar_label(rects, labels=pcts, padding=2)
    multiplier += 1

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Translation Time (ms)')

ax.set_xticks(x + width, read_types)
ax.legend(loc='upper left', ncols=3, handletextpad=0.5, columnspacing=0.5, handlelength=1, borderpad=0.3, labelspacing=0)
ax.set_yscale('log')
ax.set_ylim(1, 1000000)
ax.tick_params(axis='both', which='major', labelsize=22)


# plt.show()
fig.savefig("../plots/llm_runtime.svg", transparent=True, bbox_inches='tight')
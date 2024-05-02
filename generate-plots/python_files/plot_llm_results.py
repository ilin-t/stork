import os

import matplotlib.pyplot as plt
import numpy as np


plt.rcParams["axes.prop_cycle"] = plt.cycler('color', ['#d7191c', '#fdae61', '#018571', '#abd9e9', '#2c7bb6'])


plt.rcParams["font.size"] = '18'
plt.rcParams["figure.figsize"] = (8,3)
plt.rcParams["legend.fontsize"] = '18'
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

plt.rcParams["ytick.labelsize"] = '18'
plt.rcParams["xtick.labelsize"] = '18'

read_types = ("string path", "variable path", "external path")
outputs = {
    'Code Snippet': (8, 6, 4),
    'Invalid Data': (9, 6, 4),
    'Data Path': (2, 0, 1),
    'Other': (6, 2, 1),
    'OOM': (0, 11, 4)
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
    rects = ax.bar(x + offset, measurement, width, fill=False, edgecolor=colors[multiplier], label=attribute, hatch=hatches[multiplier])
    pcts = [int(pct) for pct in measurement]
    pcts[0] = "{:.1f}".format(pcts[0]/25*100)
    pcts[1] = "{:.1f}".format(pcts[1]/25*100)
    pcts[2] = "{:.1f}".format(pcts[2]/14*100)
    ax.bar_label(rects, labels=pcts, padding=2)
    multiplier += 1

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('\# Pipelines')

ax.set_xticks(x + width, read_types)
ax.legend(loc='upper left', ncols=3, handletextpad=0.5, columnspacing=0.5, handlelength=1, borderpad=0.3, labelspacing=0)
ax.set_ylim(0, 18)
ax.tick_params(axis='both', which='major', labelsize=18)


# plt.show()
fig.savefig("../plots/llm_results.svg", transparent=True)
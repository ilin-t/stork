import matplotlib.pyplot as plt
import numpy as np

# plt.rcParams["axes.prop_cycle"] = plt.cycler('color',
#                                              ['#66c2a5', '#8da0cb', '#fc8d62', '#e78ac3',
#                                               '#a6d854', '#ffd92f', '#e5c494', '#b3b3b3'])
# plt.rcParams["axes.prop_cycle"] = plt.cycler('color',
#                                              ['#3E89D6', '#E1A03C', '#9DA9C0', '#72DF96',
#                                               '#596366', '#ffd92f', '#e5c494', '#b3b3b3'])

# plt.rcParams["axes.prop_cycle"] = plt.cycler('color',
#                                              ['#029e73', '#d55e00', '#cc78bc', '#56b4e9', '#ca9161',
#                                               '#fbafe4', '#949494', '#ece133', '#56b4e9', '#0173b2', '#de8f05',])

plt.rcParams["axes.prop_cycle"] = plt.cycler('color', ['#d7191c', '#fdae61', '#018571', '#abd9e9', '#2c7bb6'])


plt.rcParams["font.size"] = '16'
plt.rcParams["figure.figsize"] = (11,4)
plt.rcParams["legend.fontsize"] = '16'
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

read_types = ("string path", "variable path", "external path")
outputs = {
    'Code Snippet': (8, 6, 4),
    'Invalid Data': (9, 6, 4),
    'Data Path': (2, 0, 1),
    'Other': (6, 2, 1),
    'OOM': (0, 11, 4)
}

x = np.arange(3)  # the label locations
width = 0.16  # the width of the bars
multiplier = 0

fig, ax = plt.subplots(layout='constrained')
hatches = ['//', 'oo', '++', 'xx', '|||']
colors = ['#d7191c', '#fdae61', '#018571', '#abd9e9', '#2c7bb6']

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
ax.set_title('LLM outputs by read type')
ax.set_xticks(x + width, read_types)
ax.legend(loc='upper left', ncols=5)
ax.set_ylim(0, 14)
ax.tick_params(axis='both', which='major', labelsize=16)


# plt.show()
fig.savefig("../../analysis_results/plots/evaluation/llm_results.svg", transparent=True)
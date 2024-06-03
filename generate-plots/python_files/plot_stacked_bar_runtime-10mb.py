import matplotlib.pyplot as plt
import numpy as np

from matplotlib.ticker import FuncFormatter

plt.rcParams["font.size"] = '18'
plt.rcParams["figure.figsize"] = (3, 2)
plt.rcParams["legend.fontsize"] = '12'
plt.rcParams.update({'text.usetex': True,
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
                     })

plt.rcParams.update({
    'font.size': 18,
    'svg.fonttype': 'none',
})

plt.rcParams["ytick.labelsize"] = '18'
plt.rcParams["xtick.labelsize"] = '18'

HATCHES = ['//', 'oo', '++']
COLORS = ['#018571', '#af8dc3', '#4575b4', '#d73027', '#fc8d59', '#fee090']
# Create sample data
categories = ["Postgres", "S3", "LFS"]
translation_times = np.array([1.994515,  2.859814, 1.847849])
schema_gen = np.array([5.194627, 403.693394, 0])
data_transfer = np.array([4106.353397, 8291.398719, 24.362831])

# Plotting the stacked bar chart
fig, ax = plt.subplots(layout="constrained")

ax.bar(categories, translation_times, width = 0.5, fill = False, edgecolor = COLORS[0], hatch= HATCHES[0], label='translate')
ax.bar(categories, schema_gen, width = 0.5, bottom=translation_times, fill = False, edgecolor = COLORS[1], hatch= HATCHES[1], label='transform')
ax.bar(categories, data_transfer, width = 0.5, bottom=translation_times + schema_gen, fill = False, edgecolor = COLORS[2], hatch= HATCHES[2], label='transfer')

# Adding labels and title

ax.set_yscale('log', base=10)
ax.set_ylabel('Time (ms)')
ax.set_ylim(1, 10000001)
# ax.legend(loc= (0.59,0.60), ncols=1, handletextpad=0.3,
#           columnspacing=0.3, handlelength=1, borderpad=0.2, labelspacing=0)

fig.savefig("../plots/runtime-breakdown-10mb.svg", transparent=True, bbox_inches='tight')
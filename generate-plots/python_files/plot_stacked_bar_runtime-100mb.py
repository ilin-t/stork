import matplotlib.pyplot as plt
import numpy as np

from matplotlib.ticker import FuncFormatter

plt.rcParams["font.size"] = '18'
plt.rcParams["figure.figsize"] = (3, 2)
plt.rcParams["legend.fontsize"] = '17'
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
                     'ytick.labelsize': 'xx-small'
                     })

plt.rcParams.update({
    'font.size': 17,
    'svg.fonttype': 'none',
})

plt.rcParams["ytick.labelsize"] = '18'
plt.rcParams["xtick.labelsize"] = '18'

HATCHES = ['//', 'oo', '++']
COLORS = ['#018571', '#af8dc3', '#4575b4', '#d73027', '#fc8d59', '#fee090']
# Create sample data
categories = ["Postgres", "S3", "LFS"]
translation_times = np.array([3.332,  4.122, 3.65])
schema_gen = np.array([5.36,443.112, 0])
data_transfer = np.array([41095.12, 77426.26, 500.57])

# Plotting the stacked bar chart
fig, ax = plt.subplots(layout="constrained")

ax.bar(categories, translation_times, width = 0.5, fill = False, edgecolor = COLORS[0], hatch= HATCHES[0], label='translate')
ax.bar(categories, schema_gen, width = 0.5, bottom=translation_times, fill = False, edgecolor = COLORS[1], hatch= HATCHES[1], label='transform')
ax.bar(categories, data_transfer, width = 0.5, bottom=translation_times + schema_gen, fill = False, edgecolor = COLORS[2], hatch= HATCHES[2], label='transfer')

# Adding labels and title

ax.set_yscale('log', base=10)
ax.set_ylim(1, 10000001)
# ax.set_yticks([])
# ax.legend(loc= (0.61,0.61), ncols=1, handletextpad=0.3,
#           columnspacing=0.3, handlelength=1, borderpad=0.2, labelspacing=0)

fig.savefig("../plots/runtime-breakdown-100mb.svg", transparent=True)
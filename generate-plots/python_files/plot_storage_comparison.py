import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

plt.rcParams["font.size"] = '11'
plt.rcParams["figure.figsize"] = (5, 2)
plt.rcParams["legend.fontsize"] = '11'
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
    'font.size': 11,
    'svg.fonttype': 'none',
})

plt.rcParams["ytick.labelsize"] = '10'
plt.rcParams["xtick.labelsize"] = '10'

HATCHES = ['//', 'oo', '++']
COLORS = ['#018571', '#af8dc3', '#4575b4', '#d73027', '#fc8d59', '#fee090']

def custom_scale(value, pos):
    # Adjust these values to control the unevenness of the scale
    if value < 10:
        return value ** 10
    else:
        return value


data_sizes = ("10MB", "100MB", "1000MB")
runtimes = {
    'DBMS': [(1.994515, 7.827708, 4106), (3.328946, 5.369288, 41095.120895), (2.485255, 5.194627, 412175.389484)],
    'S3': [(2.859814, 403.693394, 8291.398719), (4.122656, 443.112031, 77426.244862), (9.593349, 376.316705, 758066.7316)],
    'LFS': [(1.847849, 0, 24.362831), (3.657666, 0, 500.574081), (3.903186, 0, 3454.95699)],
}

x = np.arange(len(data_sizes))  # the label locations
width = 0.5  # the width of the bars

fig, ax = plt.subplots(layout='constrained')

for i, (attribute, components) in enumerate(runtimes.items()):
    components = (np.array(components)/1000).T  # Transpose to have each species's components in a column
    bottom = np.zeros(len(data_sizes))  # Initialize the bottom for each component
    for j, part in enumerate(components):
        ax.bar(x + i * width / len(runtimes), part, width / len(runtimes), edgecolor=COLORS[j], hatch = HATCHES[j], fill=False, bottom=bottom)
        bottom += part  # Update the bottom for the next component

# Add some text for labels, title, and custom x-axis tick labels, etc.
ax.set_ylabel('Length (mm)')
ax.set_xticks(x + width / 2)
ax.set_xticklabels(data_sizes)
ax.legend(loc='upper left', bbox_to_anchor=(1, 1))

ax.get_yaxis().set_minor_formatter(FuncFormatter(custom_scale))
ax.set_yscale('log', base=10)
ax.set_ylabel('Time(s)')
ax.legend(loc='upper left', ncols=1, handletextpad=0.5,
          labels=["translation", "schema_generation", "data_transfer"],
          columnspacing=0.5, handlelength=1, borderpad=0.3, labelspacing=0)

fig.savefig("../../../analysis_results/plots/evaluation/runtime-breakdown.svg", transparent=True)
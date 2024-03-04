import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams["font.size"] = '14'
plt.rcParams["figure.figsize"] = (5,2.5)
plt.rcParams["legend.fontsize"] = '14'

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

df = pd.read_csv("../../../analysis_results/yearly_splits/occurrences_aggregated.csv")
data = df["count"].to_numpy()
# Generate example data with a long-tail distribution
# data = np.random.pareto(2, 1000) + 1

# Sort the data
sorted_data = data

# Calculate cumulative percentages
cumulative_percentages = np.cumsum(sorted_data) / np.sum(sorted_data)

# Find the index where cumulative percentage exceeds 90%

index_30_percent = np.argmax(cumulative_percentages >= 0.3) + 1  # Add 1 to include the 30th element
index_50_percent = np.argmax(cumulative_percentages >= 0.5) + 1  # Add 1 to include the 30th element
index_90_percent = np.argmax(cumulative_percentages >= 0.9) + 1  # Add 1 to include the 30th element
index_99_percent = np.argmax(cumulative_percentages >= 0.999) + 1  # Add 1 to include the 30th element

# Plot the cumulative distribution with log-scaled x-axis
plt.figure()
plt.plot(range(1, len(sorted_data) + 1), cumulative_percentages, marker='o', markersize=4, linestyle='-', color='steelblue', label='Cum. Dist.')
plt.fill_between(range(1, len(sorted_data) + 1), 0, cumulative_percentages, color='lightsteelblue', alpha=0.5)

# Highlight the first 30 elements
plt.axvline(x=index_30_percent,color=COLORS[4], linestyle='solid', label=f'30\% ({index_30_percent:,} libs.)')
plt.axvline(x=index_50_percent,color=COLORS[4], linestyle='--', label=f'50\% ({index_50_percent:,} libs.)')
plt.axvline(x=index_90_percent,color=COLORS[4], linestyle='-.', label=f'90\% ({index_90_percent:,} libs.)')
plt.axvline(x=index_99_percent,color=COLORS[4], linestyle=':', label=f'99\% ({index_99_percent:,} libs.)')

# Set x-axis to log scale
plt.xscale('log')

# Style adjustments
plt.ylabel('Cumulative Percentage', fontsize=14)
plt.legend(loc='lower right', handletextpad=0.5, columnspacing=0.5, handlelength=1, borderpad=0.3, labelspacing=0)

plt.savefig(f"../../../analysis_results/plots/distributions/cum_library.svg", transparent=True, bbox_inches='tight')
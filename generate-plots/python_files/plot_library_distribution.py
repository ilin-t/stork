import os

import matplotlib.pyplot as plt
import numpy as np

from matplotlib.patches import ConnectionPatch

plt.rcParams["font.size"] = '11'
plt.rcParams["figure.figsize"] = (5.5,2.5)
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
plt.rcParams["ytick.labelsize"] = '10'
plt.rcParams["xtick.labelsize"] = '10'

HATCHES = ['//', 'oo', '++', 'xx', '|||', '--']
COLORS = ['#2166ac', '#fc8d59', '#fee090', '#018571', '#af8dc3', '#4575b4']

lib = {'DBMS': 50040, 'WEB': 288476.0, 'ML': 173360.0, 'BD': 269071.0, 'VISUAL': 217578.0, 'CLOUD': 22370.0,
       'SETUP': 232771.0, 'OTHER': 552735.0}

# make figure and assign axis objects
fig, (ax1, ax2) = plt.subplots(1, 2)
fig.subplots_adjust(wspace=0)

# pie chart parameters
overall_ratios = [514841, 288476, 217578, 232771, 552735]
labels = ['DM', 'Web', 'Visual', 'Setup', 'Other']
explode = [0.1, 0, 0, 0, 0]
# rotate so that first wedge is split by the x-axis
angle = -45 * overall_ratios[0]
wedges, *_ = ax1.pie(overall_ratios, autopct='%1.1f%%', startangle=angle,
                     labels=labels, explode=explode, colors=COLORS)


dm_libaries = {'Cloud': 22370, 'DBMS': 50040, 'ML \& DL': 173360, 'Big Data': 269071}

bottom = 1
width = 2

# Adding from the top matches the legend.
for x in dm_libaries.keys():
    bottom -= dm_libaries[x]
    bc = ax2.bar(0, dm_libaries[x], width, bottom=bottom, color='C0', label=x,
                 alpha=0.25 + 0.25 * list(dm_libaries.keys()).index(x))
    ax2.bar_label(bc, labels=[f"{dm_libaries[x]/514841*100:.1f}\%"], label_type='center')

# ax2.set_title('DM Distribution')
ax2.legend()
ax2.axis('off')
ax2.set_xlim(- 1 * width, 2.5 * width)

# use ConnectionPatch to draw lines between the two plots
theta1, theta2 = wedges[0].theta1, wedges[0].theta2
center, r = wedges[0].center, wedges[0].r
bar_height = -514841

# draw top connecting line
x = r * np.cos(np.pi / 180 * theta2) + center[0]
y = r * np.sin(np.pi / 180 * theta2) + center[1]
con = ConnectionPatch(xyA=(-width / 2, 1), coordsA=ax2.transData,
                      xyB=(x, y), coordsB=ax1.transData)
con.set_color([0, 0, 0])
con.set_linewidth(2)
ax2.add_artist(con)

# draw bottom connecting line
x = r * np.cos(np.pi / 180 * theta1) + center[0]
y = r * np.sin(np.pi / 180 * theta1) + center[1]
con = ConnectionPatch(xyA=(-width / 2, -514841), coordsA=ax2.transData,
                      xyB=(x, y), coordsB=ax1.transData)
con.set_color([0, 0, 0])
ax2.add_artist(con)
con.set_linewidth(2)

plt.savefig("../plots/library_distribution.svg", transparent=True, bbox_inches='tight')
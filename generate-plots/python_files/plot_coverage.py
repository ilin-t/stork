import os

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["axes.prop_cycle"] = plt.cycler('color', ['#d7191c', '#2c7bb6', '#abd9e9', '#fdae61', '#018571'])


plt.rcParams["font.size"] = '16'
plt.rcParams["figure.figsize"] = (6,4)
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


def plot_coverage(values, labels, output_file):
    explode = (np.zeros(len(values)))
    explode[:] = 0.1
    fig, ax = plt.subplots()
    ax.pie(x=values, startangle=100, explode=explode, shadow=True, autopct='%1.1f%%')
    ax.legend(labels=labels, loc=[0.75, 0], handletextpad=0.5, columnspacing=0.5, handlelength=1, borderpad=0.3, labelspacing=0)
    fig.tight_layout()
    fig.savefig(output_file, transparent=True)

def coverage_plots():
    plot_coverage(values=[56444 - 40431, 40431], labels=['Translated', 'Skipped'],
                  output_file="../plots/pipeline_coverage.svg")

    plot_coverage(values=[14498, 72663 - 14498], labels=['Accessible', 'No Data Access'],
                  output_file="../plots/dataset_availability.svg")

    plot_coverage(values=[56444, 152554 - 56444], labels=['Executable', 'Non-Executable'],
                  output_file="../plots/executable_pipelines.svg")

    plot_coverage(values=[54757, 494586 - 166631 - 54757, 166631],
                  labels=['Reading Local Data', 'Processing Data','No Data Access'],
                  output_file="../plots/repository_landscape.svg")

def plot_landscape():
    lib = {'DBMS': 50040, 'WEB': 288476.0, 'ML': 173360.0, 'DM': 269071.0, 'VISUAL': 217578.0, 'CLOUD': 22370.0,
     'SETUP': 232771.0, 'OTHER': 552735.0}

    plot_coverage(values=list(lib.values()), labels=lib.keys(), output_file="../plots/library_coverage.svg")

def main():
    coverage_plots()
    plot_landscape()



if __name__ == "__main__":
    main()

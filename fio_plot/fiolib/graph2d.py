#!/usr/bin/env python3
import matplotlib.pyplot as plt
import matplotlib.markers as markers
from matplotlib.font_manager import FontProperties
from matplotlib import rcParams, cycler
import numpy as np
import pprint as pprint
import fiolib.supporting as supporting
from datetime import datetime


def make_patch_spines_invisible(ax):
    ax.set_frame_on(True)
    ax.patch.set_visible(False)
    for sp in ax.spines.values():
        sp.set_visible(False)


def create_title_and_sub(config, plt):
    plt.suptitle(config['title'])
    if config['subtitle']:
        plt.title(config['subtitle'],
                  fontsize=8, horizontalalignment='center', y=1.02)
    else:
        plt.title(config['rw'] + " | iodepth " +
                  str(config['iodepth']).strip('[]') + " | numjobs " +
                  str(config['numjobs']).strip('[]') +
                  " | " + str(config['type']).strip('[]').replace('\'', ''),
                  fontsize=8, horizontalalignment='center', y=1.02)


def chart_2d_log_data(config, dataset):

    # datatypes = list(set([x['type'] for x in data]))

    data = supporting.process_dataset(dataset)
    datatypes = data['datatypes']

    fig, host = plt.subplots()
    fig.set_size_inches(9, 5)

    axes = supporting.generate_axes(host, datatypes)
    create_title_and_sub(config, plt)

    if 'bw' in datatypes and (len(datatypes) > 2):
        fig.subplots_adjust(left=0.21)
        fig.subplots_adjust(bottom=0.22)
    else:
        fig.subplots_adjust()
        fig.subplots_adjust(bottom=0.22)

    lines = []
    labels = []
    colors = supporting.get_colors()

    marker_list = list(markers.MarkerStyle.markers.keys())

    fontP = FontProperties(family='monospace')
    fontP.set_size('xx-small')

    for item in data['dataset']:

        if config['enable_markers']:
            marker_value = marker_list.pop(0)
        else:
            marker_value = None

        xvalues = item['xvalues']
        yvalues = item['yvalues']

        # PLOT
        dataplot = f"{item['type']}_plot"
        axes[dataplot] = axes[item['type']].plot(xvalues, yvalues, marker=marker_value, markevery=(len(
            yvalues) / (len(yvalues) * 10)), color=colors.pop(0), label=item['ylabel'])[0]
        # pprint.pprint(axes[dataplot])
        axes[item['type']].set_ylim([0, item['maximum']])
        host.set_xlabel(item['xlabel'])

        # Label Axis
        pprint.pprint(axes[f"{item['type']}_pos"])
        padding = axes[f"{item['type']}_pos"]
        axes[item['type']].set_ylabel(
            item['ylabel'],
            labelpad=padding)

        # Create legend
        lines.append(axes[dataplot])
        mean = np.mean(yvalues)
        stdv = (np.std(yvalues) / mean) * 100
        labels.append(
            f"{item['ylabel']} qd: {item['iodepth']:>2} nj: {item['numjobs']:>2} MEAN: {round(mean,3):>6} $\sigma$: {round(stdv, 2):>6}%")
    pprint.pprint(axes)
    host.legend(lines, labels, prop=fontP,
                bbox_to_anchor=(0.5, -0.33), loc='lower center', ncol=2)

    now = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    fig.savefig(f"{now}.png", dpi=config['dpi'])

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


def chart_2d_log_data(config, data):

    datatypes = list(set([x['type'] for x in data]))

    fig, host = plt.subplots()
    fig.set_size_inches(9, 5)

    if 'bw' in datatypes:
        fig.subplots_adjust(left=0.21)
        fig.subplots_adjust(bottom=0.22)
    else:
        fig.subplots_adjust()
        fig.subplots_adjust(bottom=0.22)

    create_title_and_sub(config, plt)

    cmap = plt.cm.jet
    rcParams['axes.prop_cycle'] = cycler(
        color=cmap(np.linspace(0, 1, len(data))))

    axes = supporting.generate_axes(host, datatypes)
    lines = []
    labels = []
    colors = supporting.get_colors()
    counter = 1
    table_cols = datatypes
    table_rows = []

    marker_list = list(markers.MarkerStyle.markers.keys())

    for item in data:

        datalabel = f"{item['type']}_label"
        axes[datalabel] = (supporting.lookupTable(item['type'])[0])

        datakey = f"{item['type']}_data"
        axes[datakey] = list(zip(*item['data']))

        dataplot = f"{item['type']}_plot"
        unpacked = list(zip(*item['data']))
        xvalues = unpacked[0]
        yvalues = unpacked[1]

        scaled_xaxis = supporting.scale_xaxis_time(xvalues)
        x_label = scaled_xaxis['format']
        xvalues = scaled_xaxis['data']

        if 'lat' in item['type']:
            scaled_data = supporting.scale_yaxis_latency(yvalues)
            axes[datalabel]['ylabel'] = scaled_data['format']
            yvalues = scaled_data['data']

        if config['enable_markers']:
            marker_value = marker_list.pop(0)
        else:
            marker_value = None

        # Determine max / min values to scale graph axis
        if item['type'] == 'bw':
            maximum = max(yvalues) * 1.2
        else:
            maximum = max(yvalues) * 1.3

        # PLOT
        axes[dataplot] = axes[item['type']].plot(
            xvalues, yvalues, marker=marker_value,
            markevery=(len(yvalues) / (len(yvalues) * 10)),
            color=colors.pop(0), label=axes[datalabel]['ylabel'])[0]
        # pprint.pprint(axes[dataplot])
        axes[item['type']].set_ylim([0, maximum])
        host.set_xlabel(x_label)

        # Label Axis
        # if counter % 3 == 0:
        position = supporting.get_label_position(axes[f"{item['type']}_pos"])
        axes[item['type']].set_ylabel(
            axes[datalabel]['ylabel'],
            rotation=axes[datalabel]['label_rot'],
            labelpad=position)

        # add data to table
        # table_rows.append([])

        # Create legend
        fontP = FontProperties(family='monospace')
        fontP.set_size('xx-small')
        lines.append(axes[dataplot])
        labels.append(
            f"{axes[datalabel]['ylabel']} qd: {item['iodepth']:>2} nj: {item['numjobs']:>2} MEAN: {int(round(np.mean(yvalues))):>6} STDV: {round(np.std(yvalues), 2):>6}")
        counter += 1

    host.legend(lines, labels, prop=fontP,
                bbox_to_anchor=(0.5, -0.33), loc='lower center', ncol=2)
    # Add grid (or not)
    if not config['disable_grid']:
        axes[item['type']].grid(ls='dotted')

    now = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    fig.savefig(f"{now}.png", dpi=config['dpi'])

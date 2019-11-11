#!/usr/bin/env python3
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib import rcParams, cycler
import numpy as np
import pprint as pprint
import fiolib.supporting as supporting


def make_patch_spines_invisible(ax):
    ax.set_frame_on(True)
    ax.patch.set_visible(False)
    for sp in ax.spines.values():
        sp.set_visible(False)


def chart_2d_log_data(config, data):

    datatypes = list(set([x['type'] for x in data]))

    fig, host = plt.subplots()
    if 'bw' in datatypes:
        fig.subplots_adjust(left=0.21)
        fig.subplots_adjust(bottom=0.22)
    else:
        fig.subplots_adjust()
        fig.subplots_adjust(bottom=0.22)

    fig.set_size_inches(9, 5)

    plt.suptitle(config['title'] + " | " + config['rw'] + " | iodepth " +
                 str(config['iodepth']) + " | numjobs " +
                 str(config['numjobs']) + " | " + str(config['type']),
                 fontsize=12, horizontalalignment='center')

    cmap = plt.cm.jet
    rcParams['axes.prop_cycle'] = cycler(
        color=cmap(np.linspace(0, 1, len(data))))

    axes = supporting.generate_axes(host, datatypes)
    lines = []
    labels = []
    colors = supporting.get_colors()
    counter = 1

    for item in data:

        datalabel = f"{item['type']}_label"
        axes[datalabel] = (supporting.lookupTable(item['type'])[0])

        datakey = f"{item['type']}_data"
        axes[datakey] = list(zip(*item['data']))

        dataplot = f"{item['type']}_plot"
        unpacked = list(zip(*item['data']))
        xvalues = unpacked[0]
        yvalues = unpacked[1]

        # Determine max / min values to scale graph axis
        if item['type'] == 'bw':
            maximum = max(yvalues) * 1.2
        else:
            maximum = max(yvalues) * 1.3

        # PLOT
        axes[dataplot] = axes[item['type']].plot(
            xvalues, yvalues, colors.pop(0), label=axes[datalabel]['ylabel'])[0]
        pprint.pprint(axes[dataplot])
        axes[item['type']].set_ylim([0, maximum])
        host.set_xlabel('Time in miliseconds')

        # Label Axis
        # if counter % 3 == 0:
        position = supporting.get_label_position(axes[f"{item['type']}_pos"])
        axes[item['type']].set_ylabel(
            axes[datalabel]['ylabel'],
            rotation=axes[datalabel]['label_rot'],
            labelpad=position)

        # Create legend
        fontP = FontProperties(family='monospace')
        fontP.set_size('xx-small')
        lines.append(axes[dataplot])
        labels.append(
            f"{axes[datalabel]['ylabel']} qd: {item['iodepth']:>2} nj: {item['numjobs']:>2} STDV: {round(np.std(yvalues), 2):>6}")
        counter += 1
        host.legend(lines, labels, prop=fontP,
                    bbox_to_anchor=(0.5, -0.25), loc='lower center', ncol=3)

    fig.savefig('test.png', dpi=200)
    # fig.tight_layout()
    # plt.show()

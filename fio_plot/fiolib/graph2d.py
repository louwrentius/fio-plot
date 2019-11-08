#!/usr/bin/env python3
import matplotlib.pyplot as plt
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

    fig, host = plt.subplots()
    fig.subplots_adjust(left=0.22)

    fig.set_size_inches(8, 5)

    plt.suptitle(config['title'] + " | " + config['rw'] + " | iodepth " +
                 str(config['iodepth']) + " | numjobs " +
                 str(config['numjobs']) + " | " + str(config['type']),
                 fontsize=12, horizontalalignment='center')

    cmap = plt.cm.jet
    rcParams['axes.prop_cycle'] = cycler(
        color=cmap(np.linspace(0, 1, len(data))))

    counter = 1
    axes = {}
    lines = []
    labels = []
    for item in data:
        if item['type'] not in axes.keys():
            if counter == 1:
                axes[item['type']] = host
            else:
                axes[item['type']] = host.twinx()

            if counter == 2:
                axes[item['type']].spines["right"].set_position(
                    ("axes", -0.28))

        if counter % 3 == 0:
            make_patch_spines_invisible(axes[item['type']])
            axes[item['type']].spines["right"].set_visible(True)

        datakey = f"{item['type']}_data"
        axes[datakey] = list(zip(*item['data']))
        datalabel = f"{item['type']}_label"
        axes[datalabel] = (supporting.lookupTable(item['type'])[0])

        #[pprint.pprint(x['type']) for x in data]

        dataplot = f"{item['type']}_plot"
        unpacked = list(zip(*item['data']))
        xvalues = unpacked[0]
        yvalues = unpacked[1]
        if item['type'] == 'bw':
            maximum = max(yvalues) * 1.2
        else:
            maximum = max(yvalues) * 1.3
        color = axes[datalabel]['color']
        axes[dataplot] = axes[item['type']].plot(
            xvalues, yvalues, label=axes[datalabel]['ylabel'])[0]
        pprint.pprint(axes[dataplot])
        axes[item['type']].set_ylim([0, maximum])
        host.set_xlabel('Time in miliseconds')

        if counter % 3 == 0:
            axes[item['type']].set_ylabel(
                axes[datalabel]['ylabel'], rotation='vertical', labelpad=-50)
        else:
            axes[item['type']].set_ylabel(axes[datalabel]['ylabel'])

        axes[item['type']].yaxis.label.set_color(axes[dataplot].get_color())

        tkw = dict(size=4, width=1.5)
        if counter == 0:
            host.tick_params(axis='x', **tkw)
        else:
            axes[item['type']].tick_params(
                axis='y', colors=axes[dataplot].get_color(), **tkw)

        lines.append(axes[dataplot])
        labels.append(
            f"{axes[datalabel]['ylabel']} qd: {item['iodepth']} numjobs: {item['numjobs']}")
        counter += 1
        host.legend(lines, labels)

    for item in data:

        print(f"Plotting data for {item['type']}")
        unpacked = list(zip(*item['data']))
        # minimum = min(unpacked[1])
        # pprint.pprint(minimum)
        # result = supporting.scaling(minimum)
        # scaled = [x / result['scale_factor'] for x in unpacked[1]]
        running = supporting.running_mean(
            unpacked[1], config['moving_average'])
        # maximum = max(scaled) * 1.3
        # axes[item['type']].plot(
        #    unpacked[0], running, label=f"{item['type']} \
        #        qd: {item['iodepth']} jobs: {item['numjobs']}")
        #
        # axes[item['type']].legend(loc=legend_position[axes[item['type']]])
        # axes[item['type']].set_ylim([0, maximum])
        # axes[item['type']].set_ylabel(axes_label[axes[item['type']]])
    # if config['max_y']:

    fig.savefig('test.png', dpi=200)
    # fig.tight_layout()
    # plt.show()

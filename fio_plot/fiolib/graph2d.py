#!/usr/bin/env python3
import matplotlib.pyplot as plt
from matplotlib import rcParams, cycler
import numpy as np
import pprint as pprint
import fiolib.supporting as supporting


def chart_2d_log_data(config, data):

    fig, ax1 = plt.subplots()
    fig.set_size_inches(8, 5)

    if config['source']:
        plt.text(1, -0.08, str(config['source']), ha='right', va='top',
                 transform=ax1.transAxes, fontsize=9)

    plt.suptitle(config['title'] + " | " + config['rw'] + " | iodepth " +
                 str(config['iodepth']) + " | numjobs " +
                 str(config['numjobs']) + " | " + str(config['type']),
                 fontsize=16, horizontalalignment='center')

    cmap = plt.cm.jet
    rcParams['axes.prop_cycle'] = cycler(
        color=cmap(np.linspace(0, 1, len(data))))

    # pprint.pprint(data)
    ax2 = ax1.twinx()
    colors = ['tab:red', 'tab:green', 'tab:blue',
              'tab:orange', 'tab:purple', 'r', 'g', 'b', 'c', 'm', 'g', 'b', 'c', 'm']

    axes = {'lat': ax2, 'iops': ax1, 'bw': ax1, 'slat': ax2, 'clat': ax2}
    legend_position = {ax1: 'upper left', ax2: 'upper right'}

    for item in data:

        print(item['type'])
        unpacked = list(zip(*item['data']))
        params = []

        running = supporting.running_mean(
            unpacked[1], config['moving_average'])
        maximum = max(unpacked[1]) * 1.25
        axes[item['type']].plot(
            unpacked[0], running, label=f"{item['type']} \
                qd: {item['iodepth']} jobs: {item['numjobs']}",
            color=colors.pop())
        axes[item['type']].legend(loc=legend_position[axes[item['type']]])
        axes[item['type']].set_ylim([0, maximum])

    # if config['max_y']:

    fig.savefig('test.png', dpi=200)
    # fig.tight_layout()
    # plt.show()

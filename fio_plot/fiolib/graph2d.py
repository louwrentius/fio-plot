import matplotlib.pyplot as plt
from matplotlib import rcParams, cycler
import numpy as np
import pprint as pprint


def chart_2d_log_data(config, data):

    fig, ax1 = plt.subplots()
    fig.set_size_inches(10, 6)

    if config['source']:
        plt.text(1, -0.08, str(config['source']), ha='right', va='top',
                 transform=ax1.transAxes, fontsize=9)

    plt.suptitle(config['title'] + " | " + config['rw'] + " | iodepth " +
                 str(config['iodepth']) + " | numjobs " +
                 str(config['numjobs']) + " | " + str(config['type']),
                 fontsize=16, horizontalalignment='center')

    cmap = plt.cm.tab20c
    rcParams['axes.prop_cycle'] = cycler(
        color=cmap(np.linspace(0, 1, len(data))))
    # pprint.pprint(data)

    unpacked = list(zip(*data))
    pprint.pprint(data)
    plt.plot(unpacked[0], unpacked[1])
    # if config['max_y']:

    # fig.savefig('test.png')
    plt.show()

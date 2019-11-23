#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import pprint
import fiolib.shared_chart as shared
from matplotlib import cm
from mpl_toolkits.mplot3d import axes3d
from datetime import datetime
import matplotlib as mpl


def plot_3d(settings, dataset):

    dataset_types = shared.get_dataset_types(dataset)
    # pprint.pprint(dataset_types)
    metric = settings['type'][0]
    rw = settings['rw']
    iodepth = dataset_types['iodepth']
    numjobs = dataset_types['numjobs']
    data = shared.get_record_set_3d(dataset, dataset_types,
                                    rw, metric)

    pprint.pprint(data)

    fig = plt.figure()
    ax1 = fig.add_subplot(111, projection='3d')
    fig.set_size_inches(15, 10)

    lx = len(dataset_types['iodepth'])
    ly = len(dataset_types['numjobs'])

    n = np.array(data['values'], dtype=float)

    size = lx * 0.05  # thickness of the bar
    xpos_orig = np.arange(0, lx, 1)
    ypos_orig = np.arange(0, ly, 1)

    xpos = np.arange(0, lx, 1)
    ypos = np.arange(0, ly, 1)
    xpos, ypos = np.meshgrid(xpos-(size/lx), ypos-(size))

    xpos_f = xpos.flatten()   # Convert positions to 1D array
    ypos_f = ypos.flatten()
    zpos = np.zeros(lx*ly)

    dx = size * np.ones_like(zpos)
    dy = dx.copy()
    dz = n.flatten()
    values = dz / (dz.max()/1)
    cmap = plt.get_cmap('rainbow', xpos.ravel().shape[0])
    colors = cm.rainbow(values)

    ax1.bar3d(xpos_f, ypos_f, zpos, dx, dy, dz, color=colors)
    norm = mpl.colors.Normalize(vmin=0, vmax=dz.max())
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    res = fig.colorbar(sm, fraction=0.046, pad=0.04)
    res.ax.set_title(metric)

    float_x = [float(x) for x in (xpos_orig)]
    # unused? float_y = [float(y) for y in (ypos_orig)]

    ax1.w_xaxis.set_ticks(float_x)
    ax1.w_yaxis.set_ticks(ypos_orig)

    ax1.w_xaxis.set_ticklabels(iodepth)
    ax1.w_yaxis.set_ticklabels(numjobs)

    # ax1.set_zlim3d(0,int(settings['zmax']))

    # zticks = np.arange(dz.min(), dz.max(), ((dz.max()/10)%1000))
    # ax1.w_zaxis.set_ticks(zticks)

    # axis labels
    fontsize = 14
    ax1.set_xlabel('iodepth', fontsize=fontsize)
    ax1.set_ylabel('numjobs', fontsize=fontsize)
    ax1.set_zlabel(metric,  fontsize=fontsize)

    ax1.xaxis.labelpad = 10
    ax1.zaxis.labelpad = 20
    ax1.zaxis.set_tick_params(pad=10)

    # title
    mode = rw
    plt.suptitle(settings['title'] + " | " + mode + " | " +
                 metric, fontsize=16, horizontalalignment='center')

    fig.text(0.75, 0.03, settings['source'])

    plt.tight_layout()
    now = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    plt.savefig('3d-iops-jobs' +
                str(settings['rw']) + "-" + str(now) + '.png')
    plt.close('all')

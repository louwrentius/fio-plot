import os
import sys
import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib as mpl
from matplotlib import rcParams, cycler
import numpy as np
import pprint as pprint

def chart_2d_log_data(config, data):

    #result = [ item['data'] for item in data ]
    #array = np.array(result)
    #pprint.pprint(array)
    #print(array.shape)
    cmap = plt.cm.tab20c
    rcParams['axes.prop_cycle'] = cycler(color=cmap(np.linspace(0, 1, len(data))))
    pprint.pprint(data)

    unpacked = list(zip(*data))
    lines = plt.plot(unpacked[0], unpacked[1])
    
    #fig.savefig('test.png')
    plt.show()
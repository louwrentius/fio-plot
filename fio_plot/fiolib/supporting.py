#!/usr/local/bin env
import pprint as pprint
import statistics
import numpy as np


def running_mean(l, N):
    sum = 0
    result = list(0 for x in l)

    for i in range(0, N):
        sum = sum + l[i]
        result[i] = sum / (i+1)

    for i in range(N, len(l)):
        sum = sum - l[i-N] + l[i]
        result[i] = sum / N

    return result


def scale_xaxis_time(dataset):
    result = {'format': 'Time (ms)', 'data': dataset}
    mean = statistics.mean(dataset)

    if (mean > 1000) & (mean < 1000000):
        result['data'] = [x / 1000 for x in dataset]
        result['format'] = 'Time (s)'
    if mean > 1000000:
        result['data'] = [x / 60000 for x in dataset]
        result['format'] = 'Time (m)'
    if mean > 36000000:  # only switch to hours with enough datapoints (+10)
        result['data'] = [x / 3600000 for x in dataset]
        result['format'] = 'Time (h)'
    return result


def get_scale_factor(dataset):
    mean = statistics.mean(dataset)
    scale_factors = [{'scale': 1000000, 'label': 'Latency (ms)'},
                     {'scale': 1000, 'label': 'Latency (\u03BCs)'},
                     {'scale': 0, 'label': 'Latency (ns)'}]
    for item in scale_factors:
        """ Notice the factor, prevents scaling the graph up too soon if values
            are small, thus becomming almost unreadable """
        if mean > item['scale']*5:
            return item


def get_largest_scale_factor(scale_factors):
    scalefactor = scale_factors[0]
    scalefactor = [x for x in scale_factors if x['scale']
                   >= scalefactor['scale']]
    return scalefactor[0]


def scale_yaxis_latency(dataset, scale):
    result = {}
    result['data'] = [x / scale['scale'] for x in dataset]
    result['format'] = scale['label']
    return result


def get_colors():
    return [
        'tab:blue',
        'tab:orange',
        'tab:green',
        'tab:red',
        'tab:purple',
        'tab:brown',
        'tab:pink',
        'tab:olive',
        'tab:cyan',
        'darkgreen',
        'cornflowerblue',
        'deepping',
        'red',
        'gold',
        'darkcyan'
    ]


def lookupTable(metric):

    lookup = {'iops': {'ylabel': 'IOP/s',
                       'label_pos': 0, 'label_rot': 'vertical'},
              'bw': {'ylabel': 'Througput (KB/s)',
                     'label_pos': -55, 'label_rot': 'vertical'},
              'lat': {'ylabel': 'LAT Latency (ms)',
                      'label_pos': 5, 'label_rot': 'vertical'},
              'slat': {'ylabel': 'SLAT Latency (ms)',
                       'label_pos': 5, 'label_rot': 'vertical'},
              'clat': {'ylabel': 'CLAT Latency (ms)',
                       'label_pos': 5, 'label_rot': 'vertical'},
              }
    return lookup[metric]


def generate_axes(ax, datatypes):

    axes = {}
    metrics = ['iops', 'lat', 'bw', 'clat', 'slat']
    tkw = dict(size=4, width=1.5)
    first_not_used = True
    positions = [0, 5, -55]

    for item in metrics:
        if item in datatypes:
            if first_not_used:
                value = ax
                value.tick_params(axis='x', **tkw)
                first_not_used = False
                ax.grid(ls='dotted')
            else:
                value = ax.twinx()
                value.tick_params(axis='y', **tkw)

            axes[item] = value
            axes[item].ticklabel_format(style='plain')
            axes[f"{item}_pos"] = positions.pop(0)
            if len(axes) == 6:
                axes[item].spines["right"].set_position(("axes", -0.24))
                break
    return axes


def process_dataset(dataset):

    datatypes = []
    new_list = []
    new_structure = {'datatypes': None, 'dataset': None}
    final_list = []
    scale_factors = []

    """
    This first loop is to unpack the data in series and add scale the xaxis
    """
    for item in dataset:

        datatypes.append(item['type'])

        unpacked = list(zip(*item['data']))
        item['xvalues'] = unpacked[0]
        item['yvalues'] = unpacked[1]
        item['data'] = None

        scaled_xaxis = scale_xaxis_time(item['xvalues'])
        item['xlabel'] = scaled_xaxis['format']
        item['xvalues'] = scaled_xaxis['data']

        if 'lat' in item['type']:
            scale_factors.append(get_scale_factor(item['yvalues']))

        new_list.append(item)

    """
    This second loop assures that all data is scaled with the same factor
    """
    if len(scale_factors) > 0:
        scale_factor = get_largest_scale_factor(scale_factors)

    for item in new_list:
        if 'lat' in item['type']:
            scaled_data = scale_yaxis_latency(item['yvalues'], scale_factor)
            item['ylabel'] = scaled_data['format']
            item['yvalues'] = scaled_data['data']
        else:
            item['ylabel'] = lookupTable(item['type'])['ylabel']

        mean = np.mean(item['yvalues'])
        stdv = round((np.std(item['yvalues']) / mean) * 100, 2)

        if mean > 1:
            mean = round(mean, 2)
        if mean <= 1:
            mean = round(mean, 3)
        if mean >= 20:
            mean = int(round(mean, 0))

        item['mean'] = mean
        item['stdv'] = stdv
        """
        This is soft of a hack to prevent IOPs and BW to be on top of each other
        BW and IOPS are directly related and BW should not be shown as it is
        often not relevant anyway, but for readability, this is added.
        """
        if item['type'] == 'bw':
            item['maximum'] = max(item['yvalues']) * 1.2
        else:
            item['maximum'] = max(item['yvalues']) * 1.3

        final_list.append(item)

    new_structure['datatypes'] = list(set(datatypes))
    new_structure['dataset'] = final_list

    return new_structure

#!/usr/local/bin env
import pprint as pprint
import statistics


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


def scale_yaxis_latency(dataset):
    result = {'format': 'Latency (ns)', 'data': dataset}
    mean = statistics.mean(dataset)

    if (mean > 1000) & (mean < 1000000):
        result['data'] = [x / 1000 for x in dataset]
        result['format'] = r'$Latency\ (\mu$s)'
    if mean > 1000000:
        result['data'] = [x / 1000000 for x in dataset]
        result['format'] = 'Latency (ms)'
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
            axes[f"{item}_pos"] = positions.pop(0)
            if len(axes) == 6:
                axes[item].spines["right"].set_position(("axes", -0.24))
                break
    return axes


def process_dataset(dataset):

    datatypes = []
    new_list = []
    new_structure = {'datatypes': None, 'dataset': None}

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
            scaled_data = scale_yaxis_latency(item['yvalues'])
            item['ylabel'] = scaled_data['format']
            item['yvalues'] = scaled_data['data']
        else:
            item['ylabel'] = lookupTable(item['type'])['ylabel']

        if item['type'] == 'bw':
            item['maximum'] = max(item['yvalues']) * 1.2
        else:
            item['maximum'] = max(item['yvalues']) * 1.3
        new_list.append(item)

    new_structure['datatypes'] = list(set(datatypes))
    new_structure['dataset'] = new_list

    return new_structure

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


def scale_yaxis_latency(dataset):
    result = {'format': r'$Latency\ in\ ns\ $', 'data': dataset}
    mean = statistics.mean(dataset)
    print(mean)
    if (mean > 1000) & (mean < 1000000):
        result['data'] = [x / 1000 for x in dataset]
        result['format'] = r'$Latency\ in\ \mu$s'
    if mean > 1000000:
        result['data'] = [x / 1000000 for x in dataset]
        result['format'] = r'$Latency\ in\ ms\ $'
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


def get_label_position(axis):
    integer = int(axis[1])
    if integer % 3 == 0:
        return -50
    elif integer % 2 == 0:
        return 5
    else:
        return 0


def lookupTable(metric):

    lookup = [
        {'type': 'iops', 'ylabel': 'IOP/s', 'color': 'tab:blue',
            'label_pos': 0, 'label_rot': 'vertical'},
        {'type': 'bw', 'ylabel': 'Througput (KB/s)', 'color': 'tab:orange',
         'label_pos': -50, 'label_rot': 'vertical'},
        {'type': 'lat', 'ylabel': 'LAT Latency (ms)', 'color': 'tab:green',
         'label_pos': 0, 'label_rot': 'vertical'},
        {'type': 'slat',
            'ylabel': 'SLAT Latency (ms)',
            'color': 'tab:red', 'label_pos': 0, 'label_rot': 'vertical'},
        {'type': 'clat', 'ylabel': 'CLAT Latency (ms)', 'color': 'tab:purple',
         'label_pos': 0, 'label_rot': 'vertical'},

    ]
    return [x for x in lookup if x['type'] == metric]


def generate_axes(ax, datatypes):

    axes = {}
    metrics = ['iops', 'lat', 'bw', 'clat', 'slat']
    tkw = dict(size=4, width=1.5)
    first_not_used = True

    for item in metrics:
        if item in datatypes:
            if first_not_used:
                value = ax
                value.tick_params(axis='x', **tkw)
                first_not_used = False
            else:
                value = ax.twinx()
                value.tick_params(axis='y', **tkw)
            axes[item] = value
            axes[f"{item}_pos"] = f"c{(metrics.index(item)) + 1}"
            if len(axes) == 6:
                axes[item].spines["right"].set_position(("axes", -0.24))
    return axes

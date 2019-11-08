#!/usr/local/bin env
import pprint as pprint


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


def scaling(minimum):

    if minimum < 1:
        return {'scale_factor': 1.0, 'metric': r'$Latency\ in\ \mu$s'}
    else:
        return {'scale_factor': 1000, 'metric': r'$Latency\ in\ ms\ $'}


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

    #positions = {"c1": 0, "c2": 0, "c3": -50}
    # return positions[axis]


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

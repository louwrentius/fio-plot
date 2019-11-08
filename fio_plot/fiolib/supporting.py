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


def lookupTable(metric):

    lookup = [{'type': 'iops', 'ylabel': 'IOP/s', 'color': 'tab:blue'},
              {'type': 'bw',
                  'ylabel': 'Througput (KB/s)', 'color': 'tab:orange'},
              {'type': 'lat',
                  'ylabel': 'LAT Latency (ms)', 'color': 'tab:green'},
              {'type': 'slat',
                  'ylabel': 'SLAT Latency (ms)', 'color': 'tab:red'},
              {'type': 'clat',
                  'ylabel': 'CLAT Latency (ms)', 'color': 'tab:purple'},
              ]
    return [x for x in lookup if x['type'] == metric]

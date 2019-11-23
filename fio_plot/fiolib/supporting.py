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
        'xkcd:cloudy blue',
        'xkcd:dark pastel green',
        'xkcd:cement',
        'xkcd:dark grass green',
        'xkcd:dusty teal',
        'xkcd:grey teal',
        'xkcd:macaroni and cheese',
        'xkcd:pinkish tan',
        'xkcd:spruce',
        'xkcd:strong blue',
        'xkcd:toxic green',
        'xkcd:windows blue',
        'xkcd:blue blue',
        'xkcd:blue with a hint of purple',
        'xkcd:booger',
        'xkcd:bright sea green',
        'xkcd:dark green blue',
        'xkcd:deep turquoise',
        'xkcd:green teal',
        'xkcd:strong pink',
        'xkcd:bland',
        'xkcd:deep aqua',
        'xkcd:lavender pink',
        'xkcd:light moss green',
        'xkcd:light seafoam green',
        'xkcd:olive yellow',
        'xkcd:pig pink',
        'xkcd:deep lilac',
        'xkcd:desert',
        'xkcd:dusty lavender',
        'xkcd:purpley grey',
        'xkcd:purply',
        'xkcd:candy pink',
        'xkcd:light pastel green',
        'xkcd:boring green',
        'xkcd:kiwi green',
        'xkcd:light grey green',
        'xkcd:orange pink',
        'xkcd:tea green',
        'xkcd:very light brown',
        'xkcd:egg shell',
        'xkcd:eggplant purple',
        'xkcd:powder pink',
        'xkcd:reddish grey',
        'xkcd:baby shit brown',
        'xkcd:liliac',
        'xkcd:stormy blue',
        'xkcd:ugly brown',
        'xkcd:custard',
        'xkcd:darkish pink',
        'xkcd:deep brown',
        'xkcd:greenish beige',
        'xkcd:manilla',
        'xkcd:off blue',
        'xkcd:battleship grey',
        'xkcd:browny green',
        'xkcd:bruise',
        'xkcd:kelley green',
        'xkcd:sickly yellow',
        'xkcd:sunny yellow',
        'xkcd:azul',
        'xkcd:darkgreen',
        'xkcd:green/yellow'
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


def round_metric(value):

    if value > 1:
        value = round(value, 2)
    if value <= 1:
        value = round(value, 3)
    if value >= 20:
        value = int(round(value, 0))
    return value


def round_metric_series(dataset):
    data = [round_metric(x) for x in dataset]
    return data


def raw_stddev_to_percent(values, stddev_series):
    result = []
    for x, y in zip(values, stddev_series):
        pprint.pprint(f"{x} - {y}")
        percent = round((int(y) / int(x)) * 100, 0)
        result.append(percent)
    pprint.pprint(result)
    return result


def process_dataset(settings, dataset):

    datatypes = []
    new_list = []
    new_structure = {'datatypes': None, 'dataset': None}
    final_list = []
    scale_factors = []

    """
    This first loop is to unpack the data in series and add scale the xaxis
    """
    for item in dataset:
        for rw in settings['filter']:
            if len(item['data'][rw]) > 0:
                datatypes.append(item['type'])
                # pprint.pprint(item['data'][rw])
                unpacked = list(zip(*item['data'][rw]))
                # pprint.pprint(unpacked)
                item[rw] = {}

                item[rw]['xvalues'] = unpacked[0]
                item[rw]['yvalues'] = unpacked[1]

                scaled_xaxis = scale_xaxis_time(item[rw]['xvalues'])
                item['xlabel'] = scaled_xaxis['format']
                item[rw]['xvalues'] = scaled_xaxis['data']

                if 'lat' in item['type']:
                    scale_factors.append(
                        get_scale_factor(item[rw]['yvalues']))

        new_list.append(item)

    """
    This second loop assures that all data is scaled with the same factor
    """
    if len(scale_factors) > 0:
        scale_factor = get_largest_scale_factor(scale_factors)

    for item in new_list:
        for rw in settings['filter']:
            if rw in item.keys():
                if 'lat' in item['type']:
                    scaled_data = scale_yaxis_latency(
                        item[rw]['yvalues'], scale_factor)
                    item[rw]['ylabel'] = scaled_data['format']
                    item[rw]['yvalues'] = scaled_data['data']
                else:
                    item[rw]['ylabel'] = lookupTable(item['type'])['ylabel']

                mean = np.mean(item[rw]['yvalues'])
                stdv = round((np.std(item[rw]['yvalues']) / mean) * 100, 2)
                percentile = round(np.percentile(
                    item[rw]['yvalues'], settings['percentile']), 2)

                if mean > 1:
                    mean = round(mean, 2)
                if mean <= 1:
                    mean = round(mean, 3)
                if mean >= 20:
                    mean = int(round(mean, 0))

                if percentile > 1:
                    percentile = round(percentile, 2)
                if percentile <= 1:
                    percentile = round(percentile, 3)
                if percentile >= 20:
                    percentile = int(round(percentile, 0))

                item[rw]['mean'] = mean
                item[rw]['stdv'] = stdv
                item[rw]['percentile'] = percentile
                """
                This is soft of a hack to prevent IOPs and BW to be on top of each other
                BW and IOPS are directly related and BW should not be shown as it is
                often not relevant anyway, but for readability, this is added.
                """

        final_list.append(item)

    new_structure['datatypes'] = list(set(datatypes))
    new_structure['dataset'] = final_list
    return new_structure


def create_title_and_sub(settings, plt):
    #
    # Offset title/subtitle if there is a 3rd y-axis
    #
    number_of_types = len(settings['type'])
    if number_of_types <= 2:
        x_offset = 0.5
    else:
        x_offset = 0.425
    #
    # plt.subtitle sets title and plt.title sets subtitle ....
    #
    plt.suptitle(settings['title'])

    if settings['subtitle']:
        subtitle = settings['subtitle']
    else:
        iodepth = str(settings['iodepth']).strip('[]')
        numjobs = str(settings['numjobs']).strip('[]')
        datatype = str(settings['type']).strip('[]').replace('\'', '')
        subtitle = f"| {settings['rw']} | iodepth {iodepth} | numjobs {numjobs} | {datatype}"

    plt.title(subtitle, fontsize=8,
              horizontalalignment='center', x=x_offset, y=1.02)

#!/usr/bin/env python3
import fiolib.supporting as supporting
import pprint


def get_dataset_types(dataset):
    dataset_types = {'rw': set(), 'iodepth': set(), 'numjobs': set()}
    operation = {'rw': str, 'iodepth': int, 'numjobs': int}

    for x in dataset_types.keys():
        for y in dataset:
            dataset_types[x].add(operation[x](y[x]))
        dataset_types[x] = sorted(dataset_types[x])
    return dataset_types


def get_record_set_histogram(settings, dataset):
    rw = settings['rw']
    iodepth = int(settings['iodepth'][0])
    numjobs = int(settings['numjobs'][0])

    record_set = {'iodepth': iodepth, 'numjobs': numjobs, 'data': None}

    for record in dataset:
        if (int(record['iodepth']) == iodepth) and (int(record['numjobs']) == numjobs) and record['rw'] == rw:
            record_set['data'] = record
            return record_set


def get_record_set_3d(settings, dataset, dataset_types, rw, metric):
    record_set = {'iodepth': dataset_types['iodepth'],
                  'numjobs': dataset_types['numjobs'], 'values': []}
    # pprint.pprint(dataset)
    if settings['rw'] == 'randrw':
        if len(settings['filter']) > 1 or not settings['filter']:
            print(
                "Since we are processing randrw data, you must specify a filter for either read or write data, not both.")
            exit(1)

    for depth in dataset_types['iodepth']:
        row = []
        for jobs in dataset_types['numjobs']:
            for record in dataset:
                if (int(record['iodepth']) == int(depth)) and int(record['numjobs']) == jobs and record['rw'] == rw and record['type'] in settings['filter']:
                    row.append(record[metric])
        record_set['values'].append(supporting.round_metric_series(row))
    return record_set


def get_record_set(settings, dataset, dataset_types, rw, numjobs):
    """The supplied dataset, a list of flat dictionaries with data is filtered based
    on the parameters as set by the command line. The filtered data is also scaled and rounded.
    """
    if settings['rw'] == 'randrw':
        if len(settings['filter']) > 1 or not settings['filter']:
            print(
                "Since we are processing randrw data, you must specify a filter for either read or write data, not both.")
            exit(1)

    record_set = {'x_axis': dataset_types['iodepth'], 'x_axis_format': 'Queue Depth', 'y1_axis': None,
                  'y2_axis': None, 'numjobs': numjobs}

    iops_series_raw = []
    iops_stddev_series_raw = []
    lat_series_raw = []
    lat_stddev_series_raw = []

    for depth in dataset_types['iodepth']:
        for record in dataset:
            if (int(record['iodepth']) == int(depth)) and int(record['numjobs']) == int(numjobs[0]) and record['rw'] == rw and record['type'] in settings['filter']:
                iops_series_raw.append(record['iops'])
                lat_series_raw.append(record['lat'])
                iops_stddev_series_raw.append(record['iops_stddev'])
                lat_stddev_series_raw.append(record['lat_stddev'])
    #
    # Latency data must be scaled, IOPs will not be scaled.
    #
    latency_scale_factor = supporting.get_scale_factor(lat_series_raw)
    scaled_latency_data = supporting.scale_yaxis_latency(
        lat_series_raw, latency_scale_factor)
    #
    # Latency data must be rounded.
    #
    scaled_latency_data_rounded = supporting.round_metric_series(
        scaled_latency_data['data'])
    scaled_latency_data['data'] = scaled_latency_data_rounded
    #
    # Latency stddev must be scaled with same scale factor as the data
    #
    lat_stdev_scaled = supporting.scale_yaxis_latency(
        lat_stddev_series_raw, latency_scale_factor)

    lat_stdev_scaled_rounded = supporting.round_metric_series(
        lat_stdev_scaled['data'])

    #
    # Latency data is converted to percent.
    #
    lat_stddev_percent = supporting.raw_stddev_to_percent(
        scaled_latency_data['data'], lat_stdev_scaled_rounded)

    lat_stddev_percent = [int(x) for x in lat_stddev_percent]

    scaled_latency_data['stddev'] = supporting.round_metric_series(
        lat_stddev_percent)
    #
    # IOPS data is rounded
    iops_series_rounded = supporting.round_metric_series(iops_series_raw)
    #
    # IOPS stddev is converted to percent
    iops_stdev_rounded = supporting.round_metric_series(iops_stddev_series_raw)
    iops_stdev_rounded_percent = supporting.raw_stddev_to_percent(
        iops_series_rounded, iops_stdev_rounded)
    iops_stdev_rounded_percent = [int(x) for x in iops_stdev_rounded_percent]
    #
    #
    record_set['y1_axis'] = {'data': iops_series_rounded,
                             'format': "IOPS", 'stddev': iops_stdev_rounded_percent}
    record_set['y2_axis'] = scaled_latency_data

    return record_set


def autolabel(rects, axis):
    for rect in rects:
        height = rect.get_height()
        if height < 10:
            formatter = '%.2f'
        else:
            formatter = '%d'
        value = rect.get_x()

        if height >= 10000:
            value = int(round(height / 1000, 0))
            formatter = '%dK'
        else:
            value = height

        axis.text(rect.get_x() + rect.get_width() / 2,
                  1.015 * height, formatter % value, ha='center',
                  fontsize=8)


def create_stddev_table(data, ax2):
    table_vals = [data['x_axis'], data['y1_axis']
                  ['stddev'], data['y2_axis']['stddev']]

    cols = len(data['x_axis'])
    table = ax2.table(cellText=table_vals,  loc='center right', rowLabels=[
        'IO queue depth', f'IOP/s \u03C3 %', f'Latency \u03C3 %'],
        colLoc='center right',
        cellLoc='center right', colWidths=[0.05] * cols,
        rasterized=False)
    table.scale(1, 1.2)

    for key, cell in table.get_celld().items():
        cell.set_linewidth(0)

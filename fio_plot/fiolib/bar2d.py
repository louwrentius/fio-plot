#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import pprint
from matplotlib.font_manager import FontProperties
import fiolib.supporting as supporting
from datetime import datetime


def get_dataset_types(dataset):
    dataset_types = {'rw': set(), 'iodepth': set(), 'numjobs': set()}
    operation = {'rw': str, 'iodepth': int, 'numjobs': int}

    for x in dataset_types.keys():
        for y in dataset:
            dataset_types[x].add(operation[x](y[x]))
        dataset_types[x] = sorted(dataset_types[x])

    return dataset_types


def get_record_set(dataset, dataset_types, rw, numjobs):
    record_set = {'x_axis': dataset_types['iodepth'], 'x_axis_format': 'Queue Depth', 'y1_axis': None,
                  'y2_axis': None, 'numjobs': numjobs}

    iops_series_raw = []
    iops_stddev_series_raw = []
    lat_series_raw = []
    lat_stddev_series_raw = []

    for depth in dataset_types['iodepth']:
        for record in dataset:
            if (int(record['iodepth']) == int(depth)) and (int(record['numjobs']) == int(numjobs)) and record['rw'] == rw:
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
                             'format': "IOP/s", 'stddev': iops_stdev_rounded_percent}
    record_set['y2_axis'] = scaled_latency_data

    return record_set


def autolabel(rects, axis):
    for rect in rects:
        height = rect.get_height()
        if height < 10:
            formatter = '%.4f'
        else:
            formatter = '%d'
        axis.text(rect.get_x() + rect.get_width() / 2,
                  1.015 * height, formatter % height, ha='center',
                  fontsize=8)


def create_stddev_table(data, ax2):
    table_vals = [data['x_axis'], data['y1_axis']
                  ['stddev'], data['y2_axis']['stddev']]

    cols = len(data['x_axis'])
    table = ax2.table(cellText=table_vals,  loc='center right', rowLabels=[
        'IO queue depth', r'$IOP/s\ \sigma\ \%$', r'$Latency\ \sigma\ \%$'],
        colLoc='center right',
        cellLoc='center right', colWidths=[0.05] * cols,
        rasterized=False)
    table.scale(1, 1.2)

    for key, cell in table.get_celld().items():
        cell.set_linewidth(0)


def chart_2dbarchart_jsonlogdata(settings, dataset):
    dataset_types = get_dataset_types(dataset)
    data = get_record_set(dataset, dataset_types,
                          settings['rw'], settings['numjobs'])
    pprint.pprint(data)

    fig, (ax1, ax2) = plt.subplots(
        nrows=2, gridspec_kw={'height_ratios': [7, 1]})
    ax3 = ax1.twinx()
    fig.set_size_inches(10, 6)

    if settings['source']:
        plt.text(1, -0.08, str(settings['source']), ha='right', va='top',
                 transform=ax1.transAxes, fontsize=9)

    ax2.axis('off')
    #
    #
    x_pos = np.arange(0, len(data['x_axis']) * 2, 2)
    width = 0.9

    n = np.array(data['y2_axis']['data'], dtype=float)

    rects1 = ax1.bar(x_pos, data['y1_axis']['data'], width,
                     color='#a8ed63')
    # rects2 = ax3.bar(x_pos + width, data['y_data2'], width,
    rects2 = ax3.bar(x_pos + width, n, width,
                     color='#34bafa')

    #
    # Configure axis labels and ticks
    ax1.set_ylabel(data['y1_axis']['format'])
    ax1.set_xlabel(data['x_axis_format'])
    ax3.set_ylabel(data['y2_axis']['format'])

    ax1.set_xticks(x_pos + width / 2)
    ax1.set_xticklabels(data['x_axis'])
    #
    # Set title
    settings['type'] = ""
    settings['iodepth'] = dataset_types['iodepth']
    supporting.create_title_and_sub(settings, plt)
    #
    #
    autolabel(rects1, ax1)
    autolabel(rects2, ax3)
    #
    #
    create_stddev_table(data, ax2)
    #
    # Create legend
    ax2.legend((rects1[0], rects2[0]),
               (data['y1_axis']['format'],
                data['y2_axis']['format']), loc='center left', frameon=False)
    #
    # Save graph to file
    #
    now = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    title = settings['title'].replace(" ", '_')
    plt.tight_layout(rect=[0, 0.00, 0.95, 0.95])
    fig.savefig(f"{title}_{now}.png", dpi=settings['dpi'])


class Chart(object):

    def __init__(self, data, config):
        self.data = data
        self.config = config
        d = datetime.now()
        self.date = d.strftime('%Y-%m-%d-%H:%M:%S')
        self.test_types = {
            "randread": "Random Read",
            "randwrite": "Random Write",
            "numjobs": "Number of Jobs: ",
            "iops": "IOPs",
            "lat": "Latency"
        }

    def return_unique_series(self, key):
        lala = []
        for record in self.data:
            lala.append(record[key])

        lala = [int(x) for x in lala]
        lala = sorted(set(lala))
        return lala

    def strip_leading_zero(self, value):
        sanitized = value
        if isinstance(value, str):
            if value[0] == '0':
                sanitized = value[1]
            else:
                sanitized = value

        return sanitized

    def return_record_set(self, dataset, key, value):
        lala = []
        for record in dataset:
            v = self.strip_leading_zero(str(record[key]))
            if str(v) == str(value):
                lala.append(record)
        return lala

    def filter_record_set(self, dataset, key, value):
        lala = []
        for record in dataset:
            if record[key] == value:
                lala.append(record)
        return lala

    def subselect_record_set(self, dataset, keys):
        lala = []
        for record in dataset:
            d = dict.fromkeys(keys)
            for key in keys:
                if record[key] is not float:
                    d[key] = self.strip_leading_zero(record[key])
            lala.append(d)
        return lala

    def return_latency_units(self, value):

        d = {}
        d['Nanoseconds'] = {
            "Unit": "ns",
            "Value": value
        }
        d['Microseconds'] = {
            "Unit": "us",
            "Value": value / 1000
        }

        d['Miliseconds'] = {
            "Unit": "ms",
            "Value": value / 1000000
        }

        if d['Microseconds'] > 1:
            d['Value'] = 'Microseconds'
        if d['Milisecond'] > 1:
            d['Value'] = 'Miliseconds'

        return d


class barChart(Chart):

    def __init__(self, data, config):
        super().__init__(data, config)

        self.fig, (self.ax1, self.ax2) = plt.subplots(
            nrows=2, gridspec_kw={'height_ratios': [7, 1]})
        self.ax3 = self.ax1.twinx()
        self.fig.set_size_inches(10, 6)

        self.series = {'x_series': [],
                       'y_series1': [],
                       'y_series2': [],
                       'y_series3': [],
                       }

        self.config = config

        if self.config['source']:
            plt.text(1, -0.08, str(self.config['source']), ha='right', va='top',
                     transform=self.ax1.transAxes, fontsize=9)

        self.ax2.axis('off')

    def calculate_std(self):
        # Create series for Standard Deviation table.
        std = []
        for stddev in self.series['y_series3']:
            for latency in self.series['y_series2']:
                p = round((stddev / latency) * 100)
            std.append(str(p))
        self.series['y_series3'] = std

    def generate_series(self):

        dataset = self.filter_record_set(self.data, 'rw', self.config['mode'])
        recordset = self.return_record_set(dataset, self.config['fixed_metric'],
                                           self.config['fixed_value'])

        self.series['x_series'] = self.return_unique_series('iodepth')

        for x in self.series['x_series']:
            for y in recordset:
                if int(y[self.config['x_series']]) == int(x):
                    self.series['y_series1'].append(
                        round(y[self.config['y_series1']]))  # iops
                    self.series['y_series2'].append(
                        round(y[self.config['y_series2']]))  # lat
                    self.series['y_series3'].append(
                        round(y[self.config['y_series3']]))  # lat_stddev

        self.calculate_std()

    def autolabel(self, rects, axis):
        for rect in rects:
            height = rect.get_height()
            if height < 10:
                formatter = '%.4f'
            else:
                formatter = '%d'
            axis.text(rect.get_x() + rect.get_width() / 2,
                      1.015 * height, formatter % height, ha='center',
                      fontsize=8)

    def create_stddev_table(self):
        table_vals = [self.series['x_series'], self.series['y_series3']]
        cols = len(self.series['x_series'])
        table = self.ax2.table(cellText=table_vals, loc='center right', rowLabels=[
            'IO queue depth', r'$Latency\ \sigma\ \%$'],
            colLoc='center right',
            cellLoc='center right', colWidths=[0.05] * cols,
            rasterized=False)
        table.scale(1, 1.2)

        for key, cell in table.get_celld().items():
            cell.set_linewidth(0)


class IOL_Chart(barChart):

    def __init__(self, data, config):
        super().__init__(data, config)
        self.generate_series()
        # pprint.pprint(self.series)

    def plot_io_and_latency(self, mode, numjobs):

        self.mode = mode

        x_pos = np.arange(0, len(self.series['x_series']) * 2, 2)
        width = 0.9

        n = np.array(self.series['y_series2'], dtype=float)
        n = np.divide(n, 1000000)

        rects1 = self.ax1.bar(x_pos, self.series['y_series1'], width,
                              color='#a8ed63')
        # rects2 = self.ax3.bar(x_pos + width, self.series['y_series2'], width,
        rects2 = self.ax3.bar(x_pos + width, n, width,
                              color='#34bafa')

        self.ax1.set_ylabel(self.config['y_series1_label'])
        self.ax1.set_xlabel(self.config['x_series_label'])
        self.ax3.set_ylabel(self.config['y_series2_label'])

        if self.config['title']:
            self.ax1.set_title(
                str(self.config['title']) + " | " + str(mode) + " | numjobs: " + str(numjobs))
        else:
            self.ax1.set_title(str(mode) + ' performance')

        self.ax1.set_xticks(x_pos + width / 2)
        self.ax1.set_xticklabels(self.series['x_series'])

        self.ax2.legend((rects1[0], rects2[0]),
                        (self.config['y_series1_label'],
                         self.config['y_series2_label']), loc='upper left', frameon=False)

        self.create_stddev_table()

        self.autolabel(rects1, self.ax1)
        self.autolabel(rects2, self.ax3)

        plt.tight_layout()
        plt.savefig(mode + '_iodepth_' + str(self.date) +
                    '_' + str(numjobs) + '_iops_latency.png')
        plt.close('all')

    def get_sorted_mixed_list(self, unsorted_list):

        def get_type(x):
            try:
                return int(x)
            except ValueError:
                return str(x)

        sorted_list = []
        ints = []
        strings = []

        for x in unsorted_list:
            result = get_type(x)
            if isinstance(result, int):
                ints.append(result)
            else:
                strings.append(result)

        ints.sort()
        sorted_list = ints
        strings.sort()
        [sorted_list.append(x) for x in strings]
        return sorted_list

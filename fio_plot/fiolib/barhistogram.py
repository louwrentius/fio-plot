#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import pprint
import fiolib.shared_chart as shared
import fiolib.supporting as supporting
from datetime import datetime


def sort_latency_keys(latency):
    placeholder = ""
    tmp = []
    for item in latency:
        if item == '>=2000':
            placeholder = ">=2000"
        else:
            tmp.append(item)

    tmp.sort(key=int)
    if(placeholder):
        tmp.append(placeholder)
    return tmp


def sort_latency_data(latency_dict):

    keys = latency_dict.keys()
    values = {'keys': None, 'values': []}
    sorted_keys = sort_latency_keys(keys)
    values['keys'] = sorted_keys
    for key in sorted_keys:
        values['values'].append(latency_dict[key])
    return values


def process_coverage_data(coverage):
    None


def chart_latency_histogram(settings, dataset):
    iodepth = settings['iodepth']
    numjobs = settings['numjobs']
    depth = iodepth
    mode = settings['rw']
    record_set = shared.get_record_set_histogram(settings, dataset)

    # We have to sort the data / axis from low to high
    sorted_result_ms = sort_latency_data(record_set['data']['latency_ms'])
    sorted_result_us = sort_latency_data(record_set['data']['latency_us'])
    sorted_result_ns = sort_latency_data(record_set['data']['latency_ns'])

    # This is just to use easier to understand variable names
    x_series = sorted_result_ms['keys']
    y_series1 = sorted_result_ms['values']
    y_series2 = sorted_result_us['values']
    y_series3 = sorted_result_ns['values']

    # us/ns histogram data is missing 2000/>=2000 fields that ms data has
    # so we have to add dummy data to match x-axis size
    y_series2.extend([0, 0])
    y_series3.extend([0, 0])

    # Create the plot
    fig, ax1 = plt.subplots()
    fig.set_size_inches(10, 6)

    # Make the positioning of the bars for ns/us/ms
    x_pos = np.arange(0, len(x_series) * 3, 3)
    width = 1

    # how much of the IO falls in a particular latency class ns/us/ms
    coverage_ms = round(sum(y_series1), 2)
    coverage_us = round(sum(y_series2), 2)
    coverage_ns = round(sum(y_series3), 2)

    # Draw the bars
    rects1 = ax1.bar(x_pos, y_series1, width, color='r')
    rects2 = ax1.bar(x_pos + width, y_series2, width, color='b')
    rects3 = ax1.bar(x_pos + width + width, y_series3, width, color='g')

    # Configure the axis and labels
    ax1.set_ylabel('Percentage of I/O')
    ax1.set_xlabel("Latency")
    ax1.set_xticks(x_pos + width / 2)
    ax1.set_xticklabels(x_series)

    # Make room for labels by scaling y-axis up (max is 100%)
    ax1.set_ylim(0, 100 * 1.1)

    label_ms = "Latency in ms ({0:05.2f}%)".format(coverage_ms)
    label_us = "Latency in us  ({0:05.2f}%)".format(coverage_us)
    label_ns = "Latency in ns  ({0:05.2f}%)".format(coverage_ns)

    # Configure the title
    settings['type'] = ""
    supporting.create_title_and_sub(settings, plt)
    # Configure legend
    ax1.legend((rects1[0], rects2[0], rects3[0]), (label_ms, label_us, label_ns), frameon=False,
               loc='best')

    def autolabel(rects, axis):
        fontsize = 6
        for rect in rects:
            height = rect.get_height()
            if height >= 1:
                axis.text(rect.get_x() + rect.get_width() / 2., 1 +
                          height, '{}%'.format(int(height)),
                                  ha='center', fontsize=fontsize)
            elif height > 0.4:
                axis.text(rect.get_x() + rect.get_width() /
                          2., 1 + height, "{:3.2f}%".format(height), ha='center', fontsize=fontsize)

    autolabel(rects1, ax1)
    autolabel(rects2, ax1)
    autolabel(rects3, ax1)

    fig.text(0.75, 0.03, settings['source'])

    now = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    title = settings['title'].replace(" ", '_')
    plt.tight_layout(rect=[0, 0.00, 0.95, 0.95])
    fig.savefig(f"{title}_{now}.png", dpi=settings['dpi'])

####################


class Chart():
    None


class LH_Chart(Chart):

    def generate_history_chart(self, chartdata):

        x_series = chartdata['x_series']
        y_series1 = chartdata['y_series1']
        y_series2 = chartdata['y_series2']
        depth = chartdata['iodepth']
        mode = chartdata['mode']

        coverage_ms = round(sum(y_series1), 2)
        coverage_us = round(sum(y_series2), 2)

        # Creating actual graph

        fig, (ax1, ax2) = plt.subplots(
            nrows=2, gridspec_kw={'height_ratios': [11, 1]})
        fig.set_size_inches(10, 6)

        x_pos = np.arange(0, len(x_series) * 2, 2)
        width = 1

        rects1 = ax1.bar(x_pos, y_series1, width, color='r')
        rects2 = ax1.bar(x_pos + width, y_series2, width, color='b')

        ax1.set_ylabel('Percentage of IO (ms)')
        ax1.set_xlabel(r'$Latency\ in\ ms\ or\ \mu$')
        ax1.set_title(str(self.config['title']) + " | "
                      + str(mode).title() +
                      ' latency histogram | IO depth ' +
                      str(depth))
        ax1.set_xticks(x_pos + width / 2)
        ax1.set_xticklabels(x_series)

        if coverage_ms < 1 and coverage_ms > 0:
            coverage_ms = "<1"
        if coverage_us < 1 and coverage_us > 0:
            coverage_us = "<1"

        ax2.legend((rects1[0], rects2[0]), (
            'Latency in ms (' + str(coverage_ms) + '%)',
            'Latency in us  (' + str(coverage_us) + '%)'), frameon=False,
            loc='upper left')
        ax2.axis('off')

        def autolabel(rects, axis):
            for rect in rects:
                height = rect.get_height()
                if height >= 1:
                    axis.text(rect.get_x() + rect.get_width() / 2., 1.02 *
                              height, '{}%'.format(int(height)),
                                      ha='center')
                elif height > 0:
                    axis.text(rect.get_x() + rect.get_width() /
                              2., 1.02 * height, '<1%', ha='center')

        autolabel(rects1, ax1)
        autolabel(rects2, ax1)

        plt.tight_layout()

        plt.savefig(mode + "_" + str(depth) + '_histogram.png')
        plt.close('all')

    def plot_latency_histogram(self, mode):

        # not used? latency_data = self.data

        iodepth = self.return_unique_series('iodepth')
        # numjobs = self.return_unique_series('numjobs')
        numjobs = ['1']

        datatypes = ('latency_ms', 'latency_us', 'latency_ns')

        dataset = self.filter_record_set(self.data, 'rw', mode)
        mydict = defaultdict(dict)

        # pprint.pprint(dataset)

        for datatype in datatypes:
            for x in numjobs:
                dx = self.return_record_set(dataset, 'numjobs', x)
                d = self.subselect_record_set(
                    dx, ['numjobs', 'iodepth', datatype])
                for y in iodepth:
                    for record in d:
                        if int(record['iodepth']) == int(y):
                            mydict[datatype][int(y)] = record[datatype]
        for depth in iodepth:

            x_series = []
            y_series1 = []
            y_series2 = []
            y_series3 = []

            temporary = mydict['latency_ms'][1].keys()
            x_series = self.sort_latency_keys(temporary)
            y_series1 = self.sort_latency_data(mydict['latency_ms'][depth])
            y_series2 = self.sort_latency_data(mydict['latency_us'][depth])
            y_series3 = self.sort_latency_data(mydict['latency_ns'][depth])
            y_series2.append(0)
            y_series2.append(0)

            chart_data = {
                'x_series': x_series,
                'y_series1': y_series1,
                'y_series2': y_series2,
                'y_series3': y_series3,
                'iodepth': depth,
                'numjobs': 1,
                'mode': mode

            }

            self.generate_history_chart(chart_data)

#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import pprint
import fiolib.shared_chart as shared
from matplotlib import cm
from mpl_toolkits.mplot3d import axes3d
from datetime import datetime
import matplotlib as mpl
import fiolib.supporting as supporting


class Chart():
    None


class LH_Chart(Chart):

    def sort_latency_keys(self, latency):
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

    def sort_latency_data(self, latency_dict):

        keys = latency_dict.keys()
        values = []
        sorted_keys = self.sort_latency_keys(keys)
        for key in sorted_keys:
            values.append(latency_dict[key])
        return values

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

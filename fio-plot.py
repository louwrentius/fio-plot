#!/usr/bin/env python3
#
# Generates graphs from FIO output data for various IO queue depthts
#
# Output in PNG format.
#
# Requires matplotib and numpy.
#

import os
import sys
import json
import matplotlib.pyplot as plt
import numpy as np
import argparse


class Chart(object):

    def __init__(self, data, settings):
        self.data = data
        self.settings = settings

    def plot_io_and_latency(self, mode):
        fig, (ax, ax3) = plt.subplots(
            nrows=2, gridspec_kw={'height_ratios': [7, 1]})
        ax2 = ax.twinx()
        fig.set_size_inches(10, 6)

        series = {'x_series': [], 'y_series1': [], 'y_series2': [],
                  'y_series3': [], 'y_series4': []}

        keys = list(self.data.keys())
        keys = [int(x) for x in keys]
        keys.sort()

        for x in [str(k) for k in keys]:
            series['x_series'].append(x)
            series['y_series1'].append(self.data[x]['iops'])
            series['y_series2'].append(self.data[x]['lat'])
            series['y_series3'].append(self.data[x]['lat_stddev'])

        # Create series for Standard Deviation table.

        for stddev in series['y_series3']:
            for latency in series['y_series2']:
                p = round((stddev / latency) * 100)
            series['y_series4'].append(str(p))

        x_pos = np.arange(0, len(series['x_series']) * 2, 2)
        width = 0.9

        rects1 = ax.bar(x_pos, series['y_series1'], width, color='#a8ed63')
        rects2 = ax2.bar(x_pos + width, series['y_series2'], width,
                        color='#34bafa')

        ax.set_ylabel('IOP/s')
        ax.set_xlabel('IO queue depth')
        ax2.set_ylabel(r'$Average\ latency\ in\ \mu\ seconds$')

        if self.settings['title']:
            ax.set_title(str(self.settings['title']) + " " + "Random " +
                str(mode))
        else:
            ax.set_title(str(mode) + ' performance')

        ax.set_xticks(x_pos + width / 2)
        ax.set_xticklabels(series['x_series'])

        ax3.legend((rects1[0], rects2[0]),
                  ('Random I/O operations per second',
                      r'$Latency\ in\ \mu s$'), loc='upper left',frameon=False)

        def autolabel(rects, axis):
            for rect in rects:
                height = rect.get_height()
                axis.text(rect.get_x() + rect.get_width() / 2,
                          1.02 * height, '%d' % int(height), ha='center',
                          fontsize=9)

        #
        # Create Standard Deviation Table
        #
        table_vals = [series['x_series'], series['y_series4']]
        cols = len(series['x_series'])
        table = ax3.table(cellText=table_vals, loc='center right', rowLabels=[
                          'IO queue depth', r'$Latency\ \sigma\ \%$'],
                          colLoc='center right',
                          cellLoc='center right', colWidths=[0.05] * cols,
                          rasterized=False)
        table.scale(1,1.2)

        for key, cell in table.get_celld().items():
            cell.set_linewidth(0)

        ax3.axis('off')

        autolabel(rects1, ax)
        autolabel(rects2, ax2)

        if self.settings['source']:
            plt.text(1,-0.08, str(self.settings['source']), ha='right', va='top',
                    transform=ax.transAxes,fontsize=9)

        plt.tight_layout()

        plt.savefig(mode + 'iops_latency.png')
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

    def plot_latency_histogram(self, mode):

        latency_data = self.data
        for depth in sorted(latency_data.keys()):

            keys = latency_data[depth]['latency_ms'].keys()
            x_series = self.get_sorted_mixed_list(keys)
            y_series1 = []
            y_series2 = []
            for key in x_series:
                y_series1.append(latency_data[depth]['latency_ms'][str(key)])
                if isinstance(key, int):
                    if key <= 1000:
                        y_series2.append(
                            latency_data[depth]['latency_us'][str(key)])
                    else:
                        y_series2.append(0)
                else:
                    y_series2.append(0)

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
            ax1.set_title(str(self.settings['title']) + " | "
                    + str(mode).title() +
                ' latency histogram | IO depth ' +
                str(latency_data[depth]['iodepth']))
            ax1.set_xticks(x_pos + width / 2)
            ax1.set_xticklabels(x_series)


            if coverage_ms < 1 and coverage_ms > 0:
                coverage_ms = "<1"
            if coverage_us < 1 and coverage_us > 0:
                coverage_us = "<1"

            legend = ax2.legend((rects1[0], rects2[0]),(
                'Latency in ms (' + str(coverage_ms) + '%)',
                'Latency in us  (' + str(coverage_us) + '%)'),frameon=False,
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
            plt.close()


class benchmark(object):

    def __init__(self, settings):
        self.directory = settings['input_directory']
        self.data = self.getDataSet()
        self.settings = settings

    def listJsonFiles(self, directory):
        absolute_dir = os.path.abspath(directory)
        files = os.listdir(absolute_dir)
        json_files = []
        for f in files:
            if f.endswith(".json"):
                json_files.append(os.path.join(absolute_dir, f))

        return json_files

    def getJSONFileStats(self, filename):
        with open(filename) as json_data:
            d = json.load(json_data)

        return d

    def getDataSet(self):
        d = []
        for f in self.listJsonFiles(self.directory):
            d.append(self.getJSONFileStats(f))

        return d

    def getStats(self, mode):
        result = {}
        for record in self.data:
            depth = record['jobs'][0]['job options']['iodepth'].lstrip("0")
            if record['jobs'][0]['job options']['rw'] == 'rand' + str(mode):
                row = {'iodepth': depth,
                       'iops': record['jobs'][0][mode]['iops'],
                       'lat': record['jobs'][0][mode]['lat']['mean'],
                       'lat_stddev': record['jobs'][0][mode]['lat']['stddev'],
                       'latency_ms': record['jobs'][0]['latency_ms'],
                       'latency_us': record['jobs'][0]['latency_us']}
                result[depth] = row

        return result

    def chart_iops_latency(self, mode):
        stats = self.getStats(mode)
        c = Chart(stats,self.settings)
        c.plot_io_and_latency(mode)

    def chart_latency_histogram(self, mode):
        stats = self.getStats(mode)
        c = Chart(stats,self.settings)
        c.plot_latency_histogram(mode)


def set_arguments():

    parser = argparse.ArgumentParser(description='Convert FIO JSON output \
            to charts')

    ag = parser.add_argument_group(title="Generic Settings")
    ag.add_argument("-i", "--input-directory", help="input directory" )
    ag.add_argument("-t", "--title", help="specifies title to use in charts")
    ag.add_argument("-s", "--source", help="Author" )
    ag.add_argument("-L", "--latency_iops", action='store_true', help="\
            generate latency + iops chart" )
    ag.add_argument("-H", "--histogram", action='store_true', help="\
            generate latency histogram per queue depth" )

    return parser


def main():
    settings = {}

    parser = set_arguments()


    try:
        args = parser.parse_args()
    except OSError:
        parser.print_help()
        sys.exit(1)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)


    settings = vars(args)

    b = benchmark(settings)

    if settings['latency_iops']:
        b.chart_iops_latency('read')
        b.chart_iops_latency('write')

    if settings['histogram']:
        b.chart_latency_histogram('read')
        b.chart_latency_histogram('write')

    if not settings['histogram'] and not settings['latency_iops']:
        parser.print_help()
        print("Specify -L, -H or both")
        exit(1)


if __name__ == "__main__":
    main()

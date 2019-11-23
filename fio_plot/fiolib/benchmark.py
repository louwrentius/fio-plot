#!/usr/bin/env python
import os
import sys
import json


class benchmark(object):

    def __init__(self, settings):
        self.directory = settings['input_directory']
        self.data = self.getDataSet()
        self.settings = settings
        self.stats = []

    def listJsonFiles(self, directory):
        absolute_dir = os.path.abspath(directory)
        files = os.listdir(absolute_dir)
        json_files = []
        for f in files:
            if f.endswith(".json"):
                json_files.append(os.path.join(absolute_dir, f))

        if len(json_files) == 0:
            print(
                "Could not find any JSON files in the specified directory " + str(absolute_dir))
            sys.exit(1)

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

    def get_nested_value(self, dictionary, key):
        for item in key:
            dictionary = dictionary[item]
        return dictionary

    def get_json_mapping(self, mode):
        root = ['jobs', 0]
        jobOptions = root + ['job options']
        data = root + [mode]

        dictionary = {
            'iodepth': (jobOptions + ['iodepth']),
            'numjobs': (jobOptions + ['numjobs']),
            'rw': (jobOptions + ['rw']),
            'iops': (data + ['iops']),
            'lat_ns': (data + ['lat_ns', 'mean']),
            # 'lat': (data + ['lat','mean']),
            'lat_stddev': (data + ['lat_ns', 'stddev']),
            'latency_ms': (root + ['latency_ms']),
            'latency_us': (root + ['latency_us']),
            'latency_ns': (root + ['latency_ns'])
        }

        return dictionary

    def getStats(self):
        stats = []
        for record in self.data:
            # pprint.pprint(record)
            mode = self.get_nested_value(
                record, ('jobs', 0, 'job options', 'rw'))[4:]
            m = self.get_json_mapping(mode)
            # pprint.pprint(m)
            row = {'iodepth': self.get_nested_value(record, m['iodepth']),
                   'numjobs': self.get_nested_value(record, m['numjobs']),
                   'rw': self.get_nested_value(record, m['rw']),
                   'iops': self.get_nested_value(record, m['iops']),
                   'lat': self.get_nested_value(record, m['lat_ns']),
                   'lat_stddev': self.get_nested_value(record, m['lat_stddev']),
                   'latency_ms': self.get_nested_value(record, m['latency_ms']),
                   'latency_us': self.get_nested_value(record, m['latency_us']),
                   'latency_ns': self.get_nested_value(record, m['latency_ns'])}
            stats.append(row)
        self.stats = stats

    def filterStats(self, key, value):
        l = []
        for item in self.stats:
            if item[key] == value:
                l.append(item)
        return l

    def chart_3d_iops_numjobs(self, mode, metric):
        self.getStats()
        config = {}
        config['mode'] = mode
        config['source'] = self.settings['source']
        config['title'] = self.settings['title']
        config['fixed_metric'] = 'numjobs'
        config['fixed_value'] = 1
        config['x_series'] = 'iodepth'
        config['x_series_label'] = 'I/O queue depth'
        config['y_series1'] = 'iops'
        config['y_series1_label'] = 'IOP/s'
        config['y_series2'] = 'lat'
        config['y_series2_label'] = r'$Latency\ in\ ms'
        config['y_series3'] = 'lat_stddev'
        config['maxjobs'] = self.settings['maxjobs']
        config['maxdepth'] = self.settings['maxdepth']
        config['zmax'] = self.settings['max']
        #c = ThreeDee(self.stats, config)
        #c.plot_3d(config['mode'], metric)

    def chart_iops_latency(self, mode):
        self.getStats()
        config = {}
        config['stats'] = self.stats
        config['settings'] = self.settings
        config['mode'] = mode
        config['source'] = self.settings['source']
        config['title'] = self.settings['title']
        config['fixed_metric'] = 'numjobs'
        config['fixed_value'] = self.settings['numjobs']
        config['x_series'] = 'iodepth'
        config['x_series_label'] = 'I/O Depth'
        config['y_series1'] = 'iops'
        config['y_series1_label'] = 'IOP/s'
        config['y_series2'] = 'lat'
        config['y_series2_label'] = r'Latency in ms'
        config['y_series3'] = 'lat_stddev'
        return config

    def chart_latency_histogram(self, mode):
        self.getStats()
        config = {}
        config['mode'] = mode
        config['source'] = self.settings['source']
        config['title'] = self.settings['title']
        config['fixed_metric'] = 'numjobs'
        config['fixed_value'] = 1
        config['x_series'] = 'iodepth'
        config['x_series_label'] = 'I/O Depth'
        config['y_series1'] = 'iops'
        config['y_series1_label'] = 'IOP/s'
        config['y_series2'] = 'lat'
        config['y_series2_label'] = r'$Latency\ in\ \mu$'
        config['y_series3'] = 'lat_stddev'
        #c = LH_Chart(self.stats,self.settings)
        # c.plot_latency_histogram(mode)

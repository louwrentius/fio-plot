import os
import sys
import json


def list_json_files(settings):
    absolute_dir = os.path.abspath(settings['input_directory'])
    files = os.listdir(absolute_dir)
    json_files = []
    for item in files:
        if item.endswith(".json"):
            json_files.append(os.path.join(absolute_dir, item))

    if len(json_files) == 0:
        print(
            "Could not find any JSON files in the specified directory " + str(absolute_dir))
        sys.exit(1)

    return json_files


def import_json_data(filename):
    with open(filename) as json_data:
        d = json.load(json_data)
    return d


def import_json_dataset(fileset):
    d = []
    for f in fileset:
        d.append(import_json_data(f))
    return d


def get_nested_value(dictionary, key):
    for item in key:
        dictionary = dictionary[item]
    return dictionary


def get_json_mapping(mode):
    root = ['jobs', 0]
    jobOptions = root + ['job options']
    data = root + [mode]

    dictionary = {
        'iodepth': (jobOptions + ['iodepth']),
        'numjobs': (jobOptions + ['numjobs']),
        'rw': (jobOptions + ['rw']),
        'iops': (data + ['iops']),
        'iops_stddev': (data + ['iops_stddev']),
        'lat_ns': (data + ['lat_ns', 'mean']),
        # 'lat': (data + ['lat','mean']),
        'lat_stddev': (data + ['lat_ns', 'stddev']),
        'latency_ms': (root + ['latency_ms']),
        'latency_us': (root + ['latency_us']),
        'latency_ns': (root + ['latency_ns'])
    }

    return dictionary


def get_flat_json_mapping(dataset):
    stats = []
    for record in dataset:
        # pprint.pprint(record)
        mode = get_nested_value(
            record, ('jobs', 0, 'job options', 'rw'))[4:]
        m = get_json_mapping(mode)
        # pprint.pprint(m)
        row = {'iodepth': get_nested_value(record, m['iodepth']),
               'numjobs': get_nested_value(record, m['numjobs']),
               'rw': get_nested_value(record, m['rw']),
               'iops': get_nested_value(record, m['iops']),
               'iops_stddev': get_nested_value(record, m['iops_stddev']),
               'lat': get_nested_value(record, m['lat_ns']),
               'lat_stddev': get_nested_value(record, m['lat_stddev']),
               'latency_ms': get_nested_value(record, m['latency_ms']),
               'latency_us': get_nested_value(record, m['latency_us']),
               'latency_ns': get_nested_value(record, m['latency_ns'])}
        stats.append(row)
    return stats


def filterStats(self, key, value):
    l = []
    for item in self.stats:
        if item[key] == value:
            l.append(item)
    return l

import os
import sys
import json
import pprint


def list_json_files(settings):
    """List all JSON files that maches the command line settings."""
    for directory in settings['input_directory']:
        absolute_dir = os.path.abspath(directory)
        files = os.listdir(absolute_dir)
        json_files = []
        for item in files:
            if item.endswith(".json"):
                if item.startswith(settings['rw']):
                    json_files.append(os.path.join(absolute_dir, item))

    if len(json_files) == 0:
        print(
            "Could not find any (matching) JSON files in the specified directory " + str(absolute_dir))
        sys.exit(1)

    return json_files


def import_json_data(filename):
    """Returns a dictionary of imported JSON data."""
    with open(filename) as json_data:
        d = json.load(json_data)
    return d


def import_json_dataset(fileset):
    """Returns a list of imported raw JSON data for every file in the fileset.
    """
    d = []
    for f in fileset:
        d.append(import_json_data(f))
    return d


def get_nested_value(dictionary, key):
    """This function reads the data from the FIO JSON file based on the supplied
    key (which is often a nested path within the JSON file).
    """
    for item in key:
        dictionary = dictionary[item]
    return dictionary


def get_json_mapping(mode):
    """ This function contains a hard-coded mapping of FIO nested JSON data
    to a flat dictionary.
    """
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
        'lat_stddev': (data + ['lat_ns', 'stddev']),
        'latency_ms': (root + ['latency_ms']),
        'latency_us': (root + ['latency_us']),
        'latency_ns': (root + ['latency_ns'])
    }

    return dictionary


def get_flat_json_mapping(settings, dataset):
    """This function returns a list of simplified dictionaries based on the
    data within the supplied json data."""
    stats = []
    for record in dataset:
        if settings['rw'] == 'randrw':
            if settings['filter'][0]:
                mode = settings['filter'][0]
            else:
                print(
                    "When processing randrw data, a -f filter (read/write) must also be specified.")
                exit(1)
        elif settings['rw'] == 'read' or settings['rw'] == 'write':
            mode = settings['rw']
        else:
            mode = get_nested_value(
                record, ('jobs', 0, 'job options', 'rw'))[4:]
        m = get_json_mapping(mode)
        row = {'iodepth': get_nested_value(record, m['iodepth']),
               'numjobs': get_nested_value(record, m['numjobs']),
               'rw': get_nested_value(record, m['rw']),
               'iops': get_nested_value(record, m['iops']),
               'iops_stddev': get_nested_value(record, m['iops_stddev']),
               'lat': get_nested_value(record, m['lat_ns']),
               'lat_stddev': get_nested_value(record, m['lat_stddev']),
               'latency_ms': get_nested_value(record, m['latency_ms']),
               'latency_us': get_nested_value(record, m['latency_us']),
               'latency_ns': get_nested_value(record, m['latency_ns']),
               'type': mode}
        stats.append(row)
    return stats

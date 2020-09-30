import os
import sys
import json
import pprint


def filter_json_files(settings, filename):
    """ Filter the json files to only those we need.
    My ambition is to learn to program and do this right one day.
    """
    basename = os.path.basename(filename)
    splitone = str.split(basename, '.')
    split = str.split(splitone[0], '-')
    iodepth = int(split[1])
    numjobs = int(split[2])

    if iodepth in settings['iodepth'] and numjobs in settings['numjobs']:
        return filename


def list_json_files(settings):
    """List all JSON files that maches the command line settings."""
    json_files = []
    for directory in settings['input_directory']:
        absolute_dir = os.path.abspath(directory)
        dict_structure = {'directory': absolute_dir, 'files': []}
        files = os.listdir(absolute_dir)
        for item in files:
            if item.endswith(".json"):
                if item.startswith(settings['rw']):
                    dict_structure['files'].append(
                        os.path.join(absolute_dir, item))
        json_files.append(dict_structure)

    for item in json_files:
        file_list = []
        for f in item['files']:
            result = filter_json_files(settings, f)
            if result:
                file_list.append(result)
        item['files'] = file_list
        if not item['files']:
            print(
                f"\nCould not find any (matching) JSON files in the specified directory {str(absolute_dir)}\n")
            print(f"Are the correct directories specified?\n")
            print(
                f"If so, please check the -d ({settings['iodepth']}) -n ({settings['numjobs']}) and -r ({settings['rw']}) parameters.\n")
            sys.exit(1)

    # pprint.pprint(json_files)
    return json_files


def import_json_data(filename):
    """Returns a dictionary of imported JSON data."""
    with open(filename) as json_data:
        try:
            d = json.load(json_data)
        except json.decoder.JSONDecodeError:
            print(f"Failed to JSON parse {filename}")
            sys.exit(1)
    return d


def import_json_dataset(dataset):
    """The dataset is a list of dicts containing the absolute path and the file list.
    We need to add a third key/value pair with the ingested data of those files.
    """
    for item in dataset:
        item['rawdata'] = []
        # pprint.pprint(item['files'])
        for f in item['files']:
            item['rawdata'].append(import_json_data(f))
    return dataset


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
        'latency_ns': (root + ['latency_ns']),
        'cpu_usr': (root + ['usr_cpu']),
        'cpu_sys': (root + ['sys_cpu']),
    }

    return dictionary


def get_flat_json_mapping(settings, dataset):
    """This function returns a list of simplified dictionaries based on the
    data within the supplied json data."""
    for item in dataset:
        item['data'] = []
        for record in item['rawdata']:
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
                   'type': mode,
                   'cpu_sys': get_nested_value(record, m['cpu_sys']),
                   'cpu_usr': get_nested_value(record, m['cpu_usr'])}
            item['data'].append(row)
        # item['rawdata'] = None # --> enable to throw away the data after parsing.
    return dataset

from . import (
    jsonparsing_support as jsonsupport
)


def printkeys(data, depth=0, maxdepth=3):
    """
    For debugging only
    """
    if depth <= maxdepth:
        if isinstance(data, dict):
            for key,value in data.items():
                print(f"{'-' * depth} {key}")
                printkeys(value, depth+1)
        elif isinstance(data, list):
            for item in data:
                printkeys(item, depth+1)



def get_json_root_path(record):
    rootpath = None
    keys = record.keys()
    if "jobs" in keys:
        rootpath = "jobs"
    if "client_stats" in keys:
        rootpath = "client_stats"
    if rootpath is None:
        print("\nNo valid JSON root path found, this should never happen.\n")
    return rootpath


def get_json_global_options(record):
    options = {}
    if "global options" in record.keys():
        options = record["global options"]
    return options


def sort_list_of_dictionaries(settings, data):
    sortedlist = sorted(data, key=lambda k: (int(k["iodepth"]), int(k["numjobs"])))
    return sortedlist



def build_json_mapping(settings, dataset):
    """
    This funcion traverses the relevant JSON structure to gather data
    and store it in a flat dictionary. We do this for each imported json file.
    """
    for directory in dataset: # for directory in list of directories
        directory["data"] = []
        for record in directory["rawdata"]: # each record is the raw JSON data of a file in a directory
            jsonrootpath = get_json_root_path(record)
            globaloptions = get_json_global_options(record)
            jsonsupport.process_json_record(settings, directory, record, jsonrootpath, globaloptions)

    directory["data"] = sort_list_of_dictionaries(settings, directory["data"])
    return dataset

def parse_json_data(settings, dataset):
    dataset = build_json_mapping(settings, dataset)
    #for data in dataset:
    #    for item in data['data']:
    #        print(f"{item['hostname']} - {item['iodepth']} - {item['numjobs']} : iops {item['iops']}")
    return dataset


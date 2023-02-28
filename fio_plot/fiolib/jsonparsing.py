from operator import itemgetter
import pprint


def check_for_steadystate(record, mode):
    keys = record["job options"].keys()
    if "steadystate" in keys: # remember that we merged global options into job options to make them accessible
        return True
    else:
        return False

def check_for_hostname(record, mode):
    keys = record.keys()
    if "hostname" in keys: # remember that we merged global options into job options to make them accessible
        return True
    else:
        return False

def get_json_mapping(mode, record):
    """This function contains a hard-coded mapping of FIO nested JSON data
    to a flat dictionary.
    """
    #print(record)
    #print(record["job options"].keys())
    dictionary = {
        "job options": record["job options"],
        "type": mode,
        "iodepth": record["job options"]["iodepth"],
        "numjobs": record["job options"]["numjobs"],
        "bs": record["job options"]["bs"],
        "rw": record["job options"]["rw"],
        "bw": record[mode]["bw"],
        "iops": record[mode]["iops"],
        "iops_stddev": record[mode]["iops_stddev"],
        "lat": record[mode]["lat_ns"]["mean"],
        "lat_stddev": record[mode]["lat_ns"]["stddev"],
        "latency_ms": record["latency_ms"],
        "latency_us": record["latency_us"],
        "latency_ns": record["latency_ns"],
        "cpu_usr": record["usr_cpu"],
        "cpu_sys": record["sys_cpu"]

    }

    # This is hideous, terrible code, I know.
    if check_for_steadystate(record, mode):
        dictionary["ss_attained"] = record["steadystate"]["attained"]
        dictionary["ss_settings"] = record["job options"]["steadystate"] # remember we merged global options into job options
        dictionary["ss_data_bw_mean"] = record["steadystate"]["data"]["bw_mean"]
        dictionary["ss_data_iops_mean"] = record["steadystate"]["data"]["iops_mean"]

    else:
        dictionary["ss_attained"] = None
        dictionary["ss_settings"] = None
        dictionary["ss_data_bw_mean"] = None
        dictionary["ss_data_iops_mean"] = None
    
    if check_for_hostname(record, mode):
        dictionary["hostname"] = record["hostname"]
    

    return dictionary

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

def get_record_mode(settings): # any of the rw modes must be translated to read or write
    mapping = {
        "randrw": settings["filter"][0],
        "read": "read",
        "write": "write",
        "rw": settings["filter"][0],
        "readwrite": settings["filter"][0],
        "randread": "read",
        "randwrite": "write"
    }
    mode = mapping[settings["rw"]]
    return mode

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

def return_data_row(settings, record):
    mode = get_record_mode(settings)
    data = get_json_mapping(mode, record)
    #pprint.pprint(data)
    return data


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
            joboptions = None
            for job in record[jsonrootpath]:
                if job["jobname"] != "All clients":
                    job["job options"] = {**job["job options"], **globaloptions}
                    if not joboptions:               
                        joboptions = job["job options"]
                else:
                    job["job options"] = joboptions    
                    job["hostname"] = "All clients"
                row = return_data_row(settings, job)  
                row["fio_version"] = record["fio version"]
                directory["data"].append(row)
            directory["data"] = sort_list_of_dictionaries(settings, directory["data"])
    return dataset

def parse_json_data(settings, dataset):
    dataset = build_json_mapping(settings, dataset)
    #for data in dataset:
    #    for item in data['data']:
    #        print(f"{item['hostname']} - {item['iodepth']} - {item['numjobs']} : iops {item['iops']}")
    return dataset


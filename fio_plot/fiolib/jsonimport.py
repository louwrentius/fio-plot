import os
import sys
import json
import logging
import pprint

logger = logging.getLogger(__name__)

def filter_json_files(settings, filename):
    """A bit of a slow process, but guarantees that we get legal
    json files regardless of their names"""
    with open(filename, 'r') as candidate_file:
       try:
            candidate_json = json.load(candidate_file)
            if candidate_json["fio version"]:
                if "global options" in candidate_json.keys():
                    job_options = candidate_json["jobs"][0]["job options"] 
                    job_options.update(candidate_json["global options"])
                else:
                    job_options = candidate_json["jobs"][0]["job options"]
                if job_options["rw"] == settings["rw"]:
                    iodepth = int(job_options["iodepth"])
                    numjobs = int(job_options["numjobs"])
                    if iodepth in settings["iodepth"] and numjobs in settings["numjobs"]:
                        return filename
            else:
                logger.debug(f"{filename} does not appear to be a valid fio json output file, skipping")
       except Exception as e:
            print(f"Error: {repr(e)} - please report this as a bug and please include the JSON file if possible.")
            sys.exit(1)


def list_json_files(settings, fail=True):
    """List all JSON files that maches the command line settings."""
    input_directories = []
    for directory in settings["input_directory"]:
        absolute_dir = os.path.abspath(directory)
        input_dir_struct = {"directory": absolute_dir, "files": []}
        input_dir_files = os.listdir(absolute_dir)
        for file in input_dir_files:
            if file.endswith(".json"):
                input_dir_struct["files"].append(os.path.join(absolute_dir, file))
        input_directories.append(input_dir_struct)

    for directory in input_directories:
        file_list = []
        for file in directory["files"]:
            result = filter_json_files(settings, file)
            if result:
                file_list.append(result)

        directory["files"] = sorted(file_list)
        if not directory["files"] and fail:
            print(
                f"\nCould not find any (matching) JSON files in the specified directory {str(absolute_dir)}\n"
            )
            print("Are the correct directories specified?\n")
            print(
                f"If so, please check the -d ({settings['iodepth']}) -n ({settings['numjobs']}) and -r ({settings['rw']}) parameters.\n"
            )
            sys.exit(1)
    # pprint.pprint(json_files)
    return input_directories


def import_json_data(filename):
    """Returns a dictionary of imported JSON data."""
    with open(filename) as json_data:
        try:
            d = json.load(json_data)
        except json.decoder.JSONDecodeError:
            print(f"Failed to JSON parse {filename}")
            sys.exit(1)
    return d


def import_json_dataset(settings, dataset):
    """The dataset is a list of dicts containing the absolute path and the file list.
    We need to add a third key/value pair with the ingested data of those files.
    """
    for item in dataset:
        item["rawdata"] = []
        # pprint.pprint(item['files'])
        for f in item["files"]:
            item["rawdata"].append(import_json_data(f))
    return dataset


def get_nested_value(dictionary, key):
    """This function reads the data from the FIO JSON file based on the supplied
    key (which is often a nested path within the JSON file).
    """
    if not key:
        return None
    for item in key:
        dictionary = dictionary[item]
    return dictionary


def check_for_steadystate(dataset, mode):
    keys = dataset[0]["rawdata"][0]["jobs"][0].keys()
    if "steadystate" in keys:
        return True
    else:
        return False


def walk_dictionary(dictionary, path):
    result = dictionary
    for item in path:
        result = result[item]
    return result


def validate_job_option_key(dataset, key):
    mykeys = dataset['jobs'][0]['job options'].keys()
    if key in mykeys:
        return True
    else:
        raise KeyError


def validate_job_options(dataset, key):
    # Job options can either be in the job or in global options.
    # Sometimes some options are in one and others in the other.
    # We need to figure out which one.
    jobOptionsRaw = ["jobs", 0, "job options"]
    try:
        walk_dictionary(dataset[0]['rawdata'][0], jobOptionsRaw)
        validate_job_option_key(dataset[0]['rawdata'][0], key)
        return jobOptionsRaw
    except KeyError:
        return ['global options']


def validate_number_of_jobs(dataset):
    length = len(dataset[0]['rawdata'][0]['jobs'])
    if length > 1:
        print(f"\n Unfortunately, fio-plot can't deal (yet) with JSON files containing multiple ({length}) jobs\n")
        print("See also: https://github.com/louwrentius/fio-plot/issues/64")
        sys.exit(1)


def get_json_mapping(mode, dataset):
    """This function contains a hard-coded mapping of FIO nested JSON data
    to a flat dictionary.
    """
    validate_number_of_jobs(dataset)
    root = ["jobs", 0]
    jobOptions = validate_job_options(dataset, "numjobs")
    data = root + [mode]
    dictionary = {
        "fio_version": ["fio version"],
        "iodepth": (validate_job_options(dataset, "iodepth") + ["iodepth"]),
        "numjobs": (validate_job_options(dataset, "numjobs") + ["numjobs"]),
        "bs": (validate_job_options(dataset, "bs") + ["bs"]),
        "rw": (validate_job_options(dataset, "rw") + ["rw"]),
        "bw": (data + ["bw"]),
        "iops": (data + ["iops"]),
        "iops_stddev": (data + ["iops_stddev"]),
        "lat_ns": (data + ["lat_ns", "mean"]),
        "lat_stddev": (data + ["lat_ns", "stddev"]),
        "latency_ms": (root + ["latency_ms"]),
        "latency_us": (root + ["latency_us"]),
        "latency_ns": (root + ["latency_ns"]),
        "cpu_usr": (root + ["usr_cpu"]),
        "cpu_sys": (root + ["sys_cpu"]),
    }

    # This is hideous, terrible code, I know.
    if check_for_steadystate(dataset, mode):
        dictionary["ss_attained"] = root + ["steadystate"] + ["attained"]
        dictionary["ss_settings"] = ["global options"] + ["steadystate"]
        dictionary["ss_data_bw_mean"] = root + ["steadystate"] + ["data"] + ["bw_mean"]
        dictionary["ss_data_iops_mean"] = (
                root + ["steadystate"] + ["data"] + ["iops_mean"]
        )

    else:
        dictionary["ss_attained"] = None
        dictionary["ss_settings"] = None
        dictionary["ss_data_bw_mean"] = None
        dictionary["ss_data_iops_mean"] = None

    return dictionary


def get_flat_json_mapping(settings, dataset):
    """This function returns a list of simplified dictionaries based on the
    data within the supplied json data."""
    for item in dataset:
        item["data"] = []
        for record in item["rawdata"]:
            options = validate_job_options(dataset, "numjobs")
            if settings["rw"] == "randrw":
               mode = settings["filter"][0]
            elif settings["rw"] == "read" or settings["rw"] == "write":
                mode = settings["rw"]
            elif settings["rw"] == "rw":
                mode = settings['filter'][0]
            elif settings["rw"] == "readwrite":
                mode = settings['filter'][0]
            else:
                mode = get_nested_value(record, options + ["rw"])[4:]
            m = get_json_mapping(mode, dataset)
            row = {
                "iodepth": int(get_nested_value(record, m["iodepth"])),
                "numjobs": int(get_nested_value(record, m["numjobs"])),
                "bs": get_nested_value(record, m["bs"]),
                "rw": get_nested_value(record, m["rw"]),
                "iops": get_nested_value(record, m["iops"]),
                "iops_stddev": get_nested_value(record, m["iops_stddev"]),
                "lat": get_nested_value(record, m["lat_ns"]),
                "lat_stddev": get_nested_value(record, m["lat_stddev"]),
                "latency_ms": get_nested_value(record, m["latency_ms"]),
                "latency_us": get_nested_value(record, m["latency_us"]),
                "latency_ns": get_nested_value(record, m["latency_ns"]),
                "bw": get_nested_value(record, m["bw"]),
                "type": mode,
                "cpu_sys": get_nested_value(record, m["cpu_sys"]),
                "cpu_usr": get_nested_value(record, m["cpu_usr"]),
                "ss_attained": get_nested_value(record, m["ss_attained"]),
                "ss_data_bw_mean": get_nested_value(record, m["ss_data_bw_mean"]),
                "ss_data_iops_mean": get_nested_value(record, m["ss_data_iops_mean"]),
                "ss_settings": get_nested_value(record, m["ss_settings"]),
                "fio_version": get_nested_value(record, m["fio_version"]),
            }
            item["data"].append(row)
            # item["rawdata"] = None  # --> enable to throw away the data after parsing.
    return dataset

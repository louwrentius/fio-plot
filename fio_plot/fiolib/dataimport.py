import os
import sys
import csv
import pprint as pprint
import re
import statistics
from pathlib import Path
from . import dataimport_support as ds

def get_hostname_from_filename(f):
    split = f.split(".")
    rawhostname = split[3:]
    hostname = ".".join(rawhostname)
    return hostname

def list_fio_log_files(directory):
    """
    Lists all .log files in a directory. Exits with an error if no files are found.
    client/server log files ending in the hostname are also detected.
    """
    absolute_dir = os.path.abspath(directory)
    files = os.listdir(absolute_dir)
    fiologfiles = []
    for f in files:
        absolutefilepath = os.path.join(absolute_dir, f)
        structure = { "hostname": None, "filename": absolutefilepath}
        if f.endswith(".log"):
            fiologfiles.append(structure)
        elif ".log." in f:
            structure["hostname"] = get_hostname_from_filename(f)
            fiologfiles.append(structure)

    if len(fiologfiles) == 0:
        print(
            f"\nCould not find any log files in the specified directory {str(absolute_dir)}"
        )
        print("\nAre the correct directories specified?")
        print("\nIf so, please check the -d -n and -r parameters.\n")
        sys.exit(1)
    return fiologfiles


def limit_path_part_size(path, length):
    parts = path.parts
    raw_result = [x[:length] for x in parts]
    result = "/".join(raw_result)
    return result


def return_folder_name(filename, settings, override=False):
    segment_size = settings["xlabel_segment_size"]
    parent = settings["xlabel_parent"]
    xlabeldepth = settings["xlabel_depth"]
    raw_path = Path(filename).resolve()
    #print(settings)
    if override:
        raw_path = raw_path.parent

    if xlabeldepth > 0:
        raw_path = raw_path.parents[xlabeldepth - 1]

    upperpath = raw_path.parents[parent]

    relative_path = raw_path.relative_to(upperpath)

    relative_path_processed = limit_path_part_size(relative_path, segment_size)
    return relative_path_processed


def return_filename_filter_string(settings):
    """Returns a list of dicts with, a key/value for the search string.
    This string is used to filter the log files based on the command line
    parameters.
    """
    searchstrings = []

    rw = settings["rw"]
    iodepths = settings["iodepth"]
    numjobs = settings["numjobs"]
    benchtypes = settings["type"]

    for benchtype in benchtypes:
        for iodepth in iodepths:
            for numjob in numjobs:
                searchstring = f"{rw}-iodepth-{iodepth}-numjobs-{numjob}_{benchtype}"
                attributes = {
                    "rw": rw,
                    "iodepth": iodepth,
                    "numjobs": numjob,
                    "type": benchtype,
                    "searchstring": searchstring,
                }
                searchstrings.append(attributes)
    return searchstrings


def filterLogFiles(settings, file_list):
    """
    Returns a list of log files that matches the supplied filter string(s).
    """
    searchstrings = return_filename_filter_string(settings)
    #print(searchstrings)
    result = []
    for item in file_list:
        for searchstring in searchstrings:
            filename = os.path.basename(item["filename"])
            # print(filename)
            if re.search(r"^" + searchstring["searchstring"], filename):
                data = {"filename": item}
                data.update(searchstring)
                data["directory"] = return_folder_name(item["filename"], settings, True)
                data["hostname"] = item["hostname"]
                result.append(data)
    if len(result) > 0:
        return result
    else:
        print(
            f"\nNo log files found that matches the specified parameter {settings['rw']}\n"
        )
        print(
            f"Check parameters iodepth {settings['iodepth']} and numjobs {settings['numjobs']}?\n"
        )
        exit(1)


def mergeSingleDataSet(data, datatype):
    """In this function we merge all data for one particular set of files.
    For examle, iodepth = 1 and numjobs = 8. The function returns one single
    dataset containing the summed/averaged data.
    """
    #print("==============")
    #for x in data: 
    #    print(f"Merge single dataset - {x['hostname']} - {x['filename']} - {type(x['data'])}")
    merged_set = []
    hostdatamerged = {}
    regulardatamerged = []

    for record in data:
        if record["hostname"]:
            if record["hostname"] not in hostdatamerged.keys():
                hostdatamerged[record["hostname"]] = []
            hostdatamerged[record["hostname"]].append(record)
        else:
            regulardatamerged.append(record)


    if hostdatamerged:
        for host in hostdatamerged.keys():
            result = ds.newMergeLogDataSet(hostdatamerged[host], datatype, host)
            merged_set.append(result)
    elif regulardatamerged:
        merged_set.append(ds.newMergeLogDataSet(regulardatamerged,datatype))
    else:
        print("ERROR")
        sys.exit(1)
    #merged_set = ds.mergeLogDataSet(data, datatype, hostlist)
    return merged_set


def get_unique_directories(dataset):
    directories = []
    for item in dataset:
        dirname = item["directory"]
        if dirname not in directories:
            directories.append(dirname)
    return directories


def mergeDataSet(settings, dataset):
    """We need to merge multiple datasets, for multiple iodepts and numjob
    values. The return is a list of those merged datasets.

    We also take into account if multiple folders are specified to compare
    benchmarks results across different runs.
    """
    merged_sets = []
    filterstrings = return_filename_filter_string(settings)
    directories = get_unique_directories(dataset)

    for directory in directories:
        for filterstring in filterstrings:
            record = {
                "type": filterstring["type"],
                "iodepth": filterstring["iodepth"],
                "numjobs": filterstring["numjobs"],
                "directory": directory,
                
            }
            data = []
            for item in dataset:
                if (
                    filterstring["searchstring"] in item["searchstring"]
                    and item["directory"] == directory
                ):
                    data.append(item)
            
            newdata = mergeSingleDataSet(data, filterstring["type"]) # read write hostname
            #print(newdata["hostname"])
            record["data"] = newdata
            merged_sets.append(record)
    return merged_sets


def parse_raw_cvs_data(settings, dataset):
    """This function exists mostly because I tried to test the performance
    of a 1.44MB floppy drive. The device is so slow that it can't keep up.
    This results in records that span multiple seconds, skewing the graphs.
    If this is detected, the data is averaged over the interval between records.
    """
    new_set = []
    distance_list = []
    for index, item in enumerate(dataset):
        if index == 0:
            continue
        else:
            distance = int(item["timestamp"]) - int(dataset[index - 1]["timestamp"])
            distance_list.append(distance)
    try:
        mean = int(statistics.mean(distance_list))
    except statistics.StatisticsError as e:
        print(f"ERROR: {e}")
        print("\n Could this be because of an empty log file?\n")
        sys.exit(1)

    if mean > 1000:
        #print(
        #    f"\n{supporting.bcolors.WARNING}Warning: > 1000msec log interval found\n"
        #    f"{supporting.bcolors.ENDC}"
        #    "\nIf the log_avg_msec parameter used to generate the log data is < 1000 msec\n"
        #    "it is stronly advised to cross-verify the output of the graph with the\n"
        #    "appropriate values found in the .json output if available.\n\n"
        #    "It may be advised to rerun your benchmarks with log_avg_msec = 1000 or higher\n"
        #    "to achieve correct results.\n\n"
        #)

        # log data with a log_avg_msec higher than 1000 msec should be converted back
        # to values per 1000 msec
        for index, item in enumerate(dataset):
            if index == 0:
                average_value = int(item["value"]) / int(item["timestamp"]) * 1000

            else:
                previous_timestamp = int(dataset[index - 1]["timestamp"])
                distance = int(item["timestamp"]) - previous_timestamp
                number_of_seconds = int(distance / 1000)
                try:
                    average_value = int(item["value"]) / distance * mean
                except ZeroDivisionError as e:
                    print(e)
                    print(f"{item['value']} - {distance} - {mean}")
                    continue
                for x in range(number_of_seconds):
                    temp_dict = dict(item)
                    temp_dict["value"] = average_value
                    temp_dict["timestamp"] = previous_timestamp + x
                    new_set.append(temp_dict)
        return new_set
    else:
        return dataset


def readLogData(settings, inputfile):
    """FIO log data is imported as CSV data. The scope is the import of a
    single file.
    """
    dataset = []
    if os.path.exists(inputfile["filename"]):
        #print(inputfile)
        with open(inputfile["filename"]) as csv_file:
            csv.register_dialect("CustomDialect", skipinitialspace=True, strict=True)
            csv_reader = csv.DictReader(
                csv_file,
                dialect="CustomDialect",
                delimiter=",",
                fieldnames=["timestamp", "value", "rwt", "blocksize", "offset"],
            )
            for item in csv_reader:
                dataset.append(item)
    dataset = parse_raw_cvs_data(settings, dataset)
    return dataset


def readLogDataFromFiles(settings, inputfiles):
    """Returns a list of imported datasets based on the input files."""
    data = []
    for inputfile in inputfiles:
        logdata = readLogData(settings, inputfile["filename"])
        logdict = {"data": logdata, "hostname": inputfile["hostname"]}
        logdict.update(inputfile)
        data.append(logdict)
    return data

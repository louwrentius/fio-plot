import sys
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


def sort_list_of_dictionaries(data):
    sortedlist = sorted(data, key=lambda k: (int(k["iodepth"]), int(k["numjobs"])))
    return sortedlist


def process_json_record(settings, directory, record, jsonrootpath, globaloptions):
    joboptions = None
    hosts = {}
    jobs = []
    for job in record[jsonrootpath]:
        # This section is just to deal with the "All clients" job included in 
        # client / server JSON output
        #
        if job["jobname"] != "All clients":
            job["job options"] = {**job["job options"], **globaloptions}
            if not joboptions:               
                joboptions = job["job options"]
        else:
            job["job options"] = joboptions    
            job["hostname"] = "All clients"
        #
        # End of section
        #
        if jsonsupport.check_for_valid_hostname(job):
            hostname = job["hostname"]
            if hostname not in hosts.keys():
                hosts[hostname] = []
        row = jsonsupport.return_data_row(settings, job)  
        row["fio_version"] = record["fio version"]
        if hosts:
            hosts[hostname].append(row)
        else:
            jobs.append(row)
          
    directory["data"].extend(jsonsupport.merge_job_data_hosts_jobs(settings, hosts, jobs))

    
def parse_json_data(settings, dataset):
    """
    This funcion traverses the relevant JSON structure to gather data
    and store it in a flat dictionary. We do this for each imported json file.
    """
    for directory in dataset: # for directory in list of directories
        directory["data"] = []
        for record in directory["rawdata"]: # each record is the raw JSON data of a file in a directory
            jsonrootpath = get_json_root_path(record)
            globaloptions = get_json_global_options(record)
            #for item in record["client_stats"]:
            #    if "job options" in item.keys():
            #        print(item["job options"]["iodepth"])
            process_json_record(settings, directory, record, jsonrootpath, globaloptions)
    #print("================================")
    #print(directory["data"])
    #for directory in dataset:
    #    for item in directory["data"]:
    #        print(item["iodepth"])
    directory["data"] = sort_list_of_dictionaries(directory["data"])
    return dataset




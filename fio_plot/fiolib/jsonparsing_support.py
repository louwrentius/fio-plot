import statistics

def check_for_hostname(record):
    keys = record.keys()
    if "hostname" in keys: # remember that we merged global options into job options to make them accessible
        return True
    else:
        return False
    
def check_for_valid_hostname(record):
    result = None
    if check_for_hostname(record):
        if record["hostname"]:
            result = True
        else:
            result = False
    else:
        result = False
    return result

def merge_job_data(settings, hosts):
  
    processed = []

    for host in hosts.keys():
        iops = []
        bw = []
        lat = []
        template = { "type": hosts[host][0]["type"], "iodepth": hosts[host][0]["iodepth"], "numjobs": hosts[host][0]["numjobs"], "hostname": host, "fio_version": hosts[host][0]["fio_version"], \
                     "rw": hosts[host][0]["rw"], "bs": hosts[host][0]["bs"]
                    }    

        for job in hosts[host]:
            iops.append(job["iops"])
            bw.append(job["bw"])
            lat.append(job["lat"])

        template["iops"] = sum(iops)
        template["bw"] = sum(bw)
        template["lat"] = statistics.mean(lat)
        processed.append(template)

    return processed



def process_json_record(settings, directory, record, jsonrootpath, globaloptions):
    joboptions = None
    hosts = {}
    jobs = []
    just_append = False
    for job in record[jsonrootpath]:
        if job["jobname"] != "All clients":
            job["job options"] = {**job["job options"], **globaloptions}
            if not joboptions:               
                joboptions = job["job options"]
        else:
            job["job options"] = joboptions    
            job["hostname"] = "All clients"
        if check_for_valid_hostname(job):
            hostname = job["hostname"]
            if hostname not in hosts.keys():
                hosts[hostname] = []
        row = return_data_row(settings, job)  
        row["fio_version"] = record["fio version"]
        if hosts:
            hosts[hostname].append(row)
        else:
            jobs.append(row)
    if hosts:
        for host in hosts.keys():
            if len(hosts[host]) > 1 or host == "All clients":
                #print(host)
                directory["data"] = merge_job_data(settings, hosts)
            else:
                just_append = True
    else:
        just_append = True
    if just_append:
        [ directory["data"].append(x) for x in jobs ]




def return_data_row(settings, record):
    mode = get_record_mode(settings)
    data = get_json_mapping(mode, record)
    #pprint.pprint(data)
    return data

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
    
    if check_for_hostname(record):
        dictionary["hostname"] = record["hostname"]
    

    return dictionary

def check_for_steadystate(record, mode):
    keys = record["job options"].keys()
    if "steadystate" in keys: # remember that we merged global options into job options to make them accessible
        return True
    else:
        return False
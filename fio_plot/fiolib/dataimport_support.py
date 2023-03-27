import statistics

def get_hosts_from_data(data):
    hosts = set()
    for record in data:
        hosts.add(record["hostname"])
    
    if all(x is None for x in hosts):
        hosts = None
    else:
        hosts = list(hosts)
    return hosts


def getMergeOperation(datatype):
    """FIO log files with a numjobs larger than 1 generates a separate file
    for each job thread. So if numjobs is 8, there will be eight files.

    We need to merge the data from all those job files into one result.
    Depending on the type of data, we must sum or average the data.

    This function returns the appropriate function/operation based on the type.
    """

    operationMapping = {
        "iops": sum,
        "lat": statistics.mean,
        "clat": statistics.mean,
        "slat": statistics.mean,
        "bw": sum,
        "timestamp": statistics.mean,
    }

    opfunc = operationMapping[datatype]
    return opfunc


def newMergeLogDataSet(data, datatype, hostname=None):
    mergedSet = {"read": [], "write": [], "hostname": hostname}
    lookup = {"read": 0, "write": 1}
    for rw in ["read", "write"]:
        for column in ["timestamp", "value"]:
            unmergedSet = []
            for record in data:
                templist = []
                for row in record["data"]:
                    if int(row["rwt"]) == lookup[rw]:
                        templist.append(int(row[column]))
                unmergedSet.append(templist)
            if column == "value":
                oper = getMergeOperation(datatype)
            else:
                oper = getMergeOperation(column)
            merged = [oper(x) for x in zip(*unmergedSet)]
            mergedSet[rw].append(merged)
        mergedSet[rw] = list(zip(*mergedSet[rw]))
    return mergedSet



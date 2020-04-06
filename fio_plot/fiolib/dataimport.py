import os
import sys
import csv
import pprint as pprint
import statistics
import fiolib.supporting as supporting


def list_fio_log_files(directory):
    """Lists all .log files in a directory. Exits with an error if no files are found.
    """
    absolute_dir = os.path.abspath(directory)
    files = os.listdir(absolute_dir)
    fiologfiles = []
    for f in files:
        if f.endswith(".log"):
            fiologfiles.append(os.path.join(absolute_dir, f))

    if len(fiologfiles) == 0:
        print("Could not find any log \
             files in the specified directory " + str(absolute_dir))
        sys.exit(1)

    return fiologfiles


def return_folder_name(filename):
    dirname = os.path.dirname(filename)
    basename = os.path.basename(dirname)
    return(basename)


def return_filename_filter_string(settings):
    """Returns a list of dicts with, a key/value for the search string.
    This string is used to filter the log files based on the command line
    parameters.
    """
    searchstrings = []

    rw = settings['rw']
    iodepths = settings['iodepth']
    numjobs = settings['numjobs']
    benchtypes = settings['type']

    for benchtype in benchtypes:
        for iodepth in iodepths:
            for numjob in numjobs:
                searchstring = f"{rw}-iodepth-{iodepth}-numjobs-{numjob}_{benchtype}"
                attributes = {'rw': rw, 'iodepth': iodepth,
                              'numjobs': numjob, 'type': benchtype,
                              'searchstring': searchstring}
                searchstrings.append(attributes)
    return searchstrings


def filterLogFiles(settings, file_list):
    """Returns a list of log files that matches the supplied filter string(s).
    """
    searchstrings = return_filename_filter_string(settings)
    # pprint.pprint(searchstrings)
    result = []
    for item in file_list:
        for searchstring in searchstrings:
            if searchstring['searchstring'] in item:
                data = {'filename': item}
                data.update(searchstring)
                data['directory'] = return_folder_name(item)
                result.append(data)
    # pprint.pprint(result)
    if len(result) > 0:
        return result
    else:
        print(
            f"\nNo log files found that matches the specified parameter {settings['rw']}\n")
        exit(1)


def getMergeOperation(datatype):
    """ FIO log files with a numjobs larger than 1 generates a separate file
    for each job thread. So if numjobs is 8, there will be eight files.

    We need to merge the data from all those job files into one result.
    Depending on the type of data, we must sum or average the data.

    This function returns the appropriate function/operation based on the type.
    """

    operationMapping = {'iops': sum,
                        'lat': statistics.mean,
                        'clat': statistics.mean,
                        'slat': statistics.mean,
                        'bw': sum,
                        'timestamp': statistics.mean}

    opfunc = operationMapping[datatype]
    return opfunc


def mergeSingleDataSet(data, datatype):
    """In this function we merge all data for one particular set of files.
    For examle, iodepth = 1 and numjobs = 8. The function returns one single
    dataset containing the summed/averaged data.
    """
    mergedSet = {'read': [], 'write': []}
    lookup = {'read': 0, 'write': 1}

    for rw in ['read', 'write']:
        for column in ['timestamp', 'value']:
            unmergedSet = []
            for record in data:
                templist = []
                for row in record['data']:
                    if int(row['rwt']) == lookup[rw]:
                        templist.append(int(row[column]))
                unmergedSet.append(templist)
            if column == 'value':
                oper = getMergeOperation(datatype)
            else:
                oper = getMergeOperation(column)
            merged = [oper(x) for x in zip(*unmergedSet)]
            mergedSet[rw].append(merged)
        mergedSet[rw] = list(zip(*mergedSet[rw]))
    return mergedSet


def get_unique_directories(dataset):
    directories = []
    for item in dataset:
        dirname = item['directory']
        if dirname not in directories:
            directories.append(dirname)
    return directories


def mergeDataSet(settings, dataset):
    """We need to merge multiple datasets, for multiple iodepts and numjob
    values. The return is a list of those merged datasets.

    We also take into account if multiple folders are specified to compare
    benchmarks results across different runs.
    """
    mergedSets = []
    filterstrings = return_filename_filter_string(settings)
    directories = get_unique_directories(dataset)

    for directory in directories:
        for filterstring in filterstrings:
            record = {'type': filterstring['type'],
                      'iodepth': filterstring['iodepth'], 'numjobs': filterstring['numjobs'], 'directory': directory}
            data = []
            for item in dataset:
                if filterstring['searchstring'] in item['searchstring'] and \
                        item['directory'] == directory:
                    data.append(item)
            newdata = mergeSingleDataSet(data, filterstring['type'])
            record['data'] = newdata
            mergedSets.append(record)
    return mergedSets


def parse_raw_cvs_data(dataset):
    """This function exists mostly because I tried to test the performance
    of a 1.44MB floppy drive. The device is so slow that it can't keep up.
    This results in records that span multiple seconds, skewing the graphs.
    If this is detected, the data is averaged over the interval between records.
    Although this shows a more realistic throughput of 
    """
    new_set = []
    distance_list = []
    for index, item in enumerate(dataset):
        if index == 0:
            continue
        else:
            distance = int(item['timestamp']) - \
                int(dataset[index - 1]['timestamp'])
            distance_list.append(distance)
    mean = statistics.mean(distance_list)
    if mean > 1000:
        print(f"{supporting.bcolors.WARNING} WARNING: the storage could not "
              f"keep up with the configured I/O request size. Data is interpolated.{supporting.bcolors.ENDC}")
        for index, item in enumerate(dataset):
            if index == 0:
                average_value = int(item['value']) / \
                    int(item['timestamp']) * 1000

            else:
                previous_timestamp = int(dataset[index - 1]['timestamp'])
                distance = int(item['timestamp']) - previous_timestamp
                number_of_seconds = int(distance / 1000)
                average_value = int(item['value']) / distance * 1000
                for x in range(number_of_seconds):
                    temp_dict = dict(item)
                    temp_dict['value'] = average_value
                    temp_dict['timestamp'] = previous_timestamp + x
                    new_set.append(temp_dict)
        return new_set
    else:
        return dataset


def readLogData(inputfile):
    """FIO log data is imported as CSV data. The scope is the import of a
    single file.
    """
    dataset = []
    if os.path.exists(inputfile):
        with open(inputfile) as csv_file:
            csv.register_dialect('CustomDialect', skipinitialspace=True,
                                 strict=True)
            csv_reader = csv.DictReader(
                csv_file, dialect='CustomDialect', delimiter=',',
                fieldnames=['timestamp', 'value', 'rwt', 'blocksize', 'offset'])
            for item in csv_reader:
                dataset.append(item)
    dataset = parse_raw_cvs_data(dataset)
    return dataset


def readLogDataFromFiles(settings, inputfiles):
    """Returns a list of imported datasets based on the input files.
    """
    data = []
    for inputfile in inputfiles:
        logdata = readLogData(inputfile['filename'])
        logdict = {"data": logdata}
        logdict.update(inputfile)
        data.append(logdict)
    return data

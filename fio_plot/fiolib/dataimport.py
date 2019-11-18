import os
import sys
import csv
import pprint as pprint
import statistics


def listFioLogFiles(directory):
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


def returnFilenameFilterString(settings):
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


def filterLogFiles(settings, fileList):
    searchstrings = returnFilenameFilterString(settings)
    # pprint.pprint(searchstrings)
    result = []
    for item in fileList:
        for searchstring in searchstrings:
            if searchstring['searchstring'] in item:
                data = {'filename': item}
                data.update(searchstring)
                result.append(data)
    # pprint.pprint(result)
    return result


def getValueSetsFromData(settings, dataset):

    result = {}
    iodepth = []
    numjobs = []
    benchtype = []

    for item in dataset:
        iodepth.append(item['iodepth'])
        numjobs.append(item['numjobs'])
        benchtype.append(item['type'])

    result = {'iodepth': list(set(iodepth)),
              'numjobs': list(set(numjobs)),
              'type': list(set(benchtype))}

    return result


def getMergeOperation(datatype):

    operationMapping = {'iops': sum,
                        'lat': statistics.mean,
                        'clat': statistics.mean,
                        'slat': statistics.mean,
                        'bw': sum,
                        'timestamp': statistics.mean}

    opfunc = operationMapping[datatype]
    return opfunc


def mergeSingleDataSet(data, datatype):
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


def mergeDataSet(settings, dataset):
    mergedSets = []
    filterstrings = returnFilenameFilterString(settings)
    # pprint.pprint(dataset)
    for filterstring in filterstrings:
        record = {'type': filterstring['type'],
                  'iodepth': filterstring['iodepth'], 'numjobs': filterstring['numjobs']}
        data = []
        for item in dataset:
            if filterstring['searchstring'] in item['searchstring']:
                data.append(item)
        data = mergeSingleDataSet(data, filterstring['type'])
        record['data'] = data
        mergedSets.append(record)
    return mergedSets


def readLogData(inputfile):
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
    return dataset


def readLogDataFromFiles(settings, inputfiles):
    data = []
    for inputfile in inputfiles:
        logdata = readLogData(inputfile['filename'])
        logdict = {"data": logdata}
        logdict.update(inputfile)
        data.append(logdict)
    return data

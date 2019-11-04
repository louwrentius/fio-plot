import os
import sys
import csv
from pathlib import Path
import pprint as pprint
import statistics
import itertools


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
                searchstring = str(rw) + "-iodepth-" + str(iodepth) + \
                    "-numjobs-" + str(numjob) + "_" + str(benchtype)
                attributes = {'rw': rw, 'iodepth': iodepth,
                              'numjobs': numjob, 'type': benchtype, 'searchstring': searchstring}
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
    pprint.pprint(result)
    return result


def getValueSetsFromData(dataset):

    result = {}
    iodepth = []
    numjobs = []
    benchtype = []
    pprint.pprint(dataset)
    for item in dataset:
        iodepth.append(item['iodepth'])
        numjobs.append(item['numjobs'])
        benchtype.append(item['type'])

    result = {'iodepth': list(set(iodepth)),
              'numjobs': list(set(numjobs)),
              'type': list(set(benchtype))}
    return result


def mergeSingleDataSet(dataset, iodepths, numjobs, datatypes):

    grouped = []

    for iodepth in iodepths:
        for numjob in numjobs:
            for datatype in datatypes:
                for item in dataset:
                    if item['iodepth'] == iodepth and item['numjobs'] == numjob and item['datatype'] == datatype:
                        grouped.append(item)

    # for item in dataset:
    #    for benchtype in

    # if operation in ['sum', 'mean']:
    #    templist = []
    #    for item in dataset['data']:
    #        templist.append(item[datatype])
    #    mergedset.append(templist)
    #    if operation == 'sum':
    #        merged = [sum(x) for x in zip(*mergedset)]
    #    if operation == 'mean':
    #        merged = [statistics.mean(x) for x in zip(*mergedset)]
    #    return merged


def mergeDataSet(dataset):

    mergedSets = []
    result = getValueSetsFromData(dataset)

    # for item in types:
    #    for data in dataset:
    #        # pprint.pprint(item)
    #        timestamps = mergeSingleDataSet(item, 'timestamp', 'mean')
    #        values = mergeSingleDataSet(item, 'value', 'sum')
    #        mergedSets.append(list(zip(timestamps, values)))
    # pprint.pprint(mergedSets)
    # return mergedSets


def readLogData(inputfile):
    dataset = []
    if os.path.exists(inputfile):
        with open(inputfile) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for item in csv_reader:
                data = {}
                data['timestamp'] = (int(item[0].strip()))
                data['value'] = (int(item[1].strip()))
                dataset.append(data)
    return dataset


def readLogDataFromFiles(settings, inputfiles):
    data = []
    # pprint.pprint(inputfiles)
    for inputfile in inputfiles:
        # filename = Path(inputfile['filename']).resolve().stem
        logdata = readLogData(inputfile['filename'])
        logdict = {"data": logdata}
        logdict.update(inputfile)
        data.append(logdict)
    return data

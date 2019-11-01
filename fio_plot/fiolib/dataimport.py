import os
import sys
import csv
from pathlib import Path
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
    rw = settings['rw']
    iodepth = settings['iodepth']
    numjobs = settings['numjobs']
    benchtype = settings['type']

    searchstring = str(rw) + "-iodepth-" + str(iodepth) + "-numjobs-" + str(numjobs) + "_" + str(benchtype)
    return str(searchstring)

def filterLogFiles(settings, fileList):
    searchstring = returnFilenameFilterString(settings)
    #pprint.pprint(searchstring)
    result = [ i for i in fileList if str(searchstring) in i ]
    return result

def mergeSingleDataSet(dataset, datatype, operation):
    mergedset = []
    if operation in ['sum', 'mean']:
        for recordset in dataset:
            templist = []
            for item in recordset['data']:
                templist.append(item[datatype])
            mergedset.append(templist)
        if operation == 'sum':
            merged = [sum(x) for x in zip(*mergedset)]
        if operation == 'mean':
            merged = [statistics.mean(x) for x in zip(*mergedset)]
        return merged 

def mergeDataSet(dataset):
    timestamps = mergeSingleDataSet(dataset, 'timestamp', 'mean')
    values = mergeSingleDataSet(dataset, 'value', 'sum')
    return list(zip(timestamps, values))

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
    for inputfile in inputfiles:
        filename = Path(inputfile).resolve().stem
        logdata = readLogData(inputfile)
        logdict = { "filename": filename, "data": logdata }
        data.append(logdict)
    return data
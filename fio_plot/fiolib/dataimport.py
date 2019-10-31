import os
import sys
import csv
from pathlib import Path

def listFioLogFiles(directory):
    absolute_dir = os.path.abspath(directory)
    files = os.listdir(absolute_dir)
    trace_files = []
    for f in files:
        if f.endswith(".log"):
            trace_files.append(os.path.join(absolute_dir, f))

    if len(trace_files) == 0:
        print("Could not find any log \
             files in the specified directory " + str(absolute_dir))
        sys.exit(1)

    return trace_files

def listLogTypeFiles(type, fileList):
    types = ["clat","lat","iops","bw"]
    
    if type in types:
        searchtype = "_"+type+"."
        result = [ i for i in fileList if searchtype in i ]
    return result

def readLogData(inputfile):
    if os.path.exists(inputfile):
        with open(inputfile) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            # /1000 -> miliseconds are converted to seconds
            data = { (int(element[0].strip())/1000): int(element[1].strip())\
                for element in csv_reader}
        return data

def readLogDataCollection(inputfiles):
    data = []
    for inputfile in inputfiles:
        filename = Path(inputfile).resolve().stem.split(".")
        logdata = readLogData(inputfile)
        logdict = { "filename": filename, "data": logdata }
        data.append(logdict)
    return data

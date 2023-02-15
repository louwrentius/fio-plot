## Purpose of this document

To help me remember how fio-plot works when it comes to data ingestion.

## Data sources

fio-plot can parse two types of output: JSON and the .log trace data.
The .log trace data is just CSV data which can only be graphed using the -g style graph. 
All the other graph type need one or more JSON files to work with.

Data collection starts with the getdata.py file containing the get_json_data and get_log_data functions to gather one of these types of files.

When only the log files are charting using the -g graph, fio-plot cheats and tries to read the relevant existing JSON file if it exists, to gather the fio version number.

## File name heuristics

fio-plot expects files to have a certain naming convention, or they won't be found and imported.
This is critical for the .log trace data as there is no identifying information within those files.

JSON files also require this naming convention, although it should not be required as they can be parsed and then selected/filtered based on their contents. If this is a big deal is another discussion, for now this is how it works.

## CSV log data import

CVS log data import is quite complicated because benchmarks using a numjob value higher than 1 will generate a separate log file for each job. Depending on the metric, like bandwidth or IOPs, data across all files need to be summed to obtain the correct values. 

The dataimport.py file contains all this logic. In particular, the "mergedataset" and "mergesingledataset" functions handle all this parsing.

## JSON data import workflow description

1. A list of files is found in the source directory
1. Files that match the rw iodepth and numjobs parameters will be kept
1. A dataset dictionary initially contains a list of files:

```
{'directory': '/Users/nan03/data/WD10KRPM/RAID10_64K',
 'files': ['/Users/nan03/data/WD10KRPM/RAID10_64K/randread-1-1.json',
           '/Users/nan03/data/WD10KRPM/RAID10_64K/randread-16-1.json',
           '/Users/nan03/data/WD10KRPM/RAID10_64K/randread-2-1.json',
           '/Users/nan03/data/WD10KRPM/RAID10_64K/randread-32-1.json',
           '/Users/nan03/data/WD10KRPM/RAID10_64K/randread-4-1.json',
           '/Users/nan03/data/WD10KRPM/RAID10_64K/randread-64-1.json',
           '/Users/nan03/data/WD10KRPM/RAID10_64K/randread-8-1.json'],
 'rawdata': []}
```
4. Each file is json-imported, validated and then the 'rawdata' list contains a JSON-imported dictionary for each JSON file. The order of the files matches the order of the JSON dictionaries in the rawdata list.

We have now collected the raw data, but to use it in graphs, we need to further parse and process it into a different format.

5. The jsonparsing.py module is responsible for pulling all the relevant data from the imported JSON data and put it in a flat dictionary. 

There is a hard-coded mapping of the fields to particular JSON-paths. The way it is setup currently means that we can't work with fio JSON data containing multiple jobs.
For users, the best way to deal with this is to use bench-fio for benchmarking as it generates a separate fio JSON output file for each benchmark test. 

This solution does unfortunately not work for the client-server mechanism that fio supports. (Note: fio client-server benchmarking is supported by bench-fio.) Each test does still generate one JSON output file, but it contains the results of all servers.Instead of a ["jobs"] section, there is a "["client_stats"]" section in the JSON output that works the same way. It's a list of job results, each one the result of one particular server.

6. The build_json_mapping function is fed with the dataset created in step 5 by the jsonparsing code. This is just a list of dictionaries. Each dictionary has a "rawdata" key containing the actual JSON data. The build_json_mapping adds a "data" key to each dictionary in the provided dataset, and the value contains a newly created dictionary of all the data of interest. That dictionary is just a flat dictionary, no nested structure like the original raw JSON. To create this flat dictionary, we use a semi-hard-coded mapping between the values and the "path" in the JSON structure.
This mapping is provided by the  get_json_mapping function. 

The data is now ready to be used by the graphing functions, althoug it does require further parsing and formatting.

## Formatting the data for mathplotlib

At this point, the relevant data is stored in individual dictionaries and it is not in a format suitable for matplotlib graphing yet. Imagine we want to create bar chart with iodepth 1,2,4,8,16,32,64 on the x-axis and the iops on the y-axis.
mathplotlib needs a value for each of those iodepths in a list, but this data is inside individual dictionaries, originating from the JSON output.

The get_record_set and get_record_set_improved functions loop over all iodepths, and then for each iodepth loop over all records to see if they contain relevant data. If so, this data is added to the appropriate list within the 'datadict' dictionary. That dictionary contains the actual data in a format we can almost chart with matplotlib. Almost, because the relevant data must be analised to make sure we apply proper scaling of the graph, which is done by the scale_data function.


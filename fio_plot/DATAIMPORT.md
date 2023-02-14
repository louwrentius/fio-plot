## Purpose of this document

To help me remember how fio-plot works when it comes to data ingestion.

## Data sources

fio-plot can parse two types of output: JSON and the .log trace data.
The .log trace data is just CSV data which can only be graphed using the -g style graph. 
All the other graph type need one or more JSON files to work with.

## File name heuristics

fio-plot expects files to have a certain naming convention, or they won't be found and imported.
This is critical for the .log trace data as there is no identifying information within those files.

JSON files also require this naming convention, although it should not be required as they can be parsed and then selected/filtered based on their contents. 


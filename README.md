### fio-plot
This tool is meant to create nice charts of FIO benchmark runs.
Often you vary the queue depth and/or numjobs of your benchmarks, to gauge how your storage performs under those conditions.

fio-plot consists of a simple example benchmark script that executes multiple tests for you.
You can customise this scripts to your content.

fio-plot.py will generate the actual charts from the json output data.
If you vary both queuedepth and numjobs values, you can even create 3d charts. 

Please note that fio-plot is really geared for testing with variable queuedepth and numjobs values.
It is not flexible enough to chart other values at this point. 

A lot of example data can be found in the 'benchmark_data' folder. 
For all raw benchmark_data input, 2d and 3d images have been generated in the 'images' folder.

### 2d chart 
![2d][2d]

### 3d chart
![3d][3d]

### Usage
Requires: numpy, matplotlib

    usage: fio-plot.py [-h] [-i INPUT_DIRECTORY] [-t TITLE] [-s SOURCE] [-L] [-l]
                       [-H] [-D [MAXDEPTH]] [-J [MAXJOBS]] [-n [NUMJOBS]] [-m MAX]
    
    Convert FIO JSON output to charts
    
    optional arguments:
      -h, --help            show this help message and exit
    
    Generic Settings:
      -i INPUT_DIRECTORY, --input-directory INPUT_DIRECTORY
                            input directory where JSON files can be found
      -t TITLE, --title TITLE
                            specifies title to use in charts
      -s SOURCE, --source SOURCE
                            Author
      -L, --latency_iops_3d
                            generate latency + iops 3d
      -l, --latency_iops_2d
                            generate latency + iops 2d graph
      -H, --histogram       generate latency histogram per queue depth
      -D [MAXDEPTH], --maxdepth [MAXDEPTH]
                            maximum queue depth to graph
      -J [MAXJOBS], --maxjobs [MAXJOBS]
                            maximum numjobs to graph in 3d graph
      -n [NUMJOBS], --numjobs [NUMJOBS]
                            specifies for which numjob parameter you want the 2d
                            graphs to be generated
      -m MAX, --max MAX     optional max value for z-axis

### Caveat

I've made this tool on Mac OS, using brew. I have yet to test this on (a headless) Linux.
Also, the code may leave a lot to be desired, I'm aware of that.

### Benchmark data

I consider the benchmarks on the HP Proliant Gen8 with the P420i RAID controller not representative of the performance of the SSDs.
The only think this data show is the relative performance of the SSDs and how they perform using this particular hardware. 

The benchmarks with the HP Microsoerver Gen8 and Gen10 are mostly limited by the SATA300 interface (normally used to connect CDROM drives) so you will not see maximum possible IOPs.
I do believe the difference between QD=1,2,4 and 8 can be informative even under this condition.


[2d]: https://raw.githubusercontent.com/louwrentius/fio-plot/master/images/HPMICROSERVERG8/SATA300/SAMSUNG680PRO/randread_iodepth_2019-08-25-21%3A58%3A58_1_iops_latency.png
[3d]: https://raw.githubusercontent.com/louwrentius/fio-plot/master/images/HPMICROSERVERG8/SATA300/SAMSUNG680PRO/3d-iops-jobsRandom%20Read-2019-08-25-21%3A58%3A56.png

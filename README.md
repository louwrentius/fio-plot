# fio-plot
Create charts from FIO storage benchmark tool JSON output

    >>>> The code is bad but it works <<<<< 

FIO: https://github.com/axboe/fio

### 2d chart 

### 3d chart



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
        

### fio-plot

[FIO][fio] is a tool for benchmarking storage devices. FIO helps to assess the storage performance in terms of IOPS and latency.

Fio-plot generates charts from FIO storage benchmark data. It can process FIO output in JSON format. It can also process FIO log file output (in CSV format).

[fio]: https://github.com/axboe/fio

To get to these charts, you need to follow this process:

1. Run your tests, maybe use the [included benchmark script][bms]
2. Determine which information you would like to show
3. Run fio-plot to generate the images with the appropriate command line options

[bms]: https://github.com/louwrentius/fio-plot/tree/master/benchmark_script

### 2D chart 
This kind of chart shows both IOPs and Latency for multiple queue depths.
![barchart][queuedepthlowhigh01]

*Please note that these benchmark numbers are not representative of the capabilities of the SSD as the RAID controller is the bottleneck.*

### 3D chart
A 3D bar chart that plots both queue depth an numjobs against either latency or IOPs.

![3dbarchart][3dbarchart]

[3dbarchart]: https://louwrentius.com/static/images/servermdadmraid5-3d.png


### Line chart based on FIO log data
To create this graph, the FIO log data is parsed to show how the device / file
performed during a benchmark run. Latency IOPS and bandwidth can be shown. 
![linechart][queuedepthlowhigh03]

The command line options control which data is shown, so it is possible to
customize the graph to only show the information you're interested in.

*tip:* with the latest version of fio-plot, you can combine log data with the same properties by specifying multiple directories with the -i option. 

This could be very handy if you made some performance tweaks and want to compare results.

### Latency histogram 
The FIO JSON output also contains latency histogram data. It's available in a ns, us and ms scale.
![histogram][histogram]

[histogram]: https://louwrentius.com/static/images/histogram01.png

This is the only chart type that requires / can only show the results of a single benchmark. 

### Benchmark script
A benchmark script is provided alongside fio-plot, that automates the process of running multiple benchmarks with different parameters. For example, it allows
you to gather data for different queue depths and/or number of simultaneous jobs. The benchmark script shows progress in real-time.

	████████████████████████████████████████████████████
			+++ Fio Benchmark Script +++

	Job template:                  fio-job-template.fio
	I/O Engine:                    libaio
	Number of benchmarks:          98
	Estimated duration:            1:38:00
	Devices to be tested:          /dev/md0
	Test mode (read/write):        randrw
	IOdepth to be tested:          1 2 4 8 16 32 64
	NumJobs to be tested:          1 2 4 8 16 32 64
	Blocksize(s) to be tested:     4k
	Mixed workload (% Read):       75 90

	████████████████████████████████████████████████████
	4% |█                        | - [0:04:02, 1:35:00]-]

This particular example benchmark was run with these parameters:

    ./bench-fio.py --target /dev/md0 --type device --template fio-job-template.fio  --mode randrw --output RAID_ARRAY --readmix 75 90

In this example, we run a mixed random read/write benchmark. We have two runs, one with a 75%/25 read/write mix and one with a 90%/10% mix. 

You can run the benchmark against an entire device or a file/folder.
Alongside the benchmark script, a Fio job template file is supplied (fio-job-template.fio). This file can be customised as desired.

For more examples, please consult the separate [README.md][rm]

[rm]: https://github.com/louwrentius/fio-plot/tree/master/benchmark_script

### A note about queue depths
Many SSD vendors report really high IOPs performance numbers, beyond 100.000 IOPs for a single SSD. Those numbers are always obtained using a queue depth of 32 or higher. 

![queuedepthlowhigh01][queuedepthlowhigh01]

[queuedepthlowhigh01]: https://raw.githubusercontent.com/louwrentius/fio-plot/master/images/INTEL-D3-S4610-on-IBM-M1015_2020-01-29_144451.png

In many real-life cases, such queue depths are never
encountered. Often, SSDs can only achieve 10% of those IOPs performance numbers with a queue depth of 1. Such low queue depths are way more common. 

![queuedepthlowhigh02][queuedepthlowhigh02]

[queuedepthlowhigh02]: https://louwrentius.com/static/images/impactofqueuedepth02.png

[queuedepthlowhigh03]: https://louwrentius.com/static/images/impactofqueuedepth03.png

In a virtualized environment, high queue depths and thus high IOPs numbers can be observed if many VMs simultaneously use storage. Individual VMs won't observe very high IOPs, only as a total set of VMs can those high IOPs results be observed.

This is how I understand queue depths and the impact on performance.

### Dependancies

Fio-plot requires 'matplotlib' and 'numpy' to be installed.

### Usage

	usage: fio_plot [-h] [-i INPUT_DIRECTORY] [-T TITLE] [-s SOURCE] [-L] [-l]
					[-H] [--disable-grid] [--enable-markers] [--subtitle SUBTITLE]
					[-d IODEPTH [IODEPTH ...]] [-M [MAXDEPTH]] [-D [DPI]]
					[-p [PERCENTILE]] [-J [MAXJOBS]] [-n NUMJOBS [NUMJOBS ...]]
					[-r {read,write,randread,randwrite,randrw}] [-m MAX]
					[-y MAX_Y] [-g] [-e MOVING_AVERAGE]
					[-t {bw,iops,lat,slat,clat} [{bw,iops,lat,slat,clat} ...]]
					[-f {read,write} [{read,write} ...]]

	Generates charts/graphs from FIO JSON output or logdata.

	optional arguments:
	  -h, --help            show this help message and exit

	Generic Settings:
	  -i INPUT_DIRECTORY, --input-directory INPUT_DIRECTORY
							input directory where JSON files can be found.
	  -T TITLE, --title TITLE
							specifies title to use in charts
	  -s SOURCE, --source SOURCE
							Author
	  -L, --iodepth-numjobs-3d
							Generates a 3D-chart with iodepth and numjobs on x/y
							axis and iops or latency on the z-axis.
	  -l, --latency-iops-2d
							Generates a 2D barchart of IOPs and latency for a
							particular queue depth and numjobs value.
	  -H, --histogram       Generates a latency histogram for a particular queue
							depth and numjobs value.
	  --disable-grid        Disables the dotted grid in the output graph.
	  --enable-markers      Enable markers for the plot lines.
	  --subtitle SUBTITLE   Specify your own subtitle or leave it blank with
							double quotes.
	  -d IODEPTH [IODEPTH ...], --iodepth IODEPTH [IODEPTH ...]
							The I/O queue depth to graph.
	  -M [MAXDEPTH], --maxdepth [MAXDEPTH]
							Maximum queue depth to graph in 3D graph.
	  -D [DPI], --dpi [DPI]
							The chart will be saved with this DPI setting. Higher
							means larger image.
	  -p [PERCENTILE], --percentile [PERCENTILE]
							Calculate the percentile, default 99.99th.
	  -J [MAXJOBS], --maxjobs [MAXJOBS]
							Maximum number of jobs to graph in 3D graph.
	  -n NUMJOBS [NUMJOBS ...], --numjobs NUMJOBS [NUMJOBS ...]
							Specifies for which numjob parameter you want the 2d
							graphs to be generated. You can specify multiple
							values separated by spaces.
	  -r {read,write,randread,randwrite,randrw}, --rw {read,write,randread,randwrite,randrw}
							Specifies the kind of data you want to graph.
	  -m MAX, --max MAX     Optional maximum value for Z-axis in 3D graph.
	  -y MAX_Y, --max-y MAX_Y
							Optional maximum value for y-axis.
	  -g, --loggraph        This option generates a 2D graph of the log data
							recorded by FIO.
	  -e MOVING_AVERAGE, --moving-average MOVING_AVERAGE
							The moving average helps to smooth out graphs, the
							argument is the size of the moving window (default is
							None to disable). Be carefull as this setting may
							smooth out issues you may want to be aware of.
	  -t {bw,iops,lat,slat,clat} [{bw,iops,lat,slat,clat} ...], --type {bw,iops,lat,slat,clat} [{bw,iops,lat,slat,clat} ...]
							This setting specifies which kind of metric you want
							to graph.
	  -f {read,write} [{read,write} ...], --filter {read,write} [{read,write} ...]
							filter should be read/write.


### Example Usage

Creating a 2D Bar Chart based on randread data and numjobs = 1.

    ./fio_plot -i <benchmark_data_folder> -T "Title" -s https://louwrentius.com -l -n 1 -r randread

Creating a 3D graph showing IOPS. 

    ./fio_plot -i <benchmark_data_folder> -T "Title" -s https://louwrentius.com -L -r randread -t iops
    
Creating a 3D graph with a subselection of data

    ./fio_plot -i <benchmark_data_folder> -T "Title" -s https://louwrentius.com -L -r randread -t iops -J 16 -M 16

Creating a latency histogram with a queue depth of 1 and numjobs is 1.

    ./fio_plot -i <benchmark_data_folder> -T "Title" -s https://louwrentius.com -H -r randread -d 1 -n 1

Creating a line chart from different benchmark runs in a single folder

    ./fio_plot -i <benchmark_data_folder>  -T "Test" -g -r randread -t iops lat -d 1 8 16 -n 1
  
The same result but if you want markers to help distinguish between lines:

    ./fio_plot -i <benchmark_data_folder>  -T "Test" -g -r randread -t iops lat -d 1 8 16 -n 1 --enable--markers
    
Create a line chart based on data from two different folders (but the same benchmark parameters)     

    ./fio_plot -i <benchmark_data_folder A> <benchmark_data_folder B>  -T "Test" -g -r randread -t iops lat -d 8 -n 1
    
For example, you can run a benchmark on a RAID10 setup and store data in folder A. Store the benchmark data for a RAID5 setup in folder B and you can compare the results of both RAID setups in a single Line graph.

Please note that the folder names are used in the graph to distinguish the datasets. Example:

[![multipledataset][multipledataset]][multipledataset]

[multipledataset]: https://louwrentius.com/static/images/comparingraid10raid5new.png
   
Command used: 

    ./fio_plot -i ../../RAID10 ../../RAID5 -T "Comparing RAID 10 vs. RAID 5 on 10,000 RPM Drives" -s https://louwrentius.com -g -r randread -t iops lat -d 8 -n 1 
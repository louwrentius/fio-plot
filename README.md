## fio-plot

[FIO][fio] is a tool for benchmarking storage devices. FIO helps to assess the storage performance in terms of IOPS and latency.

Fio-plot generates charts from FIO storage benchmark data. It can process FIO output in JSON format. It can also process FIO log file output (in CSV format).

[fio]: https://github.com/axboe/fio

To get to these charts, you need to follow this process:

1. Run your tests, maybe use the [included benchmark script][bms]
2. Determine which information you would like to show
3. Run fio-plot to generate the images with the appropriate command line options

[bms]: https://github.com/louwrentius/fio-plot/tree/master/benchmark_script

## 2D chart (iodepth)
This kind of chart shows both IOPs and Latency for different queue depths.
![barchart][2dchartiodepth]

[2dchartiodepth]: https://louwrentius.com/static/images/fio-plot/fioplot0001.png

This is the command-line used to generate this graph:

    fio_plot -i INTEL_D3-S4610 --source "https://louwrentius.com" -T "INTEL D3-S4610 SSD on IBM M1015" -l -r randread

## 2D chart (numjobs)
This kind of chart shows both IOPs and Latency for diffent simultaneous number of jobs.
![barchart][2dchartnumjobs]

[2dchartnumjobs]: https://louwrentius.com/static/images/fio-plot/fioplot0002.png

This is the command-line used to generate this graph:

    fio_plot -i INTEL_D3-S4610 --source "https://louwrentius.com" -T "INTEL D3-S4610 SSD on IBM M1015" -N -r randread

## 2D chart to compare benchmark results

The compare chart shows the results from multiple different benchmarks in one graph. The graph data is always for a specific queue depth and numjobs values (the examples use qd=1, nj=1 (the default)). 

![barchart][2dchartcompare]

[2dchartcompare]: https://louwrentius.com/static/images/fio-plot/fioplot0003.png

This is the command-line used to generate this graph:

    fio_plot -i INTEL_D3-S4610 SAMSUNG_860_PRO KINGSTON_DC500M SAMSUNG_PM883 --source "https://louwrentius.com" -T "Comparing the performance of various Solid State Drives" -C -r randread --xlabel-parent 0

It is also possible to group the bars for IOPs and Latency like this:

![barchart][2dchartcomparegroup]

[2dchartcomparegroup]: https://louwrentius.com/static/images/fio-plot/fioplot0004.png

This is the command-line used to generate this graph:
   
    fio_plot -i INTEL_D3-S4610 SAMSUNG_860_PRO KINGSTON_DC500M SAMSUNG_PM883 --source "https://louwrentius.com" -T "Comparing the performance of various Solid State Drives" -C -r randread --xlabel-parent 0 --group-bars


## 3D chart
A 3D bar chart that plots both queue depth an numjobs against either latency or IOPs. This example shows IOPs.

![3dbarchart][3dbarchartiops]

[3dbarchartiops]: https://louwrentius.com/static/images/fio-plot/fioplot0005.png

This is the command-line used to generate this graph:

    fio_plot -i RAID10 --source "https://louwrentius.com"  -T "RAID10 performance of 8 x WD Velociraptor 10K RPM" -L -t iops -r randread

It is also possible to chart the latency:

![3dbarchart][3dbarchartlat]

[3dbarchartlat]: https://louwrentius.com/static/images/fio-plot/fioplot0006.png

This is the command-line used to generate this graph:

    fio_plot -i RAID10 --source "https://louwrentius.com"  -T "RAID10 performance of 8 x WD Velociraptor 10K RPM" -L -t lat -r randread

## Line chart based on FIO log data

Fio records a 'performance trace' of various metrics, such as IOPs and latency over time in plain-text .log 
files. If you use the benchmark tool included with fio-plot, this data is logged every 0.5 seconds.

This data can be parsed and graphed over time. In this example, we plot the data for four different solid state drives in one chart. 

![linechart][linegraph01]

[linegraph01]: https://louwrentius.com/static/images/fio-plot/fioplot0012.png

This is the command-line used to generate this graph:

    fio_plot -i INTEL_D3-S4610/ KINGSTON_DC500M/ SAMSUNG_PM883/ SAMSUNG_860_PRO/ --source "https://louwrentius.com"  -T "Comparing IOPs performance of multiple SSDs" -g -t iops -r randread --xlabel-parent 0

It is also possible to chart the latency instead of IOPs.

![linechart][linegraph02]

[linegraph02]: https://louwrentius.com/static/images/fio-plot/fioplot0013.png

This is the command-line used to generate this graph:

    fio_plot -i INTEL_D3-S4610/ KINGSTON_DC500M/ SAMSUNG_PM883/ SAMSUNG_860_PRO/ --source "https://louwrentius.com"  -T "Comparing latency performance of multiple SSDs" -g -t lat -r randread --xlabel-parent 0

You can also include all information in one graph:

![linechart][linegraph03]

[linegraph03]: https://louwrentius.com/static/images/fio-plot/fioplot0009.png

This is the command-line used to generate this graph:

    fio_plot -i INTEL_D3-S4610/ KINGSTON_DC500M/ --source "https://louwrentius.com"  -T "Comparing performance of multiple SSDs" -g -t iops lat -r randread --xlabel-parent 0    

And this is an example with a single benchmark run, comparing the performance of multiple queue depths.

![linechart][linegraph04]

[linegraph04]: https://louwrentius.com/static/images/fio-plot/fioplot0010.png

This is the command-line used to generate this graph:

    fio_plot -i INTEL_D3-S4610 --source "https://louwrentius.com"  -T "Comparing multiple queue depths" -g -t iops lat -r randread -d 1 8 16  --xlabel-parent 0    

## Latency histogram 
The FIO JSON output also contains latency histogram data. It's available in a ns, us and ms scale.

![histogram][histogram01]

[histogram01]: https://louwrentius.com/static/images/fio-plot/fioplot0011.png

This is the command-line used to generate this graph:

    fio_plot -i SAMSUNG_860_PRO/ --source "https://louwrentius.com"  -T "Historgram of SSD" -H -r randread -d 16 -n 16

## Benchmark script
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

    ./bench_fio --target /dev/md0 --type device --template fio-job-template.fio  --mode randrw --output RAID_ARRAY --readmix 75 90

In this example, we run a mixed random read/write benchmark. We have two runs, one with a 75% / 25% read/write mix and one with a 90% / 10% mix. 

You can run the benchmark against an entire device or a file/folder.
Alongside the benchmark script, a Fio job template file is supplied (fio-job-template.fio). This file can be customised as desired.

For more examples, please consult the separate [README.md][rm]

[rm]: https://github.com/louwrentius/fio-plot/tree/master/benchmark_script

## Dependancies

Fio-plot requires 'matplotlib' and 'numpy' to be installed.

Please note that Fio-plot requires at least matplotlib version 3.3.0

Fio-plot also writes metadata to the PNG files using Pillow

## Usage

    usage: bench_fio [-h] -d TARGET [TARGET ...] -t {device,file,directory}
                 [-s SIZE] -o OUTPUT [-j TEMPLATE]
                 [-b BLOCK_SIZE [BLOCK_SIZE ...]]
                 [--iodepth IODEPTH [IODEPTH ...]]
                 [--numjobs NUMJOBS [NUMJOBS ...]] [--runtime RUNTIME] [-p]
                 [--precondition-repeat]
                 [--precondition-template PRECONDITION_TEMPLATE]
                 [-m MODE [MODE ...]] [--rwmixread RWMIXREAD [RWMIXREAD ...]]
                 [-e ENGINE] [--direct DIRECT] [--loops LOOPS] [--time-based]
                 [--entire-device] [--ss SS] [--ss-dur SS_DUR]
                 [--ss-ramp SS_RAMP]
                 [--extra-opts EXTRA_OPTS [EXTRA_OPTS ...]]
                 [--invalidate INVALIDATE] [--quiet]
                 [--loginterval LOGINTERVAL] [--dry-run]

    Automates FIO benchmarking. It can run benchmarks with different iodepths,
    jobs or other properties.

    optional arguments:
    -h, --help            show this help message and exit

    Generic Settings:
    -d TARGET [TARGET ...], --target TARGET [TARGET ...]
                            Storage device / directory / file to be tested
    -t {device,file,directory}, --type {device,file,directory}
                            Target type, device, file or directory
    -s SIZE, --size SIZE  File size if target is a file. If target is a
                            directory, a file of the specified size is created per
                            job
    -o OUTPUT, --output OUTPUT
                            Output directory for .json and .log output. If a
                            read/write mix is specified, separate directories for
                            each mix will be created.
    -j TEMPLATE, --template TEMPLATE
                            Fio job file in INI format. A file is already included
                            and this parameter is only required if you create your
                            own custom Fio job. (Default: ./fio-job-template.fio)
    -b BLOCK_SIZE [BLOCK_SIZE ...], --block-size BLOCK_SIZE [BLOCK_SIZE ...]
                            Specify block size(s). (Default: ['4k']
    --iodepth IODEPTH [IODEPTH ...]
                            Override default iodepth test series ([1, 2, 4, 8, 16,
                            32, 64]). Usage example: --iodepth 1 8 16
    --numjobs NUMJOBS [NUMJOBS ...]
                            Override default number of jobs test series ([1, 2, 4,
                            8, 16, 32, 64]). Usage example: --numjobs 1 8 16
    --runtime RUNTIME     Override the default test runtime per
                            benchmark(default: 60)
    -p, --precondition    With this option you can specify an SSD precondition
                            workload prior to performing actualbenchmarks. If you
                            don't precondition SSDs before running a benchmark,
                            results may notreflect actual real-life performance
                            under sustained load. (default: False).
    --precondition-repeat
                            After every individual benchmark, the preconditioning
                            run is executed (again). (Default: False).
    --precondition-template PRECONDITION_TEMPLATE
                            The Fio job template containing the precondition
                            workload(default=precondition.fio
    -m MODE [MODE ...], --mode MODE [MODE ...]
                            List of I/O load tests to run (default: ['randread',
                            'randwrite'])
    --rwmixread RWMIXREAD [RWMIXREAD ...]
                            If a mix of read/writes is specified with --testmode,
                            the ratio of reads vs. writes can be specified with
                            this option. the parameter is an integer and
                            represents the percentage of reads. A read/write mix
                            of 75%/25% is specified as '75' (default: None).
                            Multiple values can be specified and separate output
                            directories will be created. This argument is only
                            used if the benchmark is of type randrw. Otherwise
                            this option is ignored.
    -e ENGINE, --engine ENGINE
                            Select the ioengine to use, see fio --enghelp for an
                            overview of supported engines. (Default: libaio).
    --direct DIRECT       Use DIRECT I/O (default: 1)
    --loops LOOPS         Each individual benchmark is repeated x times
                            (default: 1)
    --time-based          All benchmarks are time based, even if a test size is
                            specifiedLookt at the Fio time based option for more
                            information.(default: False).
    --entire-device       The benchmark will keep running until all sectors are
                            read or written to.(default: False).
    --ss SS               Detect and exit on achieving steady state (spefial Fio
                            feature, 'man fio' for more detials) (default: False)
    --ss-dur SS_DUR       Steady state window (default: None)
    --ss-ramp SS_RAMP     Steady state ramp time (default: None)
    --extra-opts EXTRA_OPTS [EXTRA_OPTS ...]
                            Allows you to add extra options, for example, options
                            that are specific to the selected ioengine. It can be
                            any other Fio option. Example: --extra-opts
                            norandommap=1 invalidate=0 You may also choose to add
                            those options to the fio_template.fio file.
    --invalidate INVALIDATE
                            From the Fio manual: Invalidate buffer-cache for the
                            file prior to starting I/O.(Default: 1)
    --quiet               The progresbar will be supressed.
    --loginterval LOGINTERVAL
                            Interval that specifies how often stats are logged to
                            the .log files. (Default: 500
    --dry-run             Simulates a benchmark, does everything except running
                            Fio.

## Example Usage

### 2D Bar Charts

Creating a 2D Bar Chart based on randread data and numjobs = 1 (default).

    ./fio_plot -i <benchmark_data_folder> -T "Title" -s https://louwrentius.com -l -r randread

![regularbars][regular]

[regular]: https://louwrentius.com/static/images/iodepthregular.png

Creating a 2D Bar Chart based on randread data and numjobs = 8.

    ./fio_plot -i <benchmark_data_folder> -T "Title" -s https://louwrentius.com -l -n 8 -r randread

Creating a 2D Bar Chart grouping iops and latency data together: 

    ./fio_plot -i <benchmark_data_folder> -T "Title" -s https://louwrentius.com -l -r randread --group-bars

![groupedbars][grouped]

[grouped]: https://louwrentius.com/static/images/iodepthgroupbars.png

### 3D Bar Chart

Creating a 3D graph showing IOPS. 

    ./fio_plot -i <benchmark_data_folder> -T "Title" -s https://louwrentius.com -L -r randread -t iops
    
Creating a 3D graph with a subselection of data

    ./fio_plot -i <benchmark_data_folder> -T "Title" -s https://louwrentius.com -L -r randread -t iops -J 16 -M 16

### 2D Bar Histogram

Creating a latency histogram with a queue depth of 1 and numjobs is 1.

    ./fio_plot -i <benchmark_data_folder> -T "Title" -s https://louwrentius.com -H -r randread -d 1 -n 1

Creating a line chart from different benchmark runs in a single folder

    ./fio_plot -i <benchmark_data_folder>  -T "Test" -g -r randread -t iops lat -d 1 8 16 -n 1
  
The same result but if you want markers to help distinguish between lines:

    ./fio_plot -i <benchmark_data_folder>  -T "Test" -g -r randread -t iops lat -d 1 8 16 -n 1 --enable--markers

![markers][markers]

[markers]: https://louwrentius.com/static/images/enablemarkers.png

### Comparing two or more benchmarks based on JSON data (2D Bar Chart):

A simple example where we compare the iops and latency of a particular iodepth and numjobs value:

    ./fio_plots -i <folder_a> <folder_b> <folder_c> -T "Test" -C -r randwrite -d 8 

![compare01][compare01]

[compare01]: https://louwrentius.com/static/images/compareexample01.png 

The bars can also be grouped: 

![compare03][compare03]

[compare03]: https://louwrentius.com/static/images/compareexample03.png 

There is also an option (--show-cpu) that includes a table with CPU usage:

![comparecpu][comparecpu]

[comparecpu]: https://louwrentius.com/static/images/comparecpu.png

### Comparing two or more benchmarks in a single line chart

Create a line chart based on data from two different folders (but the same benchmark parameters)     

    ./fio_plot -i <benchmark_data_folder A> <benchmark_data_folder B>  -T "Test" -g -r randread -t iops lat -d 8 -n 1

I'm assuming that the benchmark was created with the (included) bench_fio tool.

For example, you can run a benchmark on a RAID10 setup and store data in folder A. Store the benchmark data for a RAID5 setup in folder B and you can compare the results of both RAID setups in a single Line graph.

Please note that the folder names are used in the graph to distinguish the datasets. 

[![multipledataset][multipledataset]][multipledataset]

[multipledataset]: https://louwrentius.com/static/images/comparingraid10raid5new.png
   
Command used: 

    fio_plot -i ./IBM1015/RAID10/4k/ ./IBM1015/RAID5/4k/ -T "Comparing RAID 10 vs. RAID 5 on 10,000 RPM Drives" -s https://louwrentius.com -g -r randread -t iops lat -d 8 -n 1

If you use the bench_fio tool to generate benchmark data, you may notice that you end up with folders like:

    IBM1015/RAID10/4k
    IBM1015/RAID5/4k

Those parent folders are used to distinguish and identify the lines from each other. The labels are based on the parent folder names as you can see in the graph. By default, we use only one level deep, so in this example only RAID10/4k or RAID5/4k are used. If we want to include the folder above that (IBM1015) we use the --xlabel-parent parameter like so:

    fio_plot -i ./IBM1015/RAID10/4k/ ./IBM1015/RAID5/4k/ -T "Comparing RAID 10 vs. RAID 5 on 10,000 RPM Drives" -s https://louwrentius.com -g -r randread -t iops lat -d 8 -n 1 -w 1 --xlabel-parent 2

This would look like: 

[![labellength][labellength]][labellength]

[labellength]: https://louwrentius.com/static/images/labellength.png

Some additional examples to explain how you can trim the labels to contain exactly the directories you want:

The default:

    RAID10/4k

Is equivalent to --xlabel-parent 1 --xlabel-depth 0. So by default, the parent folder is included. 
If you strip off the 4k folder with --xlabel-depth 1, you'll notice that the label becomes:

    IBM1015/RAID10 

This is because the default --xlabel-parent is 1 and the index now starts at 'RAID10'. 

If you want to strip off the 4k folder but not include the IBM1015 folder, you need to be explicit about that:

    --xlabel-parent 0 --xlabel-depth 1 

Results in:

    RAID10

Example:

![shortlabel][shortlabel]

[shortlabel]: https://louwrentius.com/static/images/shortlabel.png

## JSON / LOG file name requirements

Fio-plot parses the filename of the generated .log files. The format is:

    [rwmode]-iodepth-[iodepth]-nujobs-[numjobs]_[fio generated type].[numbjob job id].log

An example:

    randwrite-iodepth-8-numjobs-8_lat.1.log
    randwrite-iodepth-8-numjobs-8_lat.2.log
    randwrite-iodepth-8-numjobs-8_lat.3.log
    randwrite-iodepth-8-numjobs-8_lat.4.log
    randwrite-iodepth-8-numjobs-8_lat.5.log
    randwrite-iodepth-8-numjobs-8_lat.6.log
    randwrite-iodepth-8-numjobs-8_lat.7.log
    randwrite-iodepth-8-numjobs-8_lat.8.log 

In this example, there are 8 files because numjobs was set to 8. Fio autoamatically generates a file for each job.
It's important that - if you don't use the included benchmark script - to make sure files are generated with the appropriate file name structure.


## PNG metadata

All settings used to generate the PNG file are incorporated into the PNG file as metadata (tEXT).
This should help you to keep track of the exact parameters and data used to generate the graphs. 
This metadata can be viewed with ImageMagick like this: 

    identify -verbose filename.png

This is a fragment of the output: 

    Properties:
        compare_graph: True
        date:create: 2020-09-28T16:27:08+00:00
        date:modify: 2020-09-28T16:27:07+00:00
        disable_grid: False
        dpi: 200
        enable_markers: False
        filter: ('read', 'write')
        histogram: False
        input_directory: /Users/MyUserName/data/WDRAID5 /Users/MyUserName/data/WDRAID10
        iodepth: 16
        iodepth_numjobs_3d: False
        latency_iops_2d: False
        line_width: 1
        loggraph: False
        maxdepth: 64
        maxjobs: 64

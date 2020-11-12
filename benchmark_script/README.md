### Requirements

Bench_fio requires Python3. The 'numpy' python module is required.

   pip3 install -r requirements.txt 

You can also use apt/yum to satisfy this requirement.


### Notes on IO queue depth and number of jobs

As discussed in issue #41 each job has its own I/O queue. If qd=1 and nj=5, you will have 5 IOs in flight.
If you have qd=4 and nj=4 you will have 4 x 4 = 16 IOs in flight. 

### Examples
 
We benchmark two devices with a randread/randrwite workload. 

    ./bench_fio --target /dev/md0 /dev/md1 --type device --mode randread randwrite --output RAID_ARRAY 

We benchmark one device with a custom set of iodepths and numjobs:

    ./bench_fio --target /dev/md0 --type device --mode randread randwrite --output RAID_ARRAY --iodepth 1 8 16 --numjobs 8

We benchmark one device and pass extra custom parameters. 

	./bench_fio --target /dev/md0 --type device --mode randread randwrite --output RAID_ARRAY --extra-opts norandommap=1 refill_buffers=1


An example with output:

	./bench_fio --target /dev/md0 --type device --template fio-job-template.fio  --iodepth 1 8 16 --numjobs 8 --mode randrw --output RAID_ARRAY --rwmixread 75 90 

	████████████████████████████████████████████████████
			+++ Fio Benchmark Script +++

	Job template:                  fio-job-template.fio
	I/O Engine:                    libaio
	Number of benchmarks:          6
	Estimated duration:            0:06:00
	Devices to be tested:          /dev/md0
	Test mode (read/write):        randrw
	IOdepth to be tested:          1 8 16
	NumJobs to be tested:          8
	Blocksize(s) to be tested:     4k
	Mixed workload (% Read):       75 90

	████████████████████████████████████████████████████
	100% |█████████████████████████|   [0:06:06, 0:00:00]-]

Tip: Because benchmarks can run a long time, it may be advised to run them
in a 'screen' session.

### Output

The benchmark data consists of two typtes of data. 

1. Fio .json output
2. Fio .log output

This is an example to clarify the directory structure:
The folder 'RAID_ARRAY' is the folder specified in --output.

	RAID_ARRAY/ <-- folder as specified wit --output
	└── md0 <-- device
		├── randrw75 <-- mixed load with % read 
		│   ├── 4k <-- Block size
		│   │   ├── randrw-16-8.json
		│   │   ├── randrw-1-8.json
		│   │   ├── randrw-8-8.json
		│   └── 8k <-- Block size
		│       ├── randrw-16-8.json
		│       ├── randrw-1-8.json
		│       ├── randrw-8-8.json
		└── randrw90
			├── 4k
			│   ├── randrw-16-8.json
			│   ├── randrw-1-8.json
			│   ├── randrw-8-8.json
			└── 8k
				├── randrw-16-8.json
				├── randrw-1-8.json
				├── randrw-8-8.json

The .log files are ommitted. 

Please note that mixed workloads will get their own folder to prevent files being overwritten.
Pure read/write/trim workloads will appear in the *device* folder.


### Usage
	usage: bench_fio [-h] -d TARGET [TARGET ...] -t {device,file,directory}
					[-s SIZE] -o OUTPUT [-j TEMPLATE]
					[-b BLOCK_SIZE [BLOCK_SIZE ...]]
					[--iodepth IODEPTH [IODEPTH ...]]
					[--numjobs NUMJOBS [NUMJOBS ...]] [--duration DURATION]
					[-m MODE [MODE ...]] [--rwmixread RWMIXREAD [RWMIXREAD ...]]
					[-e ENGINE] [--direct DIRECT]
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
							Fio job file in INI format. (Default: ./fio-job-
							template.fio)
	-b BLOCK_SIZE [BLOCK_SIZE ...], --block-size BLOCK_SIZE [BLOCK_SIZE ...]
							Specify block size(s). (Default: ['4k']
	--iodepth IODEPTH [IODEPTH ...]
							Override default iodepth test series ([1, 2, 4, 8, 16,
							32, 64]). Usage example: --iodepth 1 8 16
	--numjobs NUMJOBS [NUMJOBS ...]
							Override default number of jobs test series ([1, 2, 4,
							8, 16, 32, 64]). Usage example: --numjobs 1 8 16
	--duration DURATION   Override the default test duration per benchmark
							(default: 60)
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

### SSD Preconditioning

If you don't precondition an SSD, you may observe inconsistent write performance. 

I found [this presentation][intelpresentation] from Intel that provides guidance for benchmarking SSDs. 
It points out that you need to precondition the SSD before benchmarking. 

[intelpresentation]: https://s3.us-east-2.amazonaws.com/intel-builders/day_2_spdk_best_practices_performance_benchmarking_tuning.pdf


   
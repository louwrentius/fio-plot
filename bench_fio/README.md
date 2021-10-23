### Introduction
 This benchmark script is provided alongside fio-plot. It automates the process of running multiple benchmarks with different parameters. For example, it allows you to gather data for different queue depths and/or number of simultaneous jobs. The benchmark script shows progress in real-time.

#### Steady State
 It supports the [Fio "steady state"][fioss] feature, that stops a benchmark when the desired steady state is reached for a configure time duration.

 [fioss]: https://github.com/axboe/fio/blob/master/examples/steadystate.fio

#### SSD Preconditioning

This benchmark script supports running configure SSD preconditioning jobs that are run before the actual benchmarks are executed. You may even specify for them to run after each benchmark if desired.

### Example output

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

### Example usage

We benchmark two devices with a randread/randrwite workload. 

    ./bench_fio --target /dev/md0 /dev/md1 --type device --mode randread randwrite --output RAID_ARRAY 

We benchmark one device with a custom set of iodepths and numjobs:

    ./bench_fio --target /dev/md0 --type device --mode randread randwrite --output RAID_ARRAY --iodepth 1 8 16 --numjobs 8

We benchmark one device and pass extra custom parameters. 

	./bench_fio --target /dev/md0 --type device --mode randread randwrite --output RAID_ARRAY --extra-opts norandommap=1 refill_buffers=1

We benchmark using the steady state feature:

    ./bench_fio --target /dev/sda --type device -o test -m randwrite --loops 1 --iodepth 1 8 16 32 --numjobs 1 --ss iops:0.1% --ss-ramp 10 --ss-dur 20 --runtime 60


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

	usage: bench_fio [-h] -d TARGET [TARGET ...] -t {device,file,directory,rbd} [-P CEPH_POOL] [-s SIZE] -o OUTPUT [-j TEMPLATE] [-b BLOCK_SIZE [BLOCK_SIZE ...]]
                 [--iodepth IODEPTH [IODEPTH ...]] [--numjobs NUMJOBS [NUMJOBS ...]] [--runtime RUNTIME] [-p] [--precondition-repeat] [--precondition-template PRECONDITION_TEMPLATE]
                 [-m MODE [MODE ...]] [--rwmixread RWMIXREAD [RWMIXREAD ...]] [-e ENGINE] [--direct DIRECT] [--loops LOOPS] [--time-based] [--entire-device] [--ss SS]
                 [--ss-dur SS_DUR] [--ss-ramp SS_RAMP] [--extra-opts EXTRA_OPTS [EXTRA_OPTS ...]] [--invalidate INVALIDATE] [--quiet] [--loginterval LOGINTERVAL] [--dry-run]

	Automates FIO benchmarking. It can run benchmarks with different iodepths, jobs or other properties.

	optional arguments:
	-h, --help            show this help message and exit

	Generic Settings:
	-d TARGET [TARGET ...], --target TARGET [TARGET ...]
							Storage device / directory / file / rbd image (Ceph) to be tested.
	-t {device,file,directory,rbd}, --type {device,file,directory,rbd}
							Target type, device, file, directory or rbd (Ceph)
	-P CEPH_POOL, --ceph-pool CEPH_POOL
							Specify the Ceph pool in wich the target rbd image resides.
	-s SIZE, --size SIZE  File size if target is a file. If target is a directory, a file of the specified size is created per job
	-o OUTPUT, --output OUTPUT
							Output directory for .json and .log output. If a read/write mix is specified, separate directories for each mix will be created.
	-j TEMPLATE, --template TEMPLATE
							Fio job file in INI format. A file is already included and this parameter is only required if you create your own custom Fio job. (Default: ./fio-job-
							template.fio)
	-b BLOCK_SIZE [BLOCK_SIZE ...], --block-size BLOCK_SIZE [BLOCK_SIZE ...]
							Specify block size(s). (Default: ['4k']
	--iodepth IODEPTH [IODEPTH ...]
							Override default iodepth test series ([1, 2, 4, 8, 16, 32, 64]). Usage example: --iodepth 1 8 16
	--numjobs NUMJOBS [NUMJOBS ...]
							Override default number of jobs test series ([1, 2, 4, 8, 16, 32, 64]). Usage example: --numjobs 1 8 16
	--runtime RUNTIME     Override the default test runtime per benchmark(default: 60)
	-p, --precondition    With this option you can specify an SSD precondition workload prior to performing actualbenchmarks. If you don't precondition SSDs before running a benchmark,
							results may notreflect actual real-life performance under sustained load. (default: False).
	--precondition-repeat
							After every individual benchmark, the preconditioning run is executed (again). (Default: False).
	--precondition-template PRECONDITION_TEMPLATE
							The Fio job template containing the precondition workload(default=precondition.fio
	-m MODE [MODE ...], --mode MODE [MODE ...]
							List of I/O load tests to run (default: ['randread', 'randwrite'])
	--rwmixread RWMIXREAD [RWMIXREAD ...]
							If a mix of read/writes is specified with --testmode, the ratio of reads vs. writes can be specified with this option. the parameter is an integer and
							represents the percentage of reads. A read/write mix of 75%/25% is specified as '75' (default: None). Multiple values can be specified and separate output
							directories will be created. This argument is only used if the benchmark is of type randrw. Otherwise this option is ignored.
	-e ENGINE, --engine ENGINE
							Select the ioengine to use, see fio --enghelp for an overview of supported engines. (Default: libaio).
	--direct DIRECT       Use DIRECT I/O (default: 1)
	--loops LOOPS         Each individual benchmark is repeated x times (default: 1)
	--time-based          All benchmarks are time based, even if a test size is specifiedLookt at the Fio time based option for more information.(default: False).
	--entire-device       The benchmark will keep running until all sectors are read or written to.(default: False).
	--ss SS               Detect and exit on achieving steady state (spefial Fio feature, 'man fio' for more detials) (default: False)
	--ss-dur SS_DUR       Steady state window (default: None)
	--ss-ramp SS_RAMP     Steady state ramp time (default: None)
	--extra-opts EXTRA_OPTS [EXTRA_OPTS ...]
							Allows you to add extra options, for example, options that are specific to the selected ioengine. It can be any other Fio option. Example: --extra-opts
							norandommap=1 invalidate=0 You may also choose to add those options to the fio_template.fio file.
	--invalidate INVALIDATE
							From the Fio manual: Invalidate buffer-cache for the file prior to starting I/O.(Default: 1)
	--quiet               The progresbar will be supressed.
	--loginterval LOGINTERVAL
							Interval that specifies how often stats are logged to the .log files. (Default: 500
	--dry-run             Simulates a benchmark, does everything except running Fio.

### SSD Preconditioning

In order to obtain performance numbers that will actually represent production, it is very important to precondition SSDs.
SSDs perform all kinds of strategies to improve write performance. Under a sustained write load, performance may dramatically deteriorate. To find out how much performance decreases, it's important to test with the SSD completely written over, multiple times. 

The included preconditioning step in this benchmark script overwrites the device twice, to make sure all flash storage is written to.

More background information about SSD preconditioning [can be found here][snia].

[snia]: https://www.snia.org/sites/default/education/tutorials/2011/fall/SolidState/EstherSpanjer_The_Why_How_SSD_Performance_Benchmarking.pdf

### Notes on IO queue depth and number of jobs

As discussed in issue #41 each job has its own I/O queue. If qd=1 and nj=5, you will have 5 IOs in flight.
If you have qd=4 and nj=4 you will have 4 x 4 = 16 IOs in flight. 

### Benchmarking Ceph RBD images

If you need to benchmark a Ceph RBD image, some tips: 

The --target should be the RBD image to benchmark 
The --ceph-pool parameter should specify the pool 
The --template parameter should point the the Ceph RBD specific fio-job-template-ceph.fio template (included.)

### Requirements

Bench_fio requires Python3. The 'numpy' python module is required.

   pip3 install -r requirements.txt 

You can also use apt/yum to satisfy this requirement.

   
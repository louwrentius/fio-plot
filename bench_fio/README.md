### Introduction
 This benchmark script is provided alongside fio-plot. It automates the process of running multiple benchmarks with different parameters. For example, it allows you to gather data for different queue depths and/or number of simultaneous jobs. The benchmark script shows progress in real-time.

#### Steady State
 It supports the [Fio "steady state"][fioss] feature, that stops a benchmark when the desired steady state is reached for a configured time duration.

 [fioss]: https://github.com/axboe/fio/blob/master/examples/steadystate.fio

#### SSD Preconditioning

This benchmark script supports running configure SSD preconditioning jobs that are run before the actual benchmarks are executed. You may even specify for them to run after each benchmark if desired. More information can be found further down into this document.

### Example output

An example with output:

	./bench_fio --target /dev/md0 --type device --iodepth 1 8 16 --numjobs 8 --mode randrw --output RAID_ARRAY --rwmixread 75 90

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

    ./bench_fio --target /dev/md0 /dev/md1 --type device --mode randread randwrite --output RAID_ARRAY --destructive

We benchmark one device with a custom set of iodepths and numjobs:

    ./bench_fio --target /dev/md0 --type device --mode randread randwrite --output RAID_ARRAY --iodepth 1 8 16 --numjobs 8 --destructive

We benchmark one device and pass extra custom parameters.

	./bench_fio --target /dev/md0 --type device --mode randread randwrite --output RAID_ARRAY --extra-opts norandommap=1 refill_buffers=1 --destructive

We benchmark using the steady state feature:

    ./bench_fio --target /dev/sda --type device -o test -m randwrite --loops 1 --iodepth 1 8 16 32 --numjobs 1 --ss iops:0.1% --ss-ramp 10 --ss-dur 20 --runtime 60 --destructive

### INI configuration file support

Originally bench_fio was configured purely by concatenating the required command line parameters.
Starting with version 1.0.20 bench_fio supports an INI file format for configuration, similar to FIO.
This is how you can run bench_fio with a INI based configuration file:

	./bench_fio /path/to/benchmark.ini

An example configuration file is included in the templates folder called benchmark.ini and contains the following:

	[benchfio]
	target = /dev/example
	output = benchmark
	type = device
	mode = randread,randwrite
	size = 10G
	iodepth = 1,2,4,8,16,32,64
	numjobs = 1,2,4,8,16,32,64
	direct = 1
	engine = libaio
	precondition = False
	precondition_repeat = False
	extra_opts = norandommap=1,refill_buffers=1
	runtime = 60
	destructive = False

Please notice that on the command line, multiple arguments are separated by spaces. However, within the INI file,
multiple arguments are separated by a comma.

### Extra (custom) Fio parameters

If you use the bench-fio comand line, extra options can be specified with the --extra-opts parameter like this:

    --extra-opts parameter1=value parameter2=value

Example:

    --extra-opts norandommap=1 refill_buffers=1

If the INI file is  used to perform bench-fio benchmarks, those extra options can just be added to the file like
a regular fio job file, one per line.

	norandommap = 1
	refill_buffers = 1

You can put any valid fio option in the bench-fio INI file and those will be passed as-is to fio. Such parameters are
marked with an asterix(*) when running bench-fio.

### Benchmarking multiple devices in parallel

By default, a test run will benchmark one device at a time, sequentially. The --parallel option allows multiple devices
to be tested in parallel. This has two benefits, it speeds up testing and it also simulates a particular load on the system.
It could be that benchmarking devices in parallel causes so much CPU impact that this impacts the benchmark results.
Depending on your intentions, this may actually be an interesting outcome or spoil the benchmark results, so keep this in mind.

Thanks @Zhucan for building this feature.

### Fio Client/Server support

The Fio tool supports a [client-server][clientserver] model where one host can issue a benchmark on just one remote host
up to hundreds of remote hosts. Bench-fio supports this feature with the --remote and --remote-checks options.

[clientserver]: https://fio.readthedocs.io/en/latest/fio_doc.html#client-server

The --remote argument requires a file containing one host per line as required by Fio.

	host01
	host02

The host can either be specified as an IP-address or as a DNS name.

So it would look like:

	--remote /some/path/to/file.txt

The --remote-checks parameter makes bench-fio check if all hosts are up before starting the benchmark.
Specifically, it checks if TCP port 8765 is open on a host.

If one of the host fails this check bench-fio will never start actual benchmarks. By default, Fio will start benchmarking
hosts that are network-accessible, but then abort when one or more host are found to be unreachable.
As this may be undesirable, the --remote-checks parameter can avoid this scenario.

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

### Benchmarking a device using --size instead of --runtime as the benchmark duration
By default, bench_fio uses a --runtime of 60 seconds unless --entire-device is specified or you specify a higher --runtime.

If you use the --size option with --type device, you must specify --runtime 0 if you want the --size parameter to be honoured.
You can also specify a large --runtime value as an upper bound to to the benchmark duration as fio stops benchmarking when the --size limit is reached.

### Installation requirements

Bench_fio requires Python3. The 'numpy' python module is required.

   pip3 install -r requirements.txt

You can also use apt/yum to satisfy this requirement.

### Usage

	usage: bench-fio [-h] -d TARGET [TARGET ...] -t {device,file,directory,rbd} [-P CEPH_POOL] [-s SIZE] -o OUTPUT
                 [-b BLOCK_SIZE [BLOCK_SIZE ...]] [--iodepth IODEPTH [IODEPTH ...]] [--numjobs NUMJOBS [NUMJOBS ...]]
                 [--runtime RUNTIME] [-p] [--precondition-repeat] [--precondition-template PRECONDITION_TEMPLATE]
                 [-m MODE [MODE ...]] [--rwmixread RWMIXREAD [RWMIXREAD ...]] [-e ENGINE] [--direct DIRECT]
                 [--loops LOOPS] [--time-based] [--entire-device] [--ss SS] [--ss-dur SS_DUR] [--ss-ramp SS_RAMP]
                 [--extra-opts EXTRA_OPTS [EXTRA_OPTS ...]] [--invalidate INVALIDATE] [--quiet]
                 [--loginterval LOGINTERVAL] [--dry-run] [--destructive] [--remote REMOTE] [--remote-checks]
                 [--remote-timeout REMOTE_TIMEOUT] [--create] [--parallel]

	Automates FIO benchmarking. It can run benchmarks with different iodepths, jobs or other properties.

	options:
	-h, --help            show this help message and exit

	Generic Settings:
	-d TARGET [TARGET ...], --target TARGET [TARGET ...]

							Storage device / directory / file / rbd image (Ceph) to be tested. When the path contains
							a colon (:), it must be escaped with a double backslash (\\) or single backslash when
							you use single quotes around the path.
							Usage example: --target /dev/disk/by-path/pci-0000\\:00\\:1f.2-ata-4.0
	-t {device,file,directory,rbd}, --type {device,file,directory,rbd}
							Target type, device, file, directory or rbd (Ceph)
	-P CEPH_POOL, --ceph-pool CEPH_POOL
							Specify the Ceph pool in wich the target rbd image resides.
	-s SIZE, --size SIZE  File size if target is a file. The value is passed straight to the fio --size parameter. See
							the Fio man page for supported syntax. If target is a directory, a file of the specified size
							is created per job
	-o OUTPUT, --output OUTPUT
							Output directory for .json and .log output. If a read/write mix is specified, separate
							directories for each mix will be created.
	-b BLOCK_SIZE [BLOCK_SIZE ...], --block-size BLOCK_SIZE [BLOCK_SIZE ...]
							Specify block size(s). (Default: ['4k']
	--iodepth IODEPTH [IODEPTH ...]
							Override default iodepth test series ([1, 2, 4, 8, 16, 32, 64]). Usage example: --iodepth 1 8
							16
	--numjobs NUMJOBS [NUMJOBS ...]
							Override default number of jobs test series ([1, 2, 4, 8, 16, 32, 64]). Usage example:
							--numjobs 1 8 16
	--runtime RUNTIME     Override the default test runtime per benchmark(default: 60)
	-p, --precondition    With this option you can specify an SSD precondition workload prior to performing
							actualbenchmarks. If you don't precondition SSDs before running a benchmark, results may
							notreflect actual real-life performance under sustained load. (default: False).
	--precondition-repeat
							After every individual benchmark, the preconditioning run is executed (again). (Default:
							False).
	--precondition-template PRECONDITION_TEMPLATE
							The Fio job template containing the precondition
							workload(default=/usr/local/lib/python3.10/dist-
							packages/fio_plot-1.1.7-py3.10.egg/bench_fio/benchlib/../templates/precondition.fio
	-m MODE [MODE ...], --mode MODE [MODE ...]
							List of I/O load tests to run (default: ['randread'])
	--rwmixread RWMIXREAD [RWMIXREAD ...]
							If a mix of read/writes is specified with --testmode, the ratio of reads vs. writes can be
							specified with this option. The parameter is an integer and represents the percentage of
							reads. A read/write mix of 75%/25% is specified as '75' (default: None). Multiple values can
							be specified and separate output directories will be created. This argument is only used if
							the benchmark is of type randrw. Otherwise this option is ignored.
	-e ENGINE, --engine ENGINE
							Select the ioengine to use, see fio --enghelp for an overview of supported engines. (Default:
							libaio).
	--direct DIRECT       Use DIRECT I/O (default: 1)
	--loops LOOPS         Each individual benchmark is repeated x times (default: 1)
	--time-based          All benchmarks are time based, even if a test size is specifiedLookt at the Fio time based
							option for more information.(default: False).
	--entire-device       The benchmark will keep running until all sectors are read or written to. Overrides runtime
							setting.(default: False).
	--ss SS               Detect and exit on achieving steady state (spefial Fio feature, 'man fio' for more detials)
							(default: False)
	--ss-dur SS_DUR       Steady state window (default: None)
	--ss-ramp SS_RAMP     Steady state ramp time (default: None)
	--extra-opts EXTRA_OPTS [EXTRA_OPTS ...]
							Allows you to add extra options, for example, options that are specific to the selected
							ioengine. It can be any other Fio option. Example: --extra-opts norandommap=1 invalidate=0
							this can also be specified in the bench-fio ini file
	--invalidate INVALIDATE
							From the Fio manual: Invalidate buffer-cache for the file prior to starting I/O.(Default: 1)
	--quiet               The progresbar will be supressed.
	--loginterval LOGINTERVAL
							Interval that specifies how often stats are logged to the .log files. (Default: 1000
	--dry-run             Simulates a benchmark, does everything except running Fio.
	--destructive         Enables benchmarks that write towards the device|file|directory
	--remote REMOTE       Uses Fio client/server mechanism. Argument requires file with name host.list containing one
							host per line. (False). Usage example: --remote host.list
	--remote-checks       When Fio client/server is used, we run a preflight check if all hosts are up using a TCP port
							check before we run the benchmark. Otherwise some hosts start benchmarking until a down host
							times out, which may be undesirable. (False).
	--remote-timeout REMOTE_TIMEOUT
							When Fio client/server is used, we run a preflight check if all hosts are up using a TCP port
							check before we run the benchmark. Otherwise some hosts start benchmarking until a down host
							times out, which may be undesirable. (False).
	--create              Create target files if they don't exist. This is the default for fio but not for bench_fio
	--parallel            Testing devices in parallel. The default for testing devices in sequential

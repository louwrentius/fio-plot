#!/usr/bin/env python3
import argparse
import sys

from . import runfio


def check_args(settings):
    """Some basic error handling."""
    try:
        parser = get_arguments(settings)
        args = parser.parse_args()

    except OSError:
        parser.print_help()
        sys.exit(1)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(2)

    if not runfio.check_fio_version(settings):
        parser.print_help()
        sys.exit(3)

    return args

def get_arguments(settings):
    parser = argparse.ArgumentParser(
        description="Automates FIO benchmarking. It can run benchmarks \
            with different iodepths, jobs or other properties."
    )
    ag = parser.add_argument_group(title="Generic Settings")
    ag.add_argument(
        "-d",
        "--target",
        help="Storage device / directory / file / rbd image (Ceph) to be tested.",
        required=True,
        nargs="+",
        type=str,
    )
    ag.add_argument(
        "-t",
        "--type",
        help="Target type, device, file, directory or rbd (Ceph)",
        choices=["device", "file", "directory", "rbd"],
        required=True,
    )
    ag.add_argument(
        "-P",
        "--ceph-pool",
        help="Specify the Ceph pool in wich the target rbd image resides.",
        type=str,
    )
    ag.add_argument(
        "-s",
        "--size",
        help="File size if target is a file. The value is passed straight to the fio --size parameter.\
        See the Fio man page for supported syntax. If target is a directory, a file of the specified size \
        is created per job",
        type=str,
    )
    ag.add_argument(
        "-o",
        "--output",
        help="Output directory for .json and .log output. If a read/write mix is specified,\
                    separate directories for each mix will be created.",
        required=True,
    )
    ag.add_argument(
        "-j",
        "--template",
        help=f"Fio job file in INI format. A file is already included and this parameter is only required if you create \
            your own custom Fio job. \
            (Default: {settings['template']})",
        default=settings["template"],
    )
    ag.add_argument(
        "-b",
        "--block-size",
        help=f"Specify block size(s). (Default: {settings['block_size']}",
        default=settings["block_size"],
        nargs="+",
    )
    ag.add_argument(
        "--iodepth",
        help=f"Override default iodepth test series\
             ({settings['iodepth']}). Usage example: --iodepth 1 8 16",
        nargs="+",
        type=int,
        default=settings["iodepth"],
    )
    ag.add_argument(
        "--numjobs",
        help=f"Override default number of jobs test series\
            ({settings['numjobs']}). Usage example: --numjobs 1 8 16",
        nargs="+",
        type=int,
        default=settings["numjobs"],
    )

    ag.add_argument(
        "--runtime",
        help=f"Override the default test runtime per benchmark"
        f"(default: {settings['runtime']})",
        type=int,
        default=settings["runtime"],
    )

    ag.add_argument(
        "-p",
        "--precondition",
        action="store_true",
        help=(
            "With this option you can specify an SSD precondition workload prior to performing actual"
            "benchmarks. If you don't precondition SSDs before running a benchmark, results may not"
            f"reflect actual real-life performance under sustained load. (default: {str(settings['precondition'])})."
        ),
    )

    ag.add_argument(
        "--precondition-repeat",
        action="store_true",
        help=(
            "After every individual benchmark, the preconditioning run is executed (again). (Default: False)."
        ),
    )

    ag.add_argument(
        "--precondition-template",
        help=(
            "The Fio job template containing the precondition workload"
            f"(default={settings['precondition_template']}"
        ),
        default=settings['precondition_template'],
        type=str,
    )

    ag.add_argument(
        "-m",
        "--mode",
        help=f"List of I/O load tests to run (default: \
            {settings['mode']})",
        default=settings["mode"],
        nargs="+",
        type=str,
    )
    ag.add_argument(
        "--rwmixread",
        help=f"If a mix of read/writes is specified \
        with --testmode, the ratio of reads vs. writes can be specified with this option.\
            the parameter is an integer and represents the percentage of reads.\
             A read/write mix of 75%%/25%%  is specified as '75' (default: {settings['rwmixread']}).\
                Multiple values can be specified and separate output directories will be created.\
                    This argument is only used if the benchmark is of type randrw. Otherwise \
                        this option is ignored.",
        nargs="+",
        type=int,
        default=settings["rwmixread"],
    )
    ag.add_argument(
        "-e",
        "--engine",
        help=f"Select the ioengine to use, see fio --enghelp \
            for an overview of supported engines. (Default: {settings['engine']}).",
        default=settings["engine"],
    )
    ag.add_argument(
        "--direct",
        help=f"Use DIRECT I/O \
            (default: {settings['direct']})",
        type=int,
        default=settings["direct"],
    )

    ag.add_argument(
        "--loops",
        help=f"Each individual benchmark is repeated x times (default: {settings['loops']})",
        type=int,
        default=settings["loops"],
    )

    ag.add_argument(
        "--time-based",
        action="store_true",
        help=(
            "All benchmarks are time based, even if a test size is specified"
            "Lookt at the Fio time based option for more information."
            f"(default: {str(settings['time_based'])})."
        ),
    )

    ag.add_argument(
        "--entire-device",
        action="store_true",
        help=(
            "The benchmark will keep running until all sectors are read or written to. Overrides runtime setting."
            f"(default: {str(settings['entire_device'])})."
        ),
    )

    ag.add_argument(
        "--ss",
        help=f"Detect and exit on achieving steady state (spefial Fio feature, 'man fio' for more detials) \
            (default: {settings['ss']})",
        type=str,
        default=settings["ss"],
    )

    ag.add_argument(
        "--ss-dur",
        help=f"Steady state window \
            (default: {settings['ss_dur']})",
        type=int,
        default=settings["ss_dur"],
    )

    ag.add_argument(
        "--ss-ramp",
        help=f"Steady state ramp time \
            (default: {settings['ss_ramp']})",
        type=str,
        default=settings["ss_ramp"],
    )

    ag.add_argument(
        "--extra-opts",
        help="Allows you to add extra options, \
        for example, options that are specific to the selected ioengine. It \
             can be any other Fio option. Example: --extra-opts norandommap=1 invalidate=0\
                 You may also choose to add those options to the fio_template.fio file.",
        nargs="+",
    )
    ag.add_argument(
        "--invalidate",
        type=int,
        help=f"From the Fio manual: Invalidate buffer-cache for the \
                        file prior to starting I/O.(Default: {settings['invalidate']})",
        default=settings["invalidate"],
    )
    ag.add_argument(
        "--quiet", help="The progresbar will be supressed.", action="store_true"
    )
    ag.add_argument(
        "--loginterval",
        help=f"Interval that specifies how often stats are \
            logged to the .log files. (Default: {settings['loginterval']}",
        type=int,
        default=settings["loginterval"],
    )
    ag.add_argument(
        "--dry-run",
        help="Simulates a benchmark, does everything except running\
             Fio.",
        action="store_true",
        default=False,
    )
    ag.add_argument(
        "--destructive",
        help="Enables benchmarks that write towards the device|file|directory",
        action="store_true",
        default=False,
    )
    return parser


def get_argument_description():
    descriptions = {
        "target": "Test target",
        "template": "Job template",
        "engine": "I/O Engine",
        "mode": "Test mode (read/write)",
        "iodepth": "IOdepth to be tested",
        "numjobs": "NumJobs to be tested",
        "block_size": "Block size",
        "direct": "Direct I/O",
        "size": "Specified test data size",
        "rwmixread": "Read/write mix in %% read",
        "runtime": "Time duration per test (s)",
        "extra_opts": "Extra custom options",
        "loginterval": "Log interval of perf data (ms)",
        "invalidate": "Invalidate buffer cache",
        "loops": "Benchmark loops",
        "type": "Target type",
        "output": "Output folder",
        "time_based": "Time based",
        "benchmarks": "Number of benchmarks",
        "precondition": "Run precondition workload",
        "precondition_template": "Precondition template",
        "precondition_repeat": "Precondition after each test",
        "ss": "Detect steady state",
        "ss_dur": "Steady state rolling window",
        "ss_ramp": "Steady state rampup",
        "entire_device": "Benchmark entire device",
        "ceph_pool": "Ceph RBD pool",
        "destructive": "Allow destructive writes"
    }
    return descriptions

#!/usr/bin/env python3
#
# Benchmark Fio based on

import argparse
import sys
import os
import subprocess
import pprint
import itertools
import datetime
import time
from numpy import linspace


def convert_dict_vals_to_str(dictionary):
    return {k.upper(): str(v) for k, v in dictionary.items()}


def run_command(settings, benchmark, command):
    env = os.environ
    settings = convert_dict_vals_to_str(settings)
    benchmark = convert_dict_vals_to_str(benchmark)
    env.update(settings)
    env.update(benchmark)
    # pprint.pprint(env)
    result = subprocess.Popen(command, shell=False,
                              stdout=subprocess.PIPE, env=env).stdout.read()


def check_fio_version(settings):
    command = ["fio", "--version"]
    result = run_command(command)
    if "fio-3" in result.stdout:
        return True
    else:
        return False


def make_folder(folder):
    try:
        if not os.path.exists(folder):
            os.makedirs(folder)
    except OSError:
        print(f"Failed to create {folder}")
        sys.exit(1)


def run_fio(settings, benchmark):

    output_folder = f"{settings['output']}/{os.path.basename(benchmark['target'])}"
    make_folder(output_folder)

    output_file = f"{output_folder}/{benchmark['mode']}-{benchmark['iodepth']}-{benchmark['numjobs']}.json"

    command = ["fio", f"--output-format=json",
               f"--output={output_file}", settings['template']]
    result = run_command(settings, benchmark, command)
    return result


def format_benchmark(benchmark):
    status = ""
    for k, v in benchmark.items():
        status += f"{k}: {v} - "
    return status


def run_benchmarks(settings, benchmarks):
    if not settings['quiet']:
        for benchmark in ProgressBar(benchmarks):
            status = format_benchmark(benchmark)
            # print(f"\n   - Current benchmark: {status} ")
            run_fio(settings, benchmark)
    else:
        for benchmark in benchmarks:
            run_fio(settings, benchmark)


def ProgressBar(iterObj):
    def SecToStr(sec):
        m, s = divmod(sec, 60)
        h, m = divmod(m, 60)
        return u'%d:%02d:%02d' % (h, m, s)
    L = len(iterObj)
    steps = {int(x): y for x, y in zip(linspace(0, L, min(100, L), endpoint=False),
                                       linspace(0, 100, min(100, L), endpoint=False))}
    # quarter and half block chars
    qSteps = ['', u'\u258E', u'\u258C', u'\u258A']
    startT = time.time()
    timeStr = '   [0:00:00, -:--:--]'
    for nn, item in enumerate(iterObj):
        if nn in steps:
            done = u'\u2588'*int(steps[nn]/4.0)+qSteps[int(steps[nn] % 4)]
            todo = ' '*(25-len(done))
            barStr = u'%4d%% |%s%s|' % (steps[nn], done, todo)
        if nn > 0:
            endT = time.time()
            timeStr = ' [%s, %s]' % (SecToStr(endT-startT),
                                     SecToStr((endT-startT)*(L/float(nn)-1)))
        sys.stdout.write('\r'+barStr+" "+timeStr)
        sys.stdout.flush()
        yield item
    barStr = u'%4d%% |%s|' % (100, u'\u2588'*25)
    timeStr = '   [%s, 0:00:00]\n' % (SecToStr(time.time()-startT))
    sys.stdout.write('\r'+barStr+" "+timeStr)
    sys.stdout.flush()


def generate_test_list(settings):
    loop_items = ['target', 'mode', 'iodepth',
                  'numjobs', 'blocksize',  'readmix']
    dataset = []
    for item in loop_items:
        result = settings[item]
        dataset.append(result)

    benchmark_list = itertools.product(*dataset)
    return [dict(zip(loop_items, item)) for item in benchmark_list]


def get_arguments(settings):
    parser = argparse.ArgumentParser(
        description="Automates FIO benchmarking by varying iodepth and numjobs \
            paramers. Parameters can be customized")
    ag = parser.add_argument_group(title="Generic Settings")
    ag.add_argument("-d", "--target",
                    help="Storage device / folder / file to be tested", required=True, nargs='+', type=str)
    ag.add_argument("-t", "--type", help="Target type, device, file or folder",
                    choices=['device', 'file', 'folder'])
    ag.add_argument(
        "-s", "--size", help="File size if target is a file. If target \
            is a directory, a file of the specified size is created per job")
    ag.add_argument("-j", "--job-template",
                    help="Path to Fio job template file.", required=True)
    ag.add_argument("-o", "--output",
                    help=f"Output folder for .json and .log output. If a read/write mix is specified,\
                    separate folders for each mix will be created.", required=True)
    ag.add_argument(
        "--template", help=f"Fio job file in INI format. (Default: {settings['template']})", default=settings['template'])
    ag.add_argument(
        "--iodepth", help=f"Override default iodepth test series ({settings['iodepth']}", nargs='+', type=int,
        default=settings['iodepth'])
    ag.add_argument(
        "--numjobs", help=f"Override default number of jobs test series \
            ({settings['numjobs']}", nargs='+', type=int, default=settings['numjobs'])
    ag.add_argument(
        "--duration", help=f"Override the default test duration per benchmark \
            (default: {settings['duration']})", default=settings['duration'])
    ag.add_argument(
        "-m", "--mode", help=f"List of I/O load tests to run (default: \
            {settings['mode']})", default=settings['mode'], nargs='+', type=str)
    ag.add_argument("--readmix", help=f"If a mix of read/writes is specified \
        with --testmode, the ratio of reads vs. writes can be specified with this option.\
            the parameter is an integer and represents the percentage of reads.\
             A read/write mix of 75%%/25%%  is specified as '75' (default: {settings['readmix']}).\
                Multiple values can be specified and separate output folders will be created.\
                    This argument is only used if the benchmark is of type randrw. Otherwise \
                        this option is ignored.", nargs='+', type=int, default=settings['readmix'])
    ag.add_argument(
        "-e", "--engine", help=f"Select the ioengine to use, see fio --enghelp \
            for an overview of supported engines. (Default: {settings['engine']}).", default=settings['engine'])
    ag.add_argument("--extra-opts", help=f"Allows you to add extra options, \
        for example, options that are specific to the selected ioengine. It \
             can be any other Fio option. Example: --extra-opts option-a=1 option-b=2.\
                 You may also choose to add those options to the fio_template.fio file.", type=list)
    ag.add_argument(
        "--quiet", help="The progresbar will be supressed.", action='store_true')
    ag.add_argument(
        "--loginterval", help=f"Interval that specifies how often stats are \
            logged to the .log files. (Default: {settings['loginterval']}", type=int, default=settings['loginterval'])
    return parser


def get_default_settings():
    settings = {}
    settings['targetfile'] = []
    settings['targetdevice'] = []
    settings['template'] = "./fio-job-template.fio"
    settings['engine'] = "libaio"
    settings['mode'] = ["randread", "randwrite"]
    settings['iodepth'] = [1, 2, 4, 8, 16, 32, 64]
    settings['numjobs'] = [1, 2, 4, 8, 16, 32, 64]
    settings['blocksize'] = ["4k"]
    settings['direct'] = 1
    settings['size'] = None
    settings['readmix'] = [75]
    settings['duration'] = 60
    settings['extra_opts'] = []
    settings['iterable'] = []
    settings['loginterval'] = 500
    return settings


def check_args(settings):
    try:
        parser = get_arguments(settings)
        args = parser.parse_args()
    except OSError:
        parser.print_help()
        sys.exit(1)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if not check_fio_version:
        parser.print_help()
        sys.exit(1)

    return args


def calculate_duration(settings, tests):
    number_of_tests = len(tests)
    time_per_test = settings['duration']
    duration_in_seconds = number_of_tests * time_per_test
    duration = str(datetime.timedelta(seconds=duration_in_seconds))
    return duration


def display_stats(settings, tests):
    duration = calculate_duration(settings, tests)
    print(f"Number of benchmarks: {len(tests):>15}")
    print(f"  Estimated duration: {duration:>15}")
    print(f"")


def check_if_template_exists(settings):
    if not os.path.exists(settings['template']):
        print(
            f"It seems that template file {settings['template']} does not exist.")
        sys.exit(1)


def main():
    print(f" ------+ Fio Benchmark Script +------")
    settings = get_default_settings()
    args = check_args(settings)
    customsettings = vars(args)
    settings = {**settings, **customsettings}
    check_if_template_exists(settings)
    # pprint.pprint(settings)
    tests = generate_test_list(settings)
    display_stats(settings, tests)
    run_benchmarks(settings, tests)


if __name__ == "__main__":
    main()

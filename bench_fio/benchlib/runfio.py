#!/usr/bin/env python3
import subprocess
import sys
import os
import copy
from numpy import linspace
import time

from . import ( 
    supporting,
    checks
)


def check_fio_version(settings):
    """The 3.x series .json format is different from the 2.x series format.
    This breaks fio-plot, thus this older version is not supported.
    """

    command = ["fio", "--version"]
    result = run_raw_command(command).stdout
    result = result.decode("UTF-8").strip()
    if "fio-3" in result:
        return True
    elif "fio-2" in result:
        print(f"Your Fio version ({result}) is not compatible. Please use Fio-3.x")
        sys.exit(1)
    else:
        print("Could not detect Fio version.")
        sys.exit(1)


def drop_caches(settings):
    command = ["echo", "3", ">", "/proc/sys/vm/drop_caches"]
    run_raw_command(command)


def run_raw_command(command, env=None):
    try: 
        result = subprocess.run(
            command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env
        )
        if result.returncode > 0 or (len(str(result.stderr)) > 3):
            stdout = result.stdout.decode("UTF-8").strip()
            stderr = result.stderr.decode("UTF-8").strip()
            print(f"\nAn error occurred: {stderr} - {stdout}")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n ctrl-c pressed - Aborted by user....\n")
        sys.exit(1)
    return result


def run_command(settings, benchmark, command):
    """This command sets up the environment that is used in conjunction
    with the Fio .ini job file.
    """
    output_directory = supporting.generate_output_directory(settings, benchmark)
    env = os.environ
    settings = supporting.convert_dict_vals_to_str(settings)
    benchmark = supporting.convert_dict_vals_to_str(benchmark)
    env.update(settings)
    env.update(benchmark)
    env.update({"OUTPUT": output_directory})
    run_raw_command(command, env)


def run_fio(settings, benchmark):
    output_directory = supporting.generate_output_directory(settings, benchmark)
    output_file = f"{output_directory}/{benchmark['mode']}-{benchmark['iodepth']}-{benchmark['numjobs']}.json"

    command = [
        "fio",
        "--output-format=json",
        f"--output={output_file}",
        settings["template"],
    ]

    command = supporting.expand_command_line(command, settings, benchmark)

    target_parameter = checks.check_target_type(benchmark["target"], settings["type"])
    if target_parameter:
        command.append(f"{target_parameter}={benchmark['target']}")

    if not settings["dry_run"]:
        supporting.make_directory(output_directory)
        run_command(settings, benchmark, command)
    # else:
    #    pprint.pprint(command)


def run_precondition_benchmark(settings, device, run):

    if settings["precondition"] and settings["destructive"]:
        if not settings["precondition_repeat"] and run > 1:
            pass # only run once if precondition_repeat is not set
        else:
            settings_copy = copy.deepcopy(settings)
            settings_copy["template"] = settings["precondition_template"]
            # make precondition run the whole disk
            settings_copy["entire_device"] = True

            template = supporting.import_fio_template(settings["precondition_template"])

            benchmark = {
                "target": device,
                "mode": template["precondition"]["rw"],
                "iodepth": template["precondition"]["iodepth"],
                "block_size": template["precondition"]["bs"],
                "numjobs": template["precondition"]["numjobs"],
                "run": run,
            }
            run_fio(settings_copy, benchmark)

    elif settings["precondition"] and not settings["destructive"]:
        print(f"\n When running preconditionning, also enable the destructive flag to be 100% sure.\n")
        sys.exit(1)


def run_benchmarks(settings, benchmarks):
    # pprint.pprint(benchmarks)
    run = 0
    if not settings["quiet"]:
        for benchmark in ProgressBar(benchmarks):
            run += 1
            run_precondition_benchmark(settings, benchmark["target"], run)
            drop_caches(settings)
            run_fio(settings, benchmark)
    else:
        for benchmark in benchmarks:
            run += 1
            run_precondition_benchmark(settings, benchmark["target"], run)
            drop_caches(settings)
            run_fio(settings, benchmark)


def ProgressBar(iterObj):
    """https://stackoverflow.com/questions/3160699/python-progress-bar/49234284#49234284"""

    def SecToStr(sec):
        m, s = divmod(sec, 60)
        h, m = divmod(m, 60)
        return "%d:%02d:%02d" % (h, m, s)

    L = len(iterObj)
    steps = {
        int(x): y
        for x, y in zip(
            linspace(0, L, min(100, L), endpoint=False),
            linspace(0, 100, min(100, L), endpoint=False),
        )
    }
    # quarter and half block chars
    qSteps = ["", "\u258E", "\u258C", "\u258A"]
    startT = time.time()
    timeStr = "   [0:00:00, -:--:--]"
    activity = [" -", " \\", " |", " /"]
    for nn, item in enumerate(iterObj):
        if nn in steps:
            done = "\u2588" * int(steps[nn] / 4.0) + qSteps[int(steps[nn] % 4)]
            todo = " " * (25 - len(done))
            barStr = "%4d%% |%s%s|" % (steps[nn], done, todo)
        if nn > 0:
            endT = time.time()
            timeStr = " [%s, %s]" % (
                SecToStr(endT - startT),
                SecToStr((endT - startT) * (L / float(nn) - 1)),
            )
        sys.stdout.write("\r" + barStr + activity[nn % 4] + timeStr)
        sys.stdout.flush()
        yield item
    barStr = "%4d%% |%s|" % (100, "\u2588" * 25)
    timeStr = "   [%s, 0:00:00]\n" % (SecToStr(time.time() - startT))
    sys.stdout.write("\r" + barStr + timeStr)
    sys.stdout.flush()

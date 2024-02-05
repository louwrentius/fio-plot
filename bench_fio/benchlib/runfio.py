#!/usr/bin/env python3
import subprocess
import sys
import os
import copy
from numpy import linspace
import time
from operator import itemgetter
from itertools import groupby
from threading import Thread
from rich.progress import Progress

from . import supporting, generatefio, defaultsettings


def drop_caches():
    command = ["echo", "3", ">", "/proc/sys/vm/drop_caches"]
    run_raw_command(command)


def handle_error(outputfile):
    if outputfile:
        if os.path.exists(outputfile):
            with open(f"{outputfile}", "r") as input:
                data = input.read().splitlines()
                for line in data:
                    print(line)


def run_raw_command(command, outputfile=None):
    try:
        result = subprocess.run(
            command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if result.returncode > 0 or (len(str(result.stderr)) > 3):
            stdout = result.stdout.decode("UTF-8").strip()
            stderr = result.stderr.decode("UTF-8").strip()
            print(
                f"\nAn error occurred: stderr: {stderr} - stdout: {stdout} - returncode: {result.returncode} \n"
            )
            handle_error(
                outputfile
            )  # it seems that the JSON output file contains STDERR/STDOUT error data
            sys.exit(result.returncode)
    except KeyboardInterrupt:
        print(f"\n ctrl-c pressed - Aborted by user....\n")
        sys.exit(1)
    return result


def run_fio(settings, benchmark):
    # The target may contains a colon (:) in the path and it's escaped
    # with a backslash (\) as per the fio manual. The backslash must be
    # passed to fio's filename but should be removed when checking the
    # existance of the path, or when writing a job file or log file in
    # the filesystem.
    benchmark.update({"target_base": benchmark['target'].replace("\\", "")})
    tmpjobfile = f"/tmp/{os.path.basename(benchmark['target_base'])}-tmpjobfile.fio"
    output_directory = supporting.generate_output_directory(settings, benchmark)
    output_file = f"{output_directory}/{benchmark['mode']}-{benchmark['iodepth']}-{benchmark['numjobs']}.json"
    generatefio.generate_fio_job_file(settings, benchmark, output_directory, tmpjobfile)

    ### We build up the fio command line here
    command = ["fio"]

    command.append("--output-format=json")
    command.append(f"--output={output_file}")  # fio bug

    if settings["remote"]:
        command.append(f"--client={settings['remote']}")

    command.append(tmpjobfile)
    # End of command line creation

    if not settings["dry_run"]:
        supporting.make_directory(output_directory)
        run_raw_command(command, output_file)
        if settings["remote"]:
            fix_json_file(output_file)  # to fix FIO json output bug


def fix_json_file(outputfile):
    """Fix FIO BUG
    See #731 on github
    Purely for client server support, proposed solutions don't work
    """
    with open(f"{outputfile}", "r") as input:
        data = input.readlines()

    with open(f"{outputfile}", "w") as output:
        for line in data:
            if not line.startswith("<"):
                output.write(line)


def run_precondition_benchmark(settings, device, run):
    if settings["precondition"] and settings["destructive"]:
        if not settings["precondition_repeat"] and run > 1:
            pass  # only run once if precondition_repeat is not set
        else:
            settings_copy = copy.deepcopy(settings)
            settings_copy["template"] = settings["precondition_template"]
            settings_copy["runtime"] = None  # want to test entire device
            settings_copy["time_based"] = False
            template = supporting.import_fio_template(settings["precondition_template"])
            benchmark = {
                "target": device,
                "mode": template["precondition"]["rw"],
                "iodepth": template["precondition"]["iodepth"],
                "block_size": template["precondition"]["bs"],
                "numjobs": template["precondition"]["numjobs"],
                "run": run,
            }
            mapping = defaultsettings.map_settings_to_fio()
            for key, value in dict(template["precondition"]).items():
                for x, y in mapping.items():
                    if str(key) == str(y):
                        settings_copy[mapping[x]] = value
                    else:
                        settings_copy[key] = value
            # print(settings_copy)
            run_fio(settings_copy, benchmark)

    elif settings["precondition"] and not settings["destructive"]:
        print(
            f"\n When running preconditionning, also enable the destructive flag to be 100% sure.\n"
        )
        sys.exit(1)


def worker(benchmarks, settings, progress):
    run = 0
    advance = len(benchmarks)
    advance += settings["loops"] - 1
    if not settings["quiet"]:
        task = progress.add_task(description=benchmarks[0]["target"], total=advance)
    for benchmark in benchmarks:
        loops = 0
        while loops < settings["loops"]:
            run += 1
            loops += 1
            run_precondition_benchmark(settings, benchmark["target"], run)
            drop_caches()
            run_fio(settings, benchmark)
            if not settings["quiet"]:
                progress.update(task, advance=1)


def run_benchmarks(settings, benchmarks):
    with Progress() as progress:
        if not settings["parallel"]:
            worker(benchmarks, settings, progress)
        else:
            group_benchmarks = []
            for _, items in groupby(benchmarks, key=itemgetter("target")):
                group_benchmarks.append(list(items))
            thread_list = []
            for target in range(len(group_benchmarks)):
                t = Thread(
                    target=worker, args=(group_benchmarks[target], settings, progress)
                )
                thread_list.append(t)

            for t in thread_list:
                t.setDaemon(True)
                t.start()

            for t in thread_list:
                t.join()

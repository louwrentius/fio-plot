#!/usr/bin/env python3
import subprocess
import sys
import os
import copy
from numpy import linspace
import time

from . import ( 
    supporting,
    generatefio,
    defaultsettings
)

def drop_caches():
    command = ["echo", "3", ">", "/proc/sys/vm/drop_caches"]
    run_raw_command(command)

def handle_error(outputfile):
    if outputfile: 
        if os.path.exists(outputfile):
            with open(f"{outputfile}", 'r') as input:
                data = input.read().splitlines() 
                for line in data:
                    print(line)

def run_raw_command(command, outputfile = None):
    try: 
        result = subprocess.run(
            command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if result.returncode > 0 or (len(str(result.stderr)) > 3):
            stdout = result.stdout.decode("UTF-8").strip()
            stderr = result.stderr.decode("UTF-8").strip()
            print(f"\nAn error occurred: stderr: {stderr} - stdout: {stdout} - returncode: {result.returncode} \n")
            handle_error(outputfile) # it seems that the JSON output file contains STDERR/STDOUT error data
            sys.exit(result.returncode)
    except KeyboardInterrupt:
        print(f"\n ctrl-c pressed - Aborted by user....\n")
        sys.exit(1)
    return result


def run_fio(settings, benchmark):
    output_directory = supporting.generate_output_directory(settings, benchmark)
    output_file = f"{output_directory}/{benchmark['mode']}-{benchmark['iodepth']}-{benchmark['numjobs']}.json"
    generatefio.generate_fio_job_file(settings, benchmark, output_directory)
    
    ### We build up the fio command line here
    command = [
        "fio"
    ]
    
    command.append("--output-format=json")
    command.append(f"--output={output_file}") # fio bug

    if settings["remote"]:
        command.append(f"--client={settings['remote']}")

    command.append(settings["tmpjobfile"])
    # End of command line creation
    
    if not settings["dry_run"]:
        supporting.make_directory(output_directory)
        run_raw_command(command, output_file)
        if settings["remote"]:
            fix_json_file(output_file) # to fix FIO json output bug


def fix_json_file(outputfile):
    """ Fix FIO BUG
        See #731 on github
        Purely for client server support, proposed solutions don't work
    """
    with open(f"{outputfile}", 'r') as input:
         data = input.readlines()
    
    with open(f"{outputfile}", 'w') as output:
        for line in data:
            if not line.startswith("<"):
                output.write(line)
         

def run_precondition_benchmark(settings, device, run):
    if settings["precondition"] and settings["destructive"]:
        if not settings["precondition_repeat"] and run > 1:
            pass # only run once if precondition_repeat is not set
        else:
            settings_copy = copy.deepcopy(settings)
            settings_copy["template"] = settings["precondition_template"]
            settings_copy["runtime"] = None # want to test entire device
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
            #print(settings_copy)
            run_fio(settings_copy, benchmark)

    elif settings["precondition"] and not settings["destructive"]:
        print(f"\n When running preconditionning, also enable the destructive flag to be 100% sure.\n")
        sys.exit(1)


def run_benchmarks(settings, benchmarks):
    # pprint.pprint(benchmarks)
    run = 0
    progress_benchmarks = ProgressBar(benchmarks) if not settings["quiet"] else benchmarks
    for benchmark in progress_benchmarks:
        loops = 0
        while loops < settings["loops"]:
            run += 1
            loops += 1
            run_precondition_benchmark(settings, benchmark["target"], run)
            drop_caches()
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

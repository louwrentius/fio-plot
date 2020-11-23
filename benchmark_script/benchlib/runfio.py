#!/usr/bin/env python3
import subprocess
import sys
import os
import pprint
import copy

import benchlib.supporting as supporting
import benchlib.display as show
import benchlib.checks as checks


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


def run_raw_command(command, env=None):
    result = subprocess.run(
        command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env
    )
    if result.returncode > 0 or (len(str(result.stderr)) > 3):
        stdout = result.stdout.decode("UTF-8").strip()
        stderr = result.stderr.decode("UTF-8").strip()
        print(f"\nAn error occurred: {stderr} - {stdout}")
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
    command.append(f"{target_parameter}={benchmark['target']}")

    if not settings["dry_run"]:
        supporting.make_directory(output_directory)
        run_command(settings, benchmark, command)
    else:
        pprint.pprint(command)


def run_precondition_benchmark(settings, device):

    if settings["precondition"] and settings["type"] == "device":

        settings_copy = copy.deepcopy(settings)
        settings_copy["template"] = settings["precondition_template"]

        template = supporting.import_fio_template(settings["precondition_template"])

        benchmark = {
            "target": device,
            "mode": template["precondition"]["rw"],
            "iodepth": template["precondition"]["iodepth"],
            "block_size": template["precondition"]["bs"],
            "numjobs": template["precondition"]["numjobs"],
        }
        run_fio(settings, benchmark)


def run_benchmarks(settings, benchmarks):
    # pprint.pprint(benchmarks)
    if not settings["quiet"]:
        for benchmark in show.ProgressBar(benchmarks):
            if settings["precondition_repeat"]:
                run_precondition_benchmark(settings, benchmark["target"])
            run_fio(settings, benchmark)
    else:
        for benchmark in benchmarks:
            run_fio(settings, benchmark)

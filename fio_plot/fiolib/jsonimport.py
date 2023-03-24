import os
import sys
import json
import logging

logger = logging.getLogger(__name__)

def validate_json_file(settings, jsondata):
    valid = False
    keysfound = 0 
    minimumkeys = 2
    validkeys = ["fio version", "global options", "client_stats", "jobs"]
    for key in validkeys:
        if key in jsondata.keys():
            keysfound += 1
    if keysfound >= minimumkeys:
        valid = True
    return valid

def filter_json_files(settings, filename):
    """A bit of a slow process, but guarantees that we get legal
    json files regardless of their names"""
    iodepth = None
    numjobs = None
    with open(filename, 'r') as candidate_file:
        try:
            candidate_json = json.load(candidate_file)
            if validate_json_file(settings, candidate_json):
                if "client_stats" in candidate_json.keys():
                    job_options = candidate_json["client_stats"][0]["job options"]
                elif "global options" in candidate_json.keys():
                    job_options = candidate_json["jobs"][0]["job options"] 
                    job_options.update(candidate_json["global options"])
                else:
                    job_options = candidate_json["jobs"][0]["job options"]
                if job_options["rw"] == settings["rw"]:
                    iodepth = int(job_options["iodepth"])
                    numjobs = int(job_options["numjobs"])
            else:
                logger.debug(f"{filename} does not appear to be a valid fio json output file, skipping")
        except Exception as e:
            print(f"\n\nFilename: {filename}")
            print(f"Error: {repr(e)}\n") 
            print("First, open the file and check for errors at the top.\nYou can remove the error lines and the JSON will likely parse\nbut results may not be trustworthy.\nIf there are no error linkes at the top, please report this as a bug\nand please include the JSON file if possible.\n\n")
            sys.exit(1)
    if iodepth in settings["iodepth"] and numjobs in settings["numjobs"]:
        return filename
    # else means this file is valid but doesn't match iodepth/numjobs so no else statement

def list_json_files(settings, fail=True):
    """List all JSON files that maches the command line settings."""
    input_directories = []
    for directory in settings["input_directory"]:
        absolute_dir = os.path.abspath(directory)
        input_dir_struct = {"directory": absolute_dir, "files": []}
        input_dir_files = os.listdir(absolute_dir)
        for file in input_dir_files:
            if file.endswith(".json"):
                input_dir_struct["files"].append(os.path.join(absolute_dir, file))
        input_directories.append(input_dir_struct)

    for directory in input_directories:
        file_list = []
        for file in directory["files"]:
            result = filter_json_files(settings, file)
            if result:
                file_list.append(result)

        directory["files"] = sorted(file_list)
        if not directory["files"] and fail:
            print(
                f"\nCould not find any (matching) JSON files in the specified directory {str(absolute_dir)}\n"
            )
            print("Are the correct directories specified?\n")
            print(
                f"If so, please check the -d ({settings['iodepth']}) -n ({settings['numjobs']}) and -r ({settings['rw']}) parameters.\n"
            )
            sys.exit(1)
    return input_directories


def import_json_data(filename):
    """Returns a dictionary of imported JSON data."""
    with open(filename) as json_data:
        try:
            d = json.load(json_data)
        except json.decoder.JSONDecodeError:
            print(f"Failed to JSON parse {filename}")
            sys.exit(1)
    return d


def import_json_dataset(settings, dataset):
    """
    The dataset is a list of dicts containing the absolute path and the file list.
    We need to add a third key/value pair with the raw ingested data of those files.
    """
    for item in dataset:
        item["rawdata"] = []
        for f in item["files"]:
            item["rawdata"].append(import_json_data(f))
    return dataset



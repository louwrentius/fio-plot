import sys
import configparser
from pathlib import Path


def read_ini_file(filename):
    """Read INI file and return data"""
    config = configparser.ConfigParser(
        converters={"list": lambda x: [i.strip() for i in x.split(",")]}
    )
    path = Path(filename)
    if path.exists():
        if path.is_file():
            try:
                config.read(filename)
                return config
            except configparser.DuplicateOptionError as e:
                print(f"\n{e}\n")
                sys.exit(1)
        else:
            print(f"\nConfig file {filename} is not a file.\n")
            sys.exit(1)
    else:
        print(f"\nConfig file {filename} does not exist\n")
        sys.exit(1)


def get_ini_filename(args):
    filename = None
    if len(args) > 1:
        if not "-" in args[1][0]:
            filename = args[1]
    return filename


def cleanup_dictionary(returndict):
    cleaned_dict = remove_none_values_from_dict(returndict)
    cleaned_dict = remove_lists_with_empty_strings_from_dict(cleaned_dict)
    return cleaned_dict


def remove_none_values_from_dict(returndict):
    cleaned_dict = {}
    for k, v in returndict.items():
        validated = True
        if v is None:
            validated = False
        else:
            if isinstance(v, str):
                if len(v) == 0:
                    validated = False
        if validated:
            cleaned_dict[k] = returndict[k]
    return cleaned_dict


def remove_lists_with_empty_strings_from_dict(returndict):
    """
    When parsing the INI file, a variable like 'colors' is a list of strings.
    Unfortunately the default return value is a list containing a single empty string.
    This function is just to clean this up and return None
    """
    cleaned_dict = {}
    for k, v in returndict.items():
        validated = True
        if isinstance(v, list):
            if len(v) == 1:
                if isinstance(v[0], str):
                    if len(v[0]) == 0:
                        # print(k)
                        validated = False
        if validated:
            cleaned_dict[k] = v
        else:
            cleaned_dict[k] = None
    return cleaned_dict

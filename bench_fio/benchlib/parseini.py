#!/usr/bin/env python3
import sys
import os
import configparser

def process_options(config):
    """
    This function translates 'untyped' options from the ini file into properly typed options.
    """
    listtypes = ['target','mode','block_size', 'iodepth', 'numjobs','extra_opts', 'rwmixread']
    booltypes = ['precondition','precondition_repeat','entire_device','time_based','destructive','dry_run','quiet',"remote_checks"]
    inttypes  = ['loops','runtime']
    returndict = {}
    for x in config["benchfio"]:
        if x == "output":       
            # Argparse seems to auto-expand paths, if we import through INI we do it ourselves
            returndict[x] = os.path.expanduser(config["benchfio"][x])
        elif x in listtypes:
            returndict[x] = config.getlist('benchfio', x)
        elif x in booltypes:
            returndict[x] = config.getboolean('benchfio', x)
        elif x in inttypes:
            returndict[x] = config.getint('benchfio', x)     
        else:
            returndict[x] = config["benchfio"][x]
    return returndict

def read_ini_data(args, config):
    if len(args) != 2:
        return False
    if args[1] == "-h" or args[1] == "--help":
        return False
    else:
        filename = args[1]
    
    if not os.path.isfile(filename):
        print(f"Config file {filename} not found.")
        sys.exit(1)
    
    try:
        config.read(filename)
    except configparser.DuplicateOptionError as e:
        print(f"{e}\n")
        sys.exit(1)
    
    return True


def get_settings_from_ini(args):
    config = configparser.ConfigParser(converters={'list': lambda x: [i.strip() for i in x.split(',')]})
    if read_ini_data(args, config):
        returndict = process_options(config)
        return returndict
    else:
        return None
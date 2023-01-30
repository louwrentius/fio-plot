#!/usr/bin/env python3
import os
import sys
import configparser
from pathlib import Path

def get_settings_from_ini(args):
    config = configparser.ConfigParser(converters={'list': lambda x: [i.strip() for i in x.split(',')]})
    listtypes = ['target','mode','block_size', 'iodepth', 'numjobs','extra_opts', 'rwmixread']
    booltypes = ['precondition','precondition_repeat','entire_device','time_based','destructive','dry_run','quiet']
    returndict = {}
    if len(args) == 2:
        filename = args[1]
        path = Path(filename)
        if path.is_file():
            try:
                config.read(filename)
            except configparser.DuplicateOptionError as e:
                print(f"{e}\n")
                sys.exit(1)
            for x in config["benchfio"]:
                if x in listtypes:
                    returndict[x] = config.getlist('benchfio', x)
                elif x in booltypes:
                    returndict[x] = config.getboolean('benchfio', x)
                else:
                    returndict[x] = config["benchfio"][x]
            #print(returndict)
            return returndict
        else:
            print(f"Config file {filename} not found.")
            sys.exit(1)
    return None
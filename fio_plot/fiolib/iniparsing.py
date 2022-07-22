import sys
import os
import configparser
from pathlib import Path

def read_ini_file(filename):
    config = configparser.ConfigParser(converters={'list': lambda x: [i.strip() for i in x.split(',')]})
    path = Path(filename)
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

def get_settings_from_ini(args):
    listtypes = ['input_directory','filter','colors','type']
    listinttypes = ['iodepth','numjobs']
    integers = ['maxdepth','maxjobs','dpi','max_z','max_lat','max_iops','max_bw','xlabel_depth','xlabel_parent','xlabel_segment_size','line_width','source_fontsize','subtitle_fontsize','title_fontsize']
    floats = ['percentile']
    booltypes = ['show_cpu','show_ss','table_lines','disable_grid','enable_markers','disable_fio_version','moving_average']
    returndict = {}
    if len(args) > 1:
        if not "-" in args[1][0]:
            filename = args[1]
            config = read_ini_file(filename)
            for x in ['graphtype', 'settings', 'layout']:
                for y in config[x]:
                    if y in listtypes:
                        returndict[y] = config.getlist(x, y)
                    elif y in listinttypes:
                        returndict[y] = [ int(item) for item in config.getlist(x,y)]
                    elif y in integers:
                        try: 
                            returndict[y] = config.getint(x,y)
                        except ValueError:
                            returndict[y] = None
                    elif y in floats:
                        try: 
                            returndict[y] = config.getfloat(x,y)
                        except ValueError:
                            returndict[y] = None
                    elif y in booltypes:
                        try: 
                            returndict[y] = config.getboolean(x,y)
                        except ValueError:
                            returndict[y] = None
                    else:
                        returndict[y] = config[x][y]
                #print(returndict)
            return returndict

    return None
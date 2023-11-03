import sys
import os
from . import iniparsing_support as inisupport


def parse_ini_data(config):
    """
    This function is atrocious but at this time I haven't found a better, cleaner solution yet.
    Maybe all the parameters should be stored in a configuration file that specifies attribute name, type and default value.
    """
    listtypes = ['input_directory','filter','colors','type']
    listinttypes = ['iodepth','numjobs']
    integers = ['maxdepth','maxjobs','dpi','max_z','max_lat','max_iops','min_lat','min_iops','max_bw','xlabel_depth','xlabel_parent','xlabel_segment_size','line_width','source_fontsize','subtitle_fontsize','title_fontsize']
    floats = ['percentile']
    booltypes = ['show_cpu','show_ss','table_lines','disable_grid','enable_markers','disable_fio_version','moving_average']
    returndict = {}
    for x in ['graphtype', 'settings', 'layout']:
        for y in config[x]:
            if y in listtypes:
                try:
                    returndict[y] = config.getlist(x,y)
                except ValueError:
                    returndict[y] = None
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
    cleaned_dict = inisupport.cleanup_dictionary(returndict)
    return cleaned_dict 

def get_settings_from_ini(args):
    filename = inisupport.get_ini_filename(args)
    inidata = None
    if filename:
        config = inisupport.read_ini_file(filename)
        inidata = parse_ini_data(config)
    return inidata
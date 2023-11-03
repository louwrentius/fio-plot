# Generates graphs from FIO output data for various IO queue depthts
#
# Output in PNG format.
#
# Requires matplotib and numpy.
#
import sys
from .fiolib import (
    argparsing,
    flightchecks as checks,
    getdata,
    iniparsing,
    defaultsettings
)

def clean_up_ini_parsing_list_of_strings(value):
    """
    When parsing the INI file, a variable like 'colors' is a list of strings.
    Unfortunately the default return value is a list containing a single empty string.
    This function is just to clean this up and return None
    """
    result = value
    if isinstance(value, list):
        if len(value) == 1:
            if isinstance(value[0], str):
                if len(value[0]) == 1:
                    result = None
    return result

#def merge_ini_and_default(settings, ini):
#    """
#    Merging dictionaries like {**settings, **settingsfromini } doesn't seem to result in 
#    """
#    returndata = {}
#    ini_items = ini.items()
#    for k,v in ini_items:
#        if not v:
#            if k in settings.keys():
#                returndata[k] = settings[k]
#            else:
#                returndata[k] = None
#        else:
#            returndata[k] = v
#    for k,v in settings.items():
#        if k not in returndata:
#            returndata[k] = v
#        returndata[k] = clean_up_ini_parsing_list_of_strings(v)

    #print(len(returndata["colors"][0]))
    #print(returndata)
    return returndata

def get_settings():
    settings = defaultsettings.get_default_settings()
    parser = None
    settingsfromini = iniparsing.get_settings_from_ini(sys.argv)
    if not settingsfromini:
        parser = argparsing.set_arguments(settings)
        parsersettings = vars(argparsing.get_command_line_arguments(parser))
        settings = {**settings, **parsersettings }
        settings["graphtype"] = defaultsettings.get_graphtype(settings)
    else:
        settings = {**settings, **settingsfromini }
    checks.run_preflight_checks(settings)
    return [parser, settings]

def main():
    option_found = False
    rawsettings = get_settings()
    settings = rawsettings[1]
    parser = rawsettings[0]
    routing_dict = getdata.get_routing_dict()
    graphtype = settings["graphtype"]
    settings = getdata.configure_default_settings(settings, routing_dict, graphtype)
    data = routing_dict[graphtype]["get_data"](settings)
    routing_dict[graphtype]["function"](settings, data)
    option_found = True
    checks.post_flight_check(parser, option_found)

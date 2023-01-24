# Generates graphs from FIO output data for various IO queue depthts
#
# Output in PNG format.
#
# Requires matplotib and numpy.
#
import pprint
import sys
from .fiolib import (
    argparsing,
    flightchecks as checks,
    getdata,
    iniparsing,
    defaultsettings
)

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
    #pprint.pprint(settings["iodepth"])
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
    #print(data)
    routing_dict[graphtype]["function"](settings, data)
    option_found = True

    checks.post_flight_check(parser, option_found)

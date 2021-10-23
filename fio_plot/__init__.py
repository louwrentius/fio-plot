# Generates graphs from FIO output data for various IO queue depthts
#
# Output in PNG format.
#
# Requires matplotib and numpy.
#
# import pprint

from .fiolib import (
    argparsing,
    flightchecks as checks,
    getdata
)

def main():
    settings = {}
    option_found = False
    parser = argparsing.set_arguments()
    settings = vars(argparsing.get_command_line_arguments(parser))
    checks.run_preflight_checks(settings)
    routing_dict = getdata.get_routing_dict()

    for item in routing_dict.keys():
        if settings[item]:
            settings = getdata.configure_default_settings(settings, routing_dict, item)
            # print(settings)
            data = routing_dict[item]["get_data"](settings)
            routing_dict[item]["function"](settings, data)
            option_found = True

    checks.post_flight_check(parser, option_found)

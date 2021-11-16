import sys
import os
import matplotlib


def check_matplotlib_version(requiredversion):

    matplotlibversion = matplotlib.__version__
    from pkg_resources import parse_version as V  # nice

    if V(matplotlibversion) < V(requiredversion):
        print(
            f"Matplotlib version {requiredversion} is required but version {matplotlibversion} is installed."
        )
        print("I'm sorry, but you'll have to update matplotlib.")
        sys.exit(1)


def check_if_target_directory_exists(dirpath):
    for directory in dirpath:
        if not os.path.exists(directory):
            print(f"Directory {directory} is not found.")
            sys.exit(1)
        elif not os.path.isdir(directory):
            print(f"Direcory {directory} is not a directory.")
            sys.exit(1)


def run_preflight_checks(settings):
    """This a very large function with all kinds of business logic checks.
    I don't have a good idea to clean this up yet, if that is possible."""
    check_matplotlib_version("3.3.0")
    check_if_target_directory_exists(settings["input_directory"])

    if settings["loggraph"] and not settings["type"]:
        print(
            "\nIf -g is specified, you must specify the type of data with -t (see help)\n"
        )
        sys.exit(1)

    if settings["iodepth_numjobs_3d"]:
        if not settings["type"]:
            print("\nIf -L is specified (3D Chart) you must specify -t (iops or lat)\n")
            sys.exit(1)

        if settings["type"][0] not in ["iops", "lat", "bw"]:
            print(
                "\nIf -L is specified (3D Chart) you can only select [iops,lat,bw] for -t type\n"
            )
            sys.exit(1)

        if len(settings["input_directory"]) > 1:
            print("\nIf -L is specified, only one input directory can be used.\n")
            sys.exit(1)

    if settings["compare_graph"]:
        message = "\nWhen creating a graph to compare values, iodepth or numjobs must be one value.\n"
        pm = False

        if settings["iodepth"]:
            if len(settings["iodepth"]) > 1:
                pm = True
        if settings["numjobs"]:
            if len(settings["numjobs"]) > 1:
                pm = True
        if pm:
            print(message)
            sys.exit(1)

        if len(settings["input_directory"]) < 2:
            print(
                "\n When you want to compare two datasets, please specify at least two directories with test data \
            using the -i parameter\n"
            )
            sys.exit(1)

    if settings["latency_iops_2d_qd"]:
        if len(settings["input_directory"]) > 1:
            print("\nIf -l is specified, only one input directory can be used.\n")
            sys.exit(1)

        if settings["numjobs"]:
            if len(settings["numjobs"]) > 1:
                print(
                    "\n This graph type only supports one particular value for the numjobs parameter. \n \
                Use the 3D graph type (-L) to plot both iodepth and numjobs for either iops or latency.\n"
                )
                sys.exit(1)
    if settings["latency_iops_2d_nj"]:
        if len(settings["input_directory"]) > 1:
            print("\nIf -l is specified, only one input directory can be used.\n")
            sys.exit(1)

        if settings["iodepth"]:
            if len(settings["iodepth"]) > 1:
                print(
                    "\n This graph type only supports one particular value for the iodepth parameter. \n \
                Use the 3D graph type (-L) to plot both iodepth and numjobs for either iops or latency.\n"
                )
                sys.exit(1)

    if settings["histogram"]:
        if len(settings["input_directory"]) > 1:
            print("\nIf -l is specified, only one input directory can be used.\n")
            sys.exit(1)

    if settings["show_ss"] and settings["show_cpu"]:
        print(
            "\nYou have to choose between either --show-ss or --show-cpu, you can't display both.\n"
        )
        sys.exit(1)

    if (
        not (settings["latency_iops_2d_qd"] or settings["latency_iops_2d_nj"])
        and settings["show_ss"]
    ):
        print(
            "\nThe --show-ss option only works with the 2D bar chart -l or -N graph.\n"
        )
        sys.exit(1)
    if settings["colors"] and not settings["loggraph"]:
        print("\nThe --colors option can only be used with the -g 2D line graph.\n")
        sys.exit(1)


def post_flight_check(parser, option_found):
    if not option_found:
        parser.print_help()
        print("Specify -g, -l, -L, -C or -H")
        exit(1)
    else:
        exit(0)
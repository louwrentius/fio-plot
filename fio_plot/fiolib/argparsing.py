import argparse
import sys

def set_arguments(settings):

    """Parses all commandline arguments. Based on argparse."""
    parser = argparse.ArgumentParser(
        description="Generates charts/graphs from FIO JSON output or logdata."
    )
    ag = parser.add_argument_group(title="Generic Settings")
    ag.add_argument(
        "-i",
        "--input-directory",
        nargs="+",
        help="input directory where\
            JSON files or log data (CSV) can be found.",
        required=True
    )
    ag.add_argument(
        "-o",
        "--output-filename",
        help="Specify output graph filename instead of the generated default. Note that the file type is always png.",
        default=None
    )
    ag.add_argument(
        "-T", "--title", help="specifies title to use in charts", required=True
    )
    ag.add_argument("-s", "--source", help="Author")

    exclusive_group = ag.add_mutually_exclusive_group(required=True)
    exclusive_group.add_argument(
        "-L",
        "--bargraph3d",
        action="store_true",
        help="\
            Generates a 3D-chart with iodepth and numjobs on x/y axis and iops or latency on the z-axis.",
    )
    exclusive_group.add_argument(
        "-l",
        "--bargraph2d-qd",
        action="store_true",
        help="\
            Generates a 2D barchart of IOPs and latency for all queue depths given a particular numjobs value.",
    )
    exclusive_group.add_argument(
        "-N",
        "--bargraph2d_nj",
        action="store_true",
        help="This graph type is like the \
        latency-iops-2d-qd barchart but instead of plotting queue depths for a particular numjobs value, it plots \
            numjobs values for a particular queue depth.",
    )
    exclusive_group.add_argument(
        "-H",
        "--histogram",
        action="store_true",
        help="\
            Generates a latency histogram for a particular queue depth and numjobs value.",
    )
    exclusive_group.add_argument(
        "-g",
        "--loggraph",
        action="store_true",
        help="This option generates a 2D graph of the log data recorded by FIO.",
    )
    exclusive_group.add_argument(
        "-C",
        "--compare-graph",
        action="store_true",
        help="This option generates a bar chart to compare results from different\
                                      benchmark runs.",
    )

    ag.add_argument(
        "--disable-grid",
        action="store_true",
        help="\
            Disables the dotted grid in the output graph.",
    )
    ag.add_argument(
        "--enable-markers",
        action="store_true",
        help="\
            Enable markers for the plot lines when graphing log data.",
    )
    ag.add_argument(
        "--subtitle",
        help="\
            Specify your own subtitle or leave it blank with double quotes.",
        type=str,
        default=None,
    )
    ag.add_argument(
        "-d",
        "--iodepth",
        type=int,
        nargs="+",
        default=None,
        help="\
            The I/O queue depth to graph. You can specify multiple values separated by spaces.",
    )
    ag.add_argument(
        "-n",
        "--numjobs",
        nargs="+",
        help="\
            Specifies for which numjob parameter you want the 2d graphs to be\
                 generated. You can specify multiple values separated by spaces.",
        default=None,
        type=int,
    )
    ag.add_argument(
        "-M",
        "--maxdepth",
        nargs="?",
        default=64,
        type=int,
        help="\
            Maximum queue depth to graph in 3D graph.",
    )
    ag.add_argument(
        "-J",
        "--maxjobs",
        help="\
            Maximum number of jobs to graph in 3D graph.",
        nargs="?",
        default=64,
        type=int,
    )
    ag.add_argument(
        "-D",
        "--dpi",
        help="\
            The chart will be saved with this DPI setting. Higher means larger\
                     image.",
        nargs="?",
        default=200,
        type=int,
    )
    ag.add_argument(
        "-p",
        "--percentile",
        help="\
            Calculate the percentile, default 99.99th.",
        nargs="?",
        default=99.99,
        type=float,
    )
    ag.add_argument(
        "-r",
        "--rw",
        choices=[
            "read",
            "write",
            "randread",
            "randwrite",
            "randrw",
            "trim",
            "rw",
            "readwrite",
            "randtrim",
            "trimwrite",
        ],
        required=True,
        help="Specifies the kind of data you want to graph.",
    )
    ag.add_argument(
        "-m",
        "--max-z",
        default=None,
        type=int,
        help="Optional maximum value for Z-axis in 3D graph.",
    )
    ag.add_argument(
        "-e",
        "--moving-average",
        default=None,
        type=int,
        help="The moving average helps to smooth out graphs,\
                         the argument is the size of the moving window\
                              (default is None to disable). Be carefull as this\
                                       setting may smooth out issues you may want to be aware of.",
    )
    ag.add_argument(
        "-x",
        "--min-y",
        help="Optional minimal value for y-axis. Use 'None' to disable.",
        type=str,
        default=0,
    )
    ag.add_argument(
        "-t",
        "--type",
        nargs="+",
        help="\
            This setting specifies which kind of metric you want to graph.",
        type=str,
        choices=["bw", "iops", "lat", "slat", "clat"],
    )
    ag.add_argument(
        "-f",
        "--filter",
        nargs="+",
        help="\
            filter should be read/write.",
        type=str,
        default=["read", "write"],
        choices=["read", "write"],
    )
    ag.add_argument(
        "--xlabel-depth",
        help="\
            Can be used to truncate the most significant folder name from the label. \
                Often used to strip off folders generated with benchfio (e.g. 4k)",
        type=int,
        default=0,
    )
    ag.add_argument(
        "--xlabel-parent",
        help="\
            use the parent folder(s) to make the label unique. The number\
                 represents how many folders up should be included. Default is 1. Use a value of \
                     0 to remove parent folder name.",
        type=int,
        default=1,
    )
    ag.add_argument(
        "--xlabel-segment-size",
        help="\
            Truncate folder names to make labels fit the graph. Disabled by default. \
                The number represents how many characters per \
                    segment are preserved. Used with -g.",
        type=int,
        default=1000,
    )
    ag.add_argument(
        "-w",
        "--line-width",
        help="Line width for line graphs. Can be a floating-point value. Used with -g.",
        type=float,
        default=1,
    ),
    ag.add_argument(
        "--group-bars",
        help="When using -l or -C, bars are grouped together by iops/lat type.",
        action="store_true",
    )
    ag.add_argument(
        "--show-cpu",
        help="When using the -C or -l option, a table is added with cpu_usr and cpu_sys data.",
        action="store_true",
    )
    ag.add_argument(
        "--show-ss",
        help="When using the -C or -l option, a table is added with steadystate data.",
        action="store_true",
    )
    ag.add_argument(
        "--table-lines",
        help="Draw the lines within a table (cpu/stdev)",
        action="store_true",
    )
    ag.add_argument(
        "--max-lat", help="Maximum latency value on y-axis", type=int, default=None
    )
    ag.add_argument(
        "--max-iops", help="Maximum IOPs value on y-axis", type=int, default=None
    )
    ag.add_argument(
        "--max-bw", help="Maximum bandwidth on y-axis", type=int, default=None
    )
    ag.add_argument(
        "--draw-total",
        help="Draw sum of read + write data in -g chart. Requires randrw benchmark, -f read write option.",
        action="store_true",
    )
    ag.add_argument(
        "--colors",
        help="Space separated list of colors (only used with -g). Color names can be found "
        "at this page: https://matplotlib.org/3.3.3/gallery/color/named_colors.html"
        "(example list: tab:red teal violet yellow). You need as many colors as lines.",
        type=str,
        nargs="+",
        default=None,
    )
    ag.add_argument(
        "--disable-fio-version",
        help="Don't display the fio version in the graph. It will also disable the fio-plot credit.",
        action="store_true",
    )
    ag.add_argument(
        "--title-fontsize", help="Title font size", type=int,  default=settings["title_fontsize"]
    )
    ag.add_argument(
        "--subtitle-fontsize", help="Subtitle font size", type=int,  default=settings["subtitle_fontsize"]
    )
    ag.add_argument(
        "--source-fontsize", help="Source credit (lower right) font size", type=int,  default=settings["source_fontsize"]
    )
    ag.add_argument(
        "--credit-fontsize", help="Fio version and Fio-plot credit font size", type=int, default=settings["credit_fontsize"]
    )
    ag.add_argument(
        "--table-fontsize", help="Standard deviation table / CPU table font size", type=int,  default=settings["table_fontsize"]
    )

    return parser

def get_command_line_arguments(parser):
    try:
        args = parser.parse_args()
    except OSError:
        parser.print_help()
        sys.exit(1)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    return args

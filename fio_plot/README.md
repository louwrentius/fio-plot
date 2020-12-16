```
usage: fio_plot [-h] -i INPUT_DIRECTORY [INPUT_DIRECTORY ...] -T TITLE
                [-s SOURCE] (-L | -l | -N | -H | -g | -C) [--disable-grid]
                [--enable-markers] [--subtitle SUBTITLE]
                [-d IODEPTH [IODEPTH ...]] [-n NUMJOBS [NUMJOBS ...]]
                [-M [MAXDEPTH]] [-J [MAXJOBS]] [-D [DPI]] [-p [PERCENTILE]] -r
                {read,write,randread,randwrite,randrw,trim,rw,randtrim,trimwrite}
                [-m MAX] [-e MOVING_AVERAGE] [-x MIN_Y]
                [-t {bw,iops,lat,slat,clat} [{bw,iops,lat,slat,clat} ...]]
                [-f {read,write} [{read,write} ...]]
                [--xlabel-depth XLABEL_DEPTH] [--xlabel-parent XLABEL_PARENT]
                [--xlabel-segment-size XLABEL_SEGMENT_SIZE] [-w LINE_WIDTH]
                [--group-bars] [--show-cpu] [--show-ss] [--table-lines]
                [--max-lat MAX_LAT] [--max-iops MAX_IOPS] [--max-bw MAX_BW]
                [--colors COLORS [COLORS ...]] [--disable-fio-version]

Generates charts/graphs from FIO JSON output or logdata.

optional arguments:
  -h, --help            show this help message and exit

Generic Settings:
  -i INPUT_DIRECTORY [INPUT_DIRECTORY ...], --input-directory INPUT_DIRECTORY [INPUT_DIRECTORY ...]
                        input directory where JSON files or log data (CSV) can
                        be found.
  -T TITLE, --title TITLE
                        specifies title to use in charts
  -s SOURCE, --source SOURCE
                        Author
  -L, --iodepth-numjobs-3d
                        Generates a 3D-chart with iodepth and numjobs on x/y
                        axis and iops or latency on the z-axis.
  -l, --latency-iops-2d-qd
                        Generates a 2D barchart of IOPs and latency for all
                        queue depths given a particular numjobs value.
  -N, --latency-iops-2d-nj
                        This graph type is like the latency-iops-2d-qd
                        barchart but instead of plotting queue depths for a
                        particular numjobs value, it plots numjobs values for
                        a particular queue depth.
  -H, --histogram       Generates a latency histogram for a particular queue
                        depth and numjobs value.
  -g, --loggraph        This option generates a 2D graph of the log data
                        recorded by FIO.
  -C, --compare-graph   This option generates a bar chart to compare results
                        from different benchmark runs.
  --disable-grid        Disables the dotted grid in the output graph.
  --enable-markers      Enable markers for the plot lines when graphing log
                        data.
  --subtitle SUBTITLE   Specify your own subtitle or leave it blank with
                        double quotes.
  -d IODEPTH [IODEPTH ...], --iodepth IODEPTH [IODEPTH ...]
                        The I/O queue depth to graph. You can specify multiple
                        values separated by spaces.
  -n NUMJOBS [NUMJOBS ...], --numjobs NUMJOBS [NUMJOBS ...]
                        Specifies for which numjob parameter you want the 2d
                        graphs to be generated. You can specify multiple
                        values separated by spaces.
  -M [MAXDEPTH], --maxdepth [MAXDEPTH]
                        Maximum queue depth to graph in 3D graph.
  -J [MAXJOBS], --maxjobs [MAXJOBS]
                        Maximum number of jobs to graph in 3D graph.
  -D [DPI], --dpi [DPI]
                        The chart will be saved with this DPI setting. Higher
                        means larger image.
  -p [PERCENTILE], --percentile [PERCENTILE]
                        Calculate the percentile, default 99.99th.
  -r {read,write,randread,randwrite,randrw,trim,rw,randtrim,trimwrite}, --rw {read,write,randread,randwrite,randrw,trim,rw,randtrim,trimwrite}
                        Specifies the kind of data you want to graph.
  -m MAX, --max MAX     Optional maximum value for Z-axis in 3D graph.
  -e MOVING_AVERAGE, --moving-average MOVING_AVERAGE
                        The moving average helps to smooth out graphs, the
                        argument is the size of the moving window (default is
                        None to disable). Be carefull as this setting may
                        smooth out issues you may want to be aware of.
  -x MIN_Y, --min-y MIN_Y
                        Optional minimal value for y-axis. Use 'None' to
                        disable.
  -t {bw,iops,lat,slat,clat} [{bw,iops,lat,slat,clat} ...], --type {bw,iops,lat,slat,clat} [{bw,iops,lat,slat,clat} ...]
                        This setting specifies which kind of metric you want
                        to graph.
  -f {read,write} [{read,write} ...], --filter {read,write} [{read,write} ...]
                        filter should be read/write.
  --xlabel-depth XLABEL_DEPTH
                        Can be used to truncate the most significant folder
                        name from the label. Often used to strip off folders
                        generated with benchfio (e.g. 4k)
  --xlabel-parent XLABEL_PARENT
                        use the parent folder(s) to make the label unique. The
                        number represents how many folders up should be
                        included. Default is 1. Use a value of 0 to remove
                        parent folder name.
  --xlabel-segment-size XLABEL_SEGMENT_SIZE
                        Truncate folder names to make labels fit the graph.
                        Disabled by default. The number represents how many
                        characters per segment are preserved. Used with -g.
  -w LINE_WIDTH, --line-width LINE_WIDTH
                        Line width for line graphs. Can be a floating-point
                        value. Used with -g.
  --group-bars          When using -l or -C, bars are grouped together by
                        iops/lat type.
  --show-cpu            When using the -C or -l option, a table is added with
                        cpu_usr and cpu_sys data.
  --show-ss             When using the -C or -l option, a table is added with
                        steadystate data.
  --table-lines         Draw the lines within a table (cpu/stdev)
  --max-lat MAX_LAT     Maximum latency value on y-axis
  --max-iops MAX_IOPS   Maximum IOPs value on y-axis
  --max-bw MAX_BW       Maximum bandwidth on y-axis
  --colors COLORS [COLORS ...]
                        Space separated list of colors (only used with -g).
                        Color names can be found at this page: https://matplot
                        lib.org/3.3.3/gallery/color/named_colors.html(example
                        list: tab:red teal violet yellow). You need as many
                        colors as lines.
  --disable-fio-version
                        Don't display the fio version in the graph. It will
                        also disable the fio-plot credit.
```

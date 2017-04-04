# fio-plot
Create charts from FIO storage benchmark tool JSON output

FIO: https://github.com/axboe/fio

Requires: numpy, matplotlib

![lat_iops](/example_plots/readiops_latency.png?raw=true "Latency vs IOPS")
![histogram](/example_plots/read_1_histogram.png?raw=true "Histogram")

    usage: fio-plot.py [-h] [-i INPUT_DIRECTORY] [-t TITLE] [-s SOURCE] [-L] [-H]

    Convert FIO JSON output to charts

    optional arguments:
      -h, --help            show this help message and exit

    Generic Settings:
      -i INPUT_DIRECTORY, --input-directory INPUT_DIRECTORY
                            input directory
      -t TITLE, --title TITLE
                            specifies title to use in charts
      -s SOURCE, --source SOURCE
                            Author
      -L, --latency_iops    generate latency + iops chart
      -H, --histogram       generate latency histogram per queue depth

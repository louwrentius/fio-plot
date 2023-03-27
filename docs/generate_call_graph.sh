find ../fio_plot -iname "*.py" | xargs pyan3 --dot --colored --no-defines --grouped | dot -Tpng -Granksep=1.8 > fio_plot_call_graph.png
find ../bench_fio -iname "*.py" | xargs pyan3 --dot --colored --no-defines --grouped | dot -Tpng -Granksep=1.8 > bench_fio_call_graph.png

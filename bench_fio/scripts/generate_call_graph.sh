# Requires pyan3 to be installled (pip3 install pyan3)
# The call graph of bench_fio shows that - at this time - the structure needs improvement
find ../ -not -path "./bench_fio_test.py" -iname "*.py" | xargs pyan3 --dot --colored --no-defines --grouped | dot -Tpng -Granksep=1.5 > call_graph.png

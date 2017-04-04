#!/bin/bash

export BLOCKSIZE=4k 
export SIZE=100G 
export DIRECTORY=/fio
export RUNTIME=60
export OUTPUT=./output

for x in randread randwrite
do
	for y in 01 02 04 08 16 32 64 128
	do
		sync
		echo 3 > /proc/sys/vm/drop_caches
		MYPWD=`pwd`
		echo "========================================="
		echo "Running benchmark $x with I/O depth of $y and size $SIZE"
		mkdir -p "$OUTPUT"
		export RW=$x
		export IODEPTH=$y
		fio $1 --output-format=json > $OUTPUT/$x-$y.json   
		cd $MYPWD
	done
done

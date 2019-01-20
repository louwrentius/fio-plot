#!/bin/bash

export BLOCKSIZE=4k 
export RUNTIME=60
export OUTPUT=/fio
export FILE=$2

for x in randread randwrite
do
	for y in 1 2 4 8 16 32
	do
		for z in 1 2 4 8 16 32
		do
			sync
			echo 3 > /proc/sys/vm/drop_caches
			MYPWD=`pwd`
			echo "=== $FILE ============================================"
			echo "Running benchmark $x with I/O depth of $y and numjobs $z"
			cd $OUTPUT
			export RW=$x
			export IODEPTH=$y
			export NUMJOBS=$z
			fio $1 --output-format=json > $OUTPUT/$x-$y-$z.json   
			cd $MYPWD
		done
	done
done

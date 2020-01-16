#!/bin/bash

set -eu

if [ $# -ne 5 ]
then
	echo "Usage: $0 <JOBFILE> <OUTPUT> <DIRECTORY> <FILE> <SIZE>"
	exit 1
fi

if [ -z ${FIO+x} ]
then
	FIO=fio
fi


export BLOCKSIZE=4k 
export RUNTIME=60
export JOBFILE=$1
export OUTPUT=$2
export DIRECTORY=$3
export FILE=$4
export SIZE=$5

if [ ! $($FIO --version | grep -i fio-3) ]
then
	echo "Fio version 3+ required because fio-plot expects nanosecond precision"
	exit 1
fi

if [ ! -e $JOBFILE ]
then
	echo "Fio job file $JOBFILE not found."
	exit 1
fi

if [ ! -e $OUTPUT ]
then
	echo "Directory for output $OUTPUT not found."
	exit 1
fi

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
			$FIO $JOBFILE --output-format=json > $OUTPUT/$x-$y-$z.json
			cd $MYPWD
		done
	done
done

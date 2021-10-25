#!/usr/bin/bash

PATH=$PATH:$HOME/Radiance/bin
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/Radiance/lib
RAYPATH=$RAYPATH:$HOME/Radiance/lib
export PATH
export LD_LIBRARY_PATH
export RAYPATH

dask-worker --interface=ib0 --nprocs 18 --nthreads 1 \
    --scheduler-file=/scratch/sayala/dask_testing/scheduler.json
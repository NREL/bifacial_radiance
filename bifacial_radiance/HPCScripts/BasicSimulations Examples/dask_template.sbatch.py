#!/usr/bin/bash

# Record starting time
date

# Start up dask scheduler
dask-scheduler --interface ib0 \
    --scheduler-file=/scratch/sayala/dask_testing/scheduler.json &

# Wait for scheduler to start
sleep 5

# Start up dask worker on all nodes (Note, script is used to also set
# environment variables on all the nodes. If these were set by default
# (using bash_profile for example), the commented command below could
# be used to start up workers.
srun dask_on_node.sh & 

# Wait for workers to start
sleep 5

# Run script to submit tasks
#python3 simulate_tracking_gendaylit.py
#python3 simulate_fixedtilt_gencumsky.py
python3 simulate_fixedtilt_gendaylit.py

# Record ending time
date


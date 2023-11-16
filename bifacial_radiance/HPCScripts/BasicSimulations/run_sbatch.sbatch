#!/usr/bin/bash

#SBATCH --job-name="demo_run"
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=36
#SBATCH --time=15
#SBATCH --export=ALL
#SBATCH --account=pvsoiling
# --partition=debug
#SBATCH --mail-type=ALL
#SBATCH --mail-user=silvana.ovaitt@nrel.gov

# Save info
python3 /home/sayala/BasicSimulations/addNewModule.py

#-----------------------
export BASE=/scratch/$USER
mkdir -p $BASE/$SLURM_JOB_ID
cd $BASE/$SLURM_JOB_ID
# Record starting time
date

# Save info
cat $0 > $SLURM_JOB_ID.script
printenv > $SLURM_JOB_ID.env
cp /home/sayala/BasicSimulations/simulate_tracking_gendaylit.py .

# Start up dask scheduler
dask-scheduler --interface ib0 \
    --scheduler-file=/scratch/sayala/dask_testing/scheduler.json &

# Wait for scheduler to start
sleep 5

# Start up dask worker on all nodes (Note, script is used to also set
# environment variables on all the nodes. If these were set by default
# (using bash_profile for example), the commented command below could
# be used to start up workers.
srun /home/sayala/BasicSimulations/dask_on_node.sh & 

mkdir RUNS
cd RUNS

# Wait for workers to start
sleep 5

# Run script to submit tasks
python3 /home/sayala/BasicSimulations/simulate_tracking_gendaylit.py

# Record ending time
date
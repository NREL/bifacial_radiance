import numpy as np
import os
import pandas as pd
import time
import math
from itertools import chain
from itertools import product
import bifacial_radiance
from dask.distributed import Client
import math

# Generate spectra for DNI, DHI and albedo using smarts

# Run simulation using the given timestamp and wavelength
def simulate_single(daydate=None, results_folder_fmt=None, weather_file=None):    
    
     # Verify test_folder exists 
    test_folder = results_folder_fmt.format(f'{daydate}')      
    if not os.path.exists(test_folder):
        os.makedirs(test_folder)

    # Variables that stay the same
    #Main Variables needed throughout
    albedo = 0.6
    sim_general_name = 'bifacial_example'
    lat = 37.5
    lon = -77.6
    moduletype = 'Prism Solar Bi60 landscape'
    gcr = 0.35
    hub_height = 0.2

    nMods = 20
    nRows = 7
    hpc = True
    cumulativesky = False

    limit_angle = 60
    backtrack = True


    sim_name = sim_general_name+'_'+str(daydate)
    demo = bifacial_radiance.RadianceObj(sim_name,str(test_folder))  
    demo.setGround(albedo)
    metdata = demo.readWeatherFile(weather_file, coerce_year=2021)
    sceneDict = {'gcr':gcr,'hub_height':hub_height, 'nMods': nMods, 'nRows': nRows} 
    trackerdict = demo.set1axis(limit_angle = limit_angle, backtrack = backtrack, gcr = gcr, cumulativesky = cumulativesky)

    # Restrict trackerdict here
    #foodict = {k: v for k, v in trackerdict.items() if k.startswith('21'+'_'+day_date)}
    #trackerdict = demo.gendaylit1axis(trackerdict = foodict)
    trackerdict = demo.gendaylit1axis(startdate=daydate, enddate=daydate)
    trackerdict = demo.makeScene1axis(moduletype=moduletype,sceneDict=sceneDict, cumulativesky=cumulativesky, hpc=hpc) #makeScene creates a .rad file with 20 modules per row, 7 rows.
    trackerdict = demo.makeOct1axis(customname = sim_name, hpc=hpc)
    demo.analysis1axis(customname = sim_name, hpc=hpc)

    results = 1

    return results


def run_simulations_dask(daylist, kwargs):
    # Create client
    
    scheduler_file = '/scratch/sayala/dask_testing/scheduler.json'
    client = Client(scheduler_file=scheduler_file)
    
    # Iterate over inputs
    futures = []
    
    # Add Iterations HERE

    for daydate in daylist:
        futures.append(client.submit(simulate_single, daydate=daydate, **kwargs)) 

    # Get results for all simulations
    res = client.gather(futures)
    
    # Close all dask workers and scheduler
    try:
    	client.shutdown()
    except:
        pass

    # Close client
    client.close()

    res = 'FINISHED!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
    return res


if __name__ == "__main__":
    print(">>>>>>>>>>>>>>>>>> STARTING !")
    # Define locations within file system
    weather_file = '/home/sayala/WeatherFiles/USA_CO_Boulder-Broomfield-Jefferson.County.AP.724699_TMY3.epw'  
    results_folder_fmt = '/scratch/sayala/RadianceScenes/BasicSimulations/Gendaylit1axis/Day_{}' 

    # Define inputs    
    kwargs = {
        'weather_file': weather_file,
        'results_folder_fmt': results_folder_fmt
    }
    
    import datetime

    FullYear = False

    if FullYear:
        start = datetime.datetime.strptime("01-01-2021", "%d-%m-%Y")
        end = datetime.datetime.strptime("31-12-2021", "%d-%m-%Y") # 2014 not a leap year.
    else:
        start = datetime.datetime.strptime("24-03-2021", "%d-%m-%Y")
        end = datetime.datetime.strptime("27-03-2021", "%d-%m-%Y") # 2014 not a leap year.

    date_generated = [start + datetime.timedelta(days=x) for x in range(0, (end-start).days)]

    daylist = []
    for date in date_generated:
        daylist.append(date.strftime("%y_%m_%d"))
    # loop doesn't add last day :
    daylist.append('21_12_31')


    # Pass variables being looped on, and kwargs
    run_simulations_dask(daylist, kwargs)

    print("*********** DONE ************")

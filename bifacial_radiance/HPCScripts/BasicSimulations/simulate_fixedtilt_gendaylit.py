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
def simulate_single(idx=None, results_folder_fmt=None, weather_file=None):    
    
     # Verify test_folder exists 
    test_folder = results_folder_fmt.format(f'{idx:04}')      
    if not os.path.exists(test_folder):
        os.makedirs(test_folder)

    # Variables that stay the same
    #Main Variables needed throughout
    albedo = 0.6
    sim_general_name = 'bifacial_example'
    lat = 37.5
    lon = -77.6
    moduletype = 'tutorial-module'
    tilt = 10
    pitch = 3
    clearance_height = 0.2
    azimuth = 180
    nMods = 20
    nRows = 7
    hpc = True

    sim_name = sim_general_name+'_'+str(idx)
    demo = bifacial_radiance.RadianceObj(sim_name,str(test_folder), hpc=True)  
    demo.setGround(albedo)
    metdata = demo.readWeatherFile(weather_file) 
    demo.gendaylit(idx)
    sceneDict = {'tilt':tilt,'pitch':pitch,'clearance_height':clearance_height,'azimuth':azimuth, 'nMods': nMods, 'nRows': nRows} 
    scene = demo.makeScene(module=moduletype,sceneDict=sceneDict,radname = sim_name)
    octfile = demo.makeOct(octname = demo.basename)  
    analysis = bifacial_radiance.AnalysisObj(octfile=octfile, name=sim_name, hpc=True)
    frontscan, backscan = analysis.moduleAnalysis(scene=scene)
    frontdict, backdict = analysis.analysis(octfile, name=sim_name, frontscan=frontscan, backscan=backscan)
    results = 1

    return results


def run_simulations_dask(indices, kwargs):
    # Create client
    
    scheduler_file = '/scratch/sayala/dask_testing/scheduler.json'
    client = Client(scheduler_file=scheduler_file)
    
    # Iterate over inputs
    futures = []
    
    # Add Iterations HERE

    for idx in indices:
        futures.append(client.submit(simulate_single, idx=idx, **kwargs)) 

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

    # Define locations within file system
    weather_file = '/home/sayala/WeatherFiles/USA_CO_Boulder-Broomfield-Jefferson.County.AP.724699_TMY3.epw'  
    results_folder_fmt = '/scratch/sayala/RadianceScenes/BasicSimulations/FixedTilt_Gendaylit/Timestamp_{}' 

    # Define inputs    
    kwargs = {
        'weather_file': weather_file,
        'results_folder_fmt': results_folder_fmt
    }
    
    # Array for all hours in the year
    indices = np.array(list(range(0, 8760)))    
    indices = np.array(list(range(4020, 4022)))

    # Pass variables being looped on, and kwargs
    run_simulations_dask(indices, kwargs)

    print("*********** DONE ************")
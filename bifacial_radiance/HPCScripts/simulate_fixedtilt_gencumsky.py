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
def simulate_single(tilt=None, results_folder_fmt=None, weather_file=None):    
    
     # Verify test_folder exists 
    test_folder = results_folder_fmt.format(f'{tilt:02}')      
    if not os.path.exists(test_folder):
        os.makedirs(test_folder)

    # Variables that stay the same
    #Main Variables needed throughout
    albedo = 0.6
    sim_general_name = 'bifacial_example'
    lat = 37.5
    lon = -77.6
    moduletype = 'Prism Solar Bi60 landscape'
    pitch = 3
    clearance_height = 0.2
    azimuth = 180
    nMods = 20
    nRows = 7
    hpc = True

    pitch = 3
    clearance_height = 0.2
    azimuth = 90
    nMods = 20
    nRows = 7
    hpc = True

    sim_name = sim_general_name+'_'+str(tilt)
    demo = bifacial_radiance.RadianceObj(sim_name,str(test_folder))  
    demo.setGround(albedo)
    metdata = demo.readWeatherFile(weather_file) 
    demo.genCumSky(savefile = sim_name)
    sceneDict = {'tilt':tilt,'pitch':pitch,'clearance_height':clearance_height,'azimuth':azimuth, 'nMods': nMods, 'nRows': nRows} 
    scene = demo.makeScene(moduletype=moduletype,sceneDict=sceneDict, hpc=hpc, radname = sim_name)
    octfile = demo.makeOct(filelist= demo.getfilelist(), octname = demo.basename , hpc=hpc)  
    analysis = bifacial_radiance.AnalysisObj(octfile=octfile, name=sim_name)
    frontscan, backscan = analysis.moduleAnalysis(scene=scene)
    frontdict, backdict = analysis.analysis(octfile, name=sim_name, frontscan=frontscan, backscan=backscan)


    results = 1

    return results


def run_simulations_dask(tilts, kwargs):
    # Create client
    
    scheduler_file = '/scratch/sayala/dask_testing/scheduler.json'
    client = Client(scheduler_file=scheduler_file)
    
    # Iterate over inputs
    futures = []
    
    # Add Iterations HERE

    for tilt in tilts:
        futures.append(client.submit(simulate_single, tilt=tilt, **kwargs)) 

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

    print(" I AM HERE")
    # Define locations within file system
    weather_file = '/home/sayala/WeatherFiles/USA_CO_Boulder-Broomfield-Jefferson.County.AP.724699_TMY3.epw'  
    results_folder_fmt = '/scratch/sayala/RadianceScenes/BasicSimulations/FixedTilt_Gencumsky/Tilt_{}' 

    # Define inputs    
    kwargs = {
        'weather_file': weather_file,
        'results_folder_fmt': results_folder_fmt
    }
    
    # Array for all hours in the year
    tilts = [25, 30]

    # Pass variables being looped on, and kwargs
    run_simulations_dask(tilts, kwargs)

    print("*********** DONE ************")

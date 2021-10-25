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
def simulate_single(daydate=None, posx=None, moduleWith=None, results_folder_fmt=None, weather_file=None):    
    
     # Verify test_folder exists                                        
    if moduleWith:
        results_folder_fmt = '/scratch/sayala/RadianceScenes/BasicSimulations/Gendaylit1axis/WithResults/Day_{}_Posx_{}'
        custname = '_WITH_'+'pos_'+str(posx)
        moduletype = 'Prism Solar Bi60 landscape With' #for with case

    else:
        results_folder_fmt = '/scratch/sayala/RadianceScenes/BasicSimulations/Gendaylit1axis/WithoutResults/Day_{}_Posx_{}'
        custname = '_WITHOUT_'+'pos_'+str(posx)
        moduletype = 'FirstSolar Imaginary Without'

    test_folder = results_folder_fmt.format(f'{daydate}', f'{str(posx)}')      
    if not os.path.exists(test_folder):
        os.makedirs(test_folder)


    # Variables that stay the same
    #Main Variables needed throughout
    albedo = 0.2
    sim_general_name = 'bifacial_example'
    lat = 39.742
    lon = -105.179
    #moduletype = 'Prism Solar Bi60 landscape'

    gcr = 0.35
    hub_height = 1.35

    nMods = 20
    nRows = 10
    hpc = True
    cumulativesky = False

    limit_angle = 60
    backtrack = True
    
    simplesim = False
    if simplesim: 
        sensorsy = 1
    else:
        sensorsy = 40

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
    #demo.analysis1axis(customname = sim_name, hpc=hpc)

    frame_thickness = 0.01
    mod_x=1
    modscanBack = {}

    modscanBack['ystart']  = mod_x/2.0 - (frame_thickness + 0.001) - 0.005*posx # (adding frame thicknes plus 1 mm so it does not overlay exactly) 

    demo.analysis1axis(singleindex=daydate+'_00', modscanfront=modscanBack, 
                       modscanback=modscanBack, sensorsy = sensorsy, 
                       customname = custname) 
                        #customname ommitted for test (journal)
        
    results = 1

    return results


def run_simulations_dask(daylist, posxs, moduleWiths,  kwargs):
    # Create client
    
    scheduler_file = '/scratch/sayala/dask_testing/scheduler.json'
    client = Client(scheduler_file=scheduler_file)
    
    # Iterate over inputs
    futures = []
    
    # Add Iterations HERE

    for daydate in daylist:
        for posx in posxs:
            for moduleWith in moduleWiths:
                futures.append(client.submit(simulate_single, daydate=daydate, posx=posx, moduleWith=moduleWith, **kwargs)) 

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

    weather_file = '/home/sayala/WeatherFiles/SRRL_WeatherFile_TMY3_60_2020_FIXED.csv'  

    With = True
#    weather_file = '/home/sarefeen/WeatherFiles/SRRL_WeatherFile_TMY3_60_2020.csv'  



    # Define inputs    
    kwargs = {
        'weather_file': weather_file,
      #  'results_folder_fmt': results_folder_fmt
    }
    
    import datetime
        
    moduleWiths = [True, False]
     
    # daylist = ['21_04_29_06', '21_04_29_07', '21_04_29_08', '21_04_29_09',
    #            '21_04_29_10', '21_04_29_11', '21_04_29_12', '21_04_29_13', '21_04_29_14',
    #            '21_04_29_15', '21_04_29_16', '21_04_29_17', '21_04_29_18']
    
    
    daylist = ['21_04_29_11']
    
   # posxs = np.array(list(range(0, 200)))    
    posxs = np.array(list(range(0, 200)))   

    # Pass variables being looped on, and kwargs
    run_simulations_dask(daylist, posxs, moduleWiths, kwargs)

    print("*********** DONE ************")
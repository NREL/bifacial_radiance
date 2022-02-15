import numpy as np
import os
import pandas as pd
import time
import math
from itertools import chain
import bifacial_radiance
from dask.distributed import Client
from math import sin, cos, radians


# Run simulation using the given timestamp 
def simulate_single(xgap=None, numpanels = None, sensorx=None,
                   test_folder_fmt=None, weather_file=None):    

    ft2m = 0.3048
    hub_height = 8.0 * ft2m
    y = 1
    pitch = 0.001 # y * np.cos(np.radians(tilt))+D
    ygap = 0.15
    tilt = 18

    sim_name = ('Coffee_'+str(numpanels)+'up_'+
                str(round(xgap,1))+'_xgap_'+str(sensorx)+'posx')

    # Verify test_folder exists before creating radiance obj
    test_folder = test_folder_fmt.format(f'{numpanels}', 
                                        f'{round(xgap,1)}',f'{sensorx:03}')

    if not os.path.exists(test_folder):
        os.makedirs(test_folder)

    lat = 18.202142
    lon = -66.759187
    albedo = 0.25 # Grass value from Torres Molina, "Measuring UHI in Puerto Rico" 18th LACCEI 
                # International Multi-Conference for Engineering, Education, and Technology
    x = 1.64      

    azimuth = 180
    if numpanels == 3:
        nMods = 9
    if numpanels == 4:
        nMods = 7
    nRows = 1
    moduletype = 'PR_'+str(numpanels)+'up_'+str(round(xgap,1))+'xgap'

    hpc = False

    demo = bifacial_radiance.RadianceObj(sim_name,str(test_folder))  
    demo.setGround(albedo)
    demo.readWeatherFile(weather_file)

    sceneDict = {'tilt':tilt,'pitch':pitch,'hub_height':hub_height,'azimuth':azimuth, 'nMods': nMods, 'nRows': nRows} 
    scene = demo.makeScene(moduletype=moduletype,sceneDict=sceneDict, hpc=hpc, radname = sim_name)

    demo.genCumSky()

    octfile = demo.makeOct(filelist = demo.getfilelist(), octname = demo.basename, hpc=hpc)  
    analysis = bifacial_radiance.AnalysisObj(octfile=octfile, name=sim_name)

    ii = 1
    jj = 1
    
    simplesim=False
    if simplesim:
        sensorsy_front = 20  
        sensorsy_back = 1
        sensorsx_front = 1
        sensorsx_back = 1
    else:
        sensorsy_front = 201
        sensorsy_back = 1
        sensorsx_front = 1
        sensorsx_back = 1


    frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy_front=sensorsy_front,
                                                        sensorsx_front=sensorsx_front,
                                                        sensorsy_back=sensorsy_back,
                                                        sensorsx_back=sensorsx_back)

 
    xinc = 0.10 # cm . Sampling every 10 cm. 
    yinc = 0.10 # cm  . Sampling every 10 cm

    frontscan['zstart'] = 0.01
    frontscan['xstart'] = -20+sensorx*xinc
    frontscan['orient'] = '0 0 -1'
    frontscan['zinc'] = 0
    frontscan['yinc'] = yinc
    frontscan['ystart'] = -10 # n
    frontdict, backdict = analysis.analysis(octfile = octfile, name = 'xloc_'+str(sensorx), 
                                            frontscan=frontscan, backscan=backscan)

    results = 1

    print("***** Finished simulation for "+ str(sim_name))

    results=1
    return results



def run_simulations_dask(xgaps, numpanelss, sensorsxs, kwargs):
    # Create client
    
    scheduler_file = '/scratch/sayala/dask_testing/scheduler.json'
    client = Client(scheduler_file=scheduler_file)
    
    # Iterate over inputs
    futures = []
    
    for nn in range (0, len(numpanelss)):
        numpanels = numpanelss[nn]
        for xx in range (0, len(xgaps)):
            xgap = xgaps[xx]
            for ii in sensorsxs:
                futures.append(client.submit(simulate_single, xgap=xgap, numpanels=numpanels, sensorx=ii,**kwargs))

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

    weather_file = '/scratch/sayala/JORDAN/PRI_Mercedita.AP.785203_TMY3.epw'
    test_folder_fmt = '/scratch/sayala/JORDAN/PUERTO_RICO_NEW/numpanels_{}_xgap_{}_Posx_{}'
    
   
    # Define inputs    
    kwargs = {
        'weather_file': weather_file,
        'test_folder_fmt': test_folder_fmt
    }
    
#    indices = np.array(list(range(2881, 6552)))
    ft2m = 0.3048
    lat = 18.202142

    # Loops

    # simplesim
    simplesim=False
    if simplesim:
        xgaps = np.array([3, 4])*ft2m
        numpanelss = np.array([3, 4])
        sensorsxs = 2
    else:
        xgaps = np.array([3, 4, 6, 9, 12, 15, 18, 21]) * ft2m
        numpanelss = np.array([3, 4])
        sensorsxs = np.array(list(range(0, 401)))   

    # Specify method for running simulation
    use_dask = True
    if use_dask:
        run_simulations_dask(xgaps, numpanelss, sensorsxs, kwargs)

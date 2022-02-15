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
def simulate_single(idx=None, test_folder_fmt=None, weather_file=None):    
    
    # Verify test_folder exists before creating radiance obj
    test_folder = test_folder_fmt.format(f'{idx}')
    if not os.path.exists(test_folder):
        os.makedirs(test_folder)


    # Input Values
    radiance_name = 'JackSolar'
    lat = 40.1217  # Given for the project site at Colorado
    lon = -105.1310  # Given for the project site at Colorado
    moduletype='PrismSolar'
    numpanels = 1  # This site have 1 module in Y-direction
    x = 1  
    y = 2
    zgap = 0.10 # no gap to torquetube.
    sensorsy = 6  # this will give 6 sensors per module in y-direction
    sensorsx = 3   # this will give 3 sensors per module in x-direction
    torquetube = True
    axisofrotationTorqueTube = True 
    diameter = 0.15  # 15 cm diameter for the torquetube
    tubetype = 'square'    # Put the right keyword upon reading the document
    material = 'black'   # Torque tube of this material (0% reflectivity)

    # Scene variables
    nMods = 20
    nRows = 7
    hub_height = 1.8 # meters
    pitch = 5.1816 # meters      # Pitch is the known parameter 
    albedo = 0.2  #'Grass'     # ground albedo
    gcr = y/pitch

    cumulativesky = False
    limit_angle = 60 # tracker rotation limit angle
    angledelta = 0.01 # we will be doing hourly simulation, we want the angle to be as close to real tracking as possible.
    backtrack = True 

    # START SIMULATION
    rad_obj = bifacial_radiance.RadianceObj(radiance_name, str(test_folder))
    
    # Set ground
    rad_obj.readWeatherFile(weather_file, label = 'center')
    
    # Query data from metadata for index of interest
    foo=rad_obj.metdata.datetime[idx]
    dni = rad_obj.metdata.dni[idx]
    dhi = rad_obj.metdata.dhi[idx]
    res_name = "irr_Jacksolar_"+str(foo.year)+"_"+str(foo.month)+"_"+str(foo.day)+"_"+str(foo.hour)+"_"+str(foo.minute)
    
    rad_obj.setGround(albedo)

    # Set sky
    solpos = rad_obj.metdata.solpos.iloc[idx]
    zen = float(solpos.zenith)
    azm = float(solpos.azimuth) - 180

    if zen > 90:
        print("Nightime ")
        return

    rad_obj.gendaylit2manual(dni, dhi, 90 - zen, azm)
    
    # Set tracker information
    tilt = round(rad_obj.getSingleTimestampTrackerAngle(rad_obj.metdata, idx, gcr, limit_angle=65),1)

    sceneDict = {'pitch': pitch, 'tilt': tilt, 'azimuth': 90, 'hub_height':hub_height, 'nMods':nMods, 'nRows': nRows}  

    scene = rad_obj.makeScene(moduletype=moduletype,sceneDict=sceneDict)
    octfile = rad_obj.makeOct(octname=res_name)  

    sensorsx = 22
    sensorsy = 105
    module_scenex = x+0.01
    extra_sampling_space_x = 0.10
    spacingsensorsx = (module_scenex+extra_sampling_space_x)/(sensorsx-1)
    startxsensors = (module_scenex+extra_sampling_space_x)/2
    xinc = pitch/(sensorsy-1) 

    analysis = bifacial_radiance.AnalysisObj()

    frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=sensorsy)
    
    #LOCATION_APOGEES
    for senx in range(0,sensorsx):
        frontscan['zstart'] = 0
        frontscan['xstart'] = 0
        frontscan['orient'] = '0 0 -1'
        frontscan['zinc'] = 0
        frontscan['xinc'] = xinc
        frontscan['ystart'] = startxsensors-spacingsensorsx*senx
        frontdict, backdict = analysis.analysis(octfile = octfile, name = 'xloc_'+str(senx), 
                                                frontscan=frontscan, backscan=backscan)

    results = 1
    
    print("***** Finished simulation for "+ str(foo))

    return results



def run_simulations_dask(indices, kwargs):
    # Create client
    
    scheduler_file = '/scratch/sayala/dask_testing/scheduler.json'
    client = Client(scheduler_file=scheduler_file)
    
    # Iterate over inputs
    futures = []
    
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

    weather_file = '/scratch/sayala/JORDAN/USA_CO_Boulder-Broomfield-Jefferson.County.AP.724699_TMY3.epw'
    test_folder_fmt = '/scratch/sayala/JORDAN/JackSolar_Hourly/Hour_{}'
    
    
    # Define inputs    
    kwargs = {
        'weather_file': weather_file,
        'test_folder_fmt': test_folder_fmt
    }
    
    indices = [4020, 4021, 4022] 
    indices = np.array(list(range(0, 8760)))
    # Specify method for running simulation
    use_dask = True
    if use_dask:
        run_simulations_dask(indices, kwargs)

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
def simulate_single(clearance_height=None, xgap=None,
                   tilt = None, D = None,
                   test_folder_fmt=None, weather_file=None):    

    ft2m = 0.3048
    y = 1
    pitch = y * np.cos(np.radians(tilt))+D

    sim_name = ('Coffee_ch_'+str(round(clearance_height,1))+
                '_xgap_'+str(round(xgap,1))+\
                '_tilt_'+str(round(tilt,1))+
                '_pitch_'+str(round(pitch,1)))

    # Verify test_folder exists before creating radiance obj
    test_folder = test_folder_fmt.format(f'{clearance_height}', 
                                        f'{xgap}',
                                        f'{tilt}',
                                        f'{pitch}')

    if not os.path.exists(test_folder):
        os.makedirs(test_folder)

    lat = 18.202142
    lon = -66.759187
    albedo = 0.25 # Grass value from Torres Molina, "Measuring UHI in Puerto Rico" 18th LACCEI 
                # International Multi-Conference for Engineering, Education, and Technology
    x = 1.64      

    azimuth = 180
    nMods = 20
    nRows = 7
    numpanels = 1
    moduletype = 'PR_'+str(round(xgap,1))

    hpc = False

    demo = bifacial_radiance.RadianceObj(sim_name,str(test_folder))  
    demo.setGround(albedo)
    demo.readWeatherFile(weather_file)

    sceneDict = {'tilt':tilt,'pitch':pitch,'clearance_height':clearance_height,'azimuth':azimuth, 'nMods': nMods, 'nRows': nRows} 
    scene = demo.makeScene(moduletype=moduletype,sceneDict=sceneDict, hpc=hpc, radname = sim_name)

    text = ''

    tree_albedo = 0.165 # Wikipedia [0.15-0.18]
    trunk_x = 0.8 * ft2m
    trunk_y = trunk_x
    trunk_z = 1 * ft2m

    tree_x = 3 * ft2m
    tree_y = tree_x
    tree_z = 4 * ft2m

    for ii in range(0,3):
        coffeeplant_x = (x+xgap)/2 + (x+xgap)*ii
        for jj in range(0,3):
            coffeeplant_y = pitch/2 + pitch*jj
            name = 'tree'+str(ii)+str(jj)
            text = '! genrev litesoil tube{}tree t*{} {} 32 | xform -t {} {} {}'.format('head'+str(ii)+str(jj),tree_z, tree_x/2.0, 
                                                                                                -trunk_x/2.0 + coffeeplant_x, 
                                                                                                -trunk_x/2.0 + coffeeplant_y, trunk_z)
            text += '\r\n! genrev litesoil tube{}tree t*{} {} 32 | xform -t {} {} 0'.format('trunk'+str(ii)+str(jj),trunk_z, trunk_x/2.0, 
                                                                                                -trunk_x/2.0 + coffeeplant_x, 
                                                                                                -trunk_x/2.0 + coffeeplant_y)
    
            customObject = demo.makeCustomObject(name,text)
            demo.appendtoScene(radfile=scene.radfiles, customObject=customObject, text="!xform -rz 0")
    demo.genCumSky()

    octfile = demo.makeOct(filelist = demo.getfilelist(), octname = demo.basename, hpc=hpc)  
    analysis = bifacial_radiance.AnalysisObj(octfile=octfile, name=sim_name)


    ii = 1
    jj = 1
    coffeeplant_x = (x+xgap)/2 + (x+xgap)*ii 
    coffeeplant_y = pitch/2 + pitch*jj
    frontscan, backscan = analysis.moduleAnalysis(scene=scene, sensorsy=1)

    treescan_south = frontscan.copy()
    treescan_north = frontscan.copy()
    treescan_east = frontscan.copy()
    treescan_west = frontscan.copy()
    
    treescan_south['xstart'] = coffeeplant_x
    treescan_south['ystart'] = coffeeplant_y  - tree_x/2.0 - 0.05
    treescan_south['zstart'] = tree_z
    treescan_south['orient'] = '0 1 0'

    treescan_north['xstart'] = coffeeplant_x
    treescan_north['ystart'] = coffeeplant_y  + tree_x/2.0 + 0.05
    treescan_north['zstart'] = tree_z
    treescan_north['orient'] = '0 -1 0'

    treescan_east['xstart'] = coffeeplant_x + tree_x/2.0 + 0.05
    treescan_east['ystart'] = coffeeplant_y 
    treescan_east['zstart'] = tree_z
    treescan_east['orient'] = '-1 0 0'

    treescan_west['xstart'] = coffeeplant_x - tree_x/2.0 - 0.05
    treescan_west['ystart'] = coffeeplant_y 
    treescan_west['zstart'] = tree_z
    treescan_west['orient'] = '1 0 0'

    groundscan = frontscan.copy() 
    groundscan['xstart'] = coffeeplant_x
    groundscan['ystart'] = coffeeplant_y
    groundscan['zstart'] = 0.05
    groundscan['orient'] = '0 0 -1'
    analysis.analysis(octfile, name=sim_name+'_North&South', frontscan=treescan_north, backscan=treescan_south)
    analysis.analysis(octfile, name=sim_name+'_East&West', frontscan=treescan_east, backscan=treescan_west)


    print("***** Finished simulation for "+ str(sim_name))

    results=1
    return results



def run_simulations_dask(clearance_heights, xgaps, Ds, tilts, kwargs):
    # Create client
    
    scheduler_file = '/scratch/sayala/dask_testing/scheduler.json'
    client = Client(scheduler_file=scheduler_file)
    
    # Iterate over inputs
    futures = []
    
    for ch in range (0, len(clearance_heights)):
        clearance_height = clearance_heights[ch]
        for xx in range (0, len(xgaps)):
            xgap = xgaps[xx]
            for tt in range (0, len(tilts)):
                tilt = tilts[tt]
                for dd in range (0, len(Ds)):
                    D = Ds[dd]
                    futures.append(client.submit(simulate_single, clearance_height=clearance_height,
                                                            xgap=xgap, tilt=tilt, D=D, **kwargs))

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
    test_folder_fmt = '/scratch/sayala/JORDAN/PUERTO_RICO/CH_{}_xgap_{}_tilt_{}_pitch_{}'
    
   
    # Define inputs    
    kwargs = {
        'weather_file': weather_file,
        'test_folder_fmt': test_folder_fmt
    }
    
#    indices = np.array(list(range(2881, 6552)))
    ft2m = 0.3048
    lat = 18.202142

    # Loops
    clearance_heights = np.array([6.0, 8.0, 10.0])* ft2m
    xgaps = np.array([2, 3, 4]) * ft2m
    Ds = np.array([2, 3, 4]) * ft2m    # D is a variable that represents the spacing between rows, not-considering the collector areas.
    tilts = [round(lat), 10]

    # Specify method for running simulation
    use_dask = True
    if use_dask:
        run_simulations_dask(clearance_heights, xgaps, Ds, tilts, kwargs)

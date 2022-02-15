import numpy as np
import os
import pandas as pd
import time
import math
from itertools import chain
from itertools import product

from bifacial_radiance import AnalysisObj, load, MetObj, RadianceObj
from bifacial_radiance.spectral_utils import (spectral_property,
                                              spectral_irradiance_smarts,
                                              spectral_albedo_smarts)

from dask.distributed import Client

#from multitask_worker.worker import run_partial
#from multitask_worker.slurm_utils import slurm_worker_id, slurm_worker_cnt

from math import sin, cos, radians

# Generate spectra for DNI, DHI and albedo using smarts

# Run simulation using the given timestamp and wavelength
def simulate_single(idx=None, wavelength=None, 
                    test_folder_fmt=None, best_data_file=None, data_folder=None):    
    
    # Verify test_folder exists before creating radiance obj
    test_folder = test_folder_fmt.format(f'{idx:04}',f'{wavelength:04}')
    if not os.path.exists(test_folder):
        os.makedirs(test_folder)

    ### NEW FOR SPECTRA 
    
    # Create radiance obj
    radiance_name = 'BEST'
    rad_obj = RadianceObj(radiance_name, str(test_folder))
    
    # Set ground
    rad_obj.readWeatherFile(best_data_file, label = 'center')
    
    # Check to see if file exists
    foo=rad_obj.metdata.datetime[idx]

    # If a wavelength was specified, assume this is a spectral simulation and
    # try to load spectra files.
    # Determine file suffix
    suffix = f'_{idx}.txt'
    
    # Generate/Load albedo
    alb_file = os.path.join(data_folder, "alb"+suffix)
    spectral_alb = spectral_property.load_file(alb_file)
                
    # Generate/Load dni and dhi
    dni_file = os.path.join(data_folder, "dni"+suffix)
    dhi_file = os.path.join(data_folder, "dhi"+suffix)
    ghi_file = os.path.join(data_folder, "ghi"+suffix)
    spectral_dni = spectral_property.load_file(dni_file)
    spectral_dhi = spectral_property.load_file(dhi_file)
    spectral_ghi = spectral_property.load_file(ghi_file)
            
    weighted_albedo = False
    if wavelength:
        alb = spectral_alb[wavelength]
        dni = spectral_dni[wavelength]
        dhi = spectral_dhi[wavelength]
    elif weighted_albedo:
        _alb = np.array(spectral_alb[range(300, 2501, 10)])
        _dni = np.array(spectral_dni[range(300, 2501, 10)])
        _dhi = np.array(spectral_dhi[range(300, 2501, 10)])
        _ghi = np.array(spectral_ghi[range(300, 2501, 10)])
        
        alb_scale = np.sum(_alb * (_ghi))/np.sum(alb * (_ghi))
        alb *= alb_scale
        print(f'For IDX {idx}, albedo scaled by {alb_scale}')
        

    res_name = "irr_Hydra_"+str(foo.year)+"_"+str(foo.month)+"_"+str(foo.day)+"_"+str(foo.hour)+"_"+str(foo.minute)+'.csv'
    
    rad_obj.setGround(alb)
    # Set sky
    solpos = rad_obj.metdata.solpos.iloc[idx]
    zen = float(solpos.zenith)
    azm = float(solpos.azimuth) - 180
    rad_obj.gendaylit2manual(dni, dhi, 90 - zen, azm)

    
    lat=39.742 # NREL SSRL location
    lon=-105.179 # NREL SSRL location
    elev=1829
    timezone=-7
    axis_tilt=0
    axis_azimuth=180
    limit_angle=60
    backtrack=True # Set to false since it's only 1 row, no shading.
    gcr=0.35
    angledelta=0 # rounding to ints
    numpanels=1
    torquetube=False # We are going to add it separately
    diameter = 0.130175        # 5 1/8 in
    torqueTubeMaterial='Metal_Grey'
    tubetype='Round'
    axisofrotationTorqueTube = True
    azimuth=90
    material = 'Metal_Grey'
    hub_height = 1.5#0.927
    postdiamy = 0.1016       # N-S measurement, 4 "
    postdiamx = 0.1524       # E-W measurement, 6 "
    ttedgeoffset = -1.07  # south edge 42 in. negative because that's how I coded the trnaslation.
    ttedgeoffsetNorth = 0.10795 # North edge $ 4 1/4 inches
    length = 21.64-ttedgeoffset+ttedgeoffsetNorth # map goes from beginning of south post, but there is a bit more post to hold the sensor
    decimate = True
    zgap = 0.05 + diameter/2     # 1 inch of arm, + 1 3/16 of panel width on average ~ 0.055 m
    decimateinterval = '15Min'
    pitch=5.7 # distance between rows
    ypostlist=[0, 4.199, 10.414, 16.63, 21.64]
    ymods=[0.589, 1.596, 2.603, 3.610, 4.788, 5.795, 6.803, 7.810, 8.818, 9.825, 11.003, 12.011, 13.018, 14.026, 15.034, 16.041, 17.220, 18.230, 19.240, 20.250]
    
    numcellsx = 6
    numcellsy = 12
    xcell = 0.142
    ycell = 0.142   
    xcellgap = 0.02
    ycellgap = 0.02
    module_type = 'Bi60' 
    
    xgap = 0.046
    ygap=0
    glass = False

    # Set tracker information
    try:
        tilt = round(rad_obj.getSingleTimestampTrackerAngle(rad_obj.metdata, idx, gcr, limit_angle=65),1)
    except: 
        print("Night time !!!!!!!!!")
        print("")
        print("")
        return None

    if math.isnan(tilt):
        return None
    
    sazm = 90    
    
    cellLevelModuleParams = {'numcellsx': numcellsx, 'numcellsy':numcellsy, 
                             'xcell': xcell, 'ycell': ycell, 'xcellgap': xcellgap, 'ycellgap': ycellgap}
    
    # Running make module on HPC can cause issues if too many works try to 
    # write to the module file at the same time. If something goes wrong,
    # assume the module has already been created.
    '''
    try:
    
        mymodule = rad_obj.makeModule(name=module_type, torquetube=torquetube, diameter=diameter, tubetype=tubetype, material=material, 
                                          xgap=xgap, ygap=ygap, zgap=zgap, numpanels=numpanels,# x=0.952, y=1.924,
                                          cellLevelModuleParams=cellLevelModuleParams, 
                                          axisofrotationTorqueTube=axisofrotationTorqueTube, glass=glass, z=0.0002)
        rad_obj.makeModule(name='sensor', x=0.15, y=0.15, z=0.04)

    except:
        print('Failed to make module.')
    '''
    radname = "Bi60_"+str(foo.year)+"_"+str(foo.month)+"_"+str(foo.day)+"_"+str(foo.hour)+"_"+str(foo.minute)+"_"
    
    sceneDict1 = {'tilt': tilt, 'pitch':pitch,'hub_height':hub_height,'azimuth':azimuth,'nMods': 1, 'nRows': 1, 'originx': pitch*0, 'originy': ymods[0]} 
    sceneObj1 = rad_obj.makeScene(moduletype=module_type, sceneDict=sceneDict1, radname = radname) 
    
    sceneDict2 = {'tilt': tilt, 'pitch':pitch,'hub_height':hub_height,'azimuth':azimuth,'nMods': 1, 'nRows': 1, 'originx': pitch*1, 'originy': ymods[0]} 
    sceneObj2 = rad_obj.makeScene(moduletype=module_type,sceneDict=sceneDict2, radname = radname) 
    
    sceneDict3 = {'tilt': tilt, 'pitch':pitch,'hub_height':hub_height,'azimuth':azimuth,'nMods': 1, 'nRows': 1, 'originx': pitch*2, 'originy': ymods[0]} 
    sceneObj3 = rad_obj.makeScene(moduletype=module_type,sceneDict=sceneDict3, radname = radname) 
    
    sceneDict4 = {'tilt': tilt, 'pitch':pitch,'hub_height':hub_height,'azimuth':azimuth,'nMods': 1, 'nRows': 1, 'originx': pitch*3, 'originy': ymods[0]} 
    sceneObj4 = rad_obj.makeScene(moduletype=module_type,sceneDict=sceneDict4, radname = radname) 
    
    sceneDict5 = {'tilt': tilt, 'pitch':pitch,'hub_height':hub_height,'azimuth':azimuth,'nMods': 1, 'nRows': 1, 'originx': pitch*4, 'originy': ymods[0]} 
    sceneObj5 = rad_obj.makeScene(moduletype=module_type,sceneDict=sceneDict5, radname = radname) 
    
    sceneDict6 = {'tilt': tilt, 'pitch':pitch,'hub_height':hub_height,'azimuth':azimuth,'nMods': 1, 'nRows': 1, 'originx': pitch*5, 'originy': ymods[0]} 
    sceneObj6 = rad_obj.makeScene(moduletype=module_type,sceneDict=sceneDict6, radname = radname) 
    
    sceneDict7 = {'tilt': tilt, 'pitch':pitch,'hub_height':hub_height,'azimuth':azimuth,'nMods': 1, 'nRows': 1, 'originx': pitch*6, 'originy': ymods[0]} 
    sceneObj7 = rad_obj.makeScene(moduletype=module_type,sceneDict=sceneDict7, radname = radname) 
    
    sceneDict8 = {'tilt': tilt, 'pitch':pitch,'hub_height':hub_height,'azimuth':azimuth,'nMods': 1, 'nRows': 1, 'originx': pitch*7, 'originy': ymods[0]} 
    sceneObj8 = rad_obj.makeScene(moduletype=module_type,sceneDict=sceneDict8, radname = radname) 
    
    sceneDict9 = {'tilt': tilt, 'pitch':pitch,'hub_height':hub_height,'azimuth':azimuth,'nMods': 1, 'nRows': 1, 'originx': pitch*8, 'originy': ymods[0]} 
    sceneObj9 = rad_obj.makeScene(moduletype=module_type,sceneDict=sceneDict9, radname = radname) 
    
    sceneDict10 = {'tilt': tilt, 'pitch':pitch,'hub_height':hub_height,'azimuth':azimuth,'nMods': 1, 'nRows': 1, 'originx': pitch*9, 'originy': ymods[0]} 
    sceneObj10 = rad_obj.makeScene(moduletype=module_type,sceneDict=sceneDict10, radname = radname)  
    
    #sceneObjects[tilt] = {'Obj1': sceneObj1, 'Obj2': sceneObj2, 'Obj3': sceneObj3, 'Obj4': sceneObj4, 'Obj5': sceneObj5, 'Obj6': sceneObj6, 'Obj7': sceneObj7, 'Obj8': sceneObj8, 'Obj9': sceneObj9, 'Obj10': sceneObj10}

    modulesArray = []
    fieldArray = []    

    modulesArray.append(sceneObj1)
    modulesArray.append(sceneObj2)
    modulesArray.append(sceneObj3)
    modulesArray.append(sceneObj4)
    modulesArray.append(sceneObj5)
    modulesArray.append(sceneObj6)
    modulesArray.append(sceneObj7)
    modulesArray.append(sceneObj8)
    modulesArray.append(sceneObj9)
    modulesArray.append(sceneObj10)   
    fieldArray.append(modulesArray)
    
    
    textrow1 = ''
    textrow2 = sceneObj2.text + '\r\n'
    textrow3 = sceneObj3.text + '\r\n'
    textrow4 = sceneObj4.text + '\r\n'
    textrow5 = sceneObj5.text + '\r\n'
    textrow6 = sceneObj6.text + '\r\n'
    textrow7 = sceneObj7.text + '\r\n'
    textrow8 = sceneObj8.text + '\r\n'
    textrow9 = sceneObj9.text + '\r\n'
    textrow10 = sceneObj10.text + '\r\n'

    # Row 1    
    for i in range(1, 20):               
        modulesArray = []

        sceneDict1 = {'tilt': tilt, 'pitch':pitch,'hub_height':hub_height,'azimuth':azimuth,'nMods': 1, 'nRows': 1, 'originx': pitch*0, 'originy': ymods[i]} 
        sceneObj1 = rad_obj.makeScene(moduletype=module_type,sceneDict=sceneDict1, radname = radname)  
    
        sceneDict2 = {'tilt': tilt, 'pitch':pitch,'hub_height':hub_height,'azimuth':azimuth,'nMods': 1, 'nRows': 1, 'originx': pitch*1, 'originy': ymods[i]} 
        sceneObj2 = rad_obj.makeScene(moduletype=module_type,sceneDict=sceneDict2, radname = radname)  
    
        sceneDict3 = {'tilt': tilt, 'pitch':pitch,'hub_height':hub_height,'azimuth':azimuth,'nMods': 1, 'nRows': 1, 'originx': pitch*2, 'originy': ymods[i]} 
        sceneObj3 = rad_obj.makeScene(moduletype=module_type,sceneDict=sceneDict3, radname = radname)  
    
        sceneDict4 = {'tilt': tilt, 'pitch':pitch,'hub_height':hub_height,'azimuth':azimuth,'nMods': 1, 'nRows': 1, 'originx': pitch*3, 'originy': ymods[i]} 
        sceneObj4 = rad_obj.makeScene(moduletype=module_type,sceneDict=sceneDict4, radname = radname)  
    
        sceneDict5 = {'tilt': tilt, 'pitch':pitch,'hub_height':hub_height,'azimuth':azimuth,'nMods': 1, 'nRows': 1, 'originx': pitch*4, 'originy': ymods[i]} 
        sceneObj5 = rad_obj.makeScene(moduletype=module_type,sceneDict=sceneDict5, radname = radname)  
    
        sceneDict6 = {'tilt': tilt, 'pitch':pitch,'hub_height':hub_height,'azimuth':azimuth,'nMods': 1, 'nRows': 1, 'originx': pitch*5, 'originy': ymods[i]} 
        sceneObj6 = rad_obj.makeScene(moduletype=module_type,sceneDict=sceneDict6, radname = radname)  
    
        sceneDict7 = {'tilt': tilt, 'pitch':pitch,'hub_height':hub_height,'azimuth':azimuth,'nMods': 1, 'nRows': 1, 'originx': pitch*6, 'originy': ymods[i]} 
        sceneObj7 = rad_obj.makeScene(moduletype=module_type,sceneDict=sceneDict7, radname = radname)  
    
        sceneDict8 = {'tilt': tilt, 'pitch':pitch,'hub_height':hub_height,'azimuth':azimuth,'nMods': 1, 'nRows': 1, 'originx': pitch*7, 'originy': ymods[i]} 
        sceneObj8 = rad_obj.makeScene(moduletype=module_type,sceneDict=sceneDict8, radname = radname)  
    
        sceneDict9 = {'tilt': tilt, 'pitch':pitch,'hub_height':hub_height,'azimuth':azimuth,'nMods': 1, 'nRows': 1, 'originx': pitch*8, 'originy': ymods[i]} 
        sceneObj9 = rad_obj.makeScene(moduletype=module_type,sceneDict=sceneDict9, radname = radname)  
    
        sceneDict10 = {'tilt': tilt, 'pitch':pitch,'hub_height':hub_height,'azimuth':azimuth,'nMods': 1, 'nRows': 1, 'originx': pitch*9, 'originy': ymods[i]} 
        sceneObj10 = rad_obj.makeScene(moduletype=module_type,sceneDict=sceneDict10, radname = radname)  
    
        textrow1 += sceneObj1.text + '\r\n'        
        textrow2 += sceneObj2.text + '\r\n'
        textrow3 += sceneObj3.text + '\r\n'
        textrow4 += sceneObj4.text + '\r\n'
        textrow5 += sceneObj5.text + '\r\n'
        textrow6 += sceneObj6.text + '\r\n'
        textrow7 += sceneObj7.text + '\r\n'
        textrow8 += sceneObj8.text + '\r\n'
        textrow9 += sceneObj9.text + '\r\n'
        textrow10 += sceneObj10.text + '\r\n'
    
        modulesArray.append(sceneObj1)
        modulesArray.append(sceneObj2)
        modulesArray.append(sceneObj3)
        modulesArray.append(sceneObj4)
        modulesArray.append(sceneObj5)
        modulesArray.append(sceneObj6)
        modulesArray.append(sceneObj7)
        modulesArray.append(sceneObj8)
        modulesArray.append(sceneObj9)
        modulesArray.append(sceneObj10)
        
        fieldArray.append(modulesArray)


    # Redoing the first module to append everything to it.
    sceneDict1 = {'tilt': tilt, 'pitch':pitch,'hub_height':hub_height,'azimuth':azimuth,'nMods': 1, 'nRows': 1, 'originx': pitch*0, 'originy': ymods[0]} 
    sceneObj1 = rad_obj.makeScene(moduletype=module_type,sceneDict=sceneDict1, radname = radname) 
    
    rad_obj.appendtoScene(sceneObj1.radfiles, '', textrow1)
    rad_obj.appendtoScene(sceneObj1.radfiles, '', textrow2)
    rad_obj.appendtoScene(sceneObj1.radfiles, '', textrow3)
    rad_obj.appendtoScene(sceneObj1.radfiles, '', textrow4)
    rad_obj.appendtoScene(sceneObj1.radfiles, '', textrow5)
    rad_obj.appendtoScene(sceneObj1.radfiles, '', textrow6)
    rad_obj.appendtoScene(sceneObj1.radfiles, '', textrow7)
    rad_obj.appendtoScene(sceneObj1.radfiles, '', textrow8)
    rad_obj.appendtoScene(sceneObj1.radfiles, '', textrow9)
    rad_obj.appendtoScene(sceneObj1.radfiles, '', textrow10)
    
    # Custom BSA Geometry
    # Bottom posttubes and torquetube:
    for i in range (0, 10):
        xpost = i*pitch    
    
        # adding torquetube
        torquetube = '\n\r! genrev Metal_Grey torquetube{} t*{} {} 32 | xform -rx -90 -t {} {} {}'.format(i, length, diameter/2.0, xpost, ttedgeoffset, hub_height-zgap)
        rad_obj.appendtoScene(sceneObj1.radfiles, '', torquetube)
    
        for j in range (0,5):
            ypost = ypostlist[j]
    
            post1='! genbox Metal_Grey pile{} {} {} {} | xform -t {} {} 0 '.format((str(i)+","+str(j)),postdiamx, postdiamy, hub_height, -postdiamx/2.0+xpost, -postdiamy+ypost)  
            rad_obj.appendtoScene(sceneObj1.radfiles, '', post1)
        
    ###########################
    # Create sensor objects   #
    ###########################
    
    
    # West Sensors
    shhw = 1.5 + (1 - 0.226/2)*sin(radians(tilt)) + (0.130175/2 + 0.05 - 0.02)*cos(radians(tilt))
    sxw = pitch*2 - (1 - 0.226/2)*cos(radians(tilt)) + (0.130175/2 + 0.05 - 0.02)*sin(radians(tilt))
    syw = ymods[9] + 0.5 + 0.226/2
    sensorw_scene = {'tilt': tilt, 'pitch':1,'hub_height': shhw, 'azimuth':azimuth,'nMods': 1, 'nRows': 1, 'originx': sxw, 'originy': syw,'appendRadfile':True} 
    res_name = "SensorW_"+str(foo.year)+"_"+str(foo.month)+"_"+str(foo.day)+"_"+str(foo.hour)+"_"+str(foo.minute)
    sensorw_sceneObj = rad_obj.makeScene(moduletype='sensor',sceneDict=sensorw_scene, radname = res_name) 

    syw = ymods[15] + 0.5 + 0.226/2
    sensorIMTw_scene = {'tilt': tilt, 'pitch':1,'hub_height': shhw, 'azimuth':azimuth,'nMods': 1, 'nRows': 1, 'originx': sxw, 'originy': syw,'appendRadfile':True} 
    res_name = "SensorIMTW_"+str(foo.year)+"_"+str(foo.month)+"_"+str(foo.day)+"_"+str(foo.hour)+"_"+str(foo.minute)
    sensorIMTw_sceneObj = rad_obj.makeScene(moduletype='sensor',sceneDict=sensorIMTw_scene, radname=res_name) 

    # East Sensors
    shhe = 1.5 - (1 - 0.226/2)*sin(radians(tilt)) + (0.130175/2 + 0.05 - 0.02)*cos(radians(tilt))
    sxe = pitch*2 + (1 - 0.226/2)*cos(radians(tilt)) + (0.130175/2 + 0.05 - 0.02)*sin(radians(tilt))
    sye = ymods[9] + 0.5 + 0.226/2
    sensore_scene = {'tilt': tilt, 'pitch':1,'hub_height': shhe, 'azimuth':azimuth,'nMods': 1, 'nRows': 1, 'originx': sxe, 'originy': sye,'appendRadfile':True} 
    res_name = "SensorE_"+str(foo.year)+"_"+str(foo.month)+"_"+str(foo.day)+"_"+str(foo.hour)+"_"+str(foo.minute)
    sensore_sceneObj = rad_obj.makeScene(moduletype='sensor',sceneDict=sensore_scene, radname=res_name) 

    sye = ymods[15] + 0.5 + 0.226/2
    sensorIMTe_scene = {'tilt': tilt, 'pitch':1,'hub_height': shhe, 'azimuth':azimuth,'nMods': 1, 'nRows': 1, 'originx': sxe, 'originy': sye,'appendRadfile':True} 
    res_name = "SensorIMTE_"+str(foo.year)+"_"+str(foo.month)+"_"+str(foo.day)+"_"+str(foo.hour)+"_"+str(foo.minute)
    sensorIMTe_sceneObj = rad_obj.makeScene(moduletype='sensor',sceneDict=sensorIMTe_scene, radname=res_name) 
        
    # Build oct file            
    sim_name = "BEST_"+str(foo.year)+"_"+str(foo.month)+"_"+str(foo.day)+"_"+str(foo.hour)+"_"+str(foo.minute)
    octfile = rad_obj.makeOct(rad_obj.getfilelist(), octname=sim_name)
    
    #################
    # Run analysis  #
    #################
    
    #Row 3 Module 10 sensors 
    analysis = AnalysisObj(octfile, rad_obj.basename)  

    frontscan, backscan = analysis.moduleAnalysis(sensorw_sceneObj, sensorsy=1)#, frontsurfaceoffset=0.021)#, backsurfaceoffset = 0.02)
    res_name = "SensorW_"+str(foo.year)+"_"+str(foo.month)+"_"+str(foo.day)+"_"+str(foo.hour)+"_"+str(foo.minute)
    frontdict, backdict = analysis.analysis(octfile, res_name, frontscan, backscan)

    frontscan, backscan = analysis.moduleAnalysis(sensore_sceneObj, sensorsy=1)#, frontsurfaceoffset=0.021)#, backsurfaceoffset = 0.02)
    res_name = "SensorE_"+str(foo.year)+"_"+str(foo.month)+"_"+str(foo.day)+"_"+str(foo.hour)+"_"+str(foo.minute)
    frontdict, backdict = analysis.analysis(octfile, res_name, frontscan, backscan)

    #IMT Sensors Row 3 Module 5 
    '''
    frontscan, backscan = analysis.moduleAnalysis(sensorIMTw_sceneObj, sensorsy=1)#, frontsurfaceoffset=0.021)#, backsurfaceoffset = 0.02)
    res_name = "SensorIMTW_"+str(foo.year)+"_"+str(foo.month)+"_"+str(foo.day)+"_"+str(foo.hour)+"_"+str(foo.minute)
    frontdict, backdict = analysis.analysis(octfile, res_name, frontscan, backscan)

    frontscan, backscan = analysis.moduleAnalysis(sensorIMTe_sceneObj, sensorsy=1)#, frontsurfaceoffset=0.021)#, backsurfaceoffset = 0.02)
    res_name = "SensorIMTE_"+str(foo.year)+"_"+str(foo.month)+"_"+str(foo.day)+"_"+str(foo.hour)+"_"+str(foo.minute)
    frontdict, backdict = analysis.analysis(octfile, res_name, frontscan, backscan)
    
    #fieldARray[module][row]

    #HYDRA
    modmod = 16
    rowrow = 1
    frontscan, backscan = analysis.moduleAnalysis(fieldArray[modmod][rowrow], sensorsy=12)#, frontsurfaceoffset=0.021)#, backsurfaceoffset = 0.02)        
    res_name = "Hydra_"+str(foo.year)+"_"+str(foo.month)+"_"+str(foo.day)+"_"+str(foo.hour)+"_"+str(foo.minute)
    frontdict, backdict = analysis.analysis(octfile, res_name, frontscan, backscan)

    '''
    
    #LOCATION_APOGEES
    modmod = 9
    rowrow = 2
    frontscan, backscan = analysis.moduleAnalysis(fieldArray[modmod][rowrow], sensorsy=4)#, frontsurfaceoffset=0.021)#, backsurfaceoffset = 0.02)        
    frontscan['ystart'] = frontscan['ystart'] + 0.45
    backscan['ystart'] = backscan['ystart'] + 0.45
    res_name = "Apogee_"+str(foo.year)+"_"+str(foo.month)+"_"+str(foo.day)+"_"+str(foo.hour)+"_"+str(foo.minute)
    frontdict, backdict = analysis.analysis(octfile, res_name, frontscan, backscan)


    '''
    # SCAN FULL ROWS
    for rowrow in range(5, 7):
        for modmod in range(0, 20):
            frontscan, backscan = analysis.moduleAnalysis(fieldArray[modmod][rowrow], sensorsy=12)#, frontsurfaceoffset=0.021)#, backsurfaceoffset = 0.02)        
            res_name = "Row_"+str(rowrow)+"_Mod_"+str(modmod)+"_"+str(foo.year)+"_"+str(foo.month)+"_"+str(foo.day)+"_"+str(foo.hour)+"_"+str(foo.minute)
            frontdict, backdict = analysis.analysis(octfile, res_name, frontscan, backscan)
    '''
    # Read in results
    #results_file = os.path.join('results', f'irr_sensor_{sim_name}.csv')
    #results = load.read1Result(results_file)
    results = 1
    
    # Format output
    #tracker_theta = tilt
    #front = ','.join([ str(f) for f in results['Wm2Front'] ])
    #back = ','.join([ str(r) for r in results['Wm2Back'] ])
    print("***** Finished simulation for "+ str(foo))
    #time_str = metdata.datetime[idx]
#    print(f"sim_results,{idx},{time_str},{wavelength},{dni},{dhi},{alb}," \
#          f"{tracker_theta},{front},{back}")
    return results



def run_simulations_dask(arraysimulations, kwargs):
    # Create client
    
    scheduler_file = '/scratch/sayala/dask_testing/scheduler.json'
    client = Client(scheduler_file=scheduler_file)
    
    # Iterate over inputs
    futures = []
    
    for ii in range(0, len(arraysimulations)):
        idx = arraysimulations.iloc[ii].idx   
        wavelength = arraysimulations.iloc[ii].wavelength
        test_folder = test_folder_fmt.format(f'{idx:04}',f'{wavelength:04}')
        if not os.path.exists(test_folder):
            futures.append(client.submit(simulate_single, idx=idx, wavelength=wavelength, **kwargs))
        else:
            print("\n\nAlready simulated ***********************\n\n", idx, wavelength)

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

def compileResults(testfolder, resultsfile):
    # ASsumes there is an overarching folder, where
    # Folder > custoname_idx_XXXX > custoname_Spectra_XXXX > results
    # and resultfiles are irr_custoname_YEAR_MONTH_DAY_HOUR_MINUTE.CSV' 
    #
    # ie. folder: r'/scratch/sayala/BEST_SpectraMarch/BEST_APOGGEE_Spectra_Mark_NotScaled'
    # testfolder = r'C:\Users\sayala\Documents\HPC_Scratch\BEST_Spectra'
    # Reading results in results/folder like: irr_SensorW_2020_10_30_8_30.csv'
    # SAving into resultsfile = r'C:\Users\sayala\Desktop\Dask\Compiled_SPECTRA_Results\TEMP\March15_Results.csv'
    
        
    arrayWm2Front = []
    arrayWm2Back = []
    arrayMatFront = []
    arrayMatBack = []
    monthlist=[]
    daylist=[]
    hourlist=[]
    yearlist=[]
    minutelist=[]
    #faillist=[]
    addresslist=[]
    wavlist = []
    sensorlist = []
    indexlist = []
    
    # List all IDX folders
    idxlist = sorted(os.listdir(testfolder))
    print('{} Indexes in the directory'.format(idxlist.__len__()))

    # Loop over Timestamps
    for ii in range (0, len(idxlist)):
        idx = int(idxlist[ii][-4:])

        spectralist = sorted(os.listdir(os.path.join(testfolder, idxlist[ii])))

        # Loop over Spectras
        for jj in range(0, len(spectralist)):
            wav = int(spectralist[jj][-4:]) 

            resultslist = sorted(os.listdir(os.path.join(testfolder, idxlist[ii], spectralist[jj], 'results')))
            
            # Loop over Sensors
            for kk in range(0, len(resultslist)): 
                
                try:
                    resultfile=os.path.join(testfolder, idxlist[ii], spectralist[jj], 'results', resultslist[kk])
                    sensorname = resultslist[kk].split('_')[1]
                    year = resultslist[kk].split('_')[2]
                    month = resultslist[kk].split('_')[3]
                    day = resultslist[kk].split('_')[4]
                    hour = resultslist[kk].split('_')[5]
                    try:
                        minute = int(resultslist[kk].split('_')[6].split('.')[0])
                    except:
                        minute = 0

#                    resultsDF = bifacial_radiance.load.read1Result(resultfile)
                    resultsDF = load.read1Result(resultfile)
                    wavlist.append(wav)
                    indexlist.append(idx)
                    arrayWm2Front.append(list(resultsDF['Wm2Front']))
                    arrayWm2Back.append(list(resultsDF['Wm2Back']))
                    arrayMatFront.append(list(resultsDF['mattype']))
                    arrayMatBack.append(list(resultsDF['rearMat']))
                    yearlist.append(year)
                    monthlist.append(month)
                    daylist.append(day)
                    hourlist.append(hour)
                    minutelist.append(minute)
                    sensorlist.append(sensorname)
                    addresslist.append(resultfile)
                except:
                    print(" FAILED index ", idx, " wav ",  wav, " file ", resultslist[kk] )
                
    resultsdf = pd.DataFrame(list(zip(arrayWm2Front, arrayWm2Back, 
                                      arrayMatFront, arrayMatBack)),
                             columns = ['br_Wm2Front', 'br_Wm2Back', 
                                        'br_MatFront', 'br_MatBack'])
    resultsdf['minute'] = minutelist
    resultsdf['hour'] = hourlist
    resultsdf['day'] = daylist
    resultsdf['month'] = monthlist
    resultsdf['year'] = yearlist
    resultsdf['wavelength'] = wavlist
    resultsdf['sensor'] = sensorlist
    resultsdf['file'] = addresslist
    resultsdf['idx'] = indexlist 
    
    format = '%Y-%m-%d %H:%M:00'
    datesread = pd.to_datetime(resultsdf[['year','month','day','hour','minute']], format=format)
    resultsdf['timestamp'] = datesread 
    
    resultsdf.to_csv(resultsfile)
    

def findMissingSimulationValues(resultsfile, idxs=None, wavs=None, sensors=None):
    
    data = pd.read_csv(resultsfile)
    #data['timestamp']= pd.to_datetime(data['timestamp'])

    if idxs is None:
        idxs = list(data.idx.unique())
    
    if wavs is None:
        wavs = list(data.wavelength.unique())
    
    if sensors is None:
        sensors = list(data.sensor.unique())
    
    # Make Ideal Dataframe
    ideal = pd.DataFrame(
        list(product(idxs, wavs, sensors)),
        columns=['idx', 'wavelength', 'sensor'])
    
    ideal.idx = ideal.idx.astype('int64')
    ideal.wavelength = ideal.wavelength.astype('int64')
    
    # Set idx, wavelenths and sensors as indexes
    ideal.set_index(['idx','wavelength','sensor'], inplace=True)
    foo = data.copy()
    foo.set_index(['idx','wavelength','sensor'], inplace=True)

    # Concatenate to generate missing values (nan)
    result = pd.concat([foo, ideal], axis=1, sort=False)
    
    # Select missing values (na)
    result = result[result['br_Wm2Back'].isna()]
    
    # Reset index and generate subset dataframe to return
    result.reset_index(inplace=True)
    missing = result[['idx','wavelength','sensor']]
     
    return missing


if __name__ == "__main__":
    # Define locations within file system

     #best_data_file = '/scratch/sayala/WeatherFiles/spectral_experiment_TMY.csv'
    best_data_file = '/scratch/sayala/SPECTRAS_Used/spctrutils_Oct2127/spectratimesTMY.csv'

    cases = ['Mark_NotScaled', 'Mark_Scaled', 'SRRL_NotScaled', 'SRRL_Scaled']
    i = 2
    
    test_folder_fmt = '/scratch/sayala/BEST_SpectraMarch/BEST_APOGGEE_Spectra_'+cases[i]+'/BEST_idx_{}/Spectra_{}'
    data_folder = '/scratch/sayala/SPECTRAS_Used/spctrutils_Oct2127/'+cases[i]
    
    # Define inputs    
    kwargs = {
        'best_data_file': best_data_file,
        'test_folder_fmt': test_folder_fmt,
        'data_folder': data_folder
    }
    
    wavelengths = np.array(list(chain(range(300, 1101, 5), range(1110, 2501, 10))))
    indices = np.array(list(range(10, 43)))
    

    try:
        # Make Dataframe with missing entries only
        resultsfile = r'/scratch/sayala/BEST_SpectraMarch/March15_Results.csv'    
        currenttestfolder = r'/scratch/sayala/BEST_SpectraMarch/BEST_APOGGEE_Spectra_'+cases[i]
        compileResults(testfolder=currenttestfolder, resultsfile=resultsfile)
        arraysimulations = findMissingSimulationValues(resultsfile, idxs=indices, wavs=wavelengths)
    except:
        # Make Ideal Dataframe
        "No files simulated yet, Strating from 0"
        arraysimulations = pd.DataFrame(
        list(product(indices, wavelengths)),
        columns=['indices', 'wavelengths'])

    run_simulations_dask(arraysimulations, kwargs)

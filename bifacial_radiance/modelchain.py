# -*- coding: utf-8 -*-
"""
Created on Sat Sep 11 15:48:21 2021

@author: sayala
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 16:39:39 2019

@author: sayala
"""

#import bifacial_radiance
#from   bifacial_radiance.config import *
#import os

# DATA_PATH = bifacial_radiance.main.DATA_PATH  # directory with module.json etc.

def _append_dicts(x, y):
    """python2 compatible way to append 2 dictionaries
    """
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

def runModelChain(simulationParamsDict, sceneParamsDict, timeControlParamsDict=None, 
                  moduleParamsDict=None, trackingParamsDict=None, torquetubeParamsDict=None, 
                  analysisParamsDict=None, cellLevelModuleParamsDict=None):
    """
    This calls config.py values, which are arranged into dictionaries,
    and runs all the respective processes based on the variables in the config.py.
 
    To import the variables from a .ini file, use::
        
        (simulationParamsDict, sceneParamsDict, timeControlParamsDict, moduleParamsDict, 
         trackingParamsDict,torquetubeParamsDict,analysisParamsDict,cellLevelModuleParamsDict) = 
        bifacial_radiance.load.readconfigurationinputfile(inifile)
    
    """
    
    import bifacial_radiance
    import os
    import numpy as np
    
    if 'testfolder' not in simulationParamsDict:
        simulationParamsDict['testfolder'] = bifacial_radiance.main._interactive_directory(
            title='Select or create an empty directory for the Radiance tree')

    testfolder = simulationParamsDict['testfolder']
    demo = bifacial_radiance.RadianceObj(
        simulationParamsDict['simulationname'], path=testfolder)  # Create a RadianceObj 'object'

    # Save INIFILE in folder
    inifilename = os.path.join(
        simulationParamsDict['testfolder'],  'simulation.ini')
    bifacial_radiance.load.savedictionariestoConfigurationIniFile(simulationParamsDict, sceneParamsDict, timeControlParamsDict,
                                                                  moduleParamsDict, trackingParamsDict, torquetubeParamsDict, analysisParamsDict, cellLevelModuleParamsDict, inifilename)
   
    # re-load configuration file to make sure all booleans are converted
    (simulationParamsDict, sceneParamsDict, timeControlParamsDict, 
     moduleParamsDict, trackingParamsDict,torquetubeParamsDict,
     analysisParamsDict,cellLevelModuleParamsDict) = \
        bifacial_radiance.load.readconfigurationinputfile(inifilename)
    
    # Load weatherfile

    if simulationParamsDict['getEPW']:
        simulationParamsDict['weatherFile'] = demo.getEPW(
            simulationParamsDict['latitude'], simulationParamsDict['longitude'])  # pull EPW data for any global lat/lon
  
    if simulationParamsDict['selectTimes']: 
        starttime = '91_'+timeControlParamsDict['starttime'] 
        endtime = '91_'+timeControlParamsDict['endtime'] 
    else: # read in full TMY file
        starttime = None; endtime=None
    
    print('Reading weather file {}'.format(simulationParamsDict['weatherFile']))
    metdata = demo.readWeatherFile(simulationParamsDict['weatherFile'],
                                   starttime=starttime, endtime=endtime, coerce_year=1991)
    
    # input albedo number or material name like 'concrete'.  To see options, run this without any input.
    demo.setGround(sceneParamsDict['albedo'])
    analysis = None  # initialize default analysis return value to none.

    A = demo.printModules()
    
    #cellLeveLParams are none by default.
    cellLevelModuleParams = None 
    try:
        if simulationParamsDict['cellLevelModule']:
            cellLevelModuleParams = cellLevelModuleParamsDict
    except: pass
    
    if torquetubeParamsDict:
        #kwargs = {**torquetubeParamsDict, **moduleParamsDict} #Py3 Only
        kwargs = _append_dicts(torquetubeParamsDict, moduleParamsDict)
    else:
        kwargs = moduleParamsDict
        
    if simulationParamsDict['moduletype'] in A:
        if simulationParamsDict['rewriteModule'] is True:
            moduleDict = demo.makeModule(name=simulationParamsDict['moduletype'],
                                         torquetube=simulationParamsDict['torqueTube'],
                                         axisofrotationTorqueTube=simulationParamsDict[
                                             'axisofrotationTorqueTube'],
                                         cellLevelModuleParams=cellLevelModuleParams,
                                         **kwargs)

        print("\nUsing Pre-determined Module Type: %s " %
              simulationParamsDict['moduletype'])
    else:
        moduleDict = demo.makeModule(name=simulationParamsDict['moduletype'],
                                     torquetube=simulationParamsDict['torqueTube'],
                                     axisofrotationTorqueTube=simulationParamsDict['axisofrotationTorqueTube'],
                                     cellLevelModuleParams=cellLevelModuleParams,
                                     **kwargs)

    
    if 'gcr' not in sceneParamsDict:  # didn't get gcr passed - need to calculate it
        sceneParamsDict['gcr'] = moduleDict['sceney'] / \
            sceneParamsDict['pitch']

    if simulationParamsDict['tracking'] == False and simulationParamsDict['cumulativeSky'] == True:
    # Fixed gencumsky condition
        scene = demo.makeScene(
        moduletype=simulationParamsDict['moduletype'], sceneDict=sceneParamsDict)
        demo.genCumSky(demo.temp_metdatafile)  
        octfile = demo.makeOct(demo.getfilelist())
        analysis = bifacial_radiance.AnalysisObj(octfile, demo.name)
        frontscan, backscan = analysis.moduleAnalysis(scene, analysisParamsDict['modWanted'],
                                                      analysisParamsDict['rowWanted'],
                                                      analysisParamsDict['sensorsy'])
        analysis.analysis(octfile, demo.name, frontscan, backscan)
        print('Bifacial ratio yearly average:  %0.3f' %
              (np.sum(analysis.Wm2Back) / np.sum(analysis.Wm2Front)))

    else:
    # Run everything through TrackerDict.    

        if simulationParamsDict['tracking'] == False:
            trackerdict = demo.set1axis(metdata, 
                                         cumulativesky=simulationParamsDict["cumulativeSky"],
                                        fixed_tilt_angle=sceneParamsDict['tilt'],
                                        fixed_tilt_azimuth=sceneParamsDict['azimuth'])
        else:
            trackerdict = demo.set1axis(metdata, gcr=sceneParamsDict['gcr'],
                                         limit_angle=trackingParamsDict['limit_angle'],
                                         angledelta=trackingParamsDict['angle_delta'],
                                         backtrack=trackingParamsDict['backtrack'],
                                         cumulativesky=simulationParamsDict["cumulativeSky"])
            


        if simulationParamsDict['cumulativeSky']:
            trackerdict = demo.genCumSky1axis(trackerdict=trackerdict)
        else:           
            trackerdict = demo.gendaylit1axis()                

        trackerdict = demo.makeScene1axis(trackerdict=trackerdict,
                                          moduletype=simulationParamsDict['moduletype'],
                                          sceneDict=sceneParamsDict,
                                          cumulativesky=simulationParamsDict['cumulativeSky'])

        trackerdict = demo.makeOct1axis(trackerdict=trackerdict,)

        trackerdict = demo.analysis1axis(trackerdict=trackerdict,
                                         modWanted=analysisParamsDict['modWanted'],
                                         rowWanted=analysisParamsDict['rowWanted'],
                                         sensorsy=analysisParamsDict['sensorsy'])
        
        # TODO: Chris, not all functions were saving/returning analysis before. 
               # It is also not a very good return as it will only include the last key
               # in teh trackerdict for this, but that is what we had before.
               # I would consider removing analysis as a return and modifying
               # the way teh ini_highAzimuth py test works.
               # What was before:         
               # analysis = trackerdict[time]['AnalysisObj']
        analysis = demo.trackerdict[list(demo.trackerdict.keys())[-1]]['AnalysisObj']
        
    return demo, analysis

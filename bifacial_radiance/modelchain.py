# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 16:39:39 2019

@author: sayala
"""

import bifacial_radiance
from bifacial_radiance.config import *

def runModelChain():
    '''
    
    This calls config.py values, which are arranged into dictionaries,
    and runs all the respective processes based on the varaibles in the config.py.
    
    Still under testing!
    '''

    if 'testfolder' not in simulationParamsDict:
        simulationParamsDict['testfolder']= _interactive_directory(title = 'Select or create an empty directory for the Radiance tree')
        
    testfolder = simulationParamsDict['testfolder']
    demo = bifacial_radiance.RadianceObj(simulationParamsDict['simulationname'], path = simulationParamsDict['testfolder'])  # Create a RadianceObj 'object'

    #All options for loading data:
    if simulationParamsDict['weatherFile'][-3:] == 'epw':
        if simulationParamsDict['getEPW']:
            simulationParamsDict['epwfile'] = demo.getEPW(simulationParamsDict['latitude'], simulationParamsDict['longitude']) # pull TMY data for any global lat/lon
        metdata = demo.readEPW(simulationParamsDict['weatherFile'])       #If file is none, select a EPW file using graphical picker
    else:
        metdata = demo.readTMY(simulationParamsDict['weatherFile']) # If file is none, select a TMY file using graphical picker

    demo.setGround(sceneParamsDict['albedo']) # input albedo number or material name like 'concrete'.  To see options, run this without any input.

    # Create module section. If module is not set it can just be read from the 
    # pre-generated modules in JSON.
    if simulationParamsDict['custommodule']:
        moduleDict = demo.makeModule(name = simulationParamsDict['moduletype'], 
                                     cellLevelModule=simulationParamsDict['cellLevelModule'], 
                                     torquetube=simulationParamsDict['torqueTube'], 
                                     axisofrotationTorqueTube=simulationParamsDict['axisofrotationTorqueTube'],
                                     numpanels=moduleParamsDict['numpanels'],   
                                     x=moduleParamsDict['x'],
                                     y=moduleParamsDict['y'],
                                     xgap=moduleParamsDict['xgap'], 
                                     ygap=moduleParamsDict['ygap'], 
                                     zgap=moduleParamsDict['zgap'], 
                                     bifi=moduleParamsDict['bifi'],                                      
                                     diameter=torquetubeParamsDict['diameter'], 
                                     tubetype=torquetubeParamsDict['tubetype'], 
                                     material=torquetubeParamsDict['torqueTubeMaterial'], 
                                     numcellsx=cellLevelModuleParamsDict['numcellsx'], 
                                     numcellsy=cellLevelModuleParamsDict['numcellsy'], 
                                     xcell=cellLevelModuleParamsDict['xcell'], 
                                     ycell=cellLevelModuleParamsDict['ycell'], 
                                     xcellgap=cellLevelModuleParamsDict['xcellgap'], 
                                     ycellgap=cellLevelModuleParamsDict['ycellgap'])
        
    else:
        A = demo.printModules()
        
        if simulationParamsDict['moduletype'] in A:
            print ("\nUsing Pre-determined Module Type: %s " % simulationParamsDict['moduletype'])
        else:
            print ("Error! Attempting to read pre-determined module %s, which is not in module list. Ending simulation! \n\n\n" %simulationParamsDict['moduletype'] )
            sys.exit()        
            
    if simulationParamsDict['tracking'] is False: # Fixed Routine

        scene = demo.makeScene(moduletype=simulationParamsDict['moduletype'], sceneDict = sceneParamsDict, hpc=simulationParamsDict['hpc']) #makeScene creates a .rad file with 20 modules per row, 7 rows.    

        if simulationParamsDict["cumulativeSky"]:
            if simulationParamsDict['timestampRangeSimulation']:
                import datetime
                startdate = datetime.datetime(2001, timeControlParamsDict['MonthStart'],
                                                    timeControlParamsDict['DayStart'],
                                                    timeControlParamsDict['HourStart'])
                enddate = datetime.datetime(2001, timeControlParamsDict['MonthEnd'],
                                                    timeControlParamsDict['DayEnd'],
                                                    timeControlParamsDict['HourEnd'])
                demo.genCumSky(demo.epwfile, startdate, enddate) # entire year.
            else:
                demo.genCumSky(demo.epwfile) # entire year.    
            octfile = demo.makeOct(demo.getfilelist())  # makeOct combines all of the ground, sky and object files into a .oct file.
            analysis = bifacial_radiance.AnalysisObj(octfile, demo.name)  # return an analysis object including the scan dimensions for back irradiance
            frontscan, backscan = analysis.moduleAnalysis(scene, analysisParamsDict['modWanted'], 
                                                              analysisParamsDict['rowWanted'],
                                                              analysisParamsDict['sensorsy'])
            analysis.analysis(octfile, demo.name, frontscan, backscan)
            print('Bifacial ratio yearly average:  %0.3f' %( sum(analysis.Wm2Back) / sum(analysis.Wm2Front) ) )

        else:
            if simulationParamsDict["timestampRangeSimulation"]:
                for timeindex in range (timeControlParamsDict['timeindexstart'], timeControlParamsDict['timeindexend']):                
                    demo.gendaylit(metdata,timeindex)  # Noon, June 17th
                    octfile = demo.makeOct(demo.getfilelist())  # makeOct combines all of the ground, sky and object files into a .oct file.
                    analysis = bifacial_radiance.AnalysisObj(octfile, demo.name)  # return an analysis object including the scan dimensions for back irradiance
                    frontscan, backscan = analysis.moduleAnalysis(scene, analysisParamsDict['modWanted'], 
                                                                  analysisParamsDict['rowWanted'],
                                                                  analysisParamsDict['sensorsy'])
                    analysis.analysis(octfile, demo.name, frontscan, backscan)
                    print('Bifacial ratio for %s average:  %0.3f' %( metdata.datetime[timeindex], sum(analysis.Wm2Back) / sum(analysis.Wm2Front) ) )    
            else: # Runn hole year
                 for timeindex in range (0, 8760):                
                    demo.gendaylit(metdata,timeindex)  # Noon, June 17th
                    octfile = demo.makeOct(demo.getfilelist())  # makeOct combines all of the ground, sky and object files into a .oct file.
                    analysis = bifacial_radiance.AnalysisObj(octfile, demo.name)  # return an analysis object including the scan dimensions for back irradiance
                    frontscan, backscan = analysis.moduleAnalysis(scene, analysisParamsDict['modWanted'], 
                                                                  analysisParamsDict['rowWanted'],
                                                                  analysisParamsDict['sensorsy'])
                    analysis.analysis(octfile, demo.name, frontscan, backscan)
                    print('Bifacial ratio for %s average:  %0.3f' %( metdata.datetime[timeindex], sum(analysis.Wm2Back) / sum(analysis.Wm2Front) ) )    
 
    else: # Tracking
        print('\n***Starting 1-axis tracking simulation***\n')
        trackerdict = demo.set1axis(metdata, axis_azimuth =  sceneParamsDict['axis_azimuth'],
                                    gcr = sceneParamsDict['gcr'],
                                    limit_angle = trackingParamsDict['limit_angle'], 
                                    angledelta = trackingParamsDict['angle_delta'],
                                    backtrack = trackingParamsDict['backtrack'],
                                    cumulativesky = simulationParamsDict["cumulativeSky"])
     
        if simulationParamsDict["cumulativeSky"]: # cumulative sky routine

            if simulationParamsDict['timestampRangeSimulation']: # This option doesn't work currently.!
                import datetime
                startdate = datetime.datetime(2001, timeControlParamsDict['MonthStart'],
                                                    timeControlParamsDict['DayStart'],
                                                    timeControlParamsDict['HourStart'])
                enddate = datetime.datetime(2001, timeControlParamsDict['MonthEnd'],
                                                    timeControlParamsDict['DayEnd'],
                                                    timeControlParamsDict['HourEnd'])
                trackerdict = demo.genCumSky1axis(trackerdict, startdt=startdate, enddt=enddate)
            else:
                trackerdict = demo.genCumSky1axis(trackerdict)
        
            trackerdict = demo.makeScene1axis(trackerdict=trackerdict,
                                              moduletype= simulationParamsDict['moduletype'],
                                              sceneDict=sceneParamsDict,
                                              cumulativesky=simulationParamsDict['cumulativeSky'],
                                              hpc=simulationParamsDict['hpc'])
            
            trackerdict = demo.makeOct1axis(trackerdict, hpc=simulationParamsDict['hpc'])

            trackerdict = demo.analysis1axis(trackerdict, modWanted = analysisParamsDict['modWanted'], 
                                             rowWanted = analysisParamsDict['rowWanted'], 
                                             sensorsy=analysisParamsDict['sensorsy'])
            print('Annual RADIANCE bifacial ratio for 1-axis tracking: %0.3f' %(sum(demo.Wm2Back)/sum(demo.Wm2Front)) )
            
        else:

            if simulationParamsDict['timestampRangeSimulation']: # This option doesn't work currently.!
                            
                monthpadding1=''
                daypadding1=''
                monthpadding2=''
                daypadding2=''

                if timeControlParamsDict['MonthStart'] < 10:
                    monthpadding1='0'
                if timeControlParamsDict['DayStart'] < 10:
                    daypadding1='0'
                if timeControlParamsDict['MonthEnd'] < 10:
                    monthpadding2='0'
                if timeControlParamsDict['DayEnd'] < 10:
                    daypadding2='0'
                    
                startday = monthpadding1+(str(timeControlParamsDict['MonthStart'])+'_'+
                            daypadding1+str(timeControlParamsDict['DayStart']))
                endday = monthpadding2+(str(timeControlParamsDict['MonthEnd'])+'_'+
                            daypadding2+str(timeControlParamsDict['DayEnd']))


                trackerdict = demo.gendaylit1axis(startdate=startday, enddate=endday)  # optional parameters 'startdate', 'enddate' inputs = string 'MM/DD' or 'MM_DD'   
            else:            
                trackerdict = demo.gendaylit1axis()  # optional parameters 'startdate', 'enddate' inputs = string 'MM/DD' or 'MM_DD' 

            # Tracker dict should go here becuase sky routine reduces the size of trackerdict.
            trackerdict = demo.makeScene1axis(trackerdict=trackerdict,
                                  moduletype= simulationParamsDict['moduletype'],
                                  sceneDict=sceneParamsDict,
                                  cumulativesky=simulationParamsDict['cumulativeSky'],
                                  hpc=simulationParamsDict['hpc'])
            if simulationParamsDict['timestampRangeSimulation']:
                hourpadding1=''
                hourpadding2=''
                if timeControlParamsDict['HourStart'] < 10:
                    hourpadding1='0'
                if timeControlParamsDict['HourEnd'] < 10:
                    hourpadding2='0'
                    
                starttime = startday+'_'+str(timeControlParamsDict['HourStart'])
                endtime = endday+'_'+str(timeControlParamsDict['HourEnd'])     
                for time in [starttime,endtime]:  # just two timepoints
                    trackerdict = demo.makeOct1axis(trackerdict,singleindex=time,  
                                                    hpc=simulationParamsDict['hpc'])
                    trackerdict = demo.analysis1axis(trackerdict,singleindex=time,
                                                     modWanted = analysisParamsDict['modWanted'], 
                                             rowWanted = analysisParamsDict['rowWanted'], 
                                             sensorsy=analysisParamsDict['sensorsy'])
            
            else:
                trackerdict = demo.makeOct1axis(trackerdict, hpc=simulationParamsDict['hpc'])
                trackerdict = demo.analysis1axis(trackerdict, modWanted = analysisParamsDict['modWanted'], 
                                             rowWanted = analysisParamsDict['rowWanted'], 
                                             sensorsy=analysisParamsDict['sensorsy'])
            
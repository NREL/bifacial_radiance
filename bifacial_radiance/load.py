# -*- coding: utf-8 -*-
"""
Created on Tue Feb 19 08:38:45 2019

@author: cdeline, sayala

load.py - load bifacial_radiance results. Module to load and clean 
bifacial_radiance irradiance result files, csv format, usually stored in RadianceScene\results folder.

Introduced in bifacial_radiance v0.2.4

functions: 
    load_inputvariablesfile(inputfile)
        loads a .py file which has all of the input variables required for a simulation.
        Everything is loaded into a dictionary
    
    loadRadianceObj(savefile)
        unpickle a RadianceObj saved with RadianceObj.save()    
    
    resultsdf = read1Result(csvfile)
        read in a csv file
        Returns: resultsDF
    
    cleanResult(resultsDF, matchers=None)
        replace irradiance values with NaN's when the scan intersects ground, sky, or anything in `matchers`.
        Returns: resultsDF
    
    deepcleanResult(resultsDF, sensorsy, numpanels, azimuth, automatic=True)
        
        Returns: resultsDF
    
    loadTrackerDict(trackerdict, fileprefix=None)
        load all csv files in a \results\ folder matching timestamps in trackerdict
        Intended to be called from RadianceObj.loadTrackerDict()

"""
                   
        
        
def load_inputvariablesfile(intputfile):
    '''
    Description
    -----------
    load_inputvariablesfile(inputfile)
    Loads inputfile which must be in the bifacial_radiance directory,
    and must be a *.py file with all the variables, and organizes the variables
    into dictionaries that it returns

    Parameters
    ----------
    inputfile:    string of a *.py file in the bifacial_radiance directory.

    Returns (Dictionaries)
    -------
    simulationParamsDict          testfolder, weatherfile, getEPW, simulationname, 
                                  moduletype, rewritemodule,
                                  rcellLevelmodule, axisofrotationtorquetube, 
                                  torqueTube, hpc, tracking, cumulativesky,
                                  daydateSimulation, timestampRangeSimulation
    sceneParamsDict:              gcrorpitch, gcr, pitch, albedo, nMods, nRows, 
                                  hub_height, clearance_height, azimuth, hub_height, axis_Azimuth
    timeControlParamsDict:        hourstart, hourend, daystart, dayend, monthstart, monthend,
                                  timestampstart, timestampend, 
    moduleParamsDict:             numpanels, x, y, bifi, xgap, ygap, zgap
    cellLevelModuleParamsDict:    numcellsx, numcellsy, xcell, ycell, xcellgap, ycellgap
    trackingParamsDict:           backtrack, limit_angle,angle_delta
    torquetubeParamsDict:         diameter, tubetype, torqueTubeMaterial
    analysisParamsDict:           sensorsy, modWanted, rowWanted
    '''
    
    import inputfile as ibf

    simulationParamsDict = {'testfolder':ibf.testfolder, 
                            'epwfile':ibf.epwfile, 
                            'simulationname':ibf.simulationname,
                            'moduletype':ibf.moduletype,
                            'rewriteModule':ibf.rewriteModule,
                            'cellLevelModule':ibf.cellLevelModule,
                            'axisofrotationTorqueTube':ibf.axisofrotationTorqueTube,
                            'torqueTube':ibf.torqueTube}

    simulationControlDict = {'fixedortracked':ibf.fixedortracked,
                             'cumulativeSky': ibf.cumulativeSky,
                             'timestampSimulation': ibf.timestampSimulation,
                             'timestampRangeSimulation': ibf.timestampRangeSimulation,
                             'hpc': ibf.hpc,
                             'daydateSimulation': ibf.dayDateSimulation,
                             'singleKeySimulation': ibf.singleKeySimulation,
                             'singleKeyRangeSimulation': ibf.singleKeyRangeSimulation}

    timeControlParamsDict = {'timestampstart': ibf.timestampstart,
                             'timestampend': ibf.timestampend,
                             'startdate': ibf.startdate,
                             'enddate': ibf.enddate,
                             'singlekeystart': ibf.singlekeystart,
                             'singlekeyend': ibf.singlekeyend,
                             'day_date':ibf.daydate}

    moduleParamsDict = {'numpanels': ibf.numpanels, 'x': ibf.x, 'y': ibf.y,
                        'bifi': ibf.bifi, 'xgap': ibf.xgap,
                        'ygap': ibf.ygap, 'zgap': ibf.zgap}

    sceneParamsDict = {'gcr': ibf.gcr, 'pitch': ibf.pitch, 'albedo': ibf.albedo,
                       'nMods':ibf.nMods, 'nRows': ibf.nRows,
                       'azimuth': ibf.azimuth_ang, 'tilt': ibf.tilt,
                       'clearance_height': ibf.clearance_height, 'hub_height': ibf.hub_height,
                       'axis_azimuth': ibf.axis_azimuth}

    trackingParamsDict = {'backtrack': ibf.backtrack, 'limit_angle': ibf.limit_angle,
                          'angle_delta': ibf.angle_delta}

    #cdeline: this isn't returned by the function ??
    torquetubeParamsDict = {'diameter': ibf.diameter, 'tubetype': ibf.tubetype,
                            'torqueTubeMaterial': ibf.torqueTubeMaterial}

    analysisParamsDict = {'sensorsy': ibf.sensorsy, 'modWanted': ibf.modWanted,
                          'rowWanted': ibf.rowWanted}

    cellLevelModuleParamsDict = {'numcellsx': ibf.numcellsx,
                                 'numcellsy': ibf.numcellsy,
                                 'xcell': ibf.xcell, 'ycell': ibf.ycell,
                                 'xcellgap': ibf.xcellgap, 'ycellgap': ibf.ycellgap}

    return(simulationParamsDict, simulationControlDict, timeControlParamsDict,
           moduleParamsDict, cellLevelModuleParamsDict, sceneParamsDict,
           trackingParamsDict, analysisParamsDict)


def loadRadianceObj(savefile=None):
    '''
    Load the pickled radiance object for further use
    usage: (once you're in the correct local directory)
      demo = bifacial_radiance.loadRadianceObj(savefile)
    
    Parameters
    ----------
    savefile :   optional savefile.  Otherwise default to save.pickle
            
    '''
    import pickle
    
    if savefile is None:
        savefile = 'save.pickle'
    with open(savefile,'rb') as f:
        loadObj= pickle.load(f)
    
    print('Loaded file {}'.format(savefile))
    return loadObj

def read1Result(selectfile):
    ''' 
    load in bifacial_radiance.csv result file name `selectfile`
    and return pandas dataframe resultsdf
    '''
    import pandas as pd
    
    #resultsDict = pd.read_csv(os.path.join('results',selectfile))
    resultsDF = pd.read_csv(selectfile)

    #return(np.array(temp['Wm2Front']), np.array(temp['Wm2Back']))
    return resultsDF
# End read1Result subroutine

def cleanResult(resultsDF, matchers=None):
    '''
    cleanResult(resultsDF, matchers=None)
    check for 'sky' or 'tube' or 'pole' or 'ground in the front or back material 
    and substitute NaN in Wm2Front and Wm2Back
    
    matchers 3267 and 1540 is to get rid of inner-sides of the module.
    
    Parameters:
        resultsDF:  pandas dataframe read from read1Result
    
    '''
    import numpy as np
    
    if matchers is None:
        matchers = ['sky','pole','tube','bar','ground', '3267', '1540']
    NaNindex = [i for i,s in enumerate(resultsDF['mattype']) if any(xs in s for xs in matchers)]
    NaNindex2 = [i for i,s in enumerate(resultsDF['rearMat']) if any(xs in s for xs in matchers)]
    #NaNindex += [i for i,s in enumerate(frontDict['mattype']) if any(xs in s for xs in matchers)]    
    for i in NaNindex:
        resultsDF['Wm2Front'].loc[i] = np.NAN 
    for i in NaNindex2:
        resultsDF['Wm2Back'].loc[i] = np.NAN
    
    return resultsDF


def loadTrackerDict(trackerdict, fileprefix=None):
    '''
    Load a trackerdict by reading all files in the \results\ directory.
    fileprefix is used to select only certain matching files in \results\
   
    It will then save the Wm2Back, Wm2Front and backRatio by reading in all valid files in the
    \results\ directory.  Note: it will match any file ending in '_key.csv'
    
    Parameters
    --------------
    trackerdict:    You need to pass in a valid trackerdict with correct keys from RadianceObj.set1axis()
    fileprefix:     (None): optional parameter to specify the initial part of the savefile prior to '_key.csv'
    
    Returns
    -------------
    trackerdict:    dictionary with additional ['Wm2Back'], ['Wm2Front'], ['backRatio']
    totaldict:      totalized dictionary with ['Wm2Back'], ['Wm2Front']. 
                    Also ['numfiles'] (number of csv files loaded) and 
                    ['finalkey'] (last index file in directory)

    '''        
    import re, os
    import numpy as np

        
    # get list of filenames in \results\
    filelist = sorted(os.listdir('results'))
    
    print('{} files in the directory'.format(filelist.__len__()))
    i = 0  # counter to track # files loaded.
    for key in sorted(trackerdict):
        if fileprefix is None:
            r = re.compile(".*_" + re.escape(key) + ".csv")
        else:   
            r = re.compile(fileprefix + re.escape(key) + ".csv")
        try:
            selectfile = list(filter(r.match,filelist))[0]
            i += 1
        except IndexError:
            continue
        
        resultsDF = read1Result(os.path.join('results',selectfile)) #return dataframe
        resultsDF = cleanResult(resultsDF)  # remove invalid materials
        
        Wm2Front = np.array(resultsDF['Wm2Front'])
        Wm2Back =  np.array(resultsDF['Wm2Back'])
        
        try:
            Wm2FrontTotal += Wm2Front
            Wm2BackTotal += Wm2Back
        except NameError:
            Wm2FrontTotal = Wm2Front
            Wm2BackTotal = Wm2Back
        trackerdict[key]['Wm2Front'] = list(Wm2Front)
        trackerdict[key]['Wm2Back'] = list(Wm2Back)
        trackerdict[key]['backRatio'] = list(Wm2Back / Wm2Front)
        finalkey = key
    totaldict = {'Wm2Front':Wm2FrontTotal, 'Wm2Back':Wm2BackTotal, 'numfiles':i, 'finalkey':finalkey}
    
    print('Files loaded: {};  Wm2Front_avg: {:0.1f}; Wm2Rear_avg: {:0.1f}'.format(i, np.nanmean(Wm2FrontTotal), np.nanmean(Wm2BackTotal) ))
    print('final key loaded: {}'.format(finalkey))
    return(trackerdict, totaldict)
    #end loadTrackerDict subroutine.  set demo.Wm2Front = totaldict.Wm2Front. demo.Wm2Back = totaldict.Wm2Back


def exportTrackerDict(trackerdict, savefile, reindex):
        '''
        save a TrackerDict output as a csv file.
        
        Inputs:
            trackerdict:   the tracker dictionary to save
            savefile:      path to .csv save file location
            reindex:       boolean to resample time index
        
        '''
        from pandas import DataFrame as df
        import numpy as np
        import pandas as pd

        # convert trackerdict into dataframe
        d = df.from_dict(trackerdict,orient='index',columns=['dhi','ghi','Wm2Back','Wm2Front','theta','surf_tilt','surf_azm','ground_clearance'])
        d['Wm2BackAvg'] = [np.nanmean(i) for i in d['Wm2Back']]
        d['Wm2FrontAvg'] = [np.nanmean(i) for i in d['Wm2Front']]
        d['BifiRatio'] =  d['Wm2BackAvg'] / d['Wm2FrontAvg']

        if reindex is True: # change to proper timestamp and interpolate to get 8760 output
            d['measdatetime'] = d.index
            d=d.set_index(pd.to_datetime(d['measdatetime'] , format='%m_%d_%H'))
            d=d.resample('H').asfreq()
  
        d.to_csv(savefile)    

    
def deepcleanResult(resultsDict, sensorsy, numpanels, automatic=True):
    '''
    cleanResults(resultsDict, sensorsy, numpanels, azimuth) 
    @author: SAyala
    
    cleans results read by read1Result specifically for 1 UP and 2UP configurations in v0.2.4
    Asks user to select material of the module (usually the one with the most results) 
    and removes sky, ground, and other materials (side of module, for exmaple)
    
    TODO: add automatization of panel select.
    
    PARAMETERS
    -----------
    sensorsy     For the interpolation routine. Can be more than original sensory or same value.
    numpanels    1 or 2
    azimuth   of the tracker for the results generated. So that it knows if sensors 
                   should be flipped or not. Particular crucial for 2 UP configurations.
    automatic      Automaticatlly detects module and ignores Ground, torque tube and sky values. If set to off, user gets queried about the right surfaces.
    
    Returns
    -------
    Frontresults, Backresults;     dataframe with only values of the material selected, 
                                   length is the number of sensors desired.

    '''
    import numpy as np
    from scipy.interpolate import interp1d
    
    fronttypes = resultsDict.groupby('mattype').count() 
    backtypes = resultsDict.groupby('rearMat').count()
    
    if numpanels == 2:

        if automatic == True:
            panBfrontmat = resultsDict[resultsDict['mattype'].str.contains('a0.PVmodule.6457')]
            panelB = panBfrontmat[panBfrontmat['rearMat'].str.contains('a0.PVmodule.2310')] # checks rear mat is also panel B only.

            panAfrontmat = resultsDict[resultsDict['mattype'].str.contains('a1.PVmodule.6457')]
            panelA = panAfrontmat[panAfrontmat['rearMat'].str.contains('a1.PVmodule.2310')]

        else: 
            print("Front type materials index and occurrences: ")
            for i in range (0, len(fronttypes)):
                print(i, " --> ", fronttypes['x'][i] , " :: ",  fronttypes.index[i])
            
            
            panBfront = int(input("Panel a0 Front material "))  # Python 2
            panAfront = int(input("Panel a1 Front material "))
            
            panBfrontmat = fronttypes.index[panBfront]
            panAfrontmat = fronttypes.index[panAfront]
            
            print("Rear type materials index and occurrences: ")
            for i in range (0, len(backtypes)):
                print(i, " --> ", backtypes['x'][i] , " :: ",  backtypes.index[i])
            
            panBrear = int(input("Panel a0 Rear material "))  # Python 2
            panArear = int(input("Panel a1 Rear material "))
              
            panBrearmat = backtypes.index[panBrear]
            panArearmat = backtypes.index[panArear]
               
            # Masking only modules, no side of the module, sky or ground values.
            panelB = resultsDict[(resultsDict.mattype == panBfrontmat) & (resultsDict.rearMat == panBrearmat)]
            panelA = resultsDict[(resultsDict.mattype == panAfrontmat) & (resultsDict.rearMat == panArearmat)]
            #panelB = test[(test.mattype == 'a10.3.a0.PVmodule.6457') & (test.rearMat == 'a10.3.a0.PVmodule.2310')]
            #panelA = test[(test.mattype == 'a10.3.a1.PVmodule.6457') & (test.rearMat == 'a10.3.a1.PVmodule.2310')]
        
        
        # Interpolating to original or givne number of sensors (so all hours results match after deleting wrong sensors).
        # This could be a sub-function but, hmm..
        x_0 = np.linspace(0, len(panelB)-1, len(panelB))    
        x_i = np.linspace(0, len(panelB)-1, int(sensorsy/2))
        f_linear = interp1d(x_0, panelB['Wm2Front'])
        panelB_front = f_linear(x_i)
        f_linear = interp1d(x_0, panelB['Wm2Back'])
        panelB_back = f_linear(x_i)
        
        # Interpolating to 200 because
        x_0 = np.linspace(0, len(panelA)-1, len(panelA))    
        x_i = np.linspace(0, len(panelA)-1, int(sensorsy/2))
        f_linear = interp1d(x_0, panelA['Wm2Front'])
        panelA_front = f_linear(x_i)
        f_linear = interp1d(x_0, panelA['Wm2Back'])
        panelA_back = f_linear(x_i)
        
        Frontresults=np.append(panelB_front,panelA_front)
        Backresults=np.append(panelB_back,panelA_back)

    else:  # ONLY ONE MODULE
        
        if automatic == True:
            panBfrontmat = resultsDict[resultsDict['mattype'].str.contains('a0.PVmodule.6457')]
            panelB = panBfrontmat[panBfrontmat['rearMat'].str.contains('a0.PVmodule.2310')] # checks rear mat is also panel B only.


        else:
            
            print("Front type materials index and occurrences: ")
            for i in range (0, len(fronttypes)):
                print(i, " --> ", fronttypes['x'][i] , " :: ",  fronttypes.index[i])
                    
            panBfront = int(input("Panel a0 Front material "))  # Python 2
            panBfrontmat = fronttypes.index[panBfront]
        
            print("Rear type materials index and occurrences: ")
            for i in range (0, len(backtypes)):
                print(i, " --> ", backtypes['x'][i] , " :: ",  backtypes.index[i])
            
            panBrear = int(input("Panel a0 Rear material "))  # Python 2
            panBrearmat = backtypes.index[panBrear]
            
            # Masking only modules, no side of the module, sky or ground values.
            panelB = resultsDict[(resultsDict.mattype == panBfrontmat) & (resultsDict.rearMat == panBrearmat)]
            #panelB = test[(test.mattype == 'a10.3.a0.PVmodule.6457') & (test.rearMat == 'a10.3.a0.PVmodule.2310')]
        
        
        # Interpolating to 200 because
        x_0 = np.linspace(0, len(panelB)-1, len(panelB))    
        x_i = np.linspace(0, len(panelB)-1, sensorsy)
        f_linear = interp1d(x_0, panelB['Wm2Front'])
        panelB_front = f_linear(x_i)
        f_linear = interp1d(x_0, panelB['Wm2Back'])
        panelB_back = f_linear(x_i)
                
        Frontresults=panelB_front
        Backresults=panelB_back
            
    return Frontresults, Backresults;    # End Deep clean Result subroutine.

def readconfigurationinputfile(inifile=None):
    """
    readconfigurationinputfile(inifile=None)
    
    input:      inifile (string):  .ini filename to read in
    
    returns:    simulationParamsDict, 
                sceneParamsDict, 
                timeControlParamsDict, 
                moduleParamsDict, 
                trackingParamsDict, 
                torquetubeParamsDict, 
                analysisParamsDict, 
                cellLevelModuleParamsDict;

    @author: sayala
    
    #TODO: check if modulename exists on jason and rewrite is set to false, then
    don't save moduleParamsDict? Discuss.

    """
    import configparser
    import os
    
    def boolConvert(d):
        """ convert strings 'True' and 'False' to boolean
        """
        for key,value in d.items():
            if value.lower() == 'true': 
                d[key] = True
            elif value.lower() == 'false':
                d[key] = False
        return d
    
    if inifile is None:
        inifile = os.path.join("data","default.ini")

    config = configparser.ConfigParser()
    config.optionxform = str  
    config.read(inifile)
    
    confdict = {section: dict(config.items(section)) for section in config.sections()}
    
    if config.has_section("simulationParamsDict"):
        simulationParamsDict = boolConvert(confdict['simulationParamsDict'])
    else:
        raise Exception("Missing simulationParamsDict! Breaking")
        
        
    if config.has_section("sceneParamsDict"):
        sceneParamsDict2 = boolConvert(confdict['sceneParamsDict'])
    else:
        raise Exception("Missing sceneParams Dictionary! Breaking")
            
    if simulationParamsDict['timestampRangeSimulation'] or simulationParamsDict['daydateSimulation']:
        if config.has_section("timeControlParamsDict"):
            timeControlParamsDict2 = boolConvert(confdict['timeControlParamsDict'])
            timeControlParamsDict={} # saving a main dictionary wiht only relevant options.
        else:
            print("Mising timeControlParamsDict for simulation options specified! Breaking")
    #        break;            
            
    if simulationParamsDict['getEPW']:
        try:
            simulationParamsDict['latitude'] = float(simulationParamsDict['latitude'])
            simulationParamsDict['longitude'] = float(simulationParamsDict['longitude'])
        except:
            if 'weatherFile' in simulationParamsDict:
                try: 
                    os.path.exists(simulationParamsDict['weatherFile'])
                    simulationParamsDict['getEPW'] = False
                    print("Load Warning: latitude or longitude missing/nan in input file.",\
                          "Since a valid weatherfile was found in the input file,",\
                          "simulationParamsDict['getepw'] has been set to false and weather file",\
                          " will be read instead.")
                except:
                    simulationParamsDict['latitude'] = 33.0
                    simulationParamsDict['longitude'] = -110.0
                    print("Load Warning: latitude or longitude missing/nan in input file.",\
                          "Weather file was attempted to read but was invalid address/notfound,",\
                          "so default values will be used,",\
                          "latitud: %s, longitude: %s" % (simulationParamsDict['latitude'], simulationParamsDict['longitude']))
            else:
                simulationParamsDict['latitude'] = 33.0
                simulationParamsDict['longitude'] = -110.0
                print("Load Warning: latitude or longitude missing/nan in input file.",\
                      "No Weather file was passed, so default values will be used,",\
                      "latitud: %s, longitude: %s" % (simulationParamsDict['latitude'], simulationParamsDict['longitude']))
    
    if config.has_section("moduleParamsDict"):
        moduleParamsDict2 = boolConvert(confdict['moduleParamsDict'])
        moduleParamsDict={} # Defining a new one to only save relevant values from passed.
        try: 
            moduleParamsDict['bifi'] = round(float(moduleParamsDict2['bifi']),2)
        except:
            moduleParamsDict['bifi'] = 0.9 #Default
            print("Load Warning: moduleParamsDict['bifi'] not specified, setting to default value: %s" % moduleParamsDict['bifi'] )    
        try: 
            moduleParamsDict['numpanels'] = int(moduleParamsDict2['numpanels'])
        except:
            moduleParamsDict['numpanels'] = 1 #Default
            print("Load Warning: moduleParamsDict['numpanels'] not specified, setting to default value: %s" % moduleParamsDict['numpanels'] ) 
        try: 
            moduleParamsDict['xgap'] = round(float(moduleParamsDict2['xgap']),3)
        except:
            moduleParamsDict['xgap'] = 0.01 #Default
            print("Load Warning: moduleParamsDict['xgap'] not specified, setting to default value: %s" % moduleParamsDict['xgap'] ) 
        try: 
            moduleParamsDict['ygap'] = round(float(moduleParamsDict2['ygap']),3)
        except:
            moduleParamsDict['ygap'] = 0.150 #Default
            print("Load Warning: moduleParamsDict['ygap'] not specified, setting to default value: %s" % moduleParamsDict['ygap'] ) 
            
        try: 
            moduleParamsDict['zgap'] = round(float(moduleParamsDict2['ygap']),3)
        except:
            moduleParamsDict['zgap'] = 0.1 #Default
            print("Load Warning: moduleParamsDict['zgap'] not specified, setting to default value: %s" % moduleParamsDict['zgap'] ) 
                    
        if simulationParamsDict['cellLevelModule']:    
            if config.has_section("cellLevelModuleParamsDict"):
                cellLevelModuleParamsDict = confdict['cellLevelModuleParamsDict']
                try: # being lazy so just validating the whole dictionary as a whole. #TODO: validate individually maybe.            
                    cellLevelModuleParamsDict['numcellsx'] = int(cellLevelModuleParamsDict['numcellsx'])
                    cellLevelModuleParamsDict['numcellsy'] = int(cellLevelModuleParamsDict['numcellsy'])
                    cellLevelModuleParamsDict['xcell'] = round(float(cellLevelModuleParamsDict['xcell']),3)
                    cellLevelModuleParamsDict['xcellgap'] = round(float(cellLevelModuleParamsDict['xcellgap']),3)
                    cellLevelModuleParamsDict['ycell'] = round(float(cellLevelModuleParamsDict['ycell']),3)
                    cellLevelModuleParamsDict['ycellgap'] = round(float(cellLevelModuleParamsDict['ycellgap']),3)
                except: 
                    print("Load Warning: celllevelModule set to True,",\
                          "but celllevelModule parameters are missing/not numbers.")
                    try:
                        moduleParamsDict['x'] = round(float(moduleParamsDict2['x']),3)
                        moduleParamsDict['y'] = round(float(moduleParamsDict2['y']),3)
                        simulationParamsDict['celllevelmodule'] = False
                        print("Due to error on celllevelModule info, ",\
                              "celllevelModule has ben set to False and the", \
                              "passed values of x and y on moduleParamsDict will",\
                              "be used to generate the custom module")
                    except:
                        print("Attempted to load x and y instead of celllevelModule parameters,",\
                              "Failed, so default values for cellLevelModule will be passed")
                        cellLevelModuleParamsDict['numcellsx'] = 12
                        cellLevelModuleParamsDict['numcellsy'] = 6
                        cellLevelModuleParamsDict['xcell'] = 0.15
                        cellLevelModuleParamsDict['xcellgap'] = 0.1
                        cellLevelModuleParamsDict['ycell'] = 0.15 
                        cellLevelModuleParamsDict['ycellgap'] = 0.1
            else: # no cellleveldictionary passed
                print("Load Warning: celllevelmodule selected, but no dictionary was passed in input file.",\
                      "attempting to proceed with regular custom module and setting celllevelmodule to false")
                simulationParamsDict['celllevelmodule'] = False
    
                try: 
                    moduleParamsDict['x'] = round(float(moduleParamsDict2['x']),3)
                except:
                    moduleParamsDict['x'] = 0.98
                    print("Load Warning: moduleParamsDict['x'] not specified, setting to default value: %s" % moduleParamsDict['x'] ) 
                try: 
                    moduleParamsDict['y'] = round(float(moduleParamsDict2['y']),3)
                except:
                    moduleParamsDict['y'] = 1.95
                    print("Load Warning: moduleParamsDict['y'] not specified, setting to default value: %s" % moduleParamsDict['y'] ) 
    
        else: # no cell level module requested:
            try: 
                moduleParamsDict['x'] = round(float(moduleParamsDict2['x']),3)
            except:
                moduleParamsDict['x'] = 0.98
                print("Load Warning: moduleParamsDict['x'] not specified, setting to default value: %s" % moduleParamsDict['x'] ) 
            try: 
                moduleParamsDict['y'] = round(float(moduleParamsDict2['y']),3)
            except:
                moduleParamsDict['y'] = 1.95
                print("Load Warning: moduleParamsDict['y'] not specified, setting to default value: %s" % moduleParamsDict['y'] ) 
           
    if simulationParamsDict['tracking']:
        if simulationParamsDict['timestampRangeSimulation']:
            try:
                timeControlParamsDict['DayEnd']=int(timeControlParamsDict2['DayEnd'])
                timeControlParamsDict['DayStart']=int(timeControlParamsDict2['DayStart'])
                timeControlParamsDict['MonthEnd']=int(timeControlParamsDict2['MonthEnd'])
                timeControlParamsDict['MonthStart']=int(timeControlParamsDict2['MonthStart'])
                timeControlParamsDict['HourEnd']=int(timeControlParamsDict2['HourEnd'])
                timeControlParamsDict['HourStart']=int(timeControlParamsDict2['HourStart'])
                
                if simulationParamsDict['daydateSimulation']:
                    print("Load Warning: timestampRangeSimulation and daydatesimulation both set to True.",\
                          "Doing timestampRangeSimulation and setting daydatesimulation to False")
                    simulationParamsDict['daydateSimulation'] = False
            except:
                try:
                    timeControlParamsDict['DayStart']=int(timeControlParamsDict2['DayStart'])
                    timeControlParamsDict['MonthStart']=int(timeControlParamsDict2['MonthStart']) 
                    print("Load Warning: timecontrolParamsDict hourend / hourstart is wrong/nan",\
                          "but since valid start day and month values were passed, switching simulation to",\
                          "daydatesimulation = True, timestampRangeSimulation = False")
                    simulationParamsDict['daydateSimulation']=True
                    simulationParamsDict['timestampRangeSimulation']=False
                except:
                    print("Load Warning: no valid day, month and hour passed for simulation.",\
                          "setting cumulative to True, and daydatesimulation and ",\
                          "timestampRangeSimulation to False")
                    simulationParamsDict['cumulativeSky']=True
                    simulationParamsDict['daydateSimulation']=False
                    simulationParamsDict['timestampRangeSimulation']=False
        if simulationParamsDict['daydateSimulation']: 
            try:
                timeControlParamsDict['DayStart']=int(timeControlParamsDict2['DayStart'])
                timeControlParamsDict['MonthStart']=int(timeControlParamsDict2['MonthStart']) 
            except:
                timeControlParamsDict['DayStart']=6
                timeControlParamsDict['MonthStart']=11
                print("Load warning: wrong dates passed for daydatesimulation. Using default",\
                      "values of dd_mm: '%s_%s' (b-day!)" % (timeControlParamsDict['DayStart'], timeControlParamsDict['MonthStart']))
    else: # fixed
        if simulationParamsDict['daydateSimulation']:
            print("Load Warning: fixed simulation does not have daydatesimulation",\
                  "Setting daydatesimulation to false.")
            simulationParamsDict['daydateSimulation']=False
            if 'timeindexend' and 'timeindexstart' in timeControlParamsDict2:
                if simulationParamsDict['timestampRangeSimulation']:    
                    print("Doing timestampRangeSimulation instead")
                else:
                    print("Since indexes for timeindexend and timeindexstart where passed, ",\
                          "setting simulationParamDict['timestampRangeSimulation'] to True",\
                          "and will attempt to use those for simulation")
                    simulationParamsDict['timestampRangeSimulation'] = True
        if simulationParamsDict['timestampRangeSimulation']: #TODO: this is crashing. KeyError: 'timeindexrangesimulation'
            try:
                 timeControlParamsDict['timeindexstart']=int(timeControlParamsDict2['timeindexstart'])
                 timeControlParamsDict['timeindexend']=int(timeControlParamsDict2['timeindexend'])
            except:
                 timeControlParamsDict['timeindexstart']=4020
                 timeControlParamsDict['timeindexend']=4024
                 print("Load warning: timeindex for start or end are wrong/nan. ", \
                       "setting to default %s to % s" % (timeControlParamsDict['timeindexstart'], timeControlParamsDict['timeindexend']) )
    
    #NEEDED sceneParamsDict parameters
    sceneParamsDict={}
    try:
        sceneParamsDict['albedo']=round(float(sceneParamsDict2['albedo']),2)
    except:
        sceneParamsDict['albedo']=sceneParamsDict2['albedo']
        #print("Load Warning: sceneParamsDict['albedo'] not specified, setting to default value: %s" % sceneParamsDict['albedo'] )    
    try:
        sceneParamsDict['nMods']=int(sceneParamsDict2['nMods'])
    except:
        sceneParamsDict['nMods']=20
        print("Load Warning: sceneParamsDict['nMods'] not specified, setting to default value: %s" % sceneParamsDict['nMods'] )    
    try:
        sceneParamsDict['nRows']=int(sceneParamsDict2['nRows'])
    except:
        sceneParamsDict['nRows']=7
        print("Load Warning: sceneParamsDict['nRows'] not specified, setting to default value: %s" % sceneParamsDict['nRows'] )    
    
    #Optional sceneParamsDict parameters
    sceneParamsDict['gcrorpitch'] = sceneParamsDict2['gcrorpitch']
    if sceneParamsDict['gcrorpitch'] == 'gcr':
        sceneParamsDict['gcr']=round(float(sceneParamsDict2['gcr']),3)
    else:
        sceneParamsDict['pitch']=round(float(sceneParamsDict2['pitch']),2)
        
    
    if simulationParamsDict['tracking']:
        sceneParamsDict['axis_azimuth']=round(float(sceneParamsDict2['axis_azimuth']),2)
        sceneParamsDict['hub_height']=round(float(sceneParamsDict2['hub_height']),2)
        
        if config.has_section("trackingParamsDict"):
            trackingParamsDict = boolConvert(confdict['trackingParamsDict']) 
            printTrackerWarning = False
        else:
            trackingParamsDict={}
            printTrackerWarning = True
        if 'limit_angle' in trackingParamsDict:
            trackingParamsDict['limit_angle']=round(float(trackingParamsDict['limit_angle']), 0)
        else:
            trackingParamsDict['limit_angle']=60
        if 'angle_delta' in trackingParamsDict:
            try:
                trackingParamsDict['angle_delta']=round(float(trackingParamsDict['angle_delta']), 2)
            except:
                trackingParamsDict['angle_delta']=1
        else:
            trackingParamsDict['angle_delta'] = (5 if simulationParamsDict['cumulativeSky'] else 0.01)
        if 'backtrack' not in trackingParamsDict:
            trackingParamsDict['backtrack']=5
 
        if printTrackerWarning:
            print("Load warning: tracking selected, but no tracking parameters specified.",\
                      "Using defaults for limit angle: 60; angle delta: %s, backtrackig: True" % trackingParamsDict['angle_delta'])                                         

    
    else: # fixed
        sceneParamsDict['azimuth']=round(float(sceneParamsDict2['azimuth']),2)
        sceneParamsDict['clearance_height']=round(float(sceneParamsDict2['clearance_height']),2)
        sceneParamsDict['tilt']=round(float(sceneParamsDict2['tilt']),2)
    
    # 
    if simulationParamsDict['torqueTube']:
        if config.has_section("torquetubeParamsDict"):
            torquetubeParamsDict = boolConvert(confdict['torquetubeParamsDict'])    
            try:
                torquetubeParamsDict['diameter'] = round(float(torquetubeParamsDict['diameter']),3)
            except:
                torquetubeParamsDict['diameter'] = 0.150
                print("Load Warning: torquetubeParamsDict['diameter'] not specified, setting to default value: %s" % torquetubeParamsDict['diameter'] )    
            #TODO: Validate for torquetube material and torquetube shape.
        else:
            print("Load warning: torquetubeParams dictionary not passed, but torquetube set to true.",\
                  "settung torquetube to false")
            simulationParamsDict['torquetube'] = False
            #TODO: decide if default values passed if this is set to true ?
            
    #Optional analysisParamsDict
    if config.has_section("analysisParamsDict"):
        analysisParamsDict = boolConvert(confdict['analysisParamsDict'])
        try: 
            analysisParamsDict['sensorsy']=int(analysisParamsDict['sensorsy']) 
        except:
            analysisParamsDict['sensorsy'] = 9 #Default
            print("Load Warning: analysisParamsDict['sensorsy'] not specified, setting to default value: %s" % analysisParamsDict['sensorsy'] )    
        try: 
            analysisParamsDict['modWanted']=int(analysisParamsDict['modWanted']) 
        except:
            analysisParamsDict['modWanted'] = None #Default
            print("Load Warning: analysisParamsDict['modWanted'] not specified, setting to default value: %s" % analysisParamsDict['modWanted'] )    
        try: 
            analysisParamsDict['rowWanted']=int(analysisParamsDict['rowWanted']) 
        except:
            analysisParamsDict['rowWanted'] = 9 #Default
            print("Load Warning: analysisParamsDict['rowWanted'] not specified, setting to default value: %s" % analysisParamsDict['rowWanted'] )    
    
    # Creating None dictionaries for those empty ones
    try: timeControlParamsDict
    except: timeControlParamsDict = None
    
    try: moduleParamsDict
    except: moduleParamsDict = None
    
    try: trackingParamsDict
    except: trackingParamsDict = None
    
    try: torquetubeParamsDict
    except: torquetubeParamsDict = None
    
    try: analysisParamsDict
    except: analysisParamsDict = None
    
    try: cellLevelModuleParamsDict
    except: cellLevelModuleParamsDict = None
    
    #returnParams = Params(simulationParamsDict, sceneParamsDict, timeControlParamsDict, moduleParamsDict, trackingParamsDict, torquetubeParamsDict, analysisParamsDict, cellLevelModuleParamsDict)
    #return returnParams
    return simulationParamsDict, sceneParamsDict, timeControlParamsDict, moduleParamsDict, trackingParamsDict, torquetubeParamsDict, analysisParamsDict, cellLevelModuleParamsDict


def savedictionariestoConfigurationIniFile(simulationParamsDict, sceneParamsDict, timeControlParamsDict=None, moduleParamsDict=None, trackingParamsDict=None, torquetubeParamsDict=None, analysisParamsDict=None, cellLevelModuleParamsDict=None, inifilename=None):
    '''
    inifilename = 'example.ini'
    '''
    
    import configparser
    
    config = configparser.ConfigParser()
    config.optionxform = str
    config['simulationParamsDict'] = simulationParamsDict
    config['sceneParamsDict'] = sceneParamsDict
    
    try: config['timeControlParamsDict'] = timeControlParamsDict
    except: pass
    
    try: config['timeControlParamsDict'] = timeControlParamsDict
    except: pass
    
    try: config['timeControlParamsDict'] = timeControlParamsDict
    except: pass
    
    try: config['moduleParamsDict'] = moduleParamsDict
    except: pass
    
    try: config['trackingParamsDict'] = trackingParamsDict
    except: pass
    
    try: config['torquetubeParamsDict'] = torquetubeParamsDict
    except: pass
    
    try: config['analysisParamsDict'] = analysisParamsDict
    except: pass
    
    try: config['cellLevelModuleParamsDict'] = cellLevelModuleParamsDict
    except: pass

    if inifilename is None:
        inifilename = 'example.ini'
    
    with open(inifilename, 'w') as configfile:
        config.write(configfile)
        


class Params():
    """

    model configuration parameters. Including the following:
    
    simulationParams          testfolder, weatherfile, getEPW, simulationname, 
                                  moduletype, rewritemodule,
                                  rcellLevelmodule, axisofrotationtorquetube, 
                                  torqueTube, hpc, tracking, cumulativesky,
                                  daydateSimulation, timestampRangeSimulation
    sceneParams:              gcrorpitch, gcr, pitch, albedo, nMods, nRows, 
                                  hub_height, clearance_height, azimuth, hub_height, axis_Azimuth
    timeControlParams:        hourstart, hourend, daystart, dayend, monthstart, monthend,
                                  timestampstart, timestampend, 
    moduleParams:             numpanels, x, y, bifi, xgap, ygap, zgap
    cellLevelModuleParams:    numcellsx, numcellsy, xcell, ycell, xcellgap, ycellgap
    trackingParams:           backtrack, limit_angle,angle_delta
    torquetubeParams:         diameter, tubetype, torqueTubeMaterial
    analysisParams:           sensorsy, modWanted, rowWanted
    
    """
    #    cdeline 5/9/19:  new class to try to make some sense of these model parameters?
    
    
    def __init__(self, simulationParams=None, sceneParams=None,
                 timeControlParams=None, moduleParams=None,
                 cellLevelModuleParams=None, trackingParams=None,
                 torquetubeParams=None, analysisParams=None):
        
        self.simulationParams = simulationParams
        self.sceneParams = sceneParams
        self.timeControlParams = timeControlParams
        self.moduleParams = moduleParams
        self.cellLevelModuleParams = cellLevelModuleParams
        self.trackingParams = trackingParams 
        self.torquetubeParams = torquetubeParams
        self.analysisParams = analysisParams 
    
    def unpack(self):
        return self.simulationParams, \
            self.sceneParams, \
            self.timeControlParams, \
            self.moduleParams, \
            self.trackingParams, \
            self.torquetubeParams, \
            self.analysisParams, \
            self.cellLevelModuleParams
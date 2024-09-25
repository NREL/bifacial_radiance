# -*- coding: utf-8 -*-
"""
Module providing routines for loading and cleaning results from bifacial_radiance.
Bifacial_radiance results are .csv format files stored in a results folder
autogenerated in the location where the RadianceObj was set to build its scene.
If no path was provided for the RadianceObj to build its scene, it defaults to
TEMP folder in bifacial_radiance \\ bifacial_radiance

"""
''' DEPRECATED - doesn't work with python3
def load_inputvariablesfile(inputfile):
    """
    Loads inputfile which must be in the bifacial_radiance directory,
    and must be a ``.py`` file with all the variables, and organizes the variables
    into dictionaries that it returns

    Parameters
    ----------
    inputfile : str
        String of a ``.py`` file in the bifacial_radiance directory.

    Returns
    -------
    simulationParamsDict : Dictionary
        Dictionary containing the parameters for performing the simulation,
        including simulation names, and types of sky, fixed or tracked systems:
            ========================  =======  =============================
            variable                   type         Description
            ========================  =======  =============================
            testfolder                str      Path to testfolder
            weatherfile               str      File (with path) to weatherfile
            getEPW                    bool     
            simulationname            str      Name for simulation
            moduletype                str      Module name as is / or will be defined in JSON
            rewritemodule             bool     If moduletype exists in JSON, True will rewrite with new parameters
            cellLevelmodule           bool        
            axisofrotationtorquetube  bool
            torqueTube                bool
            hpc                       bool
            tracking                  bool
            cumulativesky             bool
            daydateSimulation         bool
            selectTimes               bool
            ========================  =======  =============================
    sceneParamsDict : Dictionary 
        gcrorpitch, gcr, pitch, albedo, nMods, nRows, 
        hub_height, clearance_height, azimuth, hub_height, axis_Azimuth
    timeControlParamsDict : Dictionary      
        hourstart, hourend, daystart, dayend, monthstart, monthend,
        timestampstart, timestampend, 
    moduleParamsDict : Dictionary
        numpanels, x, y, bifi, xgap, ygap, zgap
    cellLevelModuleParamsDict : Dictionary
        numcellsx, numcellsy, xcell, ycell, xcellgap, ycellgap
    trackingParamsDict : Dictionary
        backtrack, limit_angle,angle_delta
    torquetubeParamsDict : Dictionary
         diameter, tubetype, torqueTubeMaterial
    analysisParamsDict : Dictionary
        sensorsy, modWanted, rowWanted
    """
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
                             'selectTimes':ibf.selectTimes
                             'hpc': ibf.hpc,
                             'daydateSimulation': ibf.dayDateSimulation}
                             #'singleKeySimulation': ibf.singleKeySimulation,
                             #'singleKeyRangeSimulation': ibf.singleKeyRangeSimulation}

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

    # #TODO: Figure out how to return this optional return items.
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

'''

def loadRadianceObj(savefile=None):
    """
    Load the pickled radiance object for further use
    Usage (once you're in the correct local directory)::
        
        demo = bifacial_radiance.loadRadianceObj(savefile)
    
    Parameters
    ----------
    savefile : str
        Optional savefile name. Otherwise default to `save.pickle`
            
    """
    import pickle
    
    if savefile is None:
        savefile = 'save.pickle'
    with open(savefile,'rb') as f:
        loadObj= pickle.load(f)
    
    print('Loaded file {}'.format(savefile))
    return loadObj

def read1Result(selectfile):
    """
    Loads in a bifacial_radiance results file ``.csv`` format,
    and return a :py:class:`~pandas.DataFrame`
    
    Parameters
    ----------
    selectfile : str
        File name (with path if not in working folder) that has been produced by
        bifacial_radiance.
    
    Returns
    -------
    resultsDF : :py:class:`~pandas.DataFrame`
        Dataframe with the bifacial_radiance .csv values read.
        
    """
    import pandas as pd
    
    #resultsDict = pd.read_csv(os.path.join('results',selectfile))
    resultsDF = pd.read_csv(selectfile)

    #return(np.array(temp['Wm2Front']), np.array(temp['Wm2Back']))
    return resultsDF
# End read1Result subroutine

def cleanResult(resultsDF, matchers=None):
    """
    Replace irradiance values with NaN's when the scan intersects ground, 
    sky, or anything in `matchers`.
    
    Matchers are words in the dataframe like  'sky' or 'tube' 
    in the front or back material description column that 
    get substituted by NaN in Wm2Front and Wm2Back
    There are default matchers established in this routine but other matchers
    can be passed.
    Default matchers: 'sky', 'tube', 'pole', 'ground', '3267', '1540'.
    Matchers 3267 and 1540 is to get rid of inner-sides of the module.
    
    Parameters
    ----------
    resultsDF : :py:class:`~pandas.DataFrame`
        DataFrame of results from bifacial_radiance, for example read 
        from :py:class:`~bifacial_radiance.load.read1Result`
    
    Returns
    --------
    resultsDF : :py:class:`~pandas.DataFrame`
        Updated resultsDF 
    
    """
    
    import numpy as np
    
    if matchers is None:
        matchers = ['sky','pole','tube','bar','ground', '3267', '1540']
    NaNindex = [i for i,s in enumerate(resultsDF['mattype']) if any(xs in s for xs in matchers)]
    NaNindex2 = [i for i,s in enumerate(resultsDF['rearMat']) if any(xs in s for xs in matchers)]
    #NaNindex += [i for i,s in enumerate(frontDict['mattype']) if any(xs in s for xs in matchers)]    
    for i in NaNindex:
        resultsDF.loc[i,'Wm2Front'] = np.nan 
    for i in NaNindex2:
        resultsDF.loc[i,'Wm2Back'] = np.nan
    
    return resultsDF


def loadTrackerDict(trackerdict, fileprefix=None):
    """
    Load a trackerdict by reading all files in the `\\results` directory.
    fileprefix is used to select only certain matching files in `\\results`
   
    It will then save the `Wm2Back`, `Wm2Front` and `backRatio` by reading in all valid files in the
    `\\results` directory.  Note: it will match any file ending in `_key.csv`
    
    Parameters
    ----------
    trackerdict : 
        You need to pass in a valid trackerdict with correct keys from 
        :py:class:`~bifacial_radiance.RadianceObj.set1axis`
    fileprefix : str
        Optional parameter to specify the initial part of the savefile prior 
        to '_key.csv'
    
    Returns
    -------
    trackerdict : Dictionary
        Dictionary with additional keys ``Wm2Back``, ``Wm2Front``, ``backRatio``
    totaldict : Dictionary
        totalized dictionary with ``Wm2Back``, ``Wm2Front``. 
        Also ``numfiles`` (number of csv files loaded) and 
        ``finalkey`` (last index file in directory)

    """
       
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
    # == TS: LoadTrackerDict failure 'Wm2FrontTotal' ==
    totaldict = {'Wm2Front':Wm2FrontTotal, 'Wm2Back':Wm2BackTotal, 'numfiles':i, 'finalkey':finalkey}
    
    print('Files loaded: {};  Wm2Front_avg: {:0.1f}; Wm2Rear_avg: {:0.1f}'.format(i, np.nanmean(Wm2FrontTotal), np.nanmean(Wm2BackTotal) ))
    print('final key loaded: {}'.format(finalkey))
    return(trackerdict, totaldict)
    #end loadTrackerDict subroutine.  set demo.Wm2Front = totaldict.Wm2Front. demo.Wm2Back = totaldict.Wm2Back


def _exportTrackerDict(trackerdict, savefile, reindex):
    """
    Save a TrackerDict output as a ``.csv`` file.
    
    Parameters
    ----------
        trackerdict : Dictionary
            The tracker dictionary to save
        savefile : str
            Path to .csv save file location
        reindex : bool
            Boolean indicating if trackerdict should be resampled to include
            all 8760 hours in the year (even those when the sun is not up and 
            irradiance results is empty).
    
    """
    from pandas import DataFrame as df
    import numpy as np
    import pandas as pd

    print("Exporting TrackerDict")
    
    # convert trackerdict into dataframe
    d = df.from_dict(trackerdict,orient='index',columns=['dhi','ghi','Wm2Back','Wm2Front','theta','surf_tilt','surf_azm','clearance_height', 'effective_irradiance', 'Pout_module'])
    d['Wm2BackAvg'] = [np.nanmean(i) for i in d['Wm2Back']]
    d['Wm2FrontAvg'] = [np.nanmean(i) for i in d['Wm2Front']]

    # Search for module object bifaciality
    try:
        keys = list(trackerdict.keys())
        bifacialityfactor = trackerdict[keys[0]]['scene'].module.bifi
    except:
        bifacialityfactor = 1.0
        print("Bifaciality factor of module not found, setting to ", bifacialityfactor,
              "for BifiRatio calculation")
        
    d['BifiRatio'] =  d['Wm2BackAvg'] * bifacialityfactor / d['Wm2FrontAvg']

    if reindex is True: # change to proper timestamp and interpolate to get 8760 output
        d['measdatetime'] = d.index
        d=d.set_index(pd.to_datetime(d['measdatetime'], format='%Y-%m-%d_%H%M'))
        d=d.resample('H').asfreq()
  
    d.to_csv(savefile)    

    
def deepcleanResult(resultsDict, sensorsy, numpanels, automatic=True):
    """    
    Cleans results file read by read1Result. If automatic = False, user is
    asked to select material of the module (usually the one with the most results) 
    and removes sky, ground, and other materials (side of module, for example).
    If you pass in results from a file with only _Front or _Back parameters,
    only the corresponding Frontresults or Backresults will be returned.
    
    Parameters
    -----------
    sensorsy : int
        For the interpolation routine. Can be more than original sensorsy or same value.
    numpanels : int
        Options are 1 or 2 panels for this function.
    automatic : bool
        Default True. Automaticatlly detects module and ignores Ground, torque tube and 
        sky values. If set to off, user gets queried about the right surfaces.
    
    Returns
    -------
    Frontresults : :py:class:`~pandas.DataFrame`
        Dataframe with only front-irradiance values for the module material selected, 
        length is the number of sensors desired.
    Backresults : :py:class:`~pandas.DataFrame`
        Dataframe with only rear-irradiance values for the module material selected, 
        length is the number of sensors desired.
    """
    
    # #TODO: add automatization of panel select.

    import numpy as np
    
    
    def interp_sub(panelDict, sensorsy, frontbackkey):
        """
        Parameters
        -----------
        panelDict : Dictionary
            resultsDict filtered for either panelA or panelB from above. 
        sensorsy : int
            Number of y sensors to interpolate to
        frontbackkey : str
            Either 'Wm2Front' or 'Wm2Back'
        
        """
        x_0 = np.linspace(0, len(panelDict)-1, len(panelDict))    
        x_i = np.linspace(0, len(panelDict)-1, int(sensorsy))
        interp_out = np.interp(x_i, x_0, panelDict[frontbackkey])
        
        return interp_out


    def filter_sub(resultsDict, sensorsy, frontmask, backmask=None):
        """  
        filter_sub: filter resultsDict to accept points where front and rear 
        materials match the list of strings in frontmask and backmask.
        
        Parameters
        ----------
        panelDict : Dictionary
            resultsDict to filter
        frontmask / backmask: List
            list of material string values to filter for, one entry per panel.
        """
        mask = np.zeros(len(resultsDict))
        for i in range(len(frontmask)):
            try:
                temp_mask = (resultsDict['mattype'].str.contains(frontmask[i]) )
            except KeyError:
                temp_mask = np.ones(len(resultsDict))
            if backmask:
                temp_mask = temp_mask & (resultsDict['rearMat'].str.contains(backmask[i]))
            mask = mask | temp_mask
        
        
        if backmask:
            try:
                Frontresults = interp_sub(resultsDict[mask], sensorsy, 'Wm2Front')
            except KeyError: # no Wm2Front data passed - rear data only.
                Frontresults = None
            Backresults = interp_sub(resultsDict[mask], sensorsy, 'Wm2Back')
        else:
            Frontresults = interp_sub(resultsDict[mask], sensorsy, resultsDict.columns[-1])
            Backresults = None
        
        return Frontresults, Backresults 
    

    if automatic == True:
        # by default, these are the material values attached to bifacial_radiance
        # modules
        if 'mattype' in resultsDict:
            frontmask = ['PVmodule.6457']
        else: frontmask = ['PVmodule.2310'] # result only has _Back file passed 
            
        if 'rearMat' in resultsDict:
            backmask = ['PVmodule.2310']
        else:  backmask = None

    else:
        # user-defined front and back material pairs to select. one per numpanel
        frontmask = []
        backmask = []
        try: # User-entered front materials to select for
            fronttypes = resultsDict.groupby('mattype').count() 
            print("Front type materials index and occurrences: ")
            for i in range (len(fronttypes)):
                print(i, " --> ", fronttypes['x'][i] , " :: ",  fronttypes.index[i])
            for i in range(numpanels):
                val = int(input(f"Panel a{i} Front material "))
                frontmask.append(fronttypes.index[val])
        except KeyError:  # no front mattype options to be selected
            pass
        
        try:  # User-eneterd rear materials to select for
            backtypes = resultsDict.groupby('rearMat').count()
            if 'rearMat' in resultsDict:
                print("Rear type materials index and occurrences: ")
                for i in range (len(backtypes)):
                    print(i, " --> ", backtypes['x'][i] , " :: ",  backtypes.index[i])
                for i in range(numpanels):
                    val = int(input(f"Panel a{i} Rear material "))
                    backmask.append(backtypes.index[val])
        except KeyError: # no rear materials to be selected
            pass

    # now that we know what material names to look for, filter resultsDict for 
    # them, removing frames, sky, torque tube, etc.     
    Frontresults, Backresults = filter_sub(resultsDict, sensorsy, frontmask, backmask)
        
    return Frontresults, Backresults;    # End Deep clean Result subroutine.

def readconfigurationinputfile(inifile=None):
    """
    Function to read configurationinput file for a bifacial_radiance simulation.
    
    Parameters
    ----------
    input : str
      Filename with extension .ini to read in
    
    Returns
    -------
    simulationParamsDict : Dictionary
    sceneParamsDict : Dictionary
    timeControlParamsDict : Dictionary 
    moduleParamsDict : Dictionary
    trackingParamsDict : Dictionary
    torquetubeParamsDict : Dictionary
    analysisParamsDict : Dictionary
    cellLevelModuleParamsDict : Dictionary

    """

    ## #TODO: check if modulename exists on jason and rewrite is set to false, then
    #don't save moduleParamsDict? Discuss.

    import configparser
    import os
    import ast
    
    def boolConvert(d):
        """ convert strings 'True' and 'False' to boolean and convert numbers to float
        """
        for key,value in d.items():
            if value.lower() == 'true': 
                d[key] = True
            elif value.lower() == 'false':
                d[key] = False
            try:
                d[key] = float(value)
            except ValueError:
                pass
        return d
    
    if inifile is None:
        inifile = os.path.join("data","default.ini")

    config = configparser.ConfigParser(allow_no_value=True)
    config.optionxform = str  
    config.read_file(open(inifile, 'r'))
    
    confdict = {section: dict(config.items(section)) for section in config.sections()}
    
    if config.has_section("simulationParamsDict"):
        simulationParamsDict = boolConvert(confdict['simulationParamsDict'])
    else:
        raise Exception("Missing simulationParamsDict! Breaking")
        
        
    if config.has_section("sceneParamsDict"):
        sceneParamsDict2 = boolConvert(confdict['sceneParamsDict'])
    else:
        raise Exception("Missing sceneParams Dictionary! Breaking")
            
    if simulationParamsDict['selectTimes']:
        if config.has_section("timeControlParamsDict"):
            timeControlParamsDict = confdict['timeControlParamsDict']
           
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
            moduleParamsDict['zgap'] = round(float(moduleParamsDict2['zgap']),3)
        except:
            moduleParamsDict['zgap'] = 0.1 #Default
            print("Load Warning: moduleParamsDict['zgap'] not specified, setting to default value: %s" % moduleParamsDict['zgap'] ) 
        if 'glass' in moduleParamsDict2:
            moduleParamsDict['glass'] = moduleParamsDict2['glass']
        if moduleParamsDict2.get('glassEdge'):
            moduleParamsDict['glassEdge'] = moduleParamsDict2['glassEdge']
        if simulationParamsDict['cellLevelModule']:    
            if config.has_section("cellLevelModuleParamsDict"):
                cellModuleDict = confdict['cellLevelModuleParamsDict']
                try: # being lazy so just validating the whole dictionary as a whole. #TODO: validate individually maybe.            
                    cellModuleDict['numcellsx'] = int(cellModuleDict['numcellsx'])
                    cellModuleDict['numcellsy'] = int(cellModuleDict['numcellsy'])
                    cellModuleDict['xcell'] = round(float(cellModuleDict['xcell']),3)
                    cellModuleDict['xcellgap'] = round(float(cellModuleDict['xcellgap']),3)
                    cellModuleDict['ycell'] = round(float(cellModuleDict['ycell']),3)
                    cellModuleDict['ycellgap'] = round(float(cellModuleDict['ycellgap']),3)
                    if 'centerJB' in cellModuleDict:
                        cellModuleDict['centerJB'] = round(float(cellModuleDict['centerJB']),3)
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
                        cellModuleDict['numcellsx'] = 12
                        cellModuleDict['numcellsy'] = 6
                        cellModuleDict['xcell'] = 0.15
                        cellModuleDict['xcellgap'] = 0.1
                        cellModuleDict['ycell'] = 0.15 
                        cellModuleDict['ycellgap'] = 0.1
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
           
    if simulationParamsDict['selectTimes']:
        if ('starttime' in timeControlParamsDict) or ('endtime' in timeControlParamsDict):
            print("Loading times to restrict weather data to")
        else:
            print("Load Warning: no valid time to restrict weather data passed"
                  "Simulating default day 06/21 at noon")
            timeControlParamsDict['starttime']='06_21_12_00'
            timeControlParamsDict['endtime']='06_21_12_00'

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
        if 'axis_aziumth' in sceneParamsDict2:
            azimuth = sceneParamsDict2['axis_azimuth']
        elif sceneParamsDict2.get('azimuth'):
            azimuth = sceneParamsDict2.get('azimuth')
        else:
            raise Exception(f'Neither "axis_azimuth" or "azimuth" in .inifile {inifile}' )
            
        sceneParamsDict['azimuth']=round(float(azimuth),2)
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
                      "Using defaults for limit angle: 60; angle delta: %s, backtracking: True" % trackingParamsDict['angle_delta'])                                         

    
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
                print("Load Warning: torquetubeParamsDict['diameter'] not "
                      "specified, setting to default value: %s" % torquetubeParamsDict['diameter'] )    
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
            analysisParamsDict['sensorsy']=ast.literal_eval(analysisParamsDict['sensorsy']) 
        except:
            analysisParamsDict['sensorsy'] = 9 #Default
            print("Load Warning: improper or no analysisParamsDict['sensorsy']"
                  " passed, setting to default value: %s" % analysisParamsDict['sensorsy'] )    
        try: 
            analysisParamsDict['modWanted']=int(analysisParamsDict['modWanted']) 
        except:
            analysisParamsDict['modWanted'] = None #Default
            print("analysisParamsDict['modWanted'] set to middle module by default" )    
        try: 
            analysisParamsDict['rowWanted']=int(analysisParamsDict['rowWanted']) 
        except:
            analysisParamsDict['rowWanted'] = None #Default
            print("analysisParamsDict['rowWanted'] set to middle row by default" )    
    
    if "frameParamsDict" in confdict:
        frameParamsDict = boolConvert(confdict['frameParamsDict'])
    else:
        frameParamsDict = None
    if "omegaParamsDict" in confdict:
        omegaParamsDict = boolConvert(confdict['omegaParamsDict'])
    else:
        omegaParamsDict = None
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
    
    try: cellModuleDict
    except: cellModuleDict = None
    
    #returnParams = Params(simulationParamsDict, sceneParamsDict, timeControlParamsDict, moduleParamsDict, trackingParamsDict, torquetubeParamsDict, analysisParamsDict, cellModuleDict)
    #return returnParams
    return (simulationParamsDict, sceneParamsDict, timeControlParamsDict, 
            moduleParamsDict, trackingParamsDict, torquetubeParamsDict, 
            analysisParamsDict, cellModuleDict, frameParamsDict, omegaParamsDict)


def savedictionariestoConfigurationIniFile(simulationParamsDict, sceneParamsDict, 
                                           timeControlParamsDict=None, moduleParamsDict=None, 
                                           trackingParamsDict=None, torquetubeParamsDict=None, 
                                           analysisParamsDict=None, cellModuleDict=None, 
                                           frameParamsDict=None, omegaParamsDict=None, inifilename=None):
    """
    Saves dictionaries from working memory into a Configuration File
    with extension format .ini.
    
    Parameters
    ----------
    simulationParamsDict
    sceneParamsDict
    timeControlParamsDict 
        Default None
    moduleParamsDict
        Default None
    trackingParamsDict
        Default None 
    torquetubeParamsDict
        Default None 
    analysisParamsDict
        Default None, 
    cellModuleDict
        Default None    
    
    Returns
    -------
    Writes output into inifilename passed (default if inifilename=None is 
    'example.ini')
    """
    
    import configparser
    
    config = configparser.ConfigParser(allow_no_value=True)
    config.optionxform = str
    config['simulationParamsDict'] = simulationParamsDict
    config['sceneParamsDict'] = sceneParamsDict
    
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
    
    try: config['cellLevelModuleParamsDict'] = cellModuleDict
    except: pass

    if frameParamsDict:    
        try: config['frameParamsDict'] = frameParamsDict
        except: pass

    if omegaParamsDict:
        try: config['omegaParamsDict'] = omegaParamsDict
        except: pass

    if inifilename is None:
        inifilename = 'example.ini'
    
    with open(inifilename, 'w') as configfile:
        config.write(configfile)
        

'''
## abandoned project to refactor this module...
class Params():
    """
    Model configuration parameters. Including the following:
    
    Parameters
    ----------
    simulationParams          testfolder, weatherfile, getEPW, simulationname, 
                                  moduletype, rewritemodule,
                                  rcellLevelmodule, axisofrotationtorquetube, 
                                  torqueTube, hpc, tracking, cumulativesky,
                                  selectTimes
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
    # #DocumentationCheck : add to updates
    # cdeline 5/9/19:  new class to try to make some sense of these model parameters?
    
    
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
'''
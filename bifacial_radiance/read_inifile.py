import configparser
import os

def load_configfile_bifacialradiance():
    config = configparser.ConfigParser()
    config.read("config.ini")
    confdict = {section: dict(config.items(section)) for section in config.sections()}
    

    if config.has_section("simulationParamsDict"):
        simulationParamsDict = confdict['simulationParamsDict']
    else:
        print("Mising simiulationParamsDict! Breaking")
        break;
        
    if config.has_section("sceneParamsDict"):
        sceneParamsDict2 = confdict['sceneParamsDict']
    else:
        print("Mising scenePArams Dictionary! Breaking")
        break;

    if simulationParamsDict['timestampRangeSimulation'] or simulationParamsDict['daydateSimulation']:
        if config.has_section("timeControlParamsDict"):
            timeControlParamsDict2 = confdict['timeControlParamsDict']
        else:
            print("Mising timeControlParamsDict for simulation options specified! Breaking")
            break;            
            
    if simulationParamsDict['getepw']:
        try:
            simulationParamsDict['latitude'] = float(simulationParamsDict['latitude'])
            simulationParamsDict['longitude'] = float(simulationParamsDict['longitude'])
        except:
            if 'weatherfile' in simulationParamsDict:
                try: 
                    os.path.exists(simulationParamsDict['weatherfile'])
                    simulationParamsDict['getepw'] = False
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
    
    if simulationParamsDict['custommodule']:
        if config.has_section("moduleParamsDict"):
            moduleParamsDict2 = confdict['moduleParamsDict']
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
                        
            if simulationParamsDict['celllevelmodule']:    
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
                        print("Load Warning: custommodule and celllevelModule set to True,",\
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
                        moduleParamsDict['y'] = round(float(moduleParamsDict2['x']),3)
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
                    moduleParamsDict['y'] = round(float(moduleParamsDict2['x']),3)
                except:
                    moduleParamsDict['y'] = 1.95
                    print("Load Warning: moduleParamsDict['y'] not specified, setting to default value: %s" % moduleParamsDict['y'] ) 
       else: # no module dictionary passed
           print ("Load Warning: custom module requested but no modulePArams Dict passed")
           #TODO: Check if name is a valid module, and if so, set custommodule to false. Else: assign custom module values.
           
    if simulationParamsDict['tracking']:
        if simulationParamsDict['timeindexrangesimulation']:
            try:
                timeControlParamsDict['dayend']=int(timeControlParamsDict2['dayend'])
                timeControlParamsDict['daystart']=int(timeControlParamsDict2['daystart'])
                timeControlParamsDict['monthend']=int(timeControlParamsDict2['monthend'])
                timeControlParamsDict['monthstart']=int(timeControlParamsDict2['monthstart'])
                timeControlParamsDict['hourend']=int(timeControlParamsDict2['hourend'])
                timeControlParamsDict['hourstart']=int(timeControlParamsDict2['hourstart'])
                
                if simulationParamsDict['daydatesimulation']:
                    print("Load Warning: timeindexrangesimulation and daydatesimulation both set to True.",\
                          "Doing timeindexrangesimulation and setting daydatesimulation to False")
                    imulationParamsDict['daydatesimulation'] = False
            except:
                try:
                    timeControlParamsDict['daystart']=int(timeControlParamsDict2['daystart'])
                    timeControlParamsDict['monthstart']=int(timeControlParamsDict2['monthstart']) 
                    print("Load Warning: timecontrolParamsDict hourend / hourstart is wrong/nan",\
                          "but since valid start day and month values were passed, switching simulation to",\
                          "daydatesimulation = True, timeindexrangesimulation = False")
                    simulationParamsDict['daydatesimulation']=True
                    simulationParamsDict['timeindexrangesimulation']=False
                except:
                    print("Load Warning: no valid day, month and hour passed for simulation.",\
                          "setting cumulative to True, and daydatesimulation and ",\
                          "timeindexrangesimulation to False")
                    simulationParamsDict['cumulative']=True
                    simulationParamsDict['daydatesimulation']=False
                    simulationParamsDict['timeindexrangesimulation']=False
        if simulationParamsDict['daydatesimulation']: 
            try:
                timeControlParamsDict['daystart']=int(timeControlParamsDict2['daystart'])
                timeControlParamsDict['monthstart']=int(timeControlParamsDict2['monthstart']) 
            except:
                timeControlParamsDict['daystart']=6
                timeControlParamsDict['monthstart']=11
                print("Load warning: wrong dates passed for daydatesimulation. Using default",\
                      "values of dd_mm: '%s_%s' (b-day!)" % (timeControlParamsDict['daystart'], timeControlParamsDict['daystart']))
    else: # fixed
        if simulationParamsDict['daydatesimulation']:
            print("Load Warning: fixed simulation does not have daydatesimulation",\
                  "Setting daydatesimulation to false.")
            simulationParamsDict['daydatesimulation']=False
            if 'timeindexend' and 'timeindexstart' in timeControlParamsDict2:
                if simulationParamsDict['timeindexrangesimulation']:    
                    print("Doing timeindexrangesimulation instead")
                else:
                    print("Since indexes for timeindexend and timeindexstart where passed, ",\
                          "setting simulationParamDict['timeindexrangesimulation'] to True",\
                          "and will attempt to use those for simulation")
                    simulationParamsDict['timeindexrangesimulation'] = True
        if simulationParamsDict['timeindexrangesimulation']:
            try:
                 timeControlParamsDict['timeindexstart']=int(timeControlParamsDict2['timeindexstart'])
                 timeControlParamsDict['timeindexend']=int(timeControlParamsDict2['timeindexend'])
             except:
                 timeControlParamsDict['timeindexstart']=4020
                 timeControlParamsDict['timeindexend']=4024
                 print("Load warning: timeindex for start or end are wrong/nan. ", \
                       "setting to default %s to % s" % (timeControlParamsDict['timeindexstart'], timeControlParamsDict['timeindexend']) )
    
    #NEEDED sceneParamsDict parameters
    try:
        sceneParamsDict['albedo']=round(float(sceneParamsDict2['albedo']),2)
    except:
        sceneParamsDict['albedo']=0.3
        print("Load Warning: sceneParamsDict['albedo'] not specified, setting to default value: %s" % sceneParamsDict['albedo'] )    
    try:
        sceneParamsDict['nMods']=int(sceneParamsDict2['nMods'])
    except:
        sceneParamsDict['nMods']=20
        print("Load Warning: sceneParamsDict['albedo'] not specified, setting to default value: %s" % sceneParamsDict['nMods'] )    
    try:
        sceneParamsDict['nRows']=int(sceneParamsDict2['nRows'])
    except:
        sceneParamsDict['nRows']=7
        print("Load Warning: sceneParamsDict['albedo'] not specified, setting to default value: %s" % sceneParamsDict['nRows'] )    
    
    #Optional sceneParamsDict parameters
    if sceneParamsDict['gcrorpitch'] == 'gcr':
        sceneParamsDict['gcr']=round(float(sceneParamsDict['gcr']),3)
    else:
        sceneParamsDict['pitch']=round(float(sceneParamsDict['pitch']),2)
        

    if simulationParamsDict['tracking']:
        sceneParamsDict['axis_azimuth']=int(sceneParamsDict['axis_azimuth'])
        sceneParamsDict['hub_height']=int(sceneParamsDict['hub_height'])
        
        if config.has_section("trackingParamsDict"):
            trackingParamsDict = confdict['trackingParamsDict']    
            trackingParamsDict['limit_angle']=int(trackingParamsDict['limit_angle'])
            trackingParamsDict['angle_delta']=float(trackingParamsDict['limit_angle'], 2)
        else:
            trackingParamsDict={}
            if simulationParamsDict['cumulativesky']:
                trackingParamsDict['angle_delta']=5
            else:
                trackingParamsDict['angle_delta']=0.01
            trackingParamsDict['backtrack']=5
            trackingParamsDict['limit_angle']=60
            print("Load warning: tracking selected, but no tracking parameters specified.",\
                  "Using defaults for limit angle: 60; angle delta: %s, backtrackig: True" % trackingParamsDict['angle_delta'])

    else: # fixed
        sceneParamsDict['azimuth_ang']=int(sceneParamsDict['azimuth_ang'])
        sceneParamsDict['clearance_height']=int(sceneParamsDict['clearance_height'])
        sceneParamsDict['tilt']=int(sceneParamsDict['tilt'])
    
    # 
    if simulationParamsDict['torquetube']:
        if config.has_section("torquetubeParamsDict"):
            torquetubeParamsDict = confdict['torquetubeParamsDict']    
            try:
                torquetubeParamsDict['diameter'] = float(torquetubeParamsDict['diameter'],3)
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
        analysisParamsDict = confdict['analysisParamsDict']
        try: 
            analysisParamsDict['sensorsy']=int(analysisParamsDict['sensorsy']) 
        except:
            analysisParamsDict['sensorsy'] = 9 #Default
            print("Load Warning: analysisParamsDict['sensorsy'] not specified, setting to default value: %s" % analysisParamsDict['sensorsy'] )    
        try: 
            analysisParamsDict['modwanted']=int(analysisParamsDict['modwanted']) 
        except:
            analysisParamsDict['modwanted'] = None #Default
            print("Load Warning: analysisParamsDict['modwanted'] not specified, setting to default value: %s" % analysisParamsDict['modwanted'] )    
        try: 
            analysisParamsDict['rowwanted']=int(analysisParamsDict['rowwanted']) 
        except:
            analysisParamsDict['rowwanted'] = 9 #Default
            print("Load Warning: analysisParamsDict['rowwanted'] not specified, setting to default value: %s" % analysisParamsDict['rowwanted'] )    
    

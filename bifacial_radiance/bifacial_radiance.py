#!/usr/bin/env python
from __future__ import division  # avoid integer division issues.
from __future__ import absolute_import # this module uses absolute imports
'''
@author: cdeline

bifacial_radiance.py - module to develop radiance bifacial scenes, including gendaylit and gencumulativesky
7/5/2016 - test script based on G173_journal_height
5/1/2017 - standalone module

Pre-requisites:
    This software is written in Python 2.7 leveraging many Anaconda tools (e.g. pandas, numpy, etc)
    
    *RADIANCE software should be installed from https://github.com/NREL/Radiance/releases

    *If you want to use gencumulativesky, move 'gencumulativesky.exe' from 
    'bifacial_radiance\data' into your RADIANCE source directory.

    *If using a Windows machine you should download the Jaloxa executables at 
    http://www.jaloxa.eu/resources/radiance/radwinexe.shtml#Download

    * Installation of  bifacial_radiance from the repo:
    1. Clone the repo
    2. Navigate to the directory using the command prompt
    3. run `pip install -e . `

Overview:  
    Bifacial_radiance includes several helper functions to make it easier to evaluate
    different PV system orientations for rear bifacial irradiance.
    Note that this is simply an optical model - identifying available rear irradiance under different conditions.
    
    For a detailed demonstration example, look at the .ipnyb notebook in \docs\
    
    There are two solar resource modes in bifacial_radiance: `gendaylit` uses hour-by-hour solar
    resource descriptions using the Perez diffuse tilted plane model.
    `gencumulativesky` is an annual average solar resource that combines hourly
    Perez skies into one single solar source, and computes an annual average.
    
    bifacial_radiance includes five object-oriented classes:
    
    RadianceObj:  top level class to work on radiance objects, keep track of filenames, 
    sky values, PV module type etc.
    
    GroundObj:    details for the ground surface and reflectance
    
    SceneObj:    scene information including array configuration (row spacing, clearance or hub height)
    
    MetObj: meteorological data from EPW (energyplus) file.  
        Future work: include other file support including TMY files
    
    AnalysisObj: Analysis class for plotting and reporting
    
'''
'''
Revision history

0.2.4:  Module orientation deprecated. Py36 and cross-platform code compliance implemented. Modified gendaylit to be based on sun positions by default. More torquetube options added (round, square, hexagonal and octagonal profiles), custom spacing between modules in a row added, included accuracy input option for 1-axis scans, updated falsecolor routine, module-select bug and module scan bug fixed, updates to pytests. Update to sensor position on 1axistracking.
0.2.3:  arbitrary length and position of module scans in makeScene. Torquetube option to makeModule. New gendaylit1axis and hourly makeOct1axis, analysis1axis
0.2.2:  Negative 1 hour offset to TMY file inputs
0.2.1:  Allow tmy3 input files.  Use a different EPW file reader.
0.2.0:  Critical 1-axis tracking update to fix geometry issues that were over-predicting 1-axis results
0.1.1:  Allow southern latitudes
0.1.0:  1-axis bug fix and validation vs PVSyst and ViewFactor model
0.0.5:  1-axis tracking draft
0.0.4:  Include configuration file module.json and custom module configuration
0.0.3:  Arbitrary NxR number of modules and rows for SceneObj 
0.0.2:  Adjustable azimuth angle other than 180
0.0.1:  Initial stable release
'''
import os, datetime, sys
import matplotlib.pyplot as plt  
import pandas as pd
import numpy as np #already imported with above pylab magic
#from scipy.interpolate import *
#from IPython.display import Image
from subprocess import Popen, PIPE  # replacement for os.system()
#import shlex
if __name__ == "__main__": #in case this is run as a script not a module.
    from readepw import readepw  
    from load import loadTrackerDict
    #from input_bf import *         # Preloads sample values for simulations.

else: # module imported or loaded normally
    from bifacial_radiance.readepw import readepw # epw file reader from pvlib development forums  #module load format
    from bifacial_radiance.load import loadTrackerDict
    #from bifacial_radiance.input_bf import * # Preloads sample values for simulations.

from time import sleep
#from pathlib import Path



# Mutual parameters across all processes
#daydate=sys.argv[1]

import pkg_resources
global DATA_PATH # path to data files including module.json.  Global context
#DATA_PATH = os.path.abspath(pkg_resources.resource_filename('bifacial_radiance', 'data/') )
DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

def _findme(lst, a): #find string match in a list. found this nifty script on stackexchange
    return [i for i, x in enumerate(lst) if x==a]


def _normRGB(r,g,b): #normalize by weight of each color for human vision sensitivity
    return r*0.216+g*0.7152+b*0.0722

def _popen(cmd, data_in, data_out=PIPE):
    """
    Helper function subprocess.popen replaces os.system 
    - gives better input/output process control
    usage: pass <data_in> to process <cmd> and return results
    based on rgbeimage.py (Thomas Bleicher 2010) 
    """
    cmd = str(cmd) # get's rid of unicode oddities
    #p = Popen(shlex.split(cmd), bufsize=-1, stdin=PIPE, stdout=data_out, stderr=PIPE)
    p = Popen(cmd, bufsize=-1, stdin=PIPE, stdout=data_out, stderr=PIPE, shell=True) #shell=True required for Linux? quick fix, but may be security concern
    data, err = p.communicate(data_in)
    #if err:
    #    return 'message: '+err.strip()
    #if data:
    #    return data. in Python3 this is returned as `bytes` and needs to be decoded
    if err:
        if data:
            returntuple = (data.decode('latin1'), 'message: '+err.decode('latin1').strip())
        else:
            returntuple = (None, 'message: '+err.decode('latin1').strip())
    else:
        if data:
            returntuple = (data.decode('latin1'),None) #Py3 requires decoding
        else:
            returntuple = (None,None)
    
    return returntuple

def _interactive_load(title=None):
    # Tkinter file picker
    import tkinter
    from tkinter import filedialog
    root = tkinter.Tk()
    root.withdraw() #Start interactive file input
    root.attributes("-topmost", True) #Bring window into foreground
    return filedialog.askopenfilename(parent = root, title = title) #initialdir = data_dir

def _interactive_directory(title=None):
    # Tkinter directory picker.  Now Py3.6 compliant!
    import tkinter
    from tkinter import filedialog
    root = tkinter.Tk()
    root.withdraw() #Start interactive file input
    root.attributes("-topmost", True) #Bring to front
    return filedialog.askdirectory(parent = root, title = title)

        
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
    simulationParamsDict          testfolder, epwfile, simulationname, moduletype, rewritemodule, cellLevelmodule, axisofrotationtorquetube, torqueTube
    simulationControlDict         fixedortracked, cumulativeSky, timestampSimulation, timestampRangeSimulation, hpc, daydateSimulation, singleKeySimulation, singleKeyRangeSimulation
    timeControlParamsDict:        timestampstart, timestampedn, startdate, enddate, singlekeystart, singlekeyend, day_date
    moduleParamsDict:             numpanels, x, y, bifi, xgap, ygap, zgap
    cellLevelModuleParamsDict:    numcellsx, numcellsy, xcell, ycell, xcellgap, ycellgap
    sceneParamsDict:              fixedortracked, gcr, pitch, albedo, nMods, nRows, hub_height, clearanche_height, azimuth_ang, hub_height, axis_Azimuth
    trackingParamsDict:           backtrack, limit_angle, roundTrackerAngle, angle_delta 
    analysisParamsDict:           sensorsy, modWanted, rowWanted
    '''
    
    import inputfile as ibf
    
    simulationParamsDict = {'testfolder': ibf.testfolder, 'epwfile': ibf.epwfile, 'simulationname': ibf.simulationname, 'moduletype': ibf.moduletype,
                            'rewriteModule': ibf.rewriteModule, 'cellLevelModule': ibf.cellLevelModule,
                            'axisofrotationTorqueTube': ibf.axisofrotationTorqueTube, 'torqueTube': ibf.torqueTube}
    
    simulationControlDict = { 'fixedortracked': ibf.fixedortracked, 'cumulativeSky': ibf.cumulativeSky,
                             'timestampSimulation': ibf.timestampSimulation, 'timestampRangeSimulation': ibf.timestampRangeSimulation, 
                             'hpc': ibf.hpc, 'daydateSimulation': ibf.dayDateSimulation, 'singleKeySimulation': ibf.singleKeySimulation, 'singleKeyRangeSimulation': ibf.singleKeyRangeSimulation}
    
    timeControlParamsDict = {'timestampstart': ibf.timestampstart, 'timestampend': ibf.timestampend,
                             'startdate': ibf.startdate, 'enddate': ibf.enddate, 
                             'singlekeystart': ibf.singlekeystart, 'singlekeyend': ibf.singlekeyend, 'day_date':ibf.daydate}
    
    moduleParamsDict = {'numpanels': ibf.numpanels, 'x': ibf.x, 'y': ibf.y, 'bifi': ibf.bifi, 'xgap': ibf.xgap, 
                  'ygap': ibf.ygap, 'zgap': ibf.zgap}
    
    sceneParamsDict = {'gcr': ibf.gcr, 'pitch': ibf.pitch, 'albedo': ibf.albedo, 'nMods':ibf.nMods, 'nRows': ibf.nRows, 'azimuth_ang': ibf.azimuth_ang, 'tilt': ibf.tilt, 'clearance_height': ibf.clearance_height, 'hub_height': ibf.hub_height, 'axis_azimuth': ibf.axis_azimuth}

    trackingParamsDict = {'backtrack': ibf.backtrack, 'limit_angle': ibf.limit_angle, 'roundTrackerAngle': ibf.roundTrackerAngle, 'angle_delta': ibf.angle_delta}    

    torquetubeParamsDict = {'diameter': ibf.diameter, 'tubetype': ibf.tubetype, 'torqueTubeMaterial': ibf.torqueTubeMaterial}
    
    analysisParamsDict = {'sensorsy': ibf.sensorsy, 'modWanted': ibf.modWanted, 'rowWanted': ibf.rowWanted}
    
    cellLevelModuleParamsDict = {'numcellsx': ibf.numcellsx, 'numcellsy': ibf.numcellsy, 'xcell': ibf.xcell, 'ycell': ibf.ycell, 'xcellgap': ibf.xcellgap, 'ycellgap': ibf.ycellgap}
    
    return simulationParamsDict, simulationControlDict, timeControlParamsDict, moduleParamsDict, cellLevelModuleParamsDict, sceneParamsDict, trackingParamsDict, analysisParamsDict


class RadianceObj:
    '''
    RadianceObj:  top level class to work on radiance objects, keep track of filenames, 
    sky values, PV module configuration etc.

    
    values:
        name    : text to append to output files
        filelist    : list of Radiance files to create oconv
        nowstr      : current date/time string
        path        : working directory with Radiance materials and objects
        TODO:  populate this more
    functions:
        __init__   : initialize the object
        _setPath    : change the working directory
        TODO:  populate this more
    
    '''
    
    def __init__(self, name=None, path=None):
        '''
        Description
        -----------
        initialize RadianceObj with path of Radiance materials and objects,
        as well as a basename to append to 
    
        Parameters
        ----------
        name: string, append temporary and output files with this value
        path: location of Radiance materials and objects
    
        Returns
        -------
        none
        '''

        self.metdata = {}        # data from epw met file
        self.data = {}           # data stored at each timestep
        self.path = ""             # path of working directory
        self.name = ""         # basename to append
        #self.filelist = []         # list of files to include in the oconv
        self.materialfiles = []    # material files for oconv
        self.skyfiles = []          # skyfiles for oconv
        self.radfiles = []      # scene rad files for oconv
        self.octfile = []       #octfile name for analysis
        self.Wm2Front = 0       # cumulative tabulation of front W/m2
        self.Wm2Back = 0        # cumulative tabulation of rear W/m2

        now = datetime.datetime.now()
        self.nowstr = str(now.date())+'_'+str(now.hour)+str(now.minute)+str(now.second)
        
        ''' DEFAULTS '''
        #TODO:  check if any of these defaults are necessary
        #self.material_path = "materials"      # directory of materials data. default 'materials'
        #self.sky_path = 'skies'         # directory of sky data. default 'skies'
        #TODO: check if lat/lon/epwfile should be defined in the meteorological object instead
        #self.latitude = 40.02           # default - Boulder
        #self.longitude = -105.25        # default - Boulder
        #self.epwfile = 'USA_CO_Boulder.724699_TMY2.epw'  # default - Boulder
        
        
        if name is None:
            self.name = self.nowstr  # set default filename for output files
        else:
            self.name = name
        self.basename = name # add backwards compatibility for prior versions
        #self.__name__ = self.name  #optional info
        #self.__str__ = self.__name__   #optional info
        if path is None:
            self._setPath(os.getcwd())
        else:
            self._setPath(path)
        
        self.materialfiles = self.returnMaterialFiles('materials')  # load files in the /materials/ directory

    def _setPath(self, path):
        '''
        setPath - move path and working directory
        
        '''
        self.path = path
        
        print('path = '+ path)
        try:
            os.chdir(self.path)
        except WindowsError:
            print('Path doesn''t exist: %s' % (path)) 
        
        # check for path in the new Radiance directory:
        def _checkPath(path):  # create the file structure if it doesn't exist
            if not os.path.exists(path):
                os.makedirs(path)
                print('Making path: '+path)
                
        _checkPath('images'); _checkPath('objects');  _checkPath('results'); _checkPath('skies'); _checkPath('EPWs'); 
        # if materials directory doesn't exist, populate it with ground.rad
        # figure out where pip installed support files. 
        from shutil import copy2 

        if not os.path.exists('materials'):  #copy ground.rad to /materials
            os.makedirs('materials') 
            print('Making path: materials')

            copy2(os.path.join(DATA_PATH,'ground.rad'),'materials')
        # if views directory doesn't exist, create it with two default views - side.vp and front.vp
        if not os.path.exists('views'):
            os.makedirs('views')
            with open(os.path.join('views','side.vp'), 'w') as f:
                f.write('rvu -vtv -vp -10 1.5 3 -vd 1.581 0 -0.519234 -vu 0 0 1 -vh 45 -vv 45 -vo 0 -va 0 -vs 0 -vl 0') 
            with open(os.path.join('views','front.vp'), 'w') as f:
                f.write('rvu -vtv -vp 0 -3 5 -vd 0 0.894427 -0.894427 -vu 0 0 1 -vh 45 -vv 45 -vo 0 -va 0 -vs 0 -vl 0') 

    def getfilelist(self):
        ''' return concat of matfiles, radfiles and skyfiles
        '''
        
        return self.materialfiles + self.skyfiles + self.radfiles
    
    def save(self,savefile=None):
        '''
        Pickle the radiance object for further use. Very basic operation - not much use right now.
        
        Parameters
        ----------
        savefile :   optional savefile.  Otherwise default to save.pickle
                
        '''
        import pickle
        
        if savefile is None:
            savefile = 'save.pickle'
        
        with open(savefile,'wb') as f:
            pickle.dump(self,f)
        print('Saved to file {}'.format(savefile))
    
    def exportTrackerDict(self, trackerdict=None, savefile=None, reindex = None):
        '''
        use bifacial_radiance.load.exportTrackerDict to save a TrackerDict output as a csv file.
        
        Inputs:
            trackerdict:   the tracker dictionary to save
            savefile:      path to .csv save file location
            reindex:       boolean to change 
        
        '''
        import bifacial_radiance.load 
        
        if trackerdict is None:
            trackerdict = self.trackerdict
        
        if savefile is None:
            savefile = _interactive_load(title='Select a .csv file to save to')
            
        if reindex is None:
            if self.cumulativesky is True:
                reindex = False  # don't re-index for cumulativesky, which has angles for index
            else:
                reindex = True
       
        bifacial_radiance.load.exportTrackerDict(trackerdict, savefile, reindex)

        
    def loadtrackerdict(self, trackerdict=None, fileprefix=None):
        '''
        loadtrackerdict(trackerdict=None, fileprefix=None)
        Use bifacial_radiance.load._loadtrackerdict to browse the results directory
        and load back any results saved in there.
        
        '''
        if trackerdict is None:
            trackerdict = self.trackerdict
        (trackerdict, totaldict) = loadTrackerDict(trackerdict, fileprefix)
        self.Wm2Front = totaldict['Wm2Front']
        self.Wm2Back  = totaldict['Wm2Back']
        
    def returnOctFiles(self):
        '''
        return files in the root directory with .oct extension
        
        Returns
        -------
        oct_files : list of .oct files
        
        '''
        oct_files = [f for f in os.listdir(self.path) if f.endswith('.oct')]
        #self.oct_files = oct_files
        return oct_files
        
    def returnMaterialFiles(self, material_path=None):
        '''
        return files in the Materials directory with .rad extension
        appends materials files to the oconv file list
        
        Parameters
        ----------
        material_path - optional parameter to point to a specific materials directory. 
        otherwise /materials/ is default
        
        Returns
        -------
        material_files : list of .rad files
        
        '''
        if material_path is None:
            material_path = 'materials'

        material_files = [f for f in os.listdir(os.path.join(self.path, material_path)) if f.endswith('.rad')]
        
        materialfilelist = [os.path.join(material_path,f) for f in material_files]
        self.materialfiles = materialfilelist
        return materialfilelist
        
    def setGround(self, material=None, material_file=None):
        ''' use GroundObj constructor and return a ground object
        '''
        
        ground_data = GroundObj(material, material_file)
        if material is not None:
            self.ground= ground_data
        else:
            self.ground = None
            
    def getEPW(self,lat,lon):
        ''' 
        Subroutine to download nearest epw files available into the directory \EPWs\
        
        based on github/aahoo
        **note that verify=false is required to operate within NREL's network.
        to avoid annoying warnings, insecurerequestwarning is disabled
        currently this function is not working within NREL's network.  annoying!
        '''
        import numpy as np
        import pandas as pd
        import requests, re
        from requests.packages.urllib3.exceptions import InsecureRequestWarning
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        hdr = {'User-Agent' : "Magic Browser",
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
        
        path_to_save = 'EPWs' # create a directory and write the name of directory here
        if not os.path.exists(path_to_save):
            os.makedirs(path_to_save)
        r = requests.get('https://github.com/NREL/EnergyPlus/raw/develop/weather/master.geojson', verify = False)
        data = r.json() #metadata for available files
        #download lat/lon and url details for each .epw file into a dataframe
        
        df = pd.DataFrame({'url':[],'lat':[],'lon':[],'name':[]})
        for location in data['features']:
            match = re.search(r'href=[\'"]?([^\'" >]+)', location['properties']['epw'])
            if match:
                url = match.group(1)
                name = url[url.rfind('/') + 1:]
                lontemp = location['geometry']['coordinates'][0]
                lattemp = location['geometry']['coordinates'][1]
                dftemp = pd.DataFrame({'url':[url],'lat':[lattemp],'lon':[lontemp],'name':[name]})
                df=df.append(dftemp, ignore_index = True)
  
        #locate the record with the nearest lat/lon
        errorvec = np.sqrt(np.square(df.lat - lat) + np.square(df.lon - lon))
        index = errorvec.idxmin()
        url = df['url'][index]
        name = df['name'][index]
        # download the .epw file to \EPWs\ and return the filename
        print('Getting weather file: ' + name),
        r = requests.get(url,verify = False, headers = hdr)
        if r.ok:
            filename = os.path.join(path_to_save,name)
            # py2 and 3 compatible: binary write, encode text first
            with open(filename, 'wb') as f:
                f.write(r.text.encode('ascii','ignore'))
            print(' ... OK!')
        else:
            print(' connection error status code: %s' %( r.status_code) )
            r.raise_for_status()
        
        self.epwfile = os.path.join('EPWs',name)
        return self.epwfile
    
    def getEPW_all(self):
        ''' 
        Subroutine to download ALL available epw files available into the directory \EPWs\
        
        based on github/aahoo
        **note that verify=false is required to operate within NREL's network.
        to avoid annoying warnings, insecurerequestwarning is disabled
        currently this function is not working within NREL's network.  annoying!
        '''
        import requests, re
        from requests.packages.urllib3.exceptions import InsecureRequestWarning
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
     
        path_to_save = 'EPWs' # create a directory and write the name of directory here
        if not os.path.exists(path_to_save):
            os.makedirs(path_to_save)
        r = requests.get('https://github.com/NREL/EnergyPlus/raw/develop/weather/master.geojson', verify = False)
        data = r.json()
    
        for location in data['features']:
            match = re.search(r'href=[\'"]?([^\'" >]+)', location['properties']['epw'])
            if match:
                url = match.group(1)
                name = url[url.rfind('/') + 1:]
                print( name )
                r = requests.get(url,verify = False)
                if r.ok:
                    filename = os.path.join(path_to_save,name)
                    # py2 and 3 compatible: binary write, encode text first
                    with open(filename, 'wb') as f:
                        f.write(r.text.encode('ascii','ignore')) 
                else:
                    print(' connection error status code: %s' %( r.status_code) )
        print('done!')
    

        
    def readTMY(self,tmyfile=None):
        '''
        use pvlib to read in a tmy3 file.  

        
        Parameters
        ------------
        tmyfile:  filename of tmy3 to be read with pvlib.tmy.readtmy3

        Returns
        -------
        metdata - MetObj collected from TMY3 file
        '''
        import pvlib

        if tmyfile is None:
            try:
                tmyfile = _interactive_load('Select TMY3 climate file')
            except:
                raise Exception('Interactive load failed. Tkinter not supported on this system. Try installing X-Quartz and reloading')

        (tmydata,metadata)=pvlib.tmy.readtmy3(filename = tmyfile)
        # TODO:  replace MetObj _init_ behavior with initTMY behavior
        self.metdata = MetObj(tmydata,metadata)
        #self.metdata = self.metdata.initTMY(tmydata,metadata) # initialize the MetObj using TMY instead of EPW
        csvfile = os.path.join('EPWs','tmy3_temp.csv') #temporary filename with 2-column GHI,DHI data
        #Create new temp csv file for gencumsky. write 8760 2-column csv:  GHI,DHI
        savedata = pd.DataFrame({'GHI':tmydata['GHI'], 'DHI':tmydata['DHI']})  # save in 2-column GHI,DHI format for gencumulativesky -G
        print('Saving file {}, # points: {}'.format(csvfile,savedata.__len__()))
        savedata.to_csv(csvfile,index = False, header = False, sep = ' ', columns = ['GHI','DHI'])
        self.epwfile = csvfile

        return self.metdata    

    def readEPW(self,epwfile=None, hpc=False, daydate=None, startindex=None, endindex=None):
        ''' 
        use readepw from pvlib development forums
        https://github.com/pvlib/pvlib-python/issues/261
        
        rename tmy columns to match: DNI, DHI, GHI, DryBulb, Wspd
        '''
        #from readepw import readepw   # epw file reader from pvlib development forums
        if epwfile is None:
            try:
                epwfile = _interactive_load()
            except:
                raise Exception('Interactive load failed. Tkinter not supported on this system. Try installing X-Quartz and reloading')
        
        if hpc is True and daydate is None:
           print('Error: HPC computing requested, but Daydate is None in readEPW. Exiting.')
           sys.exit()
           
        (tmydata,metadata) = readepw(epwfile)
        # rename different field parameters to match output from pvlib.tmy.readtmy: DNI, DHI, DryBulb, Wspd
        tmydata.rename(columns={'Direct normal radiation in Wh/m2':'DNI','Diffuse horizontal radiation in Wh/m2':'DHI',
                                'Dry bulb temperature in C':'DryBulb','Wind speed in m/s':'Wspd',
                                'Global horizontal radiation in Wh/m2':'GHI'}, inplace=True)
           
        # Daydate will work with or without hpc function. Hpc only works when daydate is passed though.
        if daydate is not None:
            tmydata = tmydata[(tmydata['day']==int(daydate[3:5])) & (tmydata['month']==int(daydate[0:2])) & (tmydata['GHI']>0)]
            print ("restraining Tmydata by daydate")

        if startindex is not None and endindex is not None:
            tmydata = tmydata[startindex:endindex]
            print ("restraining Tmydata by start and endindex")

        if daydate is not None and startindex is not None and endindex is not None:
            print ("TMYdata is restrained by daydate, startindex and endindex at the same time, which might cause issues on data selection. Please use one or the other method.")            

        self.metdata = MetObj(tmydata,metadata)

        # copy the epwfile into the /EPWs/ directory in case it isn't in there already
        if os.path.isabs(epwfile):
            from shutil import copyfile
            dst = os.path.join(self.path,'EPWs',os.path.split(epwfile)[1])
            try:
                copyfile(epwfile,dst) #this may fail if the source and destination are the same
            except:
                pass
            self.epwfile = os.path.join('EPWs',os.path.split(epwfile)[1])
                    
        else:
            self.epwfile = epwfile 
        
        return self.metdata

  
    def gendaylit_old(self, metdata, timeindex):
        '''
        previous method used v0.2.3 and before. 
        Old version runs in 5 seconds rather than 120 seconds for a full year
        
        '''
        if metdata is None:
            print('usage: gendaylit(metdata, timeindex) where metdata is loaded from readEPW() or readTMY(). ' +  
                  'timeindex is an integer from 0 to 8759' )
        locName = metdata.city
        month = metdata.datetime[timeindex].month
        day = metdata.datetime[timeindex].day
        hour = metdata.datetime[timeindex].hour-1  # this needs a -1 hour offset to get gendaylit to provide the correct sun position.
        minute = metdata.datetime[timeindex].minute
        timeZone = metdata.timezone
        dni = metdata.dni[timeindex]
        dhi = metdata.dhi[timeindex]
        
        sky_path = 'skies'

         #" -L %s %s -g %s \n" %(dni/.0079, dhi/.0079, self.ground.ReflAvg) + \
        skyStr =   ("# start of sky definition for daylighting studies\n"  
            "# location name: " + str(locName) + " LAT: " + str(metdata.latitude) 
            +" LON: " + str(metdata.longitude) + "\n"
            "!gendaylit %s %s +%s" %(month,day,hour+minute/60.0) ) + \
            " -a %s -o %s" %(metdata.latitude, metdata.longitude) +\
            " -m %s" % (float(timeZone)*15) +\
            " -W %s %s -g %s -O 1 -i 60 \n" %(dni, dhi, self.ground.ReflAvg) + \
            "skyfunc glow sky_mat\n0\n0\n4 1 1 1 0\n" + \
            "\nsky_mat source sky\n0\n0\n4 0 0 1 180\n" + \
            '\nskyfunc glow ground_glow\n0\n0\n4 ' + \
            '%s ' % (self.ground.Rrefl/self.ground.normval)  + \
            '%s ' % (self.ground.Grefl/self.ground.normval) + \
            '%s 0\n' % (self.ground.Brefl/self.ground.normval) + \
            '\nground_glow source ground\n0\n0\n4 0 0 -1 180\n' +\
            "\nvoid plastic %s\n0\n0\n5 %0.3f %0.3f %0.3f 0 0\n" %(
            self.ground.ground_type,self.ground.Rrefl,self.ground.Grefl,self.ground.Brefl) +\
            "\n%s ring groundplane\n" % (self.ground.ground_type) +\
            '0\n0\n8\n0 0 -.01\n0 0 1\n0 100'
         
        skyname = os.path.join(sky_path,"sky_%s.rad" %(self.name))
            
        skyFile = open(skyname, 'w')
        skyFile.write(skyStr)
        skyFile.close()
        
        self.skyfiles = [skyname ]
        
        return skyname

    def gendaylit(self, metdata, timeindex, debug=False):
        '''
        sets and returns sky information using gendaylit. 
        as of v0.2.4: Uses PVLIB for calculating the sun position angles instead of 
        using Radiance internal sun position calculation (for that use gendaylit function)
        If material type is known, pass it in to get
        reflectance info.  if material type isn't known, material_info.list is returned
        Note - -W and -O1 option is used to create full spectrum analysis in units of Wm-2
        Parameters
        ------------
        metdata:  MetObj object with 8760 list of dni, dhi, ghi and location
        timeindex: index from 0 to 8759 of EPW timestep
        debug:     boolean flag to print output of sky DHI and DNI
        
        Returns
        -------
        skyname:   filename of sky in /skies/ directory. If errors exist, 
                    such as DNI = 0 or sun below horizon, this skyname is None
        
        '''

        if metdata is None:
            print('usage: gendaylit(metdata, timeindex) where metdata is loaded from readEPW() or readTMY(). ' +  
                  'timeindex is an integer from 0 to 8759' )
        locName = metdata.city
        tz = metdata.timezone
        dni = metdata.dni[timeindex]
        dhi = metdata.dhi[timeindex]
        elev=metdata.elevation
        lat=metdata.latitude
        lon=metdata.longitude
        
        if debug is True:
            print('Sky generated with Gendaylit 2, with DNI: %0.1f, DHI: %0.1f' % (dni, dhi))
            print("Datetime TimeIndex", metdata.datetime[timeindex] )
        

        
        #Time conversion to correct format and offset. 
        datetime = metdata.sunrisesetdata['corrected_timestamp'][timeindex]
        #Don't need any of this any more. Already sunrise/sunset corrected and offset by appropriate interval

        # get solar position zenith and azimuth based on site metadata
        #solpos = pvlib.irradiance.solarposition.get_solarposition(datetimetz,lat,lon,elev)
        solpos = metdata.solpos.iloc[timeindex]
        sunalt = float(solpos.elevation)
        sunaz = float(solpos.azimuth)-180.0   # Radiance expects azimuth South = 0, PVlib gives South = 180. Must substract 180 to match.
        
        sky_path = 'skies'

        if sunalt <= 0 or dhi <= 0:
            self.skyfiles = [None]
            return None
            

         #" -L %s %s -g %s \n" %(dni/.0079, dhi/.0079, self.ground.ReflAvg) + \
        skyStr =   ("# start of sky definition for daylighting studies\n"  
            "# location name: " + str(locName) + " LAT: " + str(lat) 
            +" LON: " + str(lon) + " Elev: " + str(elev) + "\n"
            "# Sun position calculated w. PVLib\n" + \
            "!gendaylit -ang %s %s" %(sunalt, sunaz)) + \
            " -W %s %s -g %s -O 1 \n" %(dni, dhi, self.ground.ReflAvg) + \
            "skyfunc glow sky_mat\n0\n0\n4 1 1 1 0\n" + \
            "\nsky_mat source sky\n0\n0\n4 0 0 1 180\n" + \
            '\nskyfunc glow ground_glow\n0\n0\n4 ' + \
            '%s ' % (self.ground.Rrefl/self.ground.normval)  + \
            '%s ' % (self.ground.Grefl/self.ground.normval) + \
            '%s 0\n' % (self.ground.Brefl/self.ground.normval) + \
            '\nground_glow source ground\n0\n0\n4 0 0 -1 180\n' +\
            "\nvoid plastic %s\n0\n0\n5 %0.3f %0.3f %0.3f 0 0\n" %(
            self.ground.ground_type,self.ground.Rrefl,self.ground.Grefl,self.ground.Brefl) +\
            "\n%s ring groundplane\n" % (self.ground.ground_type) +\
            '0\n0\n8\n0 0 -.01\n0 0 1\n0 100'
        
        time = metdata.datetime[timeindex]
        filename = str(time)[5:-12].replace('-','_').replace(' ','_')
            
        skyname = os.path.join(sky_path,"sky2_%s_%s_%s.rad" %(lat, lon, filename))
            
        skyFile = open(skyname, 'w')
        skyFile.write(skyStr)
        skyFile.close()
        
        self.skyfiles = [skyname ]
        
        return skyname

    def gendaylit2manual(self, dni, dhi, sunalt, sunaz):
        '''
        sets and returns sky information using gendaylit.  
        Uses user-provided data for sun position and irradiance. 
        NOTE--> Currently half an hour offset is programed on timestamp, for wheater files.
        if material type is known, pass it in to get
        reflectance info.  if material type isn't known, material_info.list is returned
        Note - -W and -O1 option is used to create full spectrum analysis in units of Wm-2
        Parameters
        ------------
        dni: dni value (int or float)
        dhi: dhi value (int or float)
        sunalt: sun altitude (degrees) (int or float)
        sunaz: sun azimuth (degrees) (int or float)
        
        Returns
        -------
        skyname:   filename of sky in /skies/ directory
        
        '''

        print('Sky generated with Gendaylit 2 MANUAL, with DNI: %0.1f, DHI: %0.1f' % (dni, dhi))
        
        sky_path = 'skies'

        if sunalt <= 0 or dhi <= 0:
            self.skyfiles = [None]
            return None

         #" -L %s %s -g %s \n" %(dni/.0079, dhi/.0079, self.ground.ReflAvg) + \
        skyStr =   ("# start of sky definition for daylighting studies\n"  
            "# Manual inputs of DNI, DHI, SunAlt and SunAZ into Gendaylit used \n" + \
            "!gendaylit -ang %s %s" %(sunalt, sunaz)) + \
            " -W %s %s -g %s -O 1 \n" %(dni, dhi, self.ground.ReflAvg) + \
            "skyfunc glow sky_mat\n0\n0\n4 1 1 1 0\n" + \
            "\nsky_mat source sky\n0\n0\n4 0 0 1 180\n" + \
            '\nskyfunc glow ground_glow\n0\n0\n4 ' + \
            '%s ' % (self.ground.Rrefl/self.ground.normval)  + \
            '%s ' % (self.ground.Grefl/self.ground.normval) + \
            '%s 0\n' % (self.ground.Brefl/self.ground.normval) + \
            '\nground_glow source ground\n0\n0\n4 0 0 -1 180\n' +\
            "\nvoid plastic %s\n0\n0\n5 %0.3f %0.3f %0.3f 0 0\n" %(
            self.ground.ground_type,self.ground.Rrefl,self.ground.Grefl,self.ground.Brefl) +\
            "\n%s ring groundplane\n" % (self.ground.ground_type) +\
            '0\n0\n8\n0 0 -.01\n0 0 1\n0 100'
         
        skyname = os.path.join(sky_path,"sky2_%s.rad" %(self.name))
            
        skyFile = open(skyname, 'w')
        skyFile.write(skyStr)
        skyFile.close()
        
        self.skyfiles = [skyname ]
        
        return skyname
        
    def genCumSky(self,epwfile=None, startdt=None, enddt=None, savefile=None):
        ''' genCumSky
        
        skydome using gencumsky.  note: gencumulativesky.exe is required to be installed,
        which is not a standard radiance distribution.
        You can find the program in the bifacial_radiance distribution directory 
        in \Lib\site-packages\bifacial_radiance\data
        
        TODO:  error checking and auto-install of gencumulativesky.exe  
        
        update 0.0.5:  allow -G filetype option for support of 1-axis tracking
        
        Parameters
        ------------
        epwfile             - filename of the .epw file to read in (-E mode) or 2-column csv (-G mode). 
        hour                - tuple start, end hour of day. default (0,24)
        startdatetime       - datetime.datetime(Y,M,D,H,M,S) object. Only M,D,H selected. default: (0,1,1,0)
        enddatetime         - datetime.datetime(Y,M,D,H,M,S) object. Only M,D,H selected. default: (12,31,24,0)
        savefile            - 
        
        Returns
        -------
        skyname - filename of the .rad file containing cumulativesky info
        '''
        if epwfile is None:
            epwfile = self.epwfile
        if epwfile.endswith('epw'):
            filetype = '-E'  # EPW file input into gencumulativesky
        else:
            filetype = '-G'  # 2-column csv input: GHI,DHI

        if startdt is None:
            startdt = datetime.datetime(2001,1,1,0)
        if enddt is None:
            enddt = datetime.datetime(2001,12,31,23)
        if savefile is None:
            savefile = "cumulative"
        sky_path = 'skies'
        lat = self.metdata.latitude
        lon = self.metdata.longitude
        timeZone = self.metdata.timezone
        '''
        cmd = "gencumulativesky +s1 -h 0 -a %s -o %s -m %s -E " %(lat, lon, float(timeZone)*15) +\
            "-time %s %s -date 6 17 6 17 %s > cumulative.cal" % (epwfile)     
        print cmd
        os.system(cmd)
        '''
        cmd = "gencumulativesky +s1 -h 0 -a %s -o %s -m %s %s " %(lat, lon, float(timeZone)*15, filetype) +\
            "-time %s %s -date %s %s %s %s %s" % (startdt.hour, enddt.hour+1, 
                                                  startdt.month, startdt.day, 
                                                  enddt.month, enddt.day,
                                                  epwfile) 

        with open(savefile+".cal","w") as f:
            data,err = _popen(cmd,None,f)
            if err is not None:
                print( err )

            
        try:
            skyStr = "#Cumulative Sky Definition\n" +\
                "void brightfunc skyfunc\n" + \
                "2 skybright " + "%s.cal\n" % (savefile) + \
                "0\n" + \
                "0\n" + \
                "\nskyfunc glow sky_glow\n" + \
                "0\n" + \
                "0\n" + \
                "4 1 1 1 0\n" + \
                "\nsky_glow source sky\n" + \
                "0\n" + \
                "0\n" + \
                "4 0 0 1 180\n" + \
                '\nskyfunc glow ground_glow\n0\n0\n4 ' + \
                '%s ' % (self.ground.Rrefl/self.ground.normval)  + \
                '%s ' % (self.ground.Grefl/self.ground.normval) + \
                '%s 0\n' % (self.ground.Brefl/self.ground.normval) + \
                '\nground_glow source ground\n0\n0\n4 0 0 -1 180\n' +\
                "\nvoid plastic %s\n0\n0\n5 %0.3f %0.3f %0.3f 0 0\n" %(
                self.ground.ground_type,self.ground.Rrefl,self.ground.Grefl,self.ground.Brefl) +\
                "\n%s ring groundplane\n" % (self.ground.ground_type) +\
                "0\n0\n8\n0 0 -.01\n0 0 1\n0 100" 
        except AttributeError:
            raise Exception('Error: ground reflection not defined.  Run RadianceObj.setGround() first')
        skyname = os.path.join(sky_path,savefile+".rad" )
        
        skyFile = open(skyname, 'w')
        skyFile.write(skyStr)
        skyFile.close()
        
        self.skyfiles = [skyname]#, 'SunFile.rad' ]
        
        return skyname
        
    def set1axis(self, metdata=None, axis_azimuth=180, limit_angle=45, angledelta=5, backtrack=True, gcr=1.0/3.0, cumulativesky=True, roundTrackerAngle=True):
        '''
        RadianceObj set1axis
        set1axis(metdata=None, axis_azimuth=180, limit_angle=45, angledelta=5, backtrack=True, gcr=1.0/3.0, cumulativesky=True, roundTrackerAngle=True):

        Set up geometry for 1-axis tracking.  Pull in tracking angle details from 
        pvlib, create multiple 8760 metdata sub-files where datetime of met data 
        matches the tracking angle.  Returns 'trackerdict' which has keys equal to 
        either the tracker angles (gencumsky workflow) or timestamps (gendaylit hourly
        workflow)
        
        
        Parameters
        ------------
        cumulativesky       # [True] boolean. whether individual csv files are created with constant tilt angle for the cumulativesky approach.
                            # if false, the gendaylit tracking approach must be used.
        metdata             # MetObj to set up geometry.  default = self.metdata
        axis_azimuth        # [180] orientation axis of tracker torque tube. Default North-South (180 deg)
        limit_angle         # [45] +/- limit angle of the 1-axis tracker in degrees. Default 45 
        backtrack           # [True] Whether backtracking is enabled (default = True)
        gcr                 # [1.0/3.0] Ground coverage ratio for calculation backtracking. 
        angledelta          # [5] degree of rotation increment to parse irradiance bins
                             (0.4 % error for DNI).  Other options: 4 (.25%), 2.5 (0.1%).  
                             Note: the smaller the angledelta, the more simulations must be run
        roundTrackerAngle   # [True] activates the rounding to angledelta. When doing gendaylit1axis 
                            setting this to False will generate more geometries but the number of runs
                            will stay the same.
        Returns
        -------
        trackerdict      dictionary with keys for tracker tilt angles (gencumsky) or timestamps (gendaylit)
                         and list of csv metfile, and datetimes at that angle
                         trackerdict[angle]['csvfile';'surf_azm';'surf_tilt';'UTCtime']
                         - or -
                         trackerdict[time]['tracker_theta';'surf_azm';'surf_tilt']
                         
        Internal variables
        -------
        metdata.solpos          dataframe with solar position data
        metdata.surface_azimuth list of tracker azimuth data
        metdata.surface_tilt    list of tracker surface tilt data
        metdata.tracker_theta   list of tracker tilt angle
        '''
        
        if metdata == None:
            metdata = self.metdata
        
        if metdata == {}:
            raise Exception("metdata doesnt exist yet.  Run RadianceObj.readEPW() or .readTMY().")
        

        #backtrack = True   # include backtracking support in later version
        #gcr = 1.0/3.0       # default value - not used if backtrack = False.

        
        # get 1-axis tracker angles for this location, rounded to nearest 'angledelta'
        trackerdict = metdata.set1axis(cumulativesky = cumulativesky, axis_azimuth = axis_azimuth, limit_angle = limit_angle, angledelta = angledelta, backtrack = backtrack, gcr = gcr, roundTrackerAngle=roundTrackerAngle)
        self.trackerdict = trackerdict
        self.cumulativesky = cumulativesky
        
        return trackerdict
    
    def gendaylit1axis(self, metdata=None, trackerdict=None, startdate=None, enddate=None, debug=False, hpc=False):
        '''
        1-axis tracking implementation of gendaylit.
        Creates multiple sky files, one for each time of day.
        
        Parameters
        ------------
        metdata:   output from readEPW or readTMY.  Needs to have metdata.set1axis() run on it.
        startdate:  starting point for hourly data run. Optional parameter string 'MM/DD' or 'MM_DD' format 
        enddate:    ending date for hourly data run. Optional parameter string 'MM/DD' or 'MM_DD' format
        trackerdict      dictionary with keys for tracker tilt angles (gencumsky) or timestamps (gendaylit)
            
        Returns: 
        -------
        trackerdict      dictionary with keys for tracker tilt angles (gencumsky) or timestamps (gendaylit)
                        here the additional dictionary value ['skyfile'] is added
    
        '''
        import dateutil.parser as parser # used to convert startdate and enddate
        
        
        if metdata is None:
            metdata = self.metdata
        if trackerdict is None:
            try:
                trackerdict = self.trackerdict
            except:
                print('No trackerdict value passed or available in self')

        try:
            metdata.tracker_theta  # this may not exist
        except:
            print("metdata.tracker_theta doesn't exist. Run metdata.set1axis() first")
        
        # look at start and end date if they're passed.  Otherwise don't worry about it.
        if startdate is not None:
            startdate=startdate.replace('_','/') # making sure it is in 'MM/DD' format.
            datetemp = parser.parse(startdate)
            startindex = (int(datetemp.strftime('%j')) - 1) * 24 -1
        else:
            startindex = 0
        if enddate is not None:
            enddate=enddate.replace('_','/') # making sure it is in 'MM/DD' format.
            datetemp = parser.parse(enddate)
            endindex = (int(datetemp.strftime('%j')) ) * 24   # include all of enddate
        else:
            endindex = 8760            
        
        if hpc is True:
            startindex = 0
            endindex = len(metdata.datetime)

        if debug is False:
            print('Creating ~4000 skyfiles.  Takes 1-2 minutes')
        count = 0  # counter to get number of skyfiles created, just for giggles
        
        trackerdict2={}
        for i in range(startindex,endindex):
            time = metdata.datetime[i]
            filename = str(time)[5:-12].replace('-','_').replace(' ','_')
            self.name = filename

            #check for GHI > 0
            if metdata.ghi[i] > 0:
                skyfile = self.gendaylit(metdata,i, debug=debug)     
                trackerdict2[filename] = trackerdict[filename]  # trackerdict2 helps reduce the trackerdict to only the range specified.
                trackerdict2[filename]['skyfile'] = skyfile
                count +=1
        
        print('Created {} skyfiles in /skies/'.format(count))
        return trackerdict2
        
    def genCumSky1axis(self, trackerdict=None, startdt=None, enddt=None):
        '''
        1-axis tracking implementation of gencumulativesky.
        Creates multiple .cal files and .rad files, one for each tracker angle.
        
        Parameters
        ------------
        trackerdict:   output from MetObj.set1axis()
        startdatetime:  datetime.datetime(Y,M,D,H,M,S) object. Only M,D,H selected. default: (0,1,1,0)
        enddatetime:    datetime.datetime(Y,M,D,H,M,S) object. Only M,D,H selected. default: (12,31,24,0)

            
        Returns: 
        -------
        trackerdict:   append 'skyfile'  to the 1-axis dict with the location of the sky .radfile

        '''
        if trackerdict == None:
            try:
                trackerdict = self.trackerdict
            except:
                print('No trackerdict value passed or available in self')
        
        for theta in trackerdict:
            # call gencumulativesky with a new .cal and .rad name
            csvfile = trackerdict[theta]['csvfile']
            savefile = '1axis_%s'%(theta)  #prefix for .cal file and skies\*.rad file
            skyfile = self.genCumSky(epwfile = csvfile, startdt=startdt, enddt=enddt, savefile = savefile)
            trackerdict[theta]['skyfile'] = skyfile
            print('Created skyfile %s'%(skyfile))
        # delete default skyfile (not strictly necessary)
        self.skyfiles = None
        self.trackerdict = trackerdict
        return trackerdict
        
        
    def makeOct(self, filelist=None, octname=None, hpc=False):
        ''' 
        combine everything together into a .oct file
        
        Parameters
        ------------
        filelist:  overload files to include.  otherwise takes self.filelist
        octname:   filename (without .oct extension)
        hpc:        boolean, default False. Activates a wait period in case one of the files for
                    making the oct is still missing.
        
        Returns: Tuple
        -------
        octname:   filename of .oct file in root directory including extension
        err:        Error message returned from oconv (if any)
        '''
        if filelist is None:
            filelist = self.getfilelist()
        if octname is None:
            octname = self.name
        
        debug=False
        #JSS. With the way that the break is handled now, this will wait the 10 for all the hours 
        # that were not generated sky files.
        if hpc is True:
            import time
            time_to_wait = 10
            time_counter = 0
            for file in filelist:
                if debug:  
                    print("HPC Checking for file %s" % (file))
                if None in filelist:  # are we missing any files? abort!
                    print('Missing files, skipping...')
                    self.octfile = None
                    return None
                while not os.path.exists(file): #Filesky is being saved as 'none', so it crashes ! 
                  time.sleep(1)
                  time_counter += 1
                  if time_counter > time_to_wait:
                      print ("filenotfound")
                      break
         
        #os.system('oconv '+ ' '.join(filelist) + ' > %s.oct' % (octname))
        if None in filelist:  # are we missing any files? abort!
            print('Missing files, skipping...')
            self.octfile = None
            return None
        
        cmd = 'oconv ' + ' '.join(filelist)
        with open('%s.oct' % (octname),"w") as f:
            data,err = _popen(cmd,None,f)
            #TODO:  exception handling for no sun up
            if err is not None:
                if err[0:5] == 'error':
                    raise Exception(err[7:])
        
        #use rvu to see if everything looks good. use cmd for this since it locks out the terminal.
        #'rvu -vf views\side.vp -e .01 monopanel_test.oct'
        print("Created %s.oct" % (octname))
        self.octfile = '%s.oct' % (octname)
        return '%s.oct' % (octname)
        
    def makeOct1axis(self, trackerdict=None, singleindex=None, customname=None, hpc=False):
        ''' 
        combine files listed in trackerdict into multiple .oct files
        
        Parameters
        ------------
        trackerdict:    Output from makeScene1axis
        singleindex:   Single index for trackerdict to run makeOct1axis in single-value mode (new in 0.2.3)
        customname:     Custom text string added to the end of the OCT file name.
        hpc:        boolean, default False. Activates a wait period in case one of the files for
                    making the oct is still missing.
                    
        Returns: 
        -------
        trackerdict:  append 'octfile'  to the 1-axis dict with the location of the scene .octfile
        '''
        
        if customname is None:
            customname = ''
        
        if trackerdict is None:
            try:
                trackerdict = self.trackerdict
            except:
                print('No trackerdict value passed or available in self')
        if singleindex is None:   # loop through all values in the tracker dictionary
            indexlist = trackerdict.keys()
        else:  # just loop through one single index in tracker dictionary
            indexlist = [singleindex]
        
        print('\nMaking {} octfiles for 1-axis tracking in root directory.'.format(indexlist.__len__()))
        for index in indexlist:  # run through either entire key list of trackerdict, or just a single value
            try:
                filelist = self.materialfiles + [trackerdict[index]['skyfile'] , trackerdict[index]['radfile']]
                octname = '1axis_%s%s'%(index,customname)
                trackerdict[index]['octfile'] = self.makeOct(filelist,octname, hpc)
            except KeyError as e:                  
                print('Trackerdict key error: {}'.format(e))
        
        return trackerdict


    def makeModule(self,name=None,x=1,y=1,bifi=1,  modulefile=None, text=None, customtext='', 
               torquetube=False, diameter=0.1, tubetype='Round', material='Metal_Grey', xgap=0.01, ygap=0.0, zgap=0.1, numpanels=1, rewriteModulefile=True, 
                   tubeZgap=None, panelgap=None, orientation=None,
                  cellLevelModule=False, numcellsx=6, numcellsy=10, xcell=0.156, ycell=0.156, xcellgap=0.02, ycellgap=0.02, axisofrotationTorqueTube=False):
        '''
        Add module details to the .JSON module config file module.json
        This needs to be in the RadianceObj class because this is defined before a SceneObj is.
        The default orientation of the module .rad file is a portrait oriented module, origin at (x/2,0,0) i.e. 
        center of module along x, at the bottom edge.
        
        Version 0.2.4: - remove portrait or landscape `orientation`. 
            - Now define a module by x (dimension along rack) and y (dimension in slant direction)
            - Rename gap variables to be xgap, ygap and zgap
            - Introduce scenex and sceney which include torque tube and gap dimensions
        Version 0.2.3: add the ability to have torque tubes and module gaps.
        
        TODO: add transparency parameter, make modules with non-zero opacity
        
        Parameters
        ------------
        name: string input to name the module type
        
        module configuration dictionary inputs:
        x       # width of module along the axis of the torque tube or racking structure. (meters).
        y       # length of module (meters).
        bifi    # bifaciality of the panel (not currently used)
        modulefile   # existing radfile location in \objects.  Otherwise a default value is used
        text = ''    # text used in the radfile to generate the module
        customtext = ''    # added-text used in the radfile to generate any extra details in the racking/module. Does not overwrite generated module (unlike "text"), but adds to it at the end.
        rewriteModulefile # boolean, set to True. Will rewrite module file each time makeModule is run.
        
        New inputs as of 0.2.3 for torque tube and gap spacing:
        torquetube    #boolean. Is torque tube present or no?
        diameter      #float.  tube diameter in meters. For square,
                        For Square, diameter means the length of one of the square-tube side.
                        For Hex, diameter is the distance between two vertices (diameter of the circumscribing circle)
        tubetype      #'Square', 'Round' (default), 'Hex' or 'Oct'.  tube cross section
        material      #'Metal_Grey' or 'black'. Material for the torque tube.        
        numpanels     #int. number of modules arrayed in the Y-direction. e.g. 1-up or 2-up, etc. (supports any number for carport/Mesa simulations)
        xgap          #float. "Panel space in X". Separation between modules in a row. 
                      #DEPRECATED INPUTS: 
        ygap          #float. gap between modules arrayed in the Y-direction if any.
        zgap          # distance behind the modules in the z-direction to the edge of the tube (m)
        tubeZgap      #float. zgap. deprecated, use zgap instead. 
        panelgap      #float. ygap. deprecated, use ygap instead.
        axisofrotationTorqueTube # boolean. Default False. IF true, creates geometry 
                so center of rotation is at the center of the torquetube, not the modules. If false,
                axis of rotation coincides with the center point of the modules.
        
        New inputs as of 0.2.4 for creating custom cell-level module:
        cellLevelModule    #boolean. set it to True for creating cell-level modules
        numcellsx    #int. number of cells in the X-direction within the module
        numcellsy    #int. number of cells in the Y-direction within the module
        xcell    #float. width of each cell (X-direction) in the module 
        ycell    #float. length of each cell (Y-direction) in the module 
        xcellgap    #spacing between cells in the X-direction
        ycellgap    #spacing between cells in the Y-direction
        
        Returns: None
        -------
        
        '''
        if name is None:
            print("usage:  makeModule(name,x,y, bifi = 1, modulefile = '\objects\*.rad', "+
                    "torquetube=False, diameter = 0.1 (torque tube dia.), tubetype = 'Round' (or 'square', 'hex'), material = 'Metal_Grey' (or 'black'), zgap = 0.1 (module offset)"+
                    "numpanels = 1 (# of panels in portrait), ygap = 0.05 (slope distance between panels when arrayed), rewriteModulefile = True (or False)"+ 
                   "cellLevelModule=False (create cell-level module), numcellsx=6 (#cells in X-dir.), numcellsy=10 (#cells in Y-dir.), xcell=0.156 (cell size in X-dir.), ycell=0.156 (cell size in Y-dir.)"+
                    "xcellgap=0.02 (spacing between cells in X-dir.), ycellgap=0.02 (spacing between cells in Y-dir.))")
            print ("You can also override module_type info by passing 'text' variable, or add on at the end for racking details with 'customtext'. See function definition for more details")

            return
        
        if tubeZgap :
            print('Warning: tubeZgap deprecated. Replace with zgap')
            zgap = tubeZgap
        if panelgap :
            print('Warning: panelgap deprecated. Replace with ygap')
            ygap = panelgap

        import json
        if modulefile is None:
            #replace whitespace with underlines. what about \n and other weird characters?
            name2 = str(name).strip().replace(' ', '_')
            modulefile = os.path.join('objects', name2 + '.rad')
            print("\nModule Name:", name2)

        if rewriteModulefile is True:
            if os.path.isfile(modulefile):
                print('REWRITING pre-existing module file. ')
                os.remove(modulefile)
            else:
                print ('Module file did not exist before, creating new module file')
        
        if orientation is not None:
            print ('\n\n WARNING: Orientation format has been deprecated since version 0.2.4. If you want to flip your modules, on makeModule switch the x and y values. X value is the size of the panel along the row, so for a "landscape" panel x should be > than y.\n\n')
            
        #aliases for equations below
        diam = diameter
        Ny = numpanels 
        cc = 0
        import math
        
        # Defaults for rotating system around module
        modoffset=0      # Module Offset 
        
        # Update values for rotating system around torque tube.
        if axisofrotationTorqueTube == True:
            modoffset = zgap + diam/2.0
            tto = 0

        if text is None:
            
            if cellLevelModule is False:
                text = '! genbox black PVmodule {} {} 0.02 | xform -t {} {} {} '.format(x, y, -x/2.0, (-y*Ny/2.0)-(ygap*(Ny-1)/2.0), modoffset)
                text += '-a {} -t 0 {} 0'.format(Ny,y+ygap)
                packagingfactor = 100.0
                
            else:
                x = numcellsx*xcell + (numcellsx-1)*xcellgap
                y = numcellsy*ycell + (numcellsy-1)*ycellgap
                
                #center cell - 
                if numcellsx % 2 == 0:
                    cc = xcell/2.0
                    print ("Module was shifted by {} in X to avoid sensors on air".format(cc))
                    
                text = '! genbox black cellPVmodule {} {} 0.02 | xform -t {} {} {} -a {} -t {} 0 0 -a {} -t 0 {} 0 '.format(xcell, ycell, -x/2.0+cc, (-y*Ny/2.0)-(ygap*(Ny-1)/2.0), modoffset, numcellsx, xcell + xcellgap, numcellsy, ycell + ycellgap)
                text += '-a {} -t 0 {} 0'.format(Ny,y+ygap)

                # OPACITY CALCULATION
                packagingfactor = round((xcell*ycell*numcellsx*numcellsy)/(x*y),2)
                print("This is a Cell-Level detailed module with Packaging Factor of {} %".format(packagingfactor))
                
            if torquetube is True:
                if tubetype.lower() =='square':
                    if axisofrotationTorqueTube == False:
                        tto = -zgap-diam/2.0
                    text = text+'\r\n! genbox {} tube1 {} {} {} | xform -t {} {} {}'.format(material, x+xgap, diam, diam, -(x+xgap)/2.0+cc, -diam/2.0, -diam/2.0+tto)  

                elif tubetype.lower()=='round':
                    if axisofrotationTorqueTube == False:
                        tto = -zgap-diam/2.0
                    text = text+'\r\n! genrev {} tube1 t*{} {} 32 | xform -ry 90 -t {} {} {}'.format(material, x+xgap, diam/2.0,  -(x+xgap)/2.0+cc, 0, tto)
     
                elif tubetype.lower()=='hex':
                    radius = 0.5*diam
                    
                    if axisofrotationTorqueTube == False:
                        tto = -radius*math.sqrt(3.0)/2.0-zgap
                    
                    text = text+'\r\n! genbox {} hextube1a {} {} {} | xform -t {} {} {}'.format(
                            material, x+xgap, radius, radius*math.sqrt(3), -(x+xgap)/2.0+cc, -radius/2.0, -radius*math.sqrt(3.0)/2.0+tto) #ztran -radius*math.sqrt(3.0)-tto
                    

                    # Create, translate to center, rotate, translate back to prev. position and translate to overal module position.
                    text = text+'\r\n! genbox {} hextube1b {} {} {} | xform -t {} {} {} -rx 60 -t 0 0 {}'.format(
                            material, x+xgap, radius, radius*math.sqrt(3), -(x+xgap)/2.0+cc, -radius/2.0, -radius*math.sqrt(3.0)/2.0, tto) #ztran (radius*math.sqrt(3.0)/2.0)-radius*math.sqrt(3.0)-tto)
                    
                    text = text+'\r\n! genbox {} hextube1c {} {} {} | xform -t {} {} {} -rx -60 -t 0 0 {}'.format(
                            material, x+xgap, radius, radius*math.sqrt(3), -(x+xgap)/2.0+cc, -radius/2.0, -radius*math.sqrt(3.0)/2.0, tto) #ztran (radius*math.sqrt(3.0)/2.0)-radius*math.sqrt(3.0)-tto)

                elif tubetype.lower()=='oct':
                    radius = 0.5*diam   
                    s = diam / (1+math.sqrt(2.0))   # s
                    
                    if axisofrotationTorqueTube == False:
                        tto = -radius-zgap
                    
                    text = text+'\r\n! genbox {} octtube1a {} {} {} | xform -t {} {} {}'.format(
                            material, x+xgap, s, diam, -(x+xgap)/2.0, -s/2.0, -radius+tto)

                    # Create, translate to center, rotate, translate back to prev. position and translate to overal module position.
                    text = text+'\r\n! genbox {} octtube1b {} {} {} | xform -t {} {} {} -rx 45 -t 0 0 {}'.format(
                            material, x+xgap, s, diam, -(x+xgap)/2.0+cc, -s/2.0, -radius, tto)
                    
                    text = text+'\r\n! genbox {} octtube1c {} {} {} | xform -t {} {} {} -rx 90 -t 0 0 {}'.format(
                            material, x+xgap, s, diam, -(x+xgap)/2.0+cc, -s/2.0, -radius, tto)
                    
                    text = text+'\r\n! genbox {} octtube1d {} {} {} | xform -t {} {} {} -rx 135 -t 0 0 {} '.format(
                            material, x+xgap, s, diam, -(x+xgap)/2.0+cc, -s/2.0, -radius, tto)

                    
                else:
                    raise Exception("Incorrect torque tube type.  Available options: 'square' or 'round'.  Value entered: {}".format(tubetype))
            
            text += customtext  # For adding any other racking details at the module level that the user might want.

            
        moduleDict = {'x':x,
                      'y':y,
                      'scenex': x+xgap,
                      'sceney': y*Ny + ygap*(Ny-1),
                      'scenez': zgap+diam/2.0,
                      'numpanels':Ny,
                      'bifi':bifi,
                      'text':text,
                      'modulefile':modulefile,
                      'moduleoffset': modoffset
                      }
        
        filedir = os.path.join(DATA_PATH,'module.json')  # look in global DATA_PATH for module config file
        with open( filedir ) as configfile:
            data = json.load(configfile)    

        
        data.update({name:moduleDict})    
        with open(os.path.join(DATA_PATH,'module.json') ,'w') as configfile:
            json.dump(data,configfile)
        
        print('Module {} successfully created'.format(name))
        
        self.moduleDict = moduleDict

        return moduleDict


    def makeCustomObject(self,name=None, text=None):
        '''
        Function for development and experimenting with extraneous objects in the scene.
        This function creates a name.rad textfile in the objects folder
        with whatever text that is passed to it.
        It is up to the user to pass the correct radiance format.
        For example, to create a box at coordinates 0,0 (with its bottom surface 
        on the plane z=0),
        name = 'box'
        text='! genbox black PVmodule 0.5 0.5 0.5 | xform -t -0.25 -0.25 0'
        
        Parameters
        ------------
        name: string input to name the module type
        text = ''    # text used in the radfile to generate the module
        '''
        
        customradfile = os.path.join('objects','%s.rad'%(name) ) # update in 0.2.3 to shorten radnames
        # py2 and 3 compatible: binary write, encode text first
        with open(customradfile, 'wb') as f:
            f.write(text.encode('ascii'))
            
        print("\nCustom Object Name", customradfile)
        self.customradfile = customradfile
        return customradfile

        
    def printModules(self):
        # print available module types by creating a dummy SceneObj
        temp = SceneObj('simple_panel')
        modulenames = temp.readModule()
        print('Available module names: {}'.format([str(x) for x in modulenames]))

    def makeScene(self, moduletype=None, sceneDict=None, hpc=False):
        '''
        return a SceneObj which contains details of the PV system configuration including 
        tilt, row pitch, height, nMods per row, nRows in the system...
        
        Parameters
        ------------
        moduletype: string name of module created with makeModule()
        sceneDict:  dictionary with keys:[tilt] [clearance_height]* [pitch] [azimuth] [nMods] [nRows] [hub_height]* [height]*                    
                    *height deprecated from sceneDict. For makeScene (fixed systems)
                    if passed it is assumed it reffers to clearance_height.
                    clearance_height recommended for fixed_tracking systems.
                    hub_height can also be passed as a possibility.
        hpc:        boolean, default False. For makeScene, it adds the full path
                    of the objects folder where the module . rad file is saved.

        Returns: SceneObj 'scene' with configuration details
        -------
        '''
        if moduletype is None:
            print('makeScene(moduletype, sceneDict, nMods, nRows).  Available moduletypes: monopanel, simple_panel' ) #TODO: read in config file to identify available module types
            return
        self.scene = SceneObj(moduletype)
        
        if sceneDict is None:
            print('makeScene(moduletype, sceneDict, nMods, nRows).  sceneDict inputs: .tilt .clearance_height .pitch .azimuth')

        if 'orientation' in sceneDict:
            if sceneDict['orientation'] == 'landscape':
                raise Exception('\n\n ERROR: Orientation format has been deprecated since version 0.2.4. If you want to flip your modules, on makeModule switch the x and y values. X value is the size of the panel along the row, so for a "landscape" panel x should be > than y.\n\n')
        #if sceneDict.has_key('azimuth') is False:
        if 'azimuth' not in sceneDict:
            sceneDict['azimuth'] = 180
            
        if 'nRows' not in sceneDict:
            sceneDict['nRows'] = 7
        
        if 'nMods' not in sceneDict:
            sceneDict['nMods'] = 20
            
        # checking for deprecated height, and for clearance_height or hub_height.
        # since MakeScene is a fixed tilt routine, we will use clearance_height as the main
        # input for this and ignore hub_height if it s passed to.
        # If only height is passed, it is assumed to be clearance_height.
        if 'height' in sceneDict:
            if 'clearance_height' in sceneDict:
                if 'hub_height' in sceneDict:
                     print("sceneDict warning: Passed 'clearance_height', 'hub_height', and 'height' into makeScene. For makeScene fixed tilt routine, using 'clearance_height' and removing 'hub_height' and 'height' (deprecated) from sceneDict")
                     del sceneDict['height']
                     del sceneDict['hub_height']
                else:
                    print("sceneDict warning: Passed 'height' and 'clearance_height'. Using 'clearance_height' and deprecating 'height'")
                    del sceneDict['height']
            else:
                if 'hub_height' in sceneDict:
                    print("sceneDict Issue: Passed 'hub_height' and 'height' into makeScene. Using 'hub_height' and removing 'height' from sceneDict.")
                    del sceneDict['height']
                else:
                    print("sceneDict Error: Passed 'height' to makeScene(). We are assuming this is 'clearance_height'. Renaming and deprecating height.")
                    sceneDict['clearance_height']=sceneDict['height']
                    del sceneDict['height']
        else:
            if 'clearance_height' in sceneDict:
                if 'hub_height' in sceneDict:
                     print("sceneDict Error: Passed 'clearance_height' and 'hub_height' into makeScene. For this fixed tilt routine, using 'clearance_height' and removing 'hub_height' from sceneDict")
                     del sceneDict['hub_height']
            else:
                if 'hub_height' not in sceneDict:
                    print("ERROR: Issue with sceneDict. No 'clearance_height', 'hub_height' nor 'height' (deprecated) passed")
                    return

        self.nMods = sceneDict['nMods']
        self.nRows = sceneDict['nRows']
        self.sceneRAD = self.scene.makeSceneNxR(moduletype=moduletype, sceneDict=sceneDict, hpc=hpc)
        self.radfiles = [self.sceneRAD]
        
        return self.scene
    
    def appendtoScene(self, radfile=None, customObject=None, text=''):
        '''
        demo.addtoScene(scene.radfile, customObject, text='')
        Appends to the Scene radfile in \\objects the text command in Radiance lingo
        created by the user.
        Useful when using addCustomObject to the scene.
        
        TO DO: Add a custom name and replace radfile name 
        
        Parameters:
        ----------------
        'radfile': directory and name of where .rad scene file is stored
        customObject: directory and name of custom object .rad file is stored
        text: command to be appended to the radfile. Do not leave empty spaces at the end.

        Returns:
        ----------------
        Nothing, the radfile must already be created and assigned when running this.
        
        '''
        
        # py2 and 3 compatible: binary write, encode text first
        text2 = '\n' + text + ' ' + customObject
        
        with open(radfile, 'a+') as f:
            f.write(text2.encode('ascii'))
    
    def makeScene1axis(self, trackerdict=None, moduletype=None, sceneDict=None, cumulativesky=None, nMods=None, nRows=None, hpc=False):
        '''
        create a SceneObj for each tracking angle which contains details of the PV 
        system configuration including row pitch, hub_height, nMods per row, nRows in the system...
        
        Parameters
        ------------
        trackerdict: output from GenCumSky1axis
        moduletype: string name of module created with makeModule()
        sceneDict:  dictionary with keys:[tilt] [hub_height] [pitch] [azimuth]
        cumulativesky:  bool: use cumulativesky or not?
        nMods:      deprecated. int number of modules per row (default = 20). If included it will be 
                    assigned to the sceneDict
        nRows:      deprecated. int number of rows in system (default = 7). If included it will be 
                    assigned to the sceneDict
        hpc:        boolean, default False. For makeScene, it adds the full path
                    of the objects folder where the module . rad file is saved.
        
        Returns
        -----------
        trackerdict: append the following keys :
            'radfile': directory where .rad scene file is stored
            'scene' : SceneObj for each tracker theta
            'clearance_height' : calculated ground clearance based on hub height, tilt angle and module length
        '''
        import math
        
        if sceneDict is None:
            print('usage:  makeScene1axis(moduletype, sceneDict, nMods, nRows).  sceneDict inputs: .tilt .hub_height .pitch .azimuth')
            return

        # Check for deprecated variables and assign to dictionary.
        if nMods is not None or nRows is not None:
            print("nMods and nRows input is being deprecated. Please include nMods and nRows inside of your sceneDict definition")
            print("Meanwhile, this funciton will check if SceneDict has nMods and nRows and will use that as values, and if not, it will assign nMods and nRows to it.")
            
            if sceneDict['nMods'] is None:
                sceneDict['nMods'] = nMods

            if sceneDict['nRows'] is None:
                sceneDict['nRows'] = nRows
        
        # If no nRows or nMods assigned on deprecated variable or dictionary, 
        # assign default.
        if 'nRows' not in sceneDict:
            sceneDict['nRows'] = 7
        if 'nMods' not in sceneDict:
            sceneDict['nMods'] = 20

        if trackerdict is None:
            try:
                trackerdict = self.trackerdict
            except:
                print('No trackerdict value passed or available in self')

        if cumulativesky is None:
            try:
                cumulativesky = self.cumulativesky  # see if cumulativesky = False was set earlier, e.g. in RadianceObj.set1axis
            except:
                cumulativesky = True   # default cumulativesky = true to maintain backward compatibility.
                
        if moduletype is None:
            print('usage:  makeScene1axis(trackerdict, moduletype, sceneDict, nMods, nRows). ' ) 
            self.printModules() #print available module types
            return
        

        if 'orientation' in sceneDict:
            if sceneDict['orientation'] == 'landscape':
                raise Exception('\n\n ERROR: Orientation format has been deprecated since version 0.2.4. If you want to flip your modules, on makeModule switch the x and y values. X value is the size of the panel along the row, so for a "landscape" panel x should be > than y.\n\n')

        if 'hub_height' in sceneDict:
            if 'height' in sceneDict:
                if 'clearance_height' in sceneDict:
                    print("sceneDict warning: 'hub_height', 'clearance_height', and 'height' are being passed. Removing 'height' (deprecated) and 'clearance_height' from sceneDict for this tracking routine")
                    del sceneDict['clearance_height']
                    del sceneDict['height']
                else:
                    print("sceneDict warning: 'height' is being deprecated. Using 'hub_height'")                            
                    del sceneDict['height']
            else:
                if 'clearance_height' in sceneDict:
                    print("sceneDict warning: 'hub_height' and 'clearance_height' are being passed. Using 'hub_height' for tracking routine and removing 'clearance_height' from sceneDict")
                    del sceneDict['clearance_height']
        else: # if no hub_height is passed
            if 'height' in sceneDict:
                if 'clearance_height' in sceneDict:
                    print("sceneDict Issue: 'clearance_height and 'height' (deprecated) are being passed. Renaming 'height' as 'hub_height' and removing 'clearance_height' from sceneDict for this tracking routine")
                    sceneDict['hub_height']=sceneDict['height']
                    del sceneDict['clearance_height']
                    del sceneDict['height']
                else:
                    print("sceneDict warning: 'height' is being deprecated. Renaming as 'hub_height'")                            
                    sceneDict['hub_height']=sceneDict['height']
                    del sceneDict['height']
            else: # If no hub_height nor height is passed
                if 'clearance_height' in sceneDict:
                    print("sceneDict warning: Passing 'clearance_height' to a tracking routine. Assuming this is really 'hub_height' and renaming.")
                    sceneDict['hub_height']=sceneDict['clearance_height']
                    del sceneDict['clearance_height']
                else:
                    print ("sceneDict Error! no argument in sceneDict found for 'hub_height', 'height' nor 'clearance_height'. Exiting routine.")
                    return

        #the hub height is the tracker height at center of rotation.
        hubheight = sceneDict['hub_height']

        if cumulativesky is True:        # cumulativesky workflow
            print('\nMaking .rad files for cumulativesky 1-axis workflow')
            for theta in trackerdict:
                scene = SceneObj(moduletype)

                if trackerdict[theta]['surf_azm'] >= 180:
                    trackerdict[theta]['surf_azm'] = trackerdict[theta]['surf_azm']-180
                    trackerdict[theta]['surf_tilt'] = trackerdict[theta]['surf_tilt']*-1
                radname = '1axis%s'%(theta,)
                
                # Calculating clearance height for this theta.
                height = hubheight - 0.5* math.sin(abs(theta) * math.pi / 180) *  scene.sceney + scene.moduleoffset*math.sin(abs(theta)*math.pi/180) 
                # Calculate the ground clearance height based on the hub height. Add abs(theta) to avoid negative tilt angle errors
                trackerdict[theta]['clearance_height'] = height
                
                try:
                    sceneDict2 = {'tilt':trackerdict[theta]['surf_tilt'],'pitch':sceneDict['pitch'],'clearance_height':trackerdict[theta]['clearance_height'],'azimuth':trackerdict[theta]['surf_azm'], 'nMods': sceneDict['nMods'], 'nRows': sceneDict['nRows']}  
                except: #maybe gcr is passed, not pitch
                    sceneDict2 = {'tilt':trackerdict[theta]['surf_tilt'],'gcr':sceneDict['gcr'],'clearance_height':trackerdict[theta]['clearance_height'],'azimuth':trackerdict[theta]['surf_azm'], 'nMods': sceneDict['nMods'], 'nRows': sceneDict['nRows']}      
                radfile = scene.makeSceneNxR(moduletype=moduletype, sceneDict=sceneDict2, radname=radname, hpc=hpc)
                trackerdict[theta]['radfile'] = radfile
                trackerdict[theta]['scene'] = scene

            print('{} Radfiles created in /objects/'.format(trackerdict.__len__()))
        
        else:  #gendaylit workflow
            print('\nMaking ~4000 .rad files for gendaylit 1-axis workflow (this takes a minute..)')
            count = 0
            for time in trackerdict:
                scene = SceneObj(moduletype)
                
                if trackerdict[time]['surf_azm'] >= 180:
                    trackerdict[time]['surf_azm'] = trackerdict[time]['surf_azm']-180
                    trackerdict[time]['surf_tilt'] = trackerdict[time]['surf_tilt']*-1
                theta = trackerdict[time]['theta']
                radname = '1axis%s'%(time,)
                
                # Calculating clearance height for this time.
                height = hubheight - 0.5* math.sin(abs(theta) * math.pi / 180) *  scene.sceney + scene.moduleoffset*math.sin(abs(theta)*math.pi/180) 
                        
                if trackerdict[time]['ghi'] > 0:
                    trackerdict[time]['clearance_height'] = height
                    try:
                        sceneDict2 = {'tilt':trackerdict[time]['surf_tilt'],'pitch':sceneDict['pitch'],'clearance_height': trackerdict[time]['clearance_height'],'azimuth':trackerdict[time]['surf_azm'], 'nMods': sceneDict['nMods'], 'nRows': sceneDict['nRows']}  
                    except: #maybe gcr is passed instead of pitch
                        sceneDict2 = {'tilt':trackerdict[time]['surf_tilt'],'gcr':sceneDict['gcr'],'clearance_height': trackerdict[time]['clearance_height'],'azimuth':trackerdict[time]['surf_azm'], 'nMods': sceneDict['nMods'], 'nRows': sceneDict['nRows']}  
                    radfile = scene.makeSceneNxR(moduletype=moduletype, sceneDict=sceneDict2, radname=radname, hpc=hpc)
                    trackerdict[time]['radfile'] = radfile
                    trackerdict[time]['scene'] = scene
                    count+=1
            print('{} Radfiles created in /objects/'.format(count))    
        
        self.trackerdict = trackerdict
        self.nMods = sceneDict['nMods']  #assign nMods and nRows to RadianceObj
        self.nRows = sceneDict['nRows']
        return trackerdict#self.scene            
            
    
    def analysis1axis(self, trackerdict=None, singleindex=None, accuracy='low', customname=None, modWanted=None, rowWanted=None, sensorsy=9):
        '''
        loop through trackerdict and run linescans for each scene and scan in there.
        
        Parameters
        ----------------
        trackerdict
        singleindex         :For single-index mode, just the one index we want to run (new in 0.2.3)
        accuracy            : 'low' or 'high' - resolution option used during irrPlotNew and rtrace
        customname          : Custom text string to be added to the file name for the results .CSV files
        modWanted           : mod to be sampled. Index starts at 1.
        rowWanted           : row to be sampled. Index starts at 1. (row 1)
        sensorsy            : Sampling resolution for the irradiance 
        
        Returns
        ----------------
        trackerdict with new keys: 
            'AnalysisObj'  : analysis object for this tracker theta
            'Wm2Front'     : list of front Wm2 irradiances, len=sensorsy
            'Wm2Back'      : list of rear Wm2 irradiances, len=sensorsy
            'backRatio'    : list of rear irradiance ratios, len=sensorsy
       
        Also, appends new values to RadianceObj:
            'Wm2Front'     : np Array with front irradiance cumulative
            'Wm2Back'      : np Array with rear irradiance cumulative
            'backRatio'    : np Array with rear irradiance ratios
        '''
        import warnings
        
        if customname is None:
            customname = ''
            
        if trackerdict == None:
            try:
                trackerdict = self.trackerdict
            except:
                print('No trackerdict value passed or available in self')
        
        if singleindex is None:  # run over all values in trackerdict
            trackerkeys = sorted(trackerdict.keys())
        else:                   # run in single index mode.
            trackerkeys = [singleindex]

        if modWanted == None:
            modWanted = round(self.nMods / 2.0)
        if rowWanted == None:
            rowWanted = round(self.nRows / 2.0)
        
        frontWm2 = 0 # container for tracking front irradiance across module chord. Dynamically size based on first analysis run
        backWm2 = 0 # container for tracking rear irradiance across module chord.

        for index in trackerkeys:   # either full list of trackerdict keys, or single index
            name = '1axis_%s%s'%(index,customname)
            octfile = trackerdict[index]['octfile']
            scene = trackerdict[index]['scene']
            if octfile is None:
                continue  # don't run analysis if the octfile is none
            try:  # look for missing data
                analysis = AnalysisObj(octfile,name)            
                name = '1axis_%s%s'%(index,customname,)
                frontscan, backscan = analysis.moduleAnalysis(scene, modWanted=modWanted, rowWanted=rowWanted, sensorsy=sensorsy)
                analysis.analysis(octfile,name,frontscan,backscan,accuracy)
                trackerdict[index]['AnalysisObj'] = analysis
            except Exception as e: # problem with file. TODO: only catch specific error types here.
                warnings.warn('Index: {}. Problem with file. Error: {}. Skipping'.format(index,e), Warning)
                return 
            
            #combine cumulative front and back irradiance for each tracker angle
            try:  #on error, trackerdict[index] is returned empty
                trackerdict[index]['Wm2Front'] = analysis.Wm2Front
                trackerdict[index]['Wm2Back'] = analysis.Wm2Back
                trackerdict[index]['backRatio'] = analysis.backRatio
            except KeyError as  e:  # no key Wm2Front.  
                warnings.warn('Index: {}. Trackerdict key not found: {}. Skipping'.format(index,e), Warning)
                return 
            
            if np.sum(frontWm2) == 0:  # define frontWm2 the first time through 
                frontWm2 =  np.array(analysis.Wm2Front)
                backWm2 =  np.array(analysis.Wm2Back)
            else:
                frontWm2 +=  np.array(analysis.Wm2Front)
                backWm2 +=  np.array(analysis.Wm2Back)
            print('Index: {}. Wm2Front: {}. Wm2Back: {}'.format(index,np.mean(analysis.Wm2Front),np.mean(analysis.Wm2Back)))

        if np.sum(self.Wm2Front) == 0:
            self.Wm2Front = frontWm2   # these are accumulated over all indices passed in.
            self.Wm2Back = backWm2
        else:
            self.Wm2Front += frontWm2   # these are accumulated over all indices passed in.
            self.Wm2Back += backWm2
        self.backRatio = backWm2/(frontWm2+.001) 
        #self.trackerdict = trackerdict   # removed v0.2.3 - already mapped to self.trackerdict     
        
        return trackerdict  # is it really desireable to return the trackerdict here?
            
    
# End RadianceObj definition
        
class GroundObj:
    '''
    details for the ground surface and reflectance
    '''
       
    def __init__(self, materialOrAlbedo=None, material_file=None):
        '''
        sets and returns ground materials information.  if material type is known, pass it in to get
        reflectance info.  if material type isn't known, material_info.list is returned
        
        Parameters
        ------------
        materialOrAlbedo  - if known, the name of the material desired. e.g. 'litesoil'
             
        material_file - filename of the material information.  default ground.rad
        
        Returns
        -------
        material_info.names    : list of material names
        material_info.normval : normalized color value 
        material_info.ReflAvg : average reflectance
        '''
        
        self.normval = ''
        self.ReflAvg = ''
        self.ground_type = ''
        self.material_options = []
        self.Rrefl = ''
        self.Grefl = ''
        self.Brefl = ''
        albedo = None
        material_path = 'materials'

        if material_file is None:
            material_file = 'ground.rad'       
        
        #check if materialOrAlbedo is a float between 0 and 1
        try:
            albedo = float(materialOrAlbedo)
            if not (0 < albedo < 1):
                materialOrAlbedo = None
        except TypeError:
            # nothing passed
            albedo = None
        except ValueError:
            # material string passed
            albedo = None
        
        if albedo is not None:
            self.Rrefl = albedo
            self.Grefl = albedo           
            self.Brefl = albedo
            self.normval = _normRGB(albedo,albedo,albedo)
            self.ReflAvg = albedo
            self.ground_type = 'custom'

        else:
        
            f = open(os.path.join(material_path,material_file)) 
            keys = [] #list of material key names
            Rrefl = []; Grefl=[]; Brefl=[] #RGB reflectance of the material
            temp = f.read().split()
            f.close()
            #return indices for 'plastic' definition
            index = _findme(temp,'plastic')
            for i in index:
                keys.append(temp[i+1])# after plastic comes the material name
                Rrefl.append(float(temp[i+5]))#RGB reflectance comes a few more down the list
                Grefl.append(float(temp[i+6]))
                Brefl.append(float(temp[i+7]))
            
            self.material_options = keys
    
            if materialOrAlbedo is not None:
                # if material isn't specified, return list of material options
                index = _findme(keys,materialOrAlbedo)[0]
                #calculate avg reflectance of the material and normalized color using NormRGB function
                self.normval = _normRGB(Rrefl[index],Grefl[index],Brefl[index])
                self.ReflAvg = (Rrefl[index]+Grefl[index]+Brefl[index])/3
                self.ground_type = keys[index]
                self.Rrefl = Rrefl[index]
                self.Grefl = Grefl[index]            
                self.Brefl = Brefl[index]
            else:
                print('Input albedo 0-1, or ground material names:'+str(keys))
                return None
            
        '''
        #material names to choose from: litesoil, concrete, white_EPDM, beigeroof, beigeroof_lite, beigeroof_heavy, black, asphalt
        #NOTE! delete inter.amb and .oct file if you change materials !!!
        
        '''
class SceneObj:
    '''
    scene information including PV module type, bifaciality, array info
    pv module orientation defaults: Azimuth = 180 (south)
    pv module origin: z = 0 bottom of frame. y = 0 lower edge of frame. x = 0 vertical centerline of module
    
    scene includes module details (x,y,bifi, sceney (collector_width), scenex)
    '''
    def __init__(self, moduletype=None):
        ''' initialize SceneObj
        '''
        modulenames = self.readModule()
        # should sceneDict be initialized here? This is set in makeSceneNxR
        #self.sceneDict = {'nMods':None, 'tilt':None, 'pitch':None, 'clearance_height':None, 'nRows':None, 'azimuth':None}
        if moduletype is None:
            print('Usage: SceneObj(moduletype)\nNo module type selected. Available module types: {}'.format(modulenames))
            return
        else:
            if moduletype in modulenames:
                # read in module details from configuration file. 
                self.moduleDict = self.readModule(name = moduletype)
            else:
                print('incorrect panel type selection')
                return
  
       


    def readModule(self, name=None):
        '''
        Read in available modules in module.json.  If a specific module name is 
        passed, return those details into the SceneObj. Otherwise return available module list.
        
        Parameters
        ------------
        name      # name of module.
        
        Returns
        -------
        dict of module parameters
        -or- 
        list of modulenames if name is not passed in
        
        '''
                                        
        import json
        filedir = os.path.join(DATA_PATH,'module.json')
        with open( filedir ) as configfile:
            data = json.load(configfile) 
        
        modulenames = data.keys()
        if name is None:
            
            return modulenames
        
        if name in modulenames:
            moduleDict = data[name]
            self.moduletype = name
            
            radfile = moduleDict['modulefile']
            self.x = moduleDict['x'] # width of module.
            self.y = moduleDict['y'] # length of module.
            self.bifi = moduleDict['bifi']  # bifaciality of the panel. Not currently used
            if 'scenex' in moduleDict:
                self.scenex = moduleDict['scenex']
            else:
                self.scenex = moduleDict['x']
            if 'sceney' in moduleDict:
                self.sceney = moduleDict['sceney']
            else:
                self.sceney = moduleDict['y']
            if 'moduleoffset' in moduleDict:
                self.moduleoffset = moduleDict['moduleoffset']
            else:
                self.moduleoffset = 0
            #
                    #create new .RAD file
            if not os.path.isfile(radfile):
                # py2 and 3 compatible: binary write, encode text first
                with open(radfile, 'wb') as f:
                    f.write(moduleDict['text'].encode('ascii'))
            #if not os.path.isfile(radfile):
            #    raise Exception('Error: module file not found {}'.format(radfile))mod
            self.modulefile = radfile
            
            return moduleDict
        else:
            print('Error: module name {} doesnt exist'.format(name))
            return {}
    
    def makeSceneNxR(self, moduletype=None, sceneDict=None, radname=None, hpc=False):

        '''
        return a SceneObj which contains details of the PV system configuration including 
        tilt, row pitch, hub_height or clearance_height, nMods per row, nRows in the system...
        
        arrange module defined in SceneObj into a N x R array
        Valid input ranges: Tilt -90 to 90 degrees.
        Axis azimuth: A value denoting the compass direction along which the axis of rotation lies. Measured in decimal degrees East of North. [0 to 180) possible. 
        If azimuth is passed, a warning is given and Axis Azimuth and tilt are re-calculated.
        
        Module definitions assume that the module .rad file is defined with zero tilt, centered along the x-axis and y-axis for the center of rotation of the module (+X/2, -X/2, +Y/2, -Y/2 on each side)
        Y-axis is assumed the bottom edge of the module is at y = 0, top of the module at y = Y.
        self.scenex is overall module width including xgap.
        self.sceney is overall series height of module(s) including gaps, multiple-up configuration, etc
        
        The returned scene has (0,0) coordinates centered at the module at the center of the array. 
        For 5 rows, that is row 3, for 4 rows, that is row 2 also (rounds down)
        For 5 modules in the row, that is module 3, for 4 modules in the row, that is module 2 also (rounds down)
        
        Parameters
        ------------
        moduletype: string name of module created with makeModule()
        sceneDict:  dictionary with keys:[tilt] [height] [pitch] [azimuth]. Here `height` is CLEARANCE_HEIGHT
        nMods:      int number of modules per row (default = 20)
        nRows:      int number of rows in system (default = 7) 
        sensorsy:   int number of scans in the y direction (up tilted module chord, default = 9)
        modwanted:  where along row does scan start, Nth module along the row (default middle module)
        rowwanted:   which row is scanned? (default middle row)        
        mode:        0 fixed / 1 singleaxistracking
        hpc:        boolean, default False. For makeScene, it adds the full path
                    of the objects folder where the module . rad file is saved.
        
        Returns
        -------
        radfile: (string) filename of .RAD scene in /objects/
        Returns: SceneObj 'scene' with configuration details
        
        '''
        
        #Cleanup Should this still be here?
        if moduletype is None:
            print('makeScene(moduletype, sceneDict, nMods, nRows).  Available moduletypes: monopanel, simple_panel' ) #TODO: read in config file to identify available module types
            return
        self.scene = SceneObj(moduletype)   #123 is this needed with the modification?
        
        if sceneDict is None:
            print('makeScene(moduletype, sceneDict, nMods, nRows).  sceneDict inputs: .tilt .height .pitch .azimuth .nMods .nRows')


        if 'orientation' in sceneDict:
            if sceneDict['orientation'] == 'landscape':
                raise Exception('\n\n ERROR: Orientation format has been deprecated since version 0.2.4. If you want to flip your modules, on makeModule switch the x and y values. X value is the size of the panel along the row, so for a "landscape" panel x should be > than y.\n\n')
        #if sceneDict.has_key('azimuth') is False:
        if 'azimuth' not in sceneDict:
            sceneDict['azimuth'] = 180
        
        if 'axis_tilt' not in sceneDict:
            sceneDict['axis_tilt'] = 0
        
        if 'originx' not in sceneDict:
            sceneDict['originx'] = 0
            
        if 'originy' not in sceneDict:
            sceneDict['originy'] = 0
            
        if radname is None:
            radname =  str(self.moduletype).strip().replace(' ', '_')# remove whitespace
            
        # loading variables
        tilt = sceneDict['tilt']
        nMods = sceneDict['nMods'] 
        nRows = sceneDict['nRows']
        axis_tilt = sceneDict['axis_tilt']
        originx = sceneDict ['originx']
        originy = sceneDict['originy']

        # hub_height, clearance_height and height logic.
        # this routine uses hub_height to move the panels up so it's importnat to 
        # have a value for that, either obtianing from clearance_height (if coming from
        # makeScene) or from hub_height itself.
        # it is assumed htat if no clearnace_height or hub_height is passed,
        # hub_height = height.
        
        if 'height' in sceneDict:
            if 'clearance_height' in sceneDict:
                if 'hub_height' in sceneDict:
                    print("Warning: Passed 'height' (deprecated), 'clearance_height', and 'hub_height'. Removing 'height' and 'clearance_height' and using 'hub_height' for scene generation")
                    hubheight = sceneDict['hub_height'] 
                    del sceneDict['clearance_height']
                    del sceneDict['height']
                else:
                    print("Warning: Passed 'height'(deprecated) and 'clearance_height'. Removing 'height'")
                    del sceneDict['height']
                    hubheight = sceneDict['clearance_height'] + 0.5* np.sin(abs(tilt) * np.pi / 180) *  self.sceney - self.moduleoffset*np.sin(abs(tilt)*np.pi/180)     
            else:
                if 'hub_height' in sceneDict:
                    print("Warning: Passed 'height'(deprecated) and 'hub_height'. Removing 'height'")
                    hubheight = sceneDict['hub_height'] 
                    del sceneDict['height']
                else:                    
                    print("Warning: 'height' is being deprecated. Assuming height passed is hub_height") 
                    hubheight = sceneDict['hub_height'] 
                    sceneDict['hub_height']=sceneDict['height']
                    del sceneDict['height']
        else:
            if 'hub_height' in sceneDict:
                if 'clearance_height' in sceneDict:
                    print("Warning: Passed 'hub_height' and 'clearance_height'. Proceeding with 'hub_height' and removing 'clearance_height' from dictionary")
                    hubheight = sceneDict['hub_height']
                    del sceneDict['clearance_height']
                else:
                    hubheight = sceneDict['hub_height']
            else:
                if 'clearance_height' in sceneDict:
                    hubheight = sceneDict['clearance_height'] + 0.5* np.sin(abs(tilt) * np.pi / 180) *  self.sceney - self.moduleoffset*np.sin(abs(tilt)*np.pi/180)     
                else:
                    print ("ERROR with sceneDict: No hub_height, clearance_height or height (deprecated) passed! Exiting routine.")
                    return



        # this is clearance_height, used for the title.
        height = hubheight - 0.5* np.sin(abs(tilt) * np.pi / 180) *  self.sceney + self.moduleoffset*np.sin(abs(tilt)*np.pi/180)     
            
        if 'pitch' in sceneDict:
            pitch = sceneDict['pitch']
        else:
            #TODO: input either pitch or GCR here - since we know sceney
            if 'gcr' in sceneDict:
                pitch = round(self.sceney/sceneDict['gcr'],3)
            else:
                raise Exception('Error: either `pitch` or `gcr` must be defined in sceneDict')
        rad_azimuth = sceneDict['azimuth'] # Radiance considers South = 0. 
        
        
        ''' INITIALIZE VARIABLES '''
        text = '!xform '
                          
        text += '-rx %s -t %s %s %s ' %(tilt, originx, originy, hubheight)
        # create nMods-element array along x, nRows along y. 1cm module gap.
        text += '-a %s -t %s 0 0 -a %s -t 0 %s 0 ' %(nMods, self.scenex, nRows, pitch)
        
        # azimuth rotation of the entire shebang. Select the row to scan here based on y-translation.
        #text += '-i 1 -t %s %s 0 -rz %s ' %(-self.scenex*int(nMods/2), -pitch* (rowwanted - 1), 180-azimuth) 
        # Modifying so center row is centered in the array. (i.e. 3 rows, row 2. 4 rows, row 2 too)
#        text += '-i 1 -t %s %s 0 -rz %s ' %(-self.scenex*int(nMods/2), -pitch*(round(nRows / 2.0)*1.0-1), -rad_azimuth) 
        text += '-i 1 -t %s %s 0 -rz %s ' %(-self.scenex*(round(nMods/2.0)*1.0-1), -pitch*(round(nRows / 2.0)*1.0-1), 180-rad_azimuth) 
        
    
        if axis_tilt is not 0 and rad_azimuth == 90:
            text += '-rx %s -t 0 0 %s ' %(axis_tilt, self.scenex*(round(nMods/2.0)*1.0-1)*np.sin(axis_tilt * np.pi/180) )
            
        if hpc:
            text += os.path.join(testfolder, self.modulefile) #HpcChange
            radfile = os.path.join(testfolder,'objects','%s_%0.5s_%0.5s_%sx%s.rad'%(radname,height,pitch, nMods, nRows) ) #Hpc change
        else:
            text += os.path.join(self.modulefile)
            radfile = os.path.join('objects','%s_%0.5s_%0.5s_%sx%s.rad'%(radname,height,pitch, nMods, nRows) ) # update in 0.2.3 to shorten radnames
                            
        # py2 and 3 compatible: binary write, encode text first
        with open(radfile, 'wb') as f:
            f.write(text.encode('ascii'))

        # For 180 azimuth (South facing), positive tilt draws the modules correctly. However, the sensors in Z increase instead of decrease. So have to 'invert' the tilt for the sensors).
       # if azimuth == 180:
       #     tilt = -1*(tilt)
            
        self.gcr = self.sceney / pitch
        self.text = text
        self.radfiles = radfile
        self.sceneDict = sceneDict
#        self.hub_height = hubheight
        return radfile
        

class MetObj:
    '''
    meteorological data from EPW file

    '''
    def __initOld__(self, epw=None):
        ''' initialize MetObj from passed in epwdata from pyepw.epw
            used to be __init__ called from readEPW_old
        '''
        if epw is not None:
            #self.location = epw.location
            self.latitude = epw.location.latitude
            self.longitude = epw.location.longitude
            self.elevation = epw.location.elevation
            self.timezone = epw.location.timezone
            self.city = epw.location.city
            
            wd = epw.weatherdata
            
            
            self.datetime = [datetime.datetime(
                                    1990,x.month,x.day,x.hour-1)
                                    for x in wd                        
                                    ]
            self.ghi = [x.global_horizontal_radiation for x in wd]
            self.dhi = [x.diffuse_horizontal_radiation for x in wd]        
            self.dni = [x.direct_normal_radiation for x in wd]  
            self.ghl = [x.global_horizontal_illuminance for x in wd] # not used
            self.dhl = [x.diffuse_horizontal_illuminance for x in wd]  # not used       
            self.dnl = [x.direct_normal_illuminance for x in wd] # not used
            self.epw_raw = epw  # not used

    def __init__(self, tmydata, metadata):
        '''
        initTMY:  initialize the MetObj from a tmy3 file instead of a epw file
        
        Parameters
        -----------
        tmydata:  tmy3 output from pvlib.readtmy3
        metadata: metadata output from pvlib.readtmy3
        
        '''
        import pytz
        import pvlib
        
        #  location data.  so far needed:latitude, longitude, elevation, timezone, city
        self.latitude = metadata['latitude']; lat=self.latitude
        self.longitude = metadata['longitude']; lon=self.longitude
        self.elevation = metadata['altitude']; elev=self.elevation
        self.timezone = metadata['TZ']
        self.city = metadata['Name']
        #self.location.state_province_region = metadata['State'] # not necessary
        self.datetime = tmydata.index.tolist() # this is tz-aware. EPW input routine is not...
        self.ghi = tmydata.GHI.tolist()
        self.dhi = tmydata.DHI.tolist()        
        self.dni = tmydata.DNI.tolist()
        
        #v0.2.5: always initialize the MetObj with solpos, sunrise/sunset and corrected time
        datetimetz = pd.DatetimeIndex(self.datetime)
        try:  # make sure the data is tz-localized.
            datetimetz = datetimetz.tz_localize(pytz.FixedOffset(self.timezone*60))#  use pytz.FixedOffset (in minutes) 
        except:  # data is tz-localized already. Just put it in local time.
            datetimetz = datetimetz.tz_convert(pytz.FixedOffset(self.timezone*60))
        #check for data interval
        interval = datetimetz[1]-datetimetz[0]
        #Offset so it matches the single-axis tracking sun position calculation considering use of weather files
        if interval== pd.Timedelta('1h'):
            # get solar position zenith and azimuth based on site metadata
            #solpos = pvlib.irradiance.solarposition.get_solarposition(datetimetz,lat,lon,elev)
            # Sunrise/Sunset Check and adjusts position of time for that near sunrise and sunset.
            sunup= pvlib.irradiance.solarposition.get_sun_rise_set_transit(datetimetz, lat, lon) #only for pvlib <0.6.1
            #sunup= pvlib.irradiance.solarposition.sun_rise_set_transit_spa(datetimetz, lat, lon) #new for pvlib >= 0.6.1
            
            sunup['minutedelta']= int(interval.seconds/2/60) # default sun angle 30 minutes before timestamp
            # vector update of minutedelta at sunrise
            sunrisemask = sunup.index.hour-1==sunup['sunrise'].dt.hour
            sunup['minutedelta'].mask(sunrisemask,np.floor((60-(sunup['sunrise'].dt.minute))/2),inplace=True)
            # vector update of minutedelta at sunset
            sunsetmask = sunup.index.hour-1==sunup['sunset'].dt.hour
            sunup['minutedelta'].mask(sunsetmask,np.floor((60-(sunup['sunset'].dt.minute))/2),inplace=True)
            # save corrected timestamp
            sunup['corrected_timestamp'] = sunup.index-pd.to_timedelta(sunup['minutedelta'], unit='m')

        else:
            minutedelta = int(interval.seconds/2/60)
            #datetimetz=datetimetz-pd.Timedelta(minutes = minutedelta)   # This doesn't check for Sunrise or Sunset
            sunup= pvlib.irradiance.solarposition.get_sun_rise_set_transit(datetimetz, lat, lon)
            #sunup= pvlib.irradiance.solarposition.sun_rise_set_transit_spa(datetimetz, lat, lon) #new for pvlib >= 0.6.1
            sunup['corrected_timestamp'] = sunup.index-pd.Timedelta(minutes = minutedelta)
            
        self.solpos = pvlib.irradiance.solarposition.get_solarposition(sunup['corrected_timestamp'],lat,lon,elev)
        self.sunrisesetdata=sunup
 
    def set1axis(self, cumulativesky=True, axis_azimuth=180, limit_angle=45, angledelta=5, backtrack=True, gcr = 1.0/3.0, roundTrackerAngle=True):
        '''
        Set up geometry for 1-axis tracking cumulativesky.  Solpos data already stored in metdata.solpos. Pull in tracking angle details from 
        pvlib, create multiple 8760 metdata sub-files where datetime of met data 
        matches the tracking angle. 
        
        Parameters
        ------------
        cumulativesky       # boolean. whether individual csv files are created with constant tilt angle for the cumulativesky approach.
                            # if false, the gendaylit tracking approach must be used.
        axis_azimuth         # orientation axis of tracker torque tube. Default North-South (180 deg)
        limit_angle      # +/- limit angle of the 1-axis tracker in degrees. Default 45 
        angledelta      # degree of rotation increment to parse irradiance bins. Default 5 degrees
                        #  (0.4 % error for DNI).  Other options: 4 (.25%), 2.5 (0.1%).  
                        #  Note: the smaller the angledelta, the more simulations must be run
        Returns
        -------
        trackerdict      dictionary with keys for tracker tilt angles and list of csv metfile, and datetimes at that angle
                         trackerdict[angle]['csvfile';'surf_azm';'surf_tilt';'UTCtime']
                         Note: this output is mostly used for the cumulativesky approach.
                         
        Internal parameters
        --------
        metdata.solpos              pandas dataframe with output from pvlib solar position for each timestep
        metdata.sunrisesetdata      pandas dataframe with sunrise, sunset and adjusted time data.
        metdata.tracker_theta       (list) tracker tilt angle from pvlib for each timestep
        metdata.surface_tilt        (list)  tracker surface tilt angle from pvlib for each timestep
        metdata.surface_azimuth     (list)  tracker surface azimuth angle from pvlib for each timestep
        '''

        axis_tilt = 0       # only support 0 tilt trackers for now
        self.cumulativesky = cumulativesky   # track whether we're using cumulativesky or gendaylit

        # get 1-axis tracker angles for this location, rounded to nearest 'angledelta'
        trackingdata = self._getTrackingAngles(axis_azimuth, limit_angle, angledelta, axis_tilt = 0, backtrack = backtrack, gcr = gcr, roundTrackerAngle=roundTrackerAngle )
        
        # get list of unique rounded tracker angles
        theta_list = trackingdata.dropna()['theta_round'].unique() 
        
        if cumulativesky is True:
            # create a separate metfile for each unique tracker theta angle. return dict of filenames and details 
            trackerdict = self._makeTrackerCSV(theta_list,trackingdata)
        else:
            # trackerdict uses timestamp as keys. return azimuth and tilt for each timestamp
            times = [str(i)[5:-12].replace('-','_').replace(' ','_') for i in self.datetime]
            #trackerdict = dict.fromkeys(times)
            trackerdict = {}
            for i,time in enumerate(times) :
                if (self.ghi[i] > 0) & (~np.isnan(metdata.tracker_theta[i])):
                    trackerdict[time] = {
                            'surf_azm':     self.surface_azimuth[i],
                            'surf_tilt':    self.surface_tilt[i],
                            'theta':        self.tracker_theta[i],
                            'ghi':          self.ghi[i],
                            'dhi':          self.dhi[i]
                            }

        return trackerdict
    
    
    def _getTrackingAngles(self, axis_azimuth=180, limit_angle=45, angledelta=5, axis_tilt=0, backtrack=True, gcr = 1.0/3.0, roundTrackerAngle=True ):  # return tracker angle data for the system
            '''
            Helper subroutine to return 1-axis tracker tilt and azimuth data.
            
            Input Parameter
            ------------------
            same as pvlib.tracking.singleaxis, plus:
                
            angledelta:  angle in degrees to round tracker_theta to.  This is for 
            
            returns
            ------------------
            DataFrame with the following columns:
        
            * tracker_theta: The rotation angle of the tracker.
                tracker_theta = 0 is horizontal, and positive rotation angles are
                clockwise.
            * aoi: The angle-of-incidence of direct irradiance onto the
                rotated panel surface.
            * surface_tilt: The angle between the panel surface and the earth
                surface, accounting for panel rotation.
            * surface_azimuth: The azimuth of the rotated panel, determined by
                projecting the vector normal to the panel's surface to the earth's
                surface.
            * 'theta_round' : tracker_theta rounded to the nearest 'angledelta'.
            If no angledelta is specified, it is rounded to the nearest degree.
            '''
            import pytz
            import pvlib
            
            lat = self.latitude
            lon = self.longitude
            elev = self.elevation
            solpos = self.solpos
            # get 1-axis tracker tracker_theta, surface_tilt and surface_azimuth        
            trackingdata = pvlib.tracking.singleaxis(solpos['zenith'], solpos['azimuth'], axis_tilt, axis_azimuth, limit_angle, backtrack, gcr)
            # save tracker tilt information to metdata.tracker_theta, metdata.surface_tilt and metdata.surface_azimuth
            self.tracker_theta = trackingdata['tracker_theta'].tolist()
            self.surface_tilt = trackingdata['surface_tilt'].tolist()
            self.surface_azimuth = trackingdata['surface_azimuth'].tolist()
            # undo the  timestamp offset put in by solpos. It may not be exactly 30 minutes any more...
            #trackingdata.index = trackingdata.index + pd.Timedelta(minutes = 30)
            trackingdata.index = self.sunrisesetdata.index  #this has the original time data in it
            
            # round tracker_theta to increments of angledelta
            def _roundArbitrary(x, base = angledelta):
            # round to nearest 'base' value.
            # mask NaN's to avoid rounding error message
                return base * (x.dropna()/float(base)).round()
              
            if roundTrackerAngle==True:
                trackingdata['theta_round'] = _roundArbitrary(trackingdata['tracker_theta'], angledelta)
            else:
                trackingdata['theta_round'] = _roundArbitrary(trackingdata['tracker_theta'], 1)    # rounding to nearest degree.
            return trackingdata    

    def _makeTrackerCSV(self, theta_list, trackingdata):
        '''
        Create multiple new irradiance csv files with data for each unique rounded tracker angle.
        Return a dictionary with the new csv filenames and other details, Used for cumulativesky tracking
        
        Input Parameter
        ------------------
        theta_list: array of unique tracker angle values
        
        trackingdata: Pandas Series with hourly tracker angles from pvlib.tracking.singleaxis
        
        returns
        ------------------
        
        trackerdict  [dictionary]
          keys: *theta_round tracker angle  (default: -45 to +45 in 5 degree increments).
          sub-array keys:
              *datetime:  array of datetime strings in this group of angles
              *count:  number of datapoints in this group of angles
              *surf_azm:  surface azimuth of tracker during this group of angles
              *surf_tilt:  tilt angle average of tracker during this group of angles
              *csvfile:  name of csv met data file saved in /EPWs/
        '''
        
        datetime = pd.to_datetime(self.datetime)
        
        trackerdict = dict.fromkeys(theta_list)
        
        for theta in list(trackerdict) :
            trackerdict[theta] = {}
            csvfile = os.path.join('EPWs','1axis_{}.csv'.format(theta))
            tempdata = trackingdata[trackingdata['theta_round'] == theta]
            
            #Set up trackerdict output for each value of theta
            trackerdict[theta]['csvfile'] = csvfile
            trackerdict[theta]['surf_azm'] = tempdata['surface_azimuth'].median()
            trackerdict[theta]['surf_tilt'] = abs(theta)
            datetimetemp = tempdata.index.strftime('%Y-%m-%d %H:%M:%S') #local time
            trackerdict[theta]['datetime'] = datetimetemp
            trackerdict[theta]['count'] = datetimetemp.__len__()
            #Create new temp csv file with zero values for all times not equal to datetimetemp
            # write 8760 2-column csv:  GHI,DHI
            ghi_temp = []
            dhi_temp = []
            for g,d,time in zip(self.ghi,self.dhi,datetime.strftime('%Y-%m-%d %H:%M:%S') ) :
            
                if time in datetimetemp:  # is this time included in a particular theta_round angle?
                    ghi_temp.append(g)
                    dhi_temp.append(d)
                else:                     # mask out irradiance at this time, since it belongs to a different bin
                    ghi_temp.append(0.0)
                    dhi_temp.append(0.0)
            savedata = pd.DataFrame({'GHI':ghi_temp, 'DHI':dhi_temp})  # save in 2-column GHI,DHI format for gencumulativesky -G
            print('Saving file {}, # points: {}'.format(trackerdict[theta]['csvfile'],datetimetemp.__len__()))
            savedata.to_csv(csvfile,index = False, header = False, sep = ' ', columns = ['GHI','DHI'])


        return trackerdict
    

class AnalysisObj:
    '''
    Analysis class for plotting and reporting
    '''
    def __init__(self, octfile=None, name=None):
        self.octfile = octfile
        self.name = name
        
    def makeImage(self, viewfile, octfile=None, name=None, hpc=False):
        'make visible image of octfile, viewfile'
        
        if octfile is None:
            octfile = self.octfile
        if name is None:
            name = self.name
        
        #JSS         #TODO: update and test this for cross-platform compatibility using os.path.join        
        if hpc is True:
            time_to_wait = 10
            time_counter = 0
            filelist = [octfile, "views/"+viewfile]
            for file in filelist:
               while not os.path.exists(file):
                  time.sleep(1)
                  time_counter += 1
                  if time_counter > time_to_wait:break
          
        print('generating visible render of scene')
        #TODO: update and test this for cross-platform compatibility using os.path.join
        os.system("rpict -dp 256 -ar 48 -ms 1 -ds .2 -dj .9 -dt .1 -dc .5 -dr 1 -ss 1 -st .1 -ab 3  -aa .1 "+ 
                  "-ad 1536 -as 392 -av 25 25 25 -lr 8 -lw 1e-4 -vf views/"+viewfile+ " " + octfile +
                  " > images/"+name+viewfile[:-3] +".hdr")
        
    def makeFalseColor(self, viewfile, octfile=None, name=None):
        '''make false-color plot of octfile, viewfile
        Note: for Windows requires installation of falsecolor.exe, which is part of
        radwinexe-5.0.a.8-win64.zip found at http://www.jaloxa.eu/resources/radiance/radwinexe.shtml
        TODO: error checking for installation of falsecolor.exe with download suggestion
        '''
        if octfile is None:
            octfile = self.octfile
        if name is None:
            name = self.name   
        
        print('generating scene in WM-2. This may take some time.')    
        #TODO: update and test this for cross-platform compatibility using os.path.join
        cmd = "rpict -i -dp 256 -ar 48 -ms 1 -ds .2 -dj .9 -dt .1 -dc .5 -dr 1 -ss 1 -st .1 -ab 3  -aa " +\
                  ".1 -ad 1536 -as 392 -av 25 25 25 -lr 8 -lw 1e-4 -vf views/"+viewfile + " " + octfile
        
        WM2_out,err = _popen(cmd,None)
        if err is not None:
            print('Error: {}'.format(err))
            return
            
        # determine the extreme maximum value to help with falsecolor autoscale
        extrm_out,err = _popen("pextrem",WM2_out.encode('latin1'))
        WM2max = max(map(float,extrm_out.split())) # cast the pextrem string as a float and find the max value
        print('saving scene in false color') 
        #auto scale false color map
        if WM2max < 1100:
            cmd = "falsecolor -l W/m2 -m 1 -s 1100 -n 11" 
        else:
            cmd = "falsecolor -l W/m2 -m 1 -s %s"%(WM2max,) 
        with open(os.path.join("images","%s%s_FC.hdr"%(name,viewfile[:-3]) ),"w") as f:
            data,err = _popen(cmd,WM2_out.encode('latin1'),f)
            if err is not None:
                print(err)
                print( 'possible solution: install radwinexe binary package from '
                      'http://www.jaloxa.eu/resources/radiance/radwinexe.shtml')
        
    def linePtsMakeDict(self, linePtsDict):
        a = linePtsDict
        linepts = self.linePtsMake3D(a['xstart'],a['ystart'],a['zstart'],
                                a['xinc'], a['yinc'], a['zinc'],
                                a['Nx'],a['Ny'],a['Nz'],a['orient'])
        return linepts
        
    def linePtsMake3D(self, xstart, ystart, zstart, xinc, yinc, zinc, Nx, Ny, Nz, orient):
        #linePtsMake(xpos,ypos,zstart,zend,Nx,Ny,Nz,dir)
        #create linepts text input with variable x,y,z. 
        #If you don't want to iterate over a variable, inc = 0, N = 1.
        
        #now create our own matrix - 3D nested X,Y,Z
        linepts = ""
        # make sure Nx, Ny, Nz are ints.
        Nx = int(Nx)
        Ny = int(Ny)
        Nz = int(Nz)
        

        for iz in range(0,Nz):
            zpos = zstart+iz*zinc
            for iy in range(0,Ny):
                ypos = ystart+iy*yinc
                xpos = xstart+iy*xinc
                zpos = zstart+iy*zinc
                linepts = linepts + str(xpos) + ' ' + str(ypos) + ' '+str(zpos) + ' ' + orient + " \r"
        return(linepts)
    
    def irrPlotNew(self, octfile, linepts, mytitle=None, plotflag=None, accuracy='low', hpc=False):
        '''
        (plotdict) = irrPlotNew(linepts,title,time,plotflag, accuracy)
        irradiance plotting using rtrace
        pass in the linepts structure of the view along with a title string for the plots
        note that the plots appear in a blocking way unless you call pylab magic in the beginning.
        
        Parameters
        ------------
        octfile     - filename and extension of .oct file
        linepts     - output from linePtsMake3D
        mytitle     - title to append to results files
        plotflag    - true or false - include plot of resulting irradiance
        accuracy    - either 'low' (default - faster) or 'high' (better for low light)
        hpc         - boolean, default False. Waits for octfile for a longer time if parallel processing.
        
        Returns
        -------
        out.x,y,z  - coordinates of point
                .r,g,b     - r,g,b values in Wm-2
                .Wm2            - equal-weight irradiance
                .mattype        - material intersected
                .title      - title passed in
        '''
        if mytitle is None:
            mytitle = octfile[:-4]
        
        if plotflag is None:
            plotflag = False
        
        #JSS
        if hpc is True:
            import time
            time_to_wait = 10
            time_counter = 0
            while not os.path.exists(octfile):
                time.sleep(1)
                time_counter += 1
                if time_counter > time_to_wait:
                    print('JSS: OCTFILE NOT FOUND (line 2247)')
                    break
                
        if octfile is None:
            print('Analysis aborted. octfile = None' )
            return None
        
        keys = ['Wm2','x','y','z','r','g','b','mattype']
        out = {key: [] for key in keys}
        #out = dict.fromkeys(['Wm2','x','y','z','r','g','b','mattype','title'])
        out['title'] = mytitle    
        print ('Linescan in process: %s' %(mytitle))
        #rtrace ambient values set for 'very accurate':
        #cmd = "rtrace -i -ab 5 -aa .08 -ar 512 -ad 2048 -as 512 -h -oovs "+ octfile
        
        if accuracy == 'low':
            #rtrace optimized for faster scans: (ab2, others 96 is too coarse)
            cmd = "rtrace -i -ab 2 -aa .1 -ar 256 -ad 2048 -as 256 -h -oovs "+ octfile
        elif accuracy == 'high':
            #rtrace ambient values set for 'very accurate':
            cmd = "rtrace -i -ab 5 -aa .08 -ar 512 -ad 2048 -as 512 -h -oovs "+ octfile
        else:
            print('irrPlotNew accuracy options: "low" or "high"')
            return({})



        temp_out,err = _popen(cmd,linepts.encode())
        if err is not None:
            if err[0:5] == 'error':
                raise Exception(err[7:])
            else:
                print(err)
        
        if temp_out is not None:  # when file errors occur, temp_out is None, and err message is printed.
            for line in temp_out.splitlines():
                temp = line.split('\t')
                out['x'].append(float(temp[0]))
                out['y'].append(float(temp[1]))
                out['z'].append(float(temp[2]))
                out['r'].append(float(temp[3]))
                out['g'].append(float(temp[4]))
                out['b'].append(float(temp[5]))
                out['mattype'].append(temp[6])
                out['Wm2'].append(sum([float(i) for i in temp[3:6]])/3.0)
    
            
            if plotflag is True:
                plt.figure()
                plt.plot(out['Wm2'])
                plt.ylabel('Wm2 irradiance')
                plt.xlabel('variable')
                plt.title(mytitle)
                plt.show()
        else:
            out = None   # return empty if error message.
        
        return(out)   
    
    def saveResults(self, data, reardata=None, savefile=None):
        ''' 
        saveResults - function to save output from irrPlotNew 
        If rearvals is passed in, back ratio is saved
                
        Returns: savefile       
        '''
        
        if savefile is None:
            savefile = data['title'] + '.csv'
        # make dataframe from results
        data_sub = {key:data[key] for key in ['x', 'y', 'z', 'Wm2', 'mattype']}
        
        #TODO: data_sub front values don't seem to be saved to self.
        if reardata is not None:
            self.rearMat = reardata['mattype']
            data_sub['rearMat'] = self.rearMat
            self.rearZ = reardata['z']
            data_sub['rearZ'] = self.rearZ
            self.Wm2Front = data_sub.pop('Wm2')
            data_sub['Wm2Front'] = self.Wm2Front
            self.Wm2Back = reardata['Wm2']
            data_sub['Wm2Back'] = self.Wm2Back
            self.backRatio = [x/(y+.001) for x,y in zip(reardata['Wm2'],data['Wm2'])] # add 1mW/m2 to avoid dividebyzero
            data_sub['Back/FrontRatio'] = self.backRatio
            df = pd.DataFrame.from_dict(data_sub)
            #df.to_csv(os.path.join("results", savefile), sep = ',',columns = ['x','y','z','mattype','Wm2Front','Wm2Back','Back/FrontRatio'], index = False)  #previous 0.2.2 version
            df.to_csv(os.path.join("results", savefile), sep = ',',columns = ['x','y','z','rearZ','mattype','rearMat','Wm2Front','Wm2Back','Back/FrontRatio'], index = False) # new in 0.2.3
        else:
            df = pd.DataFrame.from_dict(data_sub)
            df.to_csv(os.path.join("results", savefile), sep = ',', columns = ['x','y','z','mattype','Wm2'], index = False)
            
        print('Saved: %s'%(os.path.join("results", savefile)))
        return os.path.join("results", savefile)
        
    
    def moduleAnalysis(self, scene, modWanted=None, rowWanted=None, sensorsy=9.0, debug=False):
        '''
        (frontscan, backscan) = moduleAnalysis(scene, modWanted, rowWanted, sensorsy)
        
        Definition of the Radiance scan points used in rtrace.  
        
        Parameters
        ------------
        scene         - SceneObj generated with makeScene. These details are used to identify scan points.
        modWanted     - output from linePtsMake3D
        rowWanted     - title to append to results files
        sensorsy      - number of 
        debug         - boolean
        
        Returns
        -------
        (frontscan, backscan) - tuple of scanDict for front and backside scan that is passed into `analysis` function
            
        
        
        '''
    
    # Height:  clearance height for fixed tilt systems, or torque tube height for single-axis tracked systems.
    #   Single axis tracked systems will consider the offset to calculate the final height.
    #2Do: deprecate the ambiguous term "height" and use either hubheight or clearance_height 
    
        
        if sensorsy >0:
            sensorsy = sensorsy * 1.0
        else:
            raise Exception('input sensorsy must be numeric >0')
            
        dtor = np.pi/180.0
        
        # Internal scene parameters are stored in scene.sceneDict. Load these into local variables
        sceneDict = scene.sceneDict
        moduleDict = scene.moduleDict


        azimuth = sceneDict['azimuth']
        tilt = sceneDict['tilt']
        nMods = sceneDict['nMods']
        nRows = sceneDict['nRows']
        pitch = sceneDict['pitch']
        axis_tilt = sceneDict['axis_tilt']
        originx = sceneDict['originx']
        originy = sceneDict['originy']
        
       # offset = moduleDict['moduleoffset']
        offset = scene.moduleoffset 
        sceney = scene.sceney
        scenex = scene.scenex
        
        
        # The Sensor routine below needs a "hub-height", not a clearance height.
        # The below complicated check checks to see if height (deprecated) is passed,
        # and if clearance_height or hub_height is passed as well.
        
        # height internal variable defined here is equivalent to hub_height.
        if 'hub_height' in sceneDict:
            height = sceneDict['hub_height']
            
            if 'height' in sceneDict:
                print ("sceneDict warning: 'height' is deprecated, using 'hub_height' and deleting 'height' from sceneDict.")
                del sceneDict['height']
            
            if 'clearance_height' in sceneDict:
                print ("sceneDict warning: 'hub_height' and 'clearance_height' passed to moduleAnalysis(). Using 'hub_height' instead of 'clearance_height'")
        else:
            if 'clearance_height' in sceneDict:
                height = sceneDict['clearance_height'] + 0.5* np.sin(abs(tilt) * np.pi / 180) * sceney - offset*np.sin(abs(tilt)*np.pi/180) 
                
                if 'height' in sceneDict:
                    print("sceneDict warning: 'height' is deprecated, using 'clearance_height' for moduleAnalysis()")
                    del sceneDict['height'] 
            else:
                if 'height' in sceneDict:
                    print("sceneDict warning: 'height' is deprecated. Assuming this was clearance_height that was passed as 'height' and renaming it in sceneDict for moduleAnalysis()")
                    height = sceneDict['height'] + 0.5* np.sin(abs(tilt) * np.pi / 180) * sceney - offset*np.sin(abs(tilt)*np.pi/180) 
                else:
                    print("Isue with moduleAnalysis routine. No hub_height or clearance_height passed (or even deprecated height!)")

        if debug:
            print("For debug:\n hub_height, Azimuth, Tilt, nMods, nRows, Pitch, Offset, SceneY, SceneX")
            print(height, azimuth, tilt, nMods, nRows, pitch, offset, sceney, scenex)
        
        if modWanted == 0:
            print( " FYI Modules and Rows start at index 1. Reindexing to modWanted 1"  )
            modWanted = modWanted+1  # otherwise it gives results on Space.
        
        if rowWanted ==0:
            print( " FYI Modules and Rows start at index 1. Reindexing to rowWanted 1"  )
            rowWanted = rowWanted+1
        
        if modWanted is None:
            modWanted = round(nMods / 2.0)
        if rowWanted is None:
            rowWanted = round(nRows / 2.0)
                    
        if abs(np.tan(azimuth*dtor) ) <=1 or abs(np.tan(azimuth*dtor) ) > 1:

            if debug is True:
                print( "Sampling: modWanted %i, rowWanted %i out of %i modules, %i rows" % (modWanted, rowWanted, nMods, nRows))
            
            x0 = originx + (modWanted-1)*scenex - (scenex*(round(nMods/2.0)*1.0-1))
            y0 = originy + (rowWanted-1)*pitch - (pitch*(round(nRows / 2.0)*1.0-1))

            x1 = x0 * np.cos ((180-azimuth)*dtor) - y0 * np.sin((180-azimuth)*dtor)
            y1 = x0 * np.sin ((180-azimuth)*dtor) + y0 * np.cos((180-azimuth)*dtor)
            z1 = 0
            
            if axis_tilt is not 0 and azimuth == 90:
                print ("fixing height for axis_tilt")
                z1 = (modWanted-1)*scenex * np.sin(axis_tilt*dtor)       #TODO check might need to do half a module more?
                
            # Edge of Panel 
            x2 = (sceney/2.0) * np.cos((tilt)*dtor) * np.sin((azimuth)*dtor)
            y2 = (sceney/2.0) * np.cos((tilt)*dtor) * np.cos((azimuth)*dtor)
            z2 = -(sceney/2.0) * np.sin(tilt*dtor)
            
            
            # Axis of rotation Offset (if offset is not 0)
            x3 = offset * np.sin(tilt*dtor) * np.sin((azimuth)*dtor)
            y3 = offset * np.sin(tilt*dtor) * np.cos((azimuth)*dtor)
            z3 = offset * np.cos(tilt*dtor)

            
            xstart = x1 + x2 + x3
            ystart = y1 + y2 + y3
            zstart = height + z1 + z2 + z3
                        
            xinc = -(sceney/(sensorsy + 1.0)) * np.cos((tilt)*dtor) * np.sin((azimuth)*dtor)
            yinc = -(sceney/(sensorsy + 1.0)) * np.cos((tilt)*dtor) * np.cos((azimuth)*dtor) 
            zinc = (sceney/(sensorsy + 1.0)) * np.sin(tilt*dtor) 
                     
            if debug is True:           
                print( "Azimuth", azimuth)
                print( "Coordinate Center Point of Desired Panel before azm rotation", x0,y0)
                print( "Coordinate Center Point of Desired Panel after azm rotation", x1,y1)               
                print( "Edge of Panel", x2, y2, z2)                
                print( "Offset Shift", x3, y3, z3)                
                print( "Final Start Coordinate", xstart, ystart, zstart)
                print( "Increase Coordinates", xinc, yinc, zinc ) 
            
            frontscan = {'xstart': xstart+xinc, 'ystart':   ystart+yinc, 
                         'zstart': zstart + zinc + 0.06,
                         'xinc':xinc, 'yinc': yinc, 
                         'zinc':zinc , 'Nx': 1, 'Ny':sensorsy, 'Nz':1, 'orient':'0 0 -1' }
            backscan = {'xstart':xstart+xinc, 'ystart':  ystart+yinc, 
                         'zstart': zstart + zinc - 0.03,
                         'xinc':xinc, 'yinc': yinc, 
                         'zinc':zinc, 'Nx': 1, 'Ny':sensorsy, 'Nz':1, 'orient':'0 0 1' }
                
        return frontscan, backscan

    def analysis(self, octfile, name, frontscan, backscan, plotflag=False, accuracy='low'):
        '''
        analysis(octfile,name,frontscan,backscan,plotflag, accuracy)
        general analysis where linescan is passed in
        
        pass in the linepts structure of the view along with a title string for the plots
        note that the plots appear in a blocking way unless you call pylab magic in the beginning.
        
        Parameters
        ------------
        octfile     - filename and extension of .oct file
        name        - string name to append to output files
        frontscan   - scene.frontscan object 
        backscan    - scene.backscan object
        plotflag    - true or false - include plot of resulting irradiance
        accuracy    - either 'low' (default - faster) or 'high' (better for low light)
        
        Returns
        -------
        None.  file saved in \results\irr_name.csv
        '''
        # 
        if octfile is None:
            print('Analysis aborted - no octfile \n')
            return None, None
        linepts = self.linePtsMakeDict(frontscan)
        frontDict = self.irrPlotNew(octfile,linepts,name+'_Front',plotflag=plotflag, accuracy = accuracy)        
      
        #bottom view. 
        linepts = self.linePtsMakeDict(backscan)
        backDict = self.irrPlotNew(octfile,linepts,name+'_Back',plotflag = plotflag, accuracy = accuracy)
        # don't save if irrPlotNew returns an empty file.
        if frontDict is not None:
            self.saveResults(frontDict, backDict,'irr_%s.csv'%(name) )

        return frontDict, backDict

def runJob(daydate):
        ''' 
        runjob(daydate)
        runJob routine for the HPC, assigns each daydate to a different node and performs all the 
        bifacial radiance tasks.        
        
        Parameters
        ------------
        daydate     - string 'MM_dd' corresponding to month_day i.e. '02_17' February 17th.
        '''
        
        try:
                slurm_nnodes = int(os.environ['SLURM_NNODES'])
        except:
                print("Slurm environment not set. Are you running this in a job?")
                slurm_nnodes = 1 # Doing this instead of the exit allows it to run when not in slurm at regular speed for when you are testing stuff.
                #exit(1)

        print("entering runJob on node %s" % slurm_nnodes)
        metdata = demo.readEPW(epwfile=epwfile, hpc=hpc, daydate=daydate)
        trackerdict = demo.set1axis(cumulativesky=cumulativesky, axis_azimuth=axis_azimuth, limit_angle=limit_angle, angledelta=angledelta, backtrack=backtrack, gcr=gcr)
        trackerdict = demo.gendaylit1axis(hpc=hpc)
        trackerdict = demo.makeScene1axis(trackerdict=trackerdict, moduletype=moduletype, sceneDict=sceneDict, cumulativesky=cumulativesky, hpc=hpc) 
        demo.makeOct1axis(trackerdict, hpc=True)
        trackerdict = demo.analysis1axis(trackerdict, modWanted=modWanted, rowWanted=rowWanted, sensorsy=sensorsy)


def hpcExample():   
    ''' Example of HPC Job call
    
    This allocates the day_dates generated to the different codes in as many nodes are available. 
    Works inside and outside of slurm for testing (but set FullYear to False so it only does two days)
    Full year takes 1 min in 11 Nodes.
           
    -->> Variables stored in input_bf.py     SO:
    #Modify this on top:    
    if __name__ == "__main__": #in case this is run as a script not a module.
        from readepw import readepw  
        from load import loadTrackerDict
        from input_bf import *

    else: # module imported or loaded normally
        from bifacial_radiance.readepw import readepw # epw file reader from pvlib development forums  #module load format
        from bifacial_radiance.load import loadTrackerDict
        from bifacial_radiance.input_bf import *
            
    Procedure for a Full Year Run (~1 min in 11 nodes of 36 cores each > 365 days):
    -connect to Eagle
    - $ cd bifacial_radiance/bifacial_radiance
    - $ srun -A pvsoiling -t 5 -N 11 --pty bash                  
    - $ module load conda
    - $ . activate py3
    - $ srun bifacial_radiance2.py
    
    
    Procedure for testing before joining SLURM:
    - $ cd bifacial_radiance/bifacial_radiance
    - $ module load conda
    - $ . activate py3
    - $ nano bifacial_radiance.py    
             change fullYear to False.
    - $ python bifacial_radiance2.py       
    
    
    Other important random notes:
           Do not load conda twice nor activate .py3 twice.
           (following above) Either activate conda or .py3 in the login node or on the slurm
    
    TO DO:
    # Test as a function (I usually replace the main section's content with this function's content. 
    # Figure why loading conda twice crashes
    # Do a batch file to run this maybe?
    # More elegant way to read values from .py than importing (only works on declarations at the beginning)
    
    
    '''
    import multiprocessing as mp

    daylist = []
    
    fullYear = True # running faster testing on HPC ~ only 2 days.
    
    if fullYear:
        start = datetime.datetime.strptime("01-01-2014", "%d-%m-%Y")
        end = datetime.datetime.strptime("31-12-2014", "%d-%m-%Y") # 2014 not a leap year.
        daylist.append('12_31')     # loop doesn't add last day. Adding it at the beginning because why not.
        daylimit = 365
    else:
        start = datetime.datetime.strptime("14-02-2014", "%d-%m-%Y")
        end = datetime.datetime.strptime("26-02-2014", "%d-%m-%Y") # 2014 not a leap year.
        daylimit = 1
    date_generated = [start + datetime.timedelta(days=x) for x in range(0, (end-start).days)]
    for date in date_generated:
        daylist.append(date.strftime("%m_%d"))

    #  print("This is daydate %s" % (daydate))
    demo = RadianceObj(simulationname,path=testfolder)
    demo.setGround(albedo)
#   HPC IMPORTANT NOTE:
#   Multiple Nodes get confused when trying to write the JSON at the same time,
#    so make sure moduletype is created before running slurm job for it to work.
#   2 DO: Fix at some point of course.
#    moduleDict=demo.makeModule(name=moduletype,x=x,y=y,bifi=bifi, 
#                           torquetube=torqueTube, diameter = diameter, tubetype = tubetype, 
#                           material = torqueTubeMaterial, zgap = zgap, numpanels = numpanels, ygap = ygap, 
#                           rewriteModulefile = True, xgap=xgap, 
#                           axisofrotationTorqueTube=axisofrotationTorqueTube, cellLevelModule=cellLevelModule, 
#                           numcellsx=numcellsx, numcellsy = numcellsy)
    sceneDict = {'module_type':moduletype, 'pitch': pitch, 'hub_height':hub_height, 'nMods':nMods, 'nRows':nRows}
    
    cores = mp.cpu_count()
    pool = mp.Pool(processes=cores)
    res = None

    try:
        nodeID = int(os.environ['SLURM_NODEID'])
    except:
        nodeID = 0 # in case testing for hpc not on slurm yet. 
    
    day_index = (36 * (nodeID))

    for job in range(cores):
        if day_index+job>daylimit:
            break
        pool.apply_async(runJob, (daylist[day_index+job],))
        
    pool.close()
    pool.join()
    pool.terminate()

if __name__ == "__main__":
    '''
    Example of how to run a Radiance routine for a simple rooftop bifacial system

    '''
        
#    testfolder = _interactive_directory(title = 'Select or create an empty directory for the Radiance tree')
    testfolder = r'C:\Users\sayala\Documents\RadianceScenes\Demo3'
    demo = RadianceObj('simple_panel',path = testfolder)  # Create a RadianceObj 'object'

#    A=load_inputvariablesfile()
    

    demo.setGround(0.62) # input albedo number or material name like 'concrete'.  To see options, run this without any input.
    try:
        epwfile = demo.getEPW(37.5,-77.6) # pull TMY data for any global lat/lon
    except:
        pass
        
    metdata = demo.readEPW(epwfile) # read in the EPW weather data from above
    #metdata = demo.readTMY() # select a TMY file using graphical picker
    # Now we either choose a single time point, or use cumulativesky for the entire year. 
    cumulativeSky = True
    if cumulativeSky:
        demo.genCumSky(demo.epwfile) # entire year.
    else:
        demo.gendaylit(metdata,4020)  # Noon, June 17th

        
    # create a scene using panels in landscape at 10 deg tilt, 1.5m pitch. 0.2 m ground clearance
    moduletype = 'test'
    moduleDict = demo.makeModule(name = moduletype, x = 1.59, y = 0.95 )
    sceneDict = {'tilt':10,'pitch':1.5,'clearance_height':0.2,'azimuth':180, 'nMods': 20, 'nRows': 7}          
    scene = demo.makeScene(moduletype=moduletype, sceneDict=sceneDict) #makeScene creates a .rad file with 20 modules per row, 7 rows.    
    octfile = demo.makeOct(demo.getfilelist())  # makeOct combines all of the ground, sky and object files into a .oct file.

    '''
    analysis = AnalysisObj(octfile, demo.name)  # return an analysis object including the scan dimensions for back irradiance
    #analysis.moduleAnalysis(octfile, demo.name, sceneDict, moduleDict, modwanted=0, rowwanted=0)
    frontscan, backscan = analysis.moduleAnalysis(scene, modWanted=None, rowWanted=None, sensorsy=9)
    analysis.analysis(octfile, demo.name, frontscan, backscan)

    print('Annual bifacial ratio average:  %0.3f' %( sum(analysis.Wm2Back) / sum(analysis.Wm2Front) ) )
    
    
    
    print('\n***Starting 1-axis tracking simulation***\n')
    trackerdict = demo.set1axis(metdata, limit_angle = 60, backtrack = True, gcr = 0.4)
    trackerdict = demo.genCumSky1axis(trackerdict)
    # create a scene using panels in portrait, 2m hub height, 0.4 GCR. NOTE: clearance needs to be calculated at each step. hub height is constant
    sceneDict = {'hub_height':2.0,'nMods': 10, 'nRows': 3, 'gcr':0.4, 'pitch': 0.95/0.4}          

    trackerdict = demo.makeScene1axis(trackerdict,moduletype,sceneDict) #makeScene creates a .rad file with 20 modules per row, 7 rows.
    trackerdict = demo.makeOct1axis(trackerdict)
    trackerdict = demo.analysis1axis(trackerdict, modWanted=None, rowWanted=None, sensorsy=9 )

    print('Annual RADIANCE bifacial ratio for 1-axis tracking: %0.3f' %(sum(demo.Wm2Back)/sum(demo.Wm2Front)) )

'''
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
    
    SceneObj:    scene information including array configuration (row spacing, ground height)
    
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
else: # module imported or loaded normally
    from bifacial_radiance.readepw import readepw # epw file reader from pvlib development forums  #module load format
    from bifacial_radiance.load import loadTrackerDict



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
        Pickle the radiance object for further use
        
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
        
    def loadtrackerdict(self, trackerdict, fileprefix=None):
        '''
        use bifacial_radiance.load._loadtrackerdict to browse the results directory
        and load back any results saved in there.
        
        '''
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

    def readEPW(self,epwfile=None):
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
        (tmydata,metadata) = readepw(epwfile)
        # rename different field parameters to match output from pvlib.tmy.readtmy: DNI, DHI, DryBulb, Wspd
        tmydata.rename(columns={'Direct normal radiation in Wh/m2':'DNI','Diffuse horizontal radiation in Wh/m2':'DHI',
                                'Dry bulb temperature in C':'DryBulb','Wind speed in m/s':'Wspd',
                                'Global horizontal radiation in Wh/m2':'GHI'}, inplace=True)
           
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
        import pytz
        import pvlib

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
        datetime = pd.to_datetime(metdata.datetime[timeindex])
        try:  # make sure the data is tz-localized.
            datetimetz = datetime.tz_localize(pytz.FixedOffset(tz*60))  # either use pytz.FixedOffset (in minutes) or 'Etc/GMT+5'
        except:  # data is tz-localized already. Just put it in local time.
            datetimetz = datetime.tz_convert(pytz.FixedOffset(tz*60))  
        
        #Offset so it matches the single-axis tracking sun position calculation considering use of weather files
        datetimetz=datetimetz-pd.Timedelta(minutes = 30)
        
        # get solar position zenith and azimuth based on site metadata
        #solpos = pvlib.irradiance.solarposition.get_solarposition(datetimetz,lat,lon,elev)
        solpos = pvlib.irradiance.solarposition.get_solarposition(datetimetz,lat,lon,elev)
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
         
        skyname = os.path.join(sky_path,"sky2_%s.rad" %(self.name))
            
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
        
    def set1axis(self, metdata=None, axis_azimuth=180, limit_angle=45, angledelta=5, backtrack=True, gcr=1.0/3.0, cumulativesky=True ):
        '''
        RadianceObj set1axis
        Set up geometry for 1-axis tracking.  Pull in tracking angle details from 
        pvlib, create multiple 8760 metdata sub-files where datetime of met data 
        matches the tracking angle.  Returns 'trackerdict' which has keys equal to 
        either the tracker angles (gencumsky workflow) or timestamps (gendaylit hourly
        workflow)
        
        
        Parameters
        ------------
        cumulativesky       # boolean. whether individual csv files are created with constant tilt angle for the cumulativesky approach.
                            # if false, the gendaylit tracking approach must be used.
        metdata            MetObj to set up geometry.  default = self.metdata
        axis_azimuth       orientation axis of tracker torque tube. Default North-South (180 deg)
        limit_angle        +/- limit angle of the 1-axis tracker in degrees. Default 45 
        angledelta         degree of rotation increment to parse irradiance bins. Default 5 degrees
                             (0.4 % error for DNI).  Other options: 4 (.25%), 2.5 (0.1%).  
                             Note: the smaller the angledelta, the more simulations must be run
        backtrack          Whether backtracking is enabled (default = True)
        gcr                 Ground coverage ratio for calculation backtracking.
        
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
        trackerdict = metdata.set1axis(cumulativesky = cumulativesky, axis_azimuth = axis_azimuth, limit_angle = limit_angle, angledelta = angledelta, backtrack = backtrack, gcr = gcr)
        self.trackerdict = trackerdict
        self.cumulativesky = cumulativesky
        
        return trackerdict
    
    def gendaylit1axis(self, metdata=None, trackerdict=None, startdate=None, enddate=None, debug=False):
        '''
        1-axis tracking implementation of gendaylit.
        Creates multiple sky files, one for each time of day.
        
        Parameters
        ------------
        metdata:   output from readEPW or readTMY.  Needs to have metdata.set1axis() run on it.
        startdate:  starting point for hourly data run
        enddate:    ending date for hourly data run
            
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
            datetemp = parser.parse(startdate)
            startindex = (int(datetemp.strftime('%j')) - 1) * 24 -1
        else:
            startindex = 0
        if enddate is not None:
            datetemp = parser.parse(enddate)
            endindex = (int(datetemp.strftime('%j')) ) * 24   # include all of enddate
        else:
            endindex = 8760            
        
        if debug is False:
            print('Creating ~4000 skyfiles.  Takes 1-2 minutes')
        count = 0  # counter to get number of skyfiles created, just for giggles
        for i in range(startindex,endindex):
            time = metdata.datetime[i]
            filename = str(time)[5:-12].replace('-','_').replace(' ','_')
            self.name = filename

            #check for GHI > 0
            if metdata.ghi[i] > 0:
                skyfile = self.gendaylit(metdata,i, debug=debug)   # Implemented gendaylit2 to use PVLib angles like tracker.     
                trackerdict[filename]['skyfile'] = skyfile
                count +=1
            
        print('Created {} skyfiles in /skies/'.format(count))
        return trackerdict
        
    def genCumSky1axis(self, trackerdict=None):
        '''
        1-axis tracking implementation of gencumulativesky.
        Creates multiple .cal files and .rad files, one for each tracker angle.
        
        Parameters
        ------------
        trackerdict:   output from MetObj.set1axis()
            
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
            skyfile = self.genCumSky(epwfile = csvfile,  savefile = savefile)
            trackerdict[theta]['skyfile'] = skyfile
            print('Created skyfile %s'%(skyfile))
        # delete default skyfile (not strictly necessary)
        self.skyfiles = None
        self.trackerdict = trackerdict
        return trackerdict
        
        
    def makeOct(self, filelist=None, octname=None):
        ''' 
        combine everything together into a .oct file
        
        Parameters
        ------------
        filelist:  overload files to include.  otherwise takes self.filelist
        octname:   filename (without .oct extension)
        
        Returns: Tuple
        -------
        octname:   filename of .oct file in root directory including extension
        err:        Error message returned from oconv (if any)
        '''
        if filelist is None:
            filelist = self.getfilelist()
        if octname is None:
            octname = self.name
            
        
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
        
    def makeOct1axis(self, trackerdict=None, singleindex=None, customname=None):
        ''' 
        combine files listed in trackerdict into multiple .oct files
        
        Parameters
        ------------
        trackerdict:    Output from makeScene1axis
        singleindex:   Single index for trackerdict to run makeOct1axis in single-value mode (new in 0.2.3)
        customname:     Custom text string added to the end of the OCT file name.
        
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
                trackerdict[index]['octfile'] = self.makeOct(filelist,octname)
            except KeyError as e:                  
                print('Trackerdict key error: {}'.format(e))
        
        return trackerdict

        
    """
    def analysis(self, octfile=None, name=None):
        '''
        default to AnalysisObj.PVSCanalysis(self.octfile, self.name)
        Not sure how wise it is to have RadianceObj.analysis - perhaps this is best eliminated entirely?
        '''
        if octfile is None:
            octfile = self.octfile
        if name is None:
            name = self.name
        
        analysis_obj = AnalysisObj(octfile, name)
        analysis_obj.PVSCanalysis(octfile, name)
         
        return analysis_obj
    """
    def makeModule(self,name=None,x=1,y=1,bifi=1, orientation=None, modulefile=None, text=None, customtext='', 
               torquetube=False, diameter=0.1, tubetype='Round', material='Metal_Grey', xgap=0.01, ygap=0.0, zgap=0.1, numpanels=1, rewriteModulefile=True, tubeZgap=None, panelgap=None):
        '''
        add module details to the .JSON module config file module.json
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
        x       # width of module (meters).
        y       # height of module (meters).
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
        zgap          # distance behind the modules in the z-direction to the edge of the tube (m)
        numpanels     #int. number of modules arrayed in the Y-direction. e.g. 1-up or 2-up, etc.
        ygap          #float. gap between modules arrayed in the Y-direction if any.
        xgap          #float. "Panel space in X". Separation between modules in a row. 
                      #DEPRECATED INPUTS: 
        tubeZgap      #float. zgap. deprecated. 
        panelgap      #float. ygap. deprecated. 
        
        Returns: None
        -------
        
        '''
        if name is None:
            print("usage:  makeModule(name,x,y, bifi = 1, modulefile = '\objects\*.rad', "+
                    "torquetube=False, diameter = 0.1 (torque tube dia.), tubetype = 'Round' (or 'square', 'hex'), material = 'Metal_Grey' (or 'black'), zgap = 0.1 (module offset)"+
                    "numpanels = 1 (# of panels in portrait), ygap = 0.05 (slope distance between panels when arrayed), rewriteModulefile = True (or False)")
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
        ht = zgap
        diam = diameter
        Ny = numpanels    
        import math
        
        if text is None:
            text = '! genbox black PVmodule {} {} 0.02 | xform -t {} 0 0 '.format(x, y, -x/2.0)
            text += '-a {} -t 0 {} 0'.format(Ny,y+ygap) 
            
            if torquetube is True:
                if tubetype.lower() =='square':
                    text = text+'\r\n! genbox {} tube1 {} {} {} | xform -t {} {} {}'.format(
                            material, x+xgap, diam, diam, -(x+xgap)/2.0, -diam/2+Ny/2*y+(Ny-1)/2*ygap, -diam-ht)  

                elif tubetype.lower()=='round':
                    text = text+'\r\n! genrev {} tube1 t*{} {} 32 | xform -ry 90 -t {} {} {}'.format(
                            material, x+xgap, diam/2.0,  -(x+xgap)/2.0, -diam/2.0+Ny/2.0*y+(Ny-1.0)/2.0*ygap, -diam/2.0-ht)
                    
                elif tubetype.lower()=='hex':
                    radius = 0.5*diam
                    text = text+'\r\n! genbox {} hextube1a {} {} {} | xform -t {} {} {}'.format(
                            material, x+xgap, radius, radius*math.sqrt(3), -(x+xgap)/2.0, -radius/2.0+Ny/2.0*y+(Ny-1.0)/2.0*ygap, -radius*math.sqrt(3.0)-ht)

                    # Create, translate to center, rotate, translate back to prev. position and translate to overal module position.
                    text = text+'\r\n! genbox {} hextube1b {} {} {} | xform -t {} {} {} -rx 60 -t 0 {} {}'.format(
                            material, x+xgap, radius, radius*math.sqrt(3), -(x+xgap)/2.0, -radius/2.0, -radius*math.sqrt(3.0)/2.0, radius/2.0+(-radius/2.0+Ny/2.0*y+(Ny-1.0)/2.0*ygap), (radius*math.sqrt(3.0)/2.0)-radius*math.sqrt(3.0)-ht)
                    
                    text = text+'\r\n! genbox {} hextube1c {} {} {} | xform -t {} {} {} -rx -60  -t 0 {} {}'.format(
                            material, x+xgap, radius, radius*math.sqrt(3), -(x+xgap)/2.0, -radius/2.0, -radius*math.sqrt(3.0)/2.0, radius/2.0+(-radius/2.0+Ny/2.0*y+(Ny-1.0)/2.0*ygap), (radius*math.sqrt(3.0)/2.0)-radius*math.sqrt(3.0)-ht)

                elif tubetype.lower()=='oct':
                    radius = 0.5*diam   
                    s = diam / (1+math.sqrt(2.0))   # s
                    
                    text = text+'\r\n! genbox {} octtube1a {} {} {} | xform -t {} {} {}'.format(
                            material, x+xgap, s, diam, -(x+xgap)/2.0, -s/2.0+Ny/2.0*y+(Ny-1.0)/2.0*ygap, -diam-ht)

                    # Create, translate to center, rotate, translate back to prev. position and translate to overal module position.
                    text = text+'\r\n! genbox {} octtube1b {} {} {} | xform -t {} {} {} -rx 45 -t 0 {} {}'.format(
                            material, x+xgap, s, diam, -(x+xgap)/2.0, -s/2.0, -radius, s/2.0+(-s/2.0+Ny/2.0*y+(Ny-1.0)/2.0*ygap), radius-diam-ht)
                    
                    text = text+'\r\n! genbox {} octtube1c {} {} {} | xform -t {} {} {} -rx 90  -t 0 {} {}'.format(
                            material, x+xgap, s, diam, -(x+xgap)/2.0, -s/2.0, -radius, s/2.0+(-s/2.0+Ny/2.0*y+(Ny-1.0)/2.0*ygap), radius-diam-ht)
                    
                    text = text+'\r\n! genbox {} octtube1d {} {} {} | xform -t {} {} {} -rx 135  -t 0 {} {}'.format(
                            material, x+xgap, s, diam, -(x+xgap)/2.0, -s/2.0, -radius, s/2.0+(-s/2.0+Ny/2.0*y+(Ny-1.0)/2.0*ygap), radius-diam-ht)
                    
                else:
                    raise Exception("Incorrect torque tube type.  Available options: 'square' or 'round'.  Value entered: {}".format(tubetype))
            
            text += customtext  # For adding any other racking details at the module level that the user might want.
            
        moduledict = {'x':x,
                      'y':y,
                      'scenex': x+xgap,
                      'sceney': y*Ny + ygap*(Ny-1),
                      'scenez': zgap+diam,
                      'numpanels':Ny,
                      'bifi':bifi,
                      'text':text,
                      'modulefile':modulefile
                      }
        
        filedir = os.path.join(DATA_PATH,'module.json')  # look in global DATA_PATH for module config file
        with open( filedir ) as configfile:
            data = json.load(configfile)    

        
        data.update({name:moduledict})    
        with open(os.path.join(DATA_PATH,'module.json') ,'w') as configfile:
            json.dump(data,configfile)
        
        print('Module {} successfully created'.format(name))
        
        return moduledict


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
 
        
    def makeScene(self, moduletype=None, sceneDict=None, nMods=20, nRows=7, sensorsy=9, modwanted=None, rowwanted=None ):
        '''
        return a SceneObj which contains details of the PV system configuration including 
        tilt, row pitch, height, nMods per row, nRows in the system...
        
        Parameters
        ------------
        moduletype: string name of module created with makeModule()
        sceneDict:  dictionary with keys:[tilt] [height] [pitch] [azimuth]
        nMods:      int number of modules per row (default = 20)
        nRows:      int number of rows in system (default = 7) 
        sensorsy:   int number of scans in the y direction (up tilted module chord, default = 9)
        modwanted:  where along row does scan start, Nth module along the row (default middle module)
        rowwanted:   which row is scanned? (default middle row)        

        
        Returns: SceneObj 'scene' with configuration details
        -------

        '''
        if moduletype is None:
            print('makeScene(moduletype, sceneDict, nMods, nRows).  Available moduletypes: monopanel, simple_panel' ) #TODO: read in config file to identify available module types
            return
        self.scene = SceneObj(moduletype)
        
        if sceneDict is None:
            print('makeScene(moduletype, sceneDict, nMods, nRows).  sceneDict inputs: .tilt .height .pitch .azimuth')

        if 'orientation' in sceneDict:
            if sceneDict['orientation'] == 'landscape':
                raise Exception('\n\n ERROR: Orientation format has been deprecated since version 0.2.4. If you want to flip your modules, on makeModule switch the x and y values. X value is the size of the panel along the row, so for a "landscape" panel x should be > than y.\n\n')
        #if sceneDict.has_key('azimuth') is False:
        if 'azimuth' not in sceneDict:
            sceneDict['azimuth'] = 180
            
        if modwanted is None:
            modwanted = round(nMods / 2.0)
        if rowwanted is None:
            rowwanted = round(nRows / 2.0)
            
        self.sceneRAD = self.scene.makeSceneNxR(tilt = sceneDict['tilt'], height = sceneDict['height'], pitch = sceneDict['pitch'],
                                                azimuth = sceneDict['azimuth'], nMods = nMods, nRows = nRows,
                                                sensorsy = sensorsy, modwanted = modwanted, rowwanted = rowwanted )
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
    
    def makeScene1axis(self, trackerdict=None, moduletype=None, sceneDict=None, nMods=20, nRows=7, sensorsy=9, modwanted=None, rowwanted=None, cumulativesky=None):
        '''
        create a SceneObj for each tracking angle which contains details of the PV 
        system configuration including row pitch, hub height, nMods per row, nRows in the system...
        
        Parameters
        ------------
        trackerdict: output from GenCumSky1axis
        moduletype: string name of module created with makeModule()
        sceneDict:  dictionary with keys:[tilt] [height] [pitch] [azimuth]
        nMods:      int number of modules per row (default = 20)
        nRows:      int number of rows in system (default = 7) 
        sensorsy:   int number of scans in the y direction (up tilted module chord, default = 9)
        modwanted:  where along row does scan start, Nth module along the row (default middle module)
        rowwanted:   which row is scanned? (default middle row)  
        cumulativesky:  bool: use cumulativesky or not?
        
        Returns
        -----------
        trackerdict: append the following keys :
            'radfile': directory where .rad scene file is stored
            'scene' : SceneObj for each tracker theta
            'ground_clearance' : calculated ground clearance based on hub height, tilt angle and module length
        '''
        import math
        
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
        
        if sceneDict is None:
            print('usage:  makeScene1axis(moduletype, sceneDict, nMods, nRows).  sceneDict inputs: .tilt .height .pitch .azimuth')
            return

        if 'orientation' in sceneDict:
            if sceneDict['orientation'] == 'landscape':
                raise Exception('\n\n ERROR: Orientation format has been deprecated since version 0.2.4. If you want to flip your modules, on makeModule switch the x and y values. X value is the size of the panel along the row, so for a "landscape" panel x should be > than y.\n\n')
        if modwanted is None:
            modwanted = round(nMods / 2.0)
        if rowwanted is None:
            rowwanted = round(nRows / 2.0)
        
        if cumulativesky is True:        # cumulativesky workflow
            print('\nMaking .rad files for cumulativesky 1-axis workflow')
            for theta in trackerdict:
                scene = SceneObj(moduletype)
                surf_azm = trackerdict[theta]['surf_azm']
                surf_tilt = trackerdict[theta]['surf_tilt']
                radname = '1axis%s'%(theta,)
                hubheight = sceneDict['height'] #the hub height is the tracker height at center of rotation.
                # Calculate the ground clearance height based on the hub height. Add abs(theta) to avoid negative tilt angle errors
                height = hubheight - 0.5* math.sin(abs(theta) * math.pi / 180) *  scene.sceney
                radfile = scene.makeSceneNxR(tilt = surf_tilt, height = height, pitch = sceneDict['pitch'], azimuth = surf_azm, 
                                            nMods = nMods, nRows = nRows, radname = radname,  
                                                    sensorsy = sensorsy, modwanted = modwanted, rowwanted = rowwanted )
                trackerdict[theta]['radfile'] = radfile
                trackerdict[theta]['scene'] = scene
                trackerdict[theta]['ground_clearance'] = height
            print('{} Radfiles created in /objects/'.format(trackerdict.__len__()))
        
        else:  #gendaylit workflow
            print('\nMaking ~4000 .rad files for gendaylit 1-axis workflow (this takes a minute..)')
            count = 0
            for time in trackerdict:
                scene = SceneObj(moduletype)
                surf_azm = trackerdict[time]['surf_azm']
                surf_tilt = trackerdict[time]['surf_tilt']
                theta = trackerdict[time]['theta']
                radname = '1axis%s'%(time,)
                hubheight = sceneDict['height'] #the hub height is the tracker height at center of rotation.
                # Calculate the ground clearance height based on the hub height. Add abs(theta) to avoid negative tilt angle errors
                height = hubheight - 0.5* math.sin(abs(theta) * math.pi / 180) *  scene.sceney
                
                if trackerdict[time]['ghi'] > 0:
                    radfile = scene.makeSceneNxR(tilt = surf_tilt, height = height, pitch = sceneDict['pitch'], azimuth = surf_azm, 
                                                nMods = nMods, nRows = nRows, radname = radname,  
                                                        sensorsy = sensorsy, modwanted = modwanted, rowwanted = rowwanted )
                    trackerdict[time]['radfile'] = radfile
                    trackerdict[time]['scene'] = scene
                    trackerdict[time]['ground_clearance'] = height
                    count+=1
            print('{} Radfiles created in /objects/'.format(count))    
                
        
        self.trackerdict = trackerdict
        return trackerdict#self.scene            
            
    
    def analysis1axis(self, trackerdict=None, singleindex=None, accuracy='low', customname=None):
        '''
        loop through trackerdict and run linescans for each scene and scan in there.
        
        Parameters
        ----------------
        trackerdict
        singleindex         :For single-index mode, just the one index we want to run (new in 0.2.3)
        accuracy            : 'low' or 'high' - resolution option used during irrPlotNew and rtrace
        customname          : Custom text string to be added to the file name for the results .CSV files
        
        Returns
        ----------------
        trackerdict with new keys: 
            'AnalysisObj'  : analysis object for this tracker theta
            'Wm2Front'     : list of nine front Wm2 irradiances
            'Wm2Back'      : list of nine rear Wm2 irradiances
            'backRatio'    : list of nine rear irradiance ratios
       
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

        
        frontWm2 = 0 # container for tracking front irradiance across module chord. Dynamically size based on first analysis run
        backWm2 = 0 # container for tracking rear irradiance across module chord.


        for index in trackerkeys:   # either full list of trackerdict keys, or single index
            name = '1axis_%s%s'%(index,customname)
            octfile = trackerdict[index]['octfile']
            if octfile is None:
                continue  # don't run analysis if the octfile is none
            try:  # look for missing data
                analysis = AnalysisObj(octfile,name)            
                frontscan = trackerdict[index]['scene'].frontscan
                backscan = trackerdict[index]['scene'].backscan
                name = '1axis_%s%s'%(index,customname,)
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
            
    def getTrackingGeometryTimeIndex(self, metdata = None, timeindex=4020, interval = 60, angledelta = 5, roundTrackerAngleBool = True, axis_tilt = 0.0, axis_azimuth = 180.0, limit_angle = 45.0, backtrack = True, gcr = 1.0/3.0, hubheight = 1.45, sceney = 1.980):

        '''              
        Helper subroutine to return 1-axis tracker tilt, azimuth data, and panel clearance for a specific point in time.
        
        Parameters
        ------------
        same as pvlib.tracking.singleaxis, plus:

        metdata:  MetObj object with 8760 list of dni, dhi, ghi and location
        timeindex: index from 0 to 8759 of EPW timestep
        interval: default 60 for wheater files. Will be used to offset sun position and tracker position to half an hour previous.
            
        angledelta:  angle in degrees to round tracker_theta to.  This is for  
        
        Returns
        -------
        tracker_theta:   tracker angle at specified timeindex
        tracker_height:  tracker clearance height
        tracker_azimuth_ang

        
        Parameters
        ------------
        axis_azimuth         # orientation axis of tracker torque tube. Default North-South (180 deg)
        axis_tilt            # tilt of tracker torque tube. Default is 0.
        limit_angle      # +/- limit angle of the 1-axis tracker in degrees. Default 45 
        angledelta      # degree of rotation increment to parse irradiance bins. Default 5 degrees
                        #  (0.4 % error for DNI).  Other options: 4 (.25%), 2.5 (0.1%).  
                        #  Note: the smaller the angledelta, the more simulations must be run
        roundTrackerAngleBool # Boolean to perform rounding or not of calculated angle to specified roundTrackerAngle
        backtrack       # backtracking option
        gcr             # Ground coverage ratio
        hubheight       # on tracking systems height is given by the hubheight
        sceney          # Collector width (CW) or slope (size of the panel) perpendicular to the rotation axis.

        Returns
        -------
        tracker_theta           # tilt for that timeindex 
        tracker_height,         # clearance height for that time index, based on hub height and tracker_theta calculated.
        tracker_azimuth_ang     # azimuth_angle for that time index (facing East or West))
        '''
                    
        import pytz
        import pvlib
        import math

        #month = metdata.datetime[timeindex].month
        #day = metdata.datetime[timeindex].day
        #hour = metdata.datetime[timeindex].hour
        #minute = metdata.datetime[timeindex].minute
        tz = metdata.timezone
        lat = metdata.latitude
        lon = metdata.longitude
        elev = metdata.elevation
        #elev = metdata.location.elevation

        datetime = pd.to_datetime(metdata.datetime[timeindex])
        try:  # make sure the data is tz-localized.
            datetimetz = datetime.tz_localize(pytz.FixedOffset(tz*60))  # either use pytz.FixedOffset (in minutes) or 'Etc/GMT+5'
        except:  # data is tz-localized already. Just put it in local time.
            datetimetz = datetime.tz_convert(pytz.FixedOffset(tz*60))  
        
        #Offset so it matches the single-axis tracking sun position calculation considering use of weather files
        datetimetz=datetimetz-pd.Timedelta(minutes = int(interval/2))
        
        # get solar position zenith and azimuth based on site metadata
        #solpos = pvlib.irradiance.solarposition.get_solarposition(datetimetz,lat,lon,elev)
        solpos = pvlib.irradiance.solarposition.get_solarposition(datetimetz,lat,lon,elev)
        trackingdata = pvlib.tracking.singleaxis(solpos['zenith'], solpos['azimuth'], axis_tilt, axis_azimuth, limit_angle, backtrack, gcr)
        trackingdata.index = trackingdata.index + pd.Timedelta(minutes = 30) # adding delta so it goes back to original time
        theta = float(trackingdata['tracker_theta'])


        #Calculate Tracker Theta, and azimuth according to fixed-tilt bifacial_radiance definitions.                                
        if theta <= 0:
            tracker_azimuth_ang=90.0
            print ('For this timestamp, panels are facing East')
        else:
            tracker_azimuth_ang=270.0
            print ('For this timestamp, panels are facing West')
        
        if roundTrackerAngleBool:
            theta_round=round(theta/angledelta)*angledelta
            tracker_theta = abs(theta_round)
            print ('Tracker theta has been calculated to %0.3f and rounded to nearest tracking angle %0.1f' %(abs(theta), tracker_theta))
        else:
            tracker_theta = abs(theta)    
            print ('Tracker theta has been calculated to %0.3f, no rounding performed.' %(tracker_theta))
        
        #Calculate Tracker Height
        tracker_height = hubheight - 0.5* math.sin(tracker_theta * math.pi / 180) * sceney    
    
        print ('Module clearance height has been calculated to %0.3f, for this tracker theta.' %(tracker_height))
        
        return tracker_theta, tracker_height, tracker_azimuth_ang
            
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
        
        if moduletype is None:
            print('Usage: SceneObj(moduletype)\nNo module type selected. Available module types: {}'.format(modulenames))
            return
        else:
            if moduletype in modulenames:
                # read in module details from configuration file. 
                self.readModule(name = moduletype)
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
            moduledict = data[name]
            self.moduletype = name
            
            radfile = moduledict['modulefile']
            self.x = moduledict['x'] # width of module.
            self.y = moduledict['y'] # height of module.
            self.bifi = moduledict['bifi']  # bifaciality of the panel. Not currently used
            if 'scenex' in moduledict:
                self.scenex = moduledict['scenex']
            else:
                self.scenex = moduledict['x']
            if 'sceney' in moduledict:
                self.sceney = moduledict['sceney']
            else:
                self.sceney = moduledict['y']
            #
                    #create new .RAD file
            if not os.path.isfile(radfile):
                # py2 and 3 compatible: binary write, encode text first
                with open(radfile, 'wb') as f:
                    f.write(moduledict['text'].encode('ascii'))
            #if not os.path.isfile(radfile):
            #    raise Exception('Error: module file not found {}'.format(radfile))
            self.modulefile = radfile
            
            return moduledict
        else:
            print('Error: module name {} doesnt exist'.format(name))
            return {}
    
    def makeSceneNxR(self, tilt, height, pitch, azimuth=180, nMods=20, nRows=7, radname=None, sensorsy=9, modwanted=None, rowwanted=None, orientation=None):
        '''
        arrange module defined in SceneObj into a N x R array
        Valid input ranges: Tilt 0-90 degrees.  Azimuth 0-360 degrees
        Module definitions assume that the module .rad file is defined with zero tilt, centered along the x-axis of the module (+X/2, -X/2 on each side)
        Y-axis is assumed the bottom edge of the module is at y = 0, top of the module at y = Y.
        self.scenex is overall module width including xgap.
        self.sceney is overall series height of module(s) including gaps, multiple-up configuration, etc
        
        The returned scene has (0,0) coordinates centered at the center of the row selected in 'rowwanted' (middle row default)
        
        From v0.2.4 and prior, frontscan and backscan are calculated statically. 
        In v0.2.5, the scan will be calculated dynamically to clean up all of the messy geometry
                Parameters
        ------------
        nMods:   (int)   number of modules per row
        nRows:   (int)   number of rows in system
        radname: (string) default name to save radfile. If none, use moduletype by default
        sensorsy: (int)  number of datapoints to scan along the module chord. default: 9
        modwanted: (int) which module along the row to scan along.  Default round(nMods/2)
        rowwanted: (int) which row in the system to scan along.  Default round(nRows/2)
        
        
        Returns
        -------
        radfile: (string) filename of .RAD scene in /objects/
        
        '''
        DEBUG = False  # set to True to enable inline print statements
        if radname is None:
            radname =  str(self.moduletype).strip().replace(' ', '_')# remove whitespace
        if modwanted is None:
            modwanted = round(nMods / 2.0)
        if rowwanted is None:
            rowwanted = round(nRows / 2.0)
        #TODO:  tilt and Height sometimes come in as NaN's and crash rtrace. Maybe check for this?
            
        
        if orientation is not None:
            print ('\n\n WARNING: Orientation format has been deprecated since version 0.2.4. If you want to flip your modules, on makeModule switch the x and y values. X value is the size of the panel along the row, so for a "landscape" panel x should be > than y.\n\n')

        # assign inputs
        self.tilt = tilt
        self.height = height
        self.pitch = pitch
        self.azimuth = azimuth
        ''' INITIALIZE VARIABLES '''
        dtor = np.pi/180
        text = '!xform '
        
        # Making sure sensors and modules are floats and not ints for the position calculation
        sensorsy = sensorsy*1.0
        modwanted = modwanted*1.0
        rowwanted = rowwanted*1.0

        text += '-rx %s -t 0 0 %s ' %(tilt, height)
        # create nMods-element array along x, nRows along y. 1cm module gap.
        text += '-a %s -t %s 0 0 -a %s -t 0 %s 0 ' %(nMods, self.scenex, nRows, pitch)
        
        # azimuth rotation of the entire shebang. Select the row to scan here based on y-translation.
        text += '-i 1 -t %s %s 0 -rz %s ' %(-self.scenex*int(nMods/2), -pitch* (rowwanted - 1), 180-azimuth) 
        
        text += self.modulefile
        # save the .RAD file
        
        #radfile = 'objects\\%s_%s_%s_%sx%s.rad'%(radname,height,pitch, nMods, nRows)
        radfile = os.path.join('objects','%s_%0.5s_%0.5s_%sx%s.rad'%(radname,height,pitch, nMods, nRows) ) # update in 0.2.3 to shorten radnames
        
        if self.azimuth > 180:
            tf = -1
            sensorsyinv=sensorsy
            print(" \n\n Inverted \n\n")
        else:
            tf = 1
            sensorsyinv=1
            
        # py2 and 3 compatible: binary write, encode text first
        with open(radfile, 'wb') as f:
            f.write(text.encode('ascii'))
        # define the 9-point front and back scan. if tilt < 45  else scan z
        if tilt <= 60: #scan along y facing up/down.
            zinc =  self.sceney * np.sin(tilt*dtor) / (sensorsy + 1) # z increment for rear scan
            if DEBUG: print( zinc)
            if DEBUG: print ("ZINC\n")
            if abs(np.tan(azimuth*dtor) ) <=1: #(-45 <= (azimuth-180) <= 45) ):  # less than 45 deg rotation in z. still scan y
                if DEBUG: print ("\n\nCase 1\n\n ")
                #yinc = self.sceney / (sensorsy + 1) * np.cos(tilt*dtor) / np.cos((azimuth-180)*dtor)
                yinc = self.sceney / (sensorsy + 1) * np.cos(tilt*dtor) / np.cos((azimuth-180)*dtor)
                xstart = tf*-self.scenex * (modwanted - round(nMods/2) ) * np.cos((azimuth-180)*dtor)
                ystart =  self.sceney * sensorsyinv / (sensorsy + 1) * np.cos(tilt*dtor) / np.cos((azimuth-180)*dtor)
                
                self.frontscan = {'xstart': xstart, 'ystart': ystart, 
                             'zstart': height + self.sceney *np.sin(tilt*dtor) + 1,
                             'xinc':0, 'yinc':  yinc*tf, 
                             'zinc':0 , 'Nx': 1, 'Ny':int(sensorsy), 'Nz':1, 'orient':'0 0 -1' }
                #todo:  Update z-scan to allow scans behind racking.   
                self.backscan = {'xstart':xstart, 'ystart':  ystart, 
                             'zstart': height + self.sceney * np.sin(tilt*dtor) * sensorsyinv / (sensorsy + 1) - 0.03,
                             'xinc':0, 'yinc': yinc*tf, 
                             'zinc':zinc , 'Nx': 1, 'Ny':int(sensorsy), 'Nz':1, 'orient':'0 0 1' }
                             
            elif abs(np.tan(azimuth*dtor) ) > 1:  # greater than 45 deg azimuth rotation. scan x instead
                if DEBUG: print ("Case 2 ")
                xinc = self.sceney / (sensorsy + 1) * np.cos(tilt*dtor) / np.sin((azimuth-180)*dtor)
                xstart = self.sceney * sensorsyinv / (sensorsy + 1) * np.cos(tilt*dtor) / np.sin((azimuth-180)*dtor)
                ystart = tf*-self.scenex * (modwanted - round(nMods/2) ) * np.sin((azimuth-180)*dtor)
                self.frontscan = {'xstart': xstart, 'ystart':   ystart, 
                             'zstart': height + self.sceney *np.sin(tilt*dtor) + 1,
                             'xinc':xinc*tf, 'yinc': 0, 
                             'zinc':0 , 'Nx': sensorsy, 'Ny':1, 'Nz':1, 'orient':'0 0 -1' }
                self.backscan = {'xstart':xstart, 'ystart':  ystart, 
                             'zstart': height + self.sceney * np.sin(tilt*dtor) * sensorsyinv / (sensorsy + 1) - 0.03,
                             'xinc':xinc*tf, 'yinc': 0, 
                             'zinc':zinc*tf, 'Nx': sensorsy, 'Ny':1, 'Nz':1, 'orient':'0 0 1' }
            else: # invalid azimuth (?)
                print('\n\nERROR: invalid azimuth. Value must be between 0 and 360. Value entered: %s\n\n' % (azimuth,))
                return
        else: # scan along z
          #TODO:  more testing of this case. need to update to allow tighter rear scan in case of torque tubes.
          #TODO: haven't checked -self.scenex and *tf values added to this section.
          # TODO chekc for * sensorsy
          if DEBUG: print ("Case 3 ")
          self.frontscan = {'xstart':tf*-self.scenex * (modwanted - round(nMods/2) ) * np.cos((azimuth-180)*dtor), 
                            'ystart':tf*-self.scenex * (modwanted - round(nMods/2) ) * np.sin((azimuth-180)*dtor) , 
                       'zstart': height + self.sceney / (sensorsy + 1) *np.sin(tilt*dtor),
                       'xinc':0, 'yinc': 0, 
                       'zinc':self.sceney / (sensorsy + 1) * np.sin(tilt*dtor), 'Nx': 1, 'Ny':1, 'Nz':sensorsy, 'orient':'%s %s 0'%(-1*np.sin(azimuth*dtor), -1*np.cos(azimuth*dtor)) }
          self.backscan = {'xstart':self.sceney * -1*np.sin(azimuth*dtor) + tf*-self.scenex * (modwanted - round(nMods/2) ) * np.cos((azimuth-180)*dtor), 
                           'ystart':self.sceney * -1*np.cos(azimuth*dtor) + tf*-self.scenex * (modwanted - round(nMods/2) ) * np.sin((azimuth-180)*dtor), 
                       'zstart': height + self.sceney / (sensorsy + 1) *np.sin(tilt*dtor),
                       'xinc':0, 'yinc':0, 
                       'zinc':self.sceney / (sensorsy + 1) * np.sin(tilt*dtor), 'Nx': 1, 'Ny':1, 'Nz':sensorsy, 'orient':'%s %s 0'%(np.sin(azimuth*dtor), np.cos(azimuth*dtor)) }

        self.gcr = self.sceney / pitch
        self.text = text
        self.radfile = radfile
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
        #  location data.  so far needed:latitude, longitude, elevation, timezone, city
        self.latitude = metadata['latitude']
        self.longitude = metadata['longitude']
        self.elevation = metadata['altitude']
        self.timezone = metadata['TZ']
        self.city = metadata['Name']
        #self.location.state_province_region = metadata['State'] # not necessary
        self.datetime = tmydata.index.tolist() # this is tz-aware. EPW input routine is not...
        self.ghi = tmydata.GHI.tolist()
        self.dhi = tmydata.DHI.tolist()        
        self.dni = tmydata.DNI.tolist()

 
    def set1axis(self, cumulativesky=True, axis_azimuth=180, limit_angle=45, angledelta=5, backtrack=True, gcr = 1.0/3.0):
        '''
        Set up geometry for 1-axis tracking cumulativesky.  Pull in tracking angle details from 
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
        metdata.tracker_theta       (list) tracker tilt angle from pvlib for each timestep
        metdata.surface_tilt        (list)  tracker surface tilt angle from pvlib for each timestep
        metdata.surface_azimuth     (list)  tracker surface azimuth angle from pvlib for each timestep
        '''

        axis_tilt = 0       # only support 0 tilt trackers for now
        self.cumulativesky = cumulativesky   # track whether we're using cumulativesky or gendaylit

        # get 1-axis tracker angles for this location, rounded to nearest 'angledelta'
        trackingdata = self._getTrackingAngles(axis_azimuth, limit_angle, angledelta, axis_tilt = 0, backtrack = backtrack, gcr = gcr )
        
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
                if self.ghi[i] > 0:
                    trackerdict[time] = {
                            'surf_azm':     self.surface_azimuth[i],
                            'surf_tilt':    self.surface_tilt[i],
                            'theta':        self.tracker_theta[i],
                            'ghi':          self.ghi[i],
                            'dhi':          self.dhi[i]
                            }

        return trackerdict
    
    
    def _getTrackingAngles(self, axis_azimuth=180, limit_angle=45, angledelta=5, axis_tilt=0, backtrack=True, gcr = 1.0/3.0 ):  # return tracker angle data for the system
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
            * 'theta_round' : tracker_theta rounded to the nearest 'angledelta'
            '''
            import pytz
            import pvlib
            
            lat = self.latitude
            lon = self.longitude
            elev = self.elevation
            datetime = pd.to_datetime(self.datetime)
            tz = self.timezone
            try:  # make sure the data is tz-localized.
                datetimetz = datetime.tz_localize(pytz.FixedOffset(tz*60))  # either use pytz.FixedOffset (in minutes) or 'Etc/GMT+5'
            except:  # data is tz-localized already. Just put it in local time.
                datetimetz = datetime.tz_convert(pytz.FixedOffset(tz*60))  
            # get solar position zenith and azimuth based on site metadata
            #solpos = pvlib.irradiance.solarposition.get_solarposition(datetimetz,lat,lon,elev)
            solpos = pvlib.irradiance.solarposition.get_solarposition(datetimetz-pd.Timedelta(minutes = 30),lat,lon,elev)
            self.solpos = solpos  # save solar position for each timestamp
            # get 1-axis tracker tracker_theta, surface_tilt and surface_azimuth        
            trackingdata = pvlib.tracking.singleaxis(solpos['zenith'], solpos['azimuth'], axis_tilt, axis_azimuth, limit_angle, backtrack, gcr)
            # save tracker tilt information to metdata.tracker_theta, metdata.surface_tilt and metdata.surface_azimuth
            self.tracker_theta = trackingdata['tracker_theta'].tolist()
            self.surface_tilt = trackingdata['surface_tilt'].tolist()
            self.surface_azimuth = trackingdata['surface_azimuth'].tolist()
            # undo the 30 minute timestamp offset put in by solpos
            trackingdata.index = trackingdata.index + pd.Timedelta(minutes = 30)

            
            # round tracker_theta to increments of angledelta
            def _roundArbitrary(x, base = angledelta):
            # round to nearest 'base' value.
            # mask NaN's to avoid rounding error message
                return base * (x.dropna()/float(base)).round()
            trackingdata['theta_round'] = _roundArbitrary(trackingdata['tracker_theta'])
            
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
        
    def makeImage(self, viewfile, octfile=None, name=None):
        'make visible image of octfile, viewfile'
        
        if octfile is None:
            octfile = self.octfile
        if name is None:
            name = self.name
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
        
        #now create our own matrix - 3D nested Z,Y,Z
        linepts = ""
        # make sure Nx, Ny, Nz are ints.
        Nx = int(Nx)
        Ny = int(Ny)
        Nz = int(Nz)
        
        #check for backscan where z-orientation is positive. scan along x and z in this case to allow tight scans (experimental)
        zscanFlag = False
        try:
            if int(orient.split(' ')[2])>0:
                zscanFlag = True
        except:
            pass
        
        for iz in range(0,Nz):
            zpos = zstart+iz*zinc
            for iy in range(0,Ny):
                ypos = ystart+iy*yinc
                for ix in range(0,Nx):
                    xpos = xstart+ix*xinc
                    if zscanFlag is True:
                        zpos = zstart+ix*zinc  # starting in v0.2.3, scan x and z at the same time to allow tight rear scans. only on rear scans facing up.
                    linepts = linepts + str(xpos) + ' ' + str(ypos) + ' '+str(zpos) + ' ' + orient + " \r"
        return(linepts)
    
    def irrPlotNew(self, octfile, linepts, mytitle=None, plotflag=None, accuracy='low'):
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
      
    def PVSCanalysis(self, octfile, name):
        # analysis of octfile results based on the PVSC architecture.
        # usable for \objects\PVSC_4array.rad
        # PVSC front view. iterate x = 0.1 to 4 in 26 increments of 0.15. z = 0.9 to 2.25 in 9 increments of .15
        #x = 3.2 - middle of east panel
        
        frontScan = {'xstart':3.2, 'ystart': -0.1,'zstart': 0.9,'xinc':0, 'yinc': 0,
                     'zinc':0.15, 'Nx': 1, 'Ny':1, 'Nz':10, 'orient':'0 1 0' }
        rearScan = {'xstart':3.2, 'ystart': 3,'zstart': 0.9,'xinc':0, 'yinc': 0,
                     'zinc':0.15, 'Nx': 1, 'Ny':1, 'Nz':10, 'orient':'0 -1 0' }    
        self.analysis(octfile, name, frontScan, rearScan)

    def G173analysis(self, octfile, name):
        # analysis of octfile results based on the G173 architecture.
        # usable for \objects\monopanel_G173_ht_1.0.rad
        # top view. centered at z = 10 y = -.1 to 1.5 in 10 increments of .15
       
        frontScan = {'xstart':0.15, 'ystart': -0.1,'zstart': 10,'xinc':0, 'yinc': 0.15,
                     'zinc':0, 'Nx': 1, 'Ny':10, 'Nz':1, 'orient':'0 0 -1' }
        rearScan = {'xstart':0.15, 'ystart': -0.1,'zstart': 0,'xinc':0, 'yinc': 0.15,
                     'zinc':0, 'Nx': 1, 'Ny':10, 'Nz':1, 'orient':'0 0 1' }  
        self.analysis(octfile, name, frontScan, rearScan)
        
        
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
            print('Analysis aborted - no octfile')
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

    
if __name__ == "__main__":
    '''
    Example of how to run a Radiance routine for a simple rooftop bifacial system

    '''
    testfolder = _interactive_directory(title = 'Select or create an empty directory for the Radiance tree')
    demo = RadianceObj('simple_panel',path = testfolder)  # Create a RadianceObj 'object'
    demo.setGround(0.62) # input albedo number or material name like 'concrete'.  To see options, run this without any input.
    try:
        epwfile = demo.getEPW(37.5,-77.6) # pull TMY data for any global lat/lon
    except:
        pass
        
    metdata = demo.readEPW(epwfile) # read in the EPW weather data from above
    #metdata = demo.readTMY() # select a TMY file using graphical picker
    # Now we either choose a single time point, or use cumulativesky for the entire year. 
    fullYear = True
    if fullYear:
        demo.genCumSky(demo.epwfile) # entire year.
    else:
        demo.gendaylit(metdata,4020)  # Noon, June 17th

        
    # create a scene using panels in landscape at 10 deg tilt, 1.5m pitch. 0.2 m ground clearance
    sceneDict = {'tilt':10,'pitch':1.5,'height':0.2,'azimuth':180}  
    moduleDict = demo.makeModule(name = 'test', x = 1.59, y = 0.95 )
    scene = demo.makeScene('test',sceneDict, nMods = 20, nRows = 7) #makeScene creates a .rad file with 20 modules per row, 7 rows.
    octfile = demo.makeOct(demo.getfilelist())  # makeOct combines all of the ground, sky and object files into a .oct file.
    analysis = AnalysisObj(octfile, demo.name)  # return an analysis object including the scan dimensions for back irradiance
    analysis.analysis(octfile, demo.name, scene.frontscan, scene.backscan)  # compare the back vs front irradiance  
    print('Annual bifacial ratio average:  %0.3f' %( sum(analysis.Wm2Back) / sum(analysis.Wm2Front) ) )


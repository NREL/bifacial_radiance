#!/usr/bin/env python

"""
@author: cdeline

bifacial_radiance.py - module to develop radiance bifacial scenes, including gendaylit and gencumulativesky
7/5/2016 - test script based on G173_journal_height
5/1/2017 - standalone module

Pre-requisites:
    This software is written for Python >3.6 leveraging many Anaconda tools (e.g. pandas, numpy, etc)

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

"""
import logging
logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

import os, datetime
from subprocess import Popen, PIPE  # replacement for os.system()
import pandas as pd
import numpy as np 
#from input import *

# Mutual parameters across all processes
#daydate=sys.argv[1]


global DATA_PATH # path to data files including module.json.  Global context
#DATA_PATH = os.path.abspath(pkg_resources.resource_filename('bifacial_radiance', 'data/') )
DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

def _findme(lst, a): #find string match in a list. script from stackexchange
    return [i for i, x in enumerate(lst) if x == a]


def _normRGB(r, g, b): #normalize by each color for human vision sensitivity
    return r*0.216+g*0.7152+b*0.0722

def _popen(cmd, data_in, data_out=PIPE):
    """
    Helper function subprocess.popen replaces os.system
    - gives better input/output process control
    usage: pass <data_in> to process <cmd> and return results
    based on rgbeimage.py (Thomas Bleicher 2010)
    """
    cmd = str(cmd) # gets rid of unicode oddities

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
            returntuple = (data.decode('latin1'), None) #Py3 requires decoding
        else:
            returntuple = (None, None)

    return returntuple

def _interactive_load(title=None):
    # Tkinter file picker
    import tkinter
    from tkinter import filedialog
    root = tkinter.Tk()
    root.withdraw() #Start interactive file input
    root.attributes("-topmost", True) #Bring window into foreground
    return filedialog.askopenfilename(parent=root, title=title) #initialdir = data_dir

def _interactive_directory(title=None):
    # Tkinter directory picker.  Now Py3.6 compliant!
    import tkinter
    from tkinter import filedialog
    root = tkinter.Tk()
    root.withdraw() #Start interactive file input
    root.attributes("-topmost", True) #Bring to front
    return filedialog.askdirectory(parent=root, title=title)


class RadianceObj:
    """
    The RadianceObj top level class is used to work on radiance objects, 
    keep track of filenames,  sky values, PV module configuration, etc.

    Parameters
    ----------
    name : text to append to output files
    filelist : list of Radiance files to create oconv
    nowstr : current date/time string
    path : working directory with Radiance materials and objects

    Methods
    -------
    __init__ : initialize the object
    _setPath : change the working directory

    """

    def __init__(self, name=None, path=None):
        '''
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
        self.backRatio = 0      # ratio of rear / front Wm2
        self.nMods = None        # number of modules per row
        self.nRows = None        # number of rows per scene

        now = datetime.datetime.now()
        self.nowstr = str(now.date())+'_'+str(now.hour)+str(now.minute)+str(now.second)

        # DEFAULTS

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
        # load files in the /materials/ directory
        self.materialfiles = self.returnMaterialFiles('materials')

    def _setPath(self, path):
        """
        setPath - move path and working directory

        """
        self.path = os.path.abspath(path)

        print('path = '+ path)
        try:
            os.chdir(self.path)
        except OSError as exc:
            LOGGER.error('Path doesn''t exist: %s' % (path))
            LOGGER.exception(exc)
            raise(exc)

        # check for path in the new Radiance directory:
        def _checkPath(path):  # create the file structure if it doesn't exist
            if not os.path.exists(path):
                os.makedirs(path)
                print('Making path: '+path)

        _checkPath('images'); _checkPath('objects')
        _checkPath('results'); _checkPath('skies'); _checkPath('EPWs')
        # if materials directory doesn't exist, populate it with ground.rad
        # figure out where pip installed support files.
        from shutil import copy2

        if not os.path.exists('materials'):  #copy ground.rad to /materials
            os.makedirs('materials')
            print('Making path: materials')

            copy2(os.path.join(DATA_PATH, 'ground.rad'), 'materials')
        # if views directory doesn't exist, create it with two default views - side.vp and front.vp
        if not os.path.exists('views'):
            os.makedirs('views')
            with open(os.path.join('views', 'side.vp'), 'w') as f:
                f.write('rvu -vtv -vp -10 1.5 3 -vd 1.581 0 -0.519234 '+
                        '-vu 0 0 1 -vh 45 -vv 45 -vo 0 -va 0 -vs 0 -vl 0')
            with open(os.path.join('views', 'front.vp'), 'w') as f:
                f.write('rvu -vtv -vp 0 -3 5 -vd 0 0.894427 -0.894427 '+
                        '-vu 0 0 1 -vh 45 -vv 45 -vo 0 -va 0 -vs 0 -vl 0')

    def getfilelist(self):
        """ 
        Return concat of matfiles, radfiles and skyfiles
        """

        return self.materialfiles + self.skyfiles + self.radfiles

    def save(self, savefile=None):
        """
        Pickle the radiance object for further use.
        Very basic operation - not much use right now.

        Parameters
        ----------
        savefile : str
            Optional savefile name, with .pickle extension.
            Otherwise default to save.pickle

        """
        
        import pickle

        if savefile is None:
            savefile = 'save.pickle'

        with open(savefile, 'wb') as f:
            pickle.dump(self, f)
        print('Saved to file {}'.format(savefile))

    def exportTrackerDict(self, trackerdict=None,
                          savefile=None, reindex=None):
        """
        Use :py:func:`~bifacial_radiance.load._exportTrackerDict` to save a
        TrackerDict output as a csv file.

        Parameters
        ----------
            trackerdict
                The tracker dictionary to save
            savefile : str 
                path to .csv save file location
            reindex : bool
                True saves the trackerdict in TMY format, including rows for hours
                where there is no sun/irradiance results (empty)
                
        """
        
        import bifacial_radiance.load

        if trackerdict is None:
            trackerdict = self.trackerdict

        if savefile is None:
            savefile = _interactive_load(title='Select a .csv file to save to')

        if reindex is None:
            if self.cumulativesky is True:
                # don't re-index for cumulativesky,
                # which has angles for index
                reindex = False
            else:
                reindex = True

        if self.cumulativesky is True and reindex is True:
            # don't re-index for cumulativesky,
            # which has angles for index
            print ("\n Warning: For cumulativesky simulations, exporting the TrackerDict requires reindex = False. Setting reindex = False and proceeding")
            reindex = False

        bifacial_radiance.load._exportTrackerDict(trackerdict,
                                                 savefile,
                                                 reindex)


    def loadtrackerdict(self, trackerdict=None, fileprefix=None):
        """
        Use :py:class:`bifacial_radiance.load._loadtrackerdict` 
        to browse the results directory and load back any results saved in there.

        Parameters
        ----------
        trackerdict
        fileprefix : str

        """
        from bifacial_radiance.load import loadTrackerDict
        if trackerdict is None:
            trackerdict = self.trackerdict
        (trackerdict, totaldict) = loadTrackerDict(trackerdict, fileprefix)
        self.Wm2Front = totaldict['Wm2Front']
        self.Wm2Back = totaldict['Wm2Back']

    def returnOctFiles(self):
        """
        Return files in the root directory with `.oct` extension

        Returns
        -------
        oct_files : list
            List of .oct files
        
        """
        oct_files = [f for f in os.listdir(self.path) if f.endswith('.oct')]
        #self.oct_files = oct_files
        return oct_files

    def returnMaterialFiles(self, material_path=None):
        """
        Return files in the Materials directory with .rad extension
        appends materials files to the oconv file list

        Parameters
        ----------
        material_path : str
            Optional parameter to point to a specific materials directory.
            otherwise /materials/ is default

        Returns
        -------
        material_files : list
            List of .rad files

        """
        
        if material_path is None:
            material_path = 'materials'

        material_files = [f for f in os.listdir(os.path.join(self.path,
                                                             material_path)) if f.endswith('.rad')]

        materialfilelist = [os.path.join(material_path, f) for f in material_files]
        self.materialfiles = materialfilelist
        return materialfilelist

    def setGround(self, material=None, material_file=None):
        """ 
        Use GroundObj constructor class and return a ground object
        
        Parameters
        ------------
        material : numeric or str
            If number between 0 and 1 is passed, albedo input is assumed and assigned.    
            If string is passed with the name of the material desired. e.g. 'litesoil',
            properties are searched in `material_file`.
            Default Material names to choose from: litesoil, concrete, white_EPDM, 
            beigeroof, beigeroof_lite, beigeroof_heavy, black, asphalt
        material_file : str
            Filename of the material information. Default `ground.rad`
    
        Returns
        -------
        self.ground : tuple
            self.ground.normval : numeric
            Normalized color value
            self.ground.ReflAvg : numeric
            Average reflectance
        """

        if material is None:
            try:
                if self.metdata.albedo is not None:
                    material = self.metdata.albedo
                    print(" Assigned Albedo from metdata.albedo")
            except:
                pass
            
        self.ground = GroundObj(material, material_file)


    def getEPW(self, lat=None, lon=None, GetAll=False):
        """
        Subroutine to download nearest epw files to latitude and longitude provided,
        into the directory \EPWs\
        based on github/aahoo.
        
        .. warning::
            verify=false is required to operate within NREL's network.
            to avoid annoying warnings, insecurerequestwarning is disabled
            currently this function is not working within NREL's network.  annoying!
        
        Parameters
        ----------
        lat : decimal 
            Used to find closest EPW file.
        lon : decimal 
            Longitude value to find closest EPW file.
        GetAll : boolean 
            Download all available files. Note that no epw file will be loaded into memory
        
        
        """

        import requests, re
        from requests.packages.urllib3.exceptions import InsecureRequestWarning
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        hdr = {'User-Agent' : "Magic Browser",
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
               }

        path_to_save = 'EPWs' # create a directory and write the name of directory here
        if not os.path.exists(path_to_save):
            os.makedirs(path_to_save)

        def _returnEPWnames():
            ''' return a dataframe with the name, lat, lon, url of available files'''
            r = requests.get('https://github.com/NREL/EnergyPlus/raw/develop/weather/master.geojson', verify=False)
            data = r.json() #metadata for available files
            #download lat/lon and url details for each .epw file into a dataframe
            df = pd.DataFrame({'url':[], 'lat':[], 'lon':[], 'name':[]})
            for location in data['features']:
                match = re.search(r'href=[\'"]?([^\'" >]+)', location['properties']['epw'])
                if match:
                    url = match.group(1)
                    name = url[url.rfind('/') + 1:]
                    lontemp = location['geometry']['coordinates'][0]
                    lattemp = location['geometry']['coordinates'][1]
                    dftemp = pd.DataFrame({'url':[url], 'lat':[lattemp], 'lon':[lontemp], 'name':[name]})
                    df = df.append(dftemp, ignore_index=True)
            return df

        def _findClosestEPW(lat, lon, df):
            #locate the record with the nearest lat/lon
            errorvec = np.sqrt(np.square(df.lat - lat) + np.square(df.lon - lon))
            index = errorvec.idxmin()
            url = df['url'][index]
            name = df['name'][index]
            return url, name

        def _downloadEPWfile(url, path_to_save, name):
            r = requests.get(url, verify=False, headers=hdr)
            if r.ok:
                filename = os.path.join(path_to_save, name)
                # py2 and 3 compatible: binary write, encode text first
                with open(filename, 'wb') as f:
                    f.write(r.text.encode('ascii', 'ignore'))
                print(' ... OK!')
            else:
                print(' connection error status code: %s' %(r.status_code))
                r.raise_for_status()

        # Get the list of EPW filenames and lat/lon
        df = _returnEPWnames()

        # find the closest EPW file to the given lat/lon
        if (lat is not None) & (lon is not None) & (GetAll is False):
            url, name = _findClosestEPW(lat, lon, df)

            # download the EPW file to the local drive.
            print('Getting weather file: ' + name)
            _downloadEPWfile(url, path_to_save, name)
            self.epwfile = os.path.join('EPWs', name)

        elif GetAll is True:
            if input('Downloading ALL EPW files available. OK? [y/n]') == 'y':
                # get all of the EPW files
                for index, row in df.iterrows():
                    print('Getting weather file: ' + row['name'])
                    _downloadEPWfile(row['url'], path_to_save, row['name'])
            self.epwfile = None
        else:
            print('Nothing returned. Proper usage: epwfile = getEPW(lat,lon)')
            self.epwfile = None

        return self.epwfile



    def getEPW_all(self):
        '''
        Deprecated. now run getEPW(GetAll=True)
        '''


    def readWeatherFile(self, weatherFile=None, starttime=None, 
                        endtime=None, daydate=None, label = 'right'):
        """
        Read either a EPW or a TMY file, calls the functions 
        :py:class:`~bifacial_radiance.readTMY` or
        :py:class:`~bifacial_radiance.readEPW` 
        according to the weatherfile extention.
        
        Parameters
        ----------
        weatherFile : str
            File containing the weather information. TMY or EPW accepted.
            
        starttime : str
            Limited start time option in 'MM_DD_HH' format
        endtime : str
            Limited end time option in 'MM_DD_HH' format
        label : str
            'left', 'right', or 'center'. For data that is averaged, defines if
            the timestamp refers to the left edge, the right edge, or the 
            center of the averaging interval, for purposes of calculating 
            sunposition. For example, TMY3 data is right-labeled, so 11 AM data 
            represents data from 10 to 11, and sun position is calculated 
            at 10:30 AM.  Currently SAM and PVSyst use left-labeled interval 
            data and NSRDB uses centered.
        """
        
        if weatherFile is None:
            try:
                weatherFile = _interactive_load('Select EPW or TMY3 climate file')
            except:
                raise Exception('Interactive load failed. Tkinter not supported'+
                                'on this system. Try installing X-Quartz and reloading')
            
        if weatherFile[-3:] == 'epw':
            metdata = self.readEPW(weatherFile, starttime=starttime,
                                   endtime=endtime, daydate=daydate, label=label)
        else:
            metdata = self.readTMY(weatherFile, starttime=starttime,
                                   endtime=endtime, daydate=daydate, label=label)

        return metdata

            
    def _saveTempTMY(self, tmydata, filename=None, starttime=None, endtime=None):
        '''
        private function to save part or all of tmydata into /EPWs/ for use 
        in gencumsky -G mode and return truncated  tmydata
        
        starttime:  'MM_DD_HH' string for limited time temp file
        endtime:  'MM_DD_HH' string for limited time temp file
        
        returns: tmydata_truncated  : subset of tmydata based on start & end
        '''
        if filename is None:
            filename = 'temp.csv'
        if starttime is None:
            starttime = '01_01_00'
        if endtime is None:
            endtime = '12_31_23'
        # re-cast index with constant 2001 year to avoid datetime issues.
        i = pd.to_datetime({'month':tmydata.index.month, 
                            'day':tmydata.index.day,
                            'hour':tmydata.index.hour,
                            'Year':2001*np.ones(tmydata.index.__len__())})
        i.index = i
        startdt = pd.to_datetime('2001_'+starttime, format='%Y_%m_%d_%H')
        enddt = pd.to_datetime('2001_'+endtime, format='%Y_%m_%d_%H')
        
        # create mask for when data should be kept. Otherwise set to 0
        indexmask = (i>=startdt) & (i<=enddt)
        indexmask.index = tmydata.index
        tmydata_trunc = tmydata[indexmask]

        #Create new temp file for gencumsky-G: 8760 2-column csv GHI,DHI.
        # Pad with zeros if len != 8760
        savedata = pd.DataFrame({'GHI':tmydata['GHI'], 'DHI':tmydata['DHI']})
        savedata[~indexmask]=0
        # switch to 2001 index
        savedata.index =i
        if savedata.__len__() != 8760:
            savedata.loc[pd.to_datetime('2001-01-01 0:0:0')]=0
            savedata.loc[pd.to_datetime('2001-12-31 23:0:0')]=0
            savedata = savedata.resample('1h').asfreq(fill_value=0)
        csvfile = os.path.join('EPWs', filename)
        print('Saving file {}, # points: {}'.format(csvfile, savedata.__len__()))
        savedata.to_csv(csvfile, index=False, header=False, sep=' ', 
                        columns=['GHI','DHI'])
        self.epwfile = csvfile
        
        # return tmydata truncated by startdt and enddt
        return tmydata_trunc
        
        
    def readTMY(self, tmyfile=None, starttime=None, endtime=None, daydate=None, 
                label = 'right'):
        '''
        use pvlib to read in a tmy3 file.

        Parameters
        ------------
        tmyfile : str
            Filename of tmy3 to be read with pvlib.tmy.readtmy3
        starttime : str 
            'MM_DD_HH' string for limited time temp file
        endtime: str
            'MM_DD_HH' string for limited time temp file
        daydate : str 
            For single day in 'MM/DD' or MM_DD format.
        label : str
            'left', 'right', or 'center'. For data that is averaged, defines if
            the timestamp refers to the left edge, the right edge, or the 
            center of the averaging interval, for purposes of calculating 
            sunposition. For example, TMY3 data is right-labeled, so 11 AM data 
            represents data from 10 to 11, and sun position is calculated 
            at 10:30 AM.  Currently SAM and PVSyst use left-labeled interval 
            data and NSRDB uses centered.
        
        Returns
        -------
        metdata - MetObj collected from TMY3 file
        '''
        import pvlib, re

        if tmyfile is None:  # use interactive picker in readWeatherFile()
            metdata = self.readWeatherFile()
            return metdata

        #(tmydata, metadata) = pvlib.tmy.readtmy3(filename=tmyfile) #pvlib<=0.6
        (tmydata, metadata) = pvlib.iotools.tmy.read_tmy3(filename=tmyfile) 
        
        if daydate is not None: 
            dd = re.split('_|/',daydate)
            starttime = dd[0]+'_'+dd[1] + '_00'
            endtime = dd[0]+'_'+dd[1] + '_23'
        
        tmydata_trunc = self._saveTempTMY(tmydata,'tmy3_temp.csv', 
                                          starttime=starttime, endtime=endtime)
        if daydate is not None:  # also remove GHI = 0 for HPC daydate call.
            tmydata_trunc = tmydata_trunc[tmydata_trunc.GHI > 0]
            
        self.metdata = MetObj(tmydata_trunc, metadata, label = label)
        return self.metdata

    def readEPW(self, epwfile=None, hpc=False, starttime=None, endtime=None, 
                daydate=None, label = 'right'):
        """
        Uses readepw from pvlib>0.6.1 but un-do -1hr offset and
        rename columns to match TMY3: DNI, DHI, GHI, DryBulb, Wspd
    
        Parameters
        ------------
        epwfile : str
            Direction and filename of the epwfile. If None, opens an interactive
            loading window.
        hpc : bool
            Default False.  DEPRECATED
        starttime : str 
            'MM_DD_HH' string for limited time temp file
        endtime: str
            'MM_DD_HH' string for limited time temp file
        daydate : str 
            For single day in 'MM/DD' or MM_DD format.
        label : str
            'left', 'right', or 'center'. For data that is averaged, defines if
            the timestamp refers to the left edge, the right edge, or the 
            center of the averaging interval, for purposes of calculating 
            sunposition. For example, TMY3 data is right-labeled, so 11 AM data 
            represents data from 10 to 11, and sun position is calculated 
            at 10:30 AM.  Currently SAM and PVSyst use left-labeled interval 
            data and NSRDB uses centered.
            
        
        """
        
        #from bifacial_radiance.readepw import readepw # from pvlib dev forum
        import pvlib
        import re
        
        if epwfile is None:  # use interactive picker in readWeatherFile()
            metdata = self.readWeatherFile()
            return metdata
        '''
        if hpc is True and daydate is None:
            print('Error: HPC computing requested, but Daydate is None '+
                  'in readEPW. Exiting.')
            sys.exit()
        '''
        '''
        NOTE: In PVLib > 0.6.1 the new epw.read_epw() function reads in time 
        with a default -1 hour offset.  This is not reflected in our existing
        workflow, and must be investigated further. 
        '''
        #(tmydata, metadata) = readepw(epwfile) #
        (tmydata, metadata) = pvlib.iotools.epw.read_epw(epwfile, coerce_year=2001) #pvlib>0.6.1
        #pvlib uses -1hr offset that needs to be un-done. Why did they do this?
        tmydata.index = tmydata.index+pd.Timedelta(hours=1) 
        # rename different field parameters to match output from 
        # pvlib.tmy.readtmy: DNI, DHI, DryBulb, Wspd
        tmydata.rename(columns={'dni':'DNI',
                                'dhi':'DHI',
                                'temp_air':'DryBulb',
                                'wind_speed':'Wspd',
                                'ghi':'GHI',
                                'albedo':'Alb'
                                }, inplace=True)    

        tempTMYtitle = 'epw_temp.csv'
        # Hpc only works when daydate is passed through. Daydate gives single-
        # day run option with zero GHI values removed.
        if daydate is not None: 
            dd = re.split('_|/',daydate)
            starttime = dd[0]+'_'+dd[1] + '_00'
            endtime = dd[0]+'_'+dd[1] + '_23'
            tempTMYtitle = 'epw_temp_'+dd[0]+'_'+dd[1]+'.csv'
        
        tmydata_trunc = self._saveTempTMY(tmydata,filename=tempTMYtitle, 
                                          starttime=starttime, endtime=endtime)
        if daydate is not None:  # also remove GHI = 0 for HPC daydate call.
            tmydata_trunc = tmydata_trunc[tmydata_trunc.GHI > 0]
        
        self.metdata = MetObj(tmydata_trunc, metadata, label = label)

        
        return self.metdata


    def getSingleTimestampTrackerAngle(self, metdata, timeindex, gcr=None, 
                                       axis_azimuth=180, axis_tilt=0, 
                                       limit_angle=60, backtrack=True):
        """
        Helper function to calculate a tracker's angle for use with the 
        fixed tilt routines of bifacial_radiance.
        
        Parameters
        ----------
        metdata : :py:class:`~bifacial_radiance.MetObj` 
            Meterological object to set up geometry. Usually set automatically by
            `bifacial_radiance` after running :py:class:`bifacial_radiance.readepw`. 
            Default = self.metdata
        timeindex : int
            Index between 0 to 8760 indicating hour to simulate.
        gcr : float
            Ground coverage ratio for calculation backtracking. Defualt [1.0/3.0] 
        axis_azimuth : float or int
            Orientation axis of tracker torque tube. Default North-South (180 deg)
        axis_tilt : float or int
            Default 0. Axis tilt -- not implemented in sensors locations so it's pointless
            at this release to change it.
        limit_angle : float or int
            Limit angle (+/-) of the 1-axis tracker in degrees. Default 45
        backtrack : boolean
            Whether backtracking is enabled (default = True)
        
        """
        '''
        elev = metdata.elevation
        lat = metdata.latitude
        lon = metdata.longitude
        timestamp = metdata.datetime[timeindex]
        '''
        
        import pvlib
                
        solpos = metdata.solpos.iloc[timeindex]
        sunzen = float(solpos.apparent_zenith)
        sunaz = float(solpos.azimuth) # not substracting the 180 
        
        trackingdata = pvlib.tracking.singleaxis(sunzen, sunaz,
                                             axis_tilt, axis_azimuth,
                                             limit_angle, backtrack, gcr)
        
        tracker_theta = float(np.round(trackingdata['tracker_theta'],2))
        tracker_theta = tracker_theta*-1 # bifacial_radiance uses East (morning) theta as positive
            
        return tracker_theta


    def gendaylit(self, timeindex, metdata=None, debug=False):
        """
        Sets and returns sky information using gendaylit.
        Uses PVLIB for calculating the sun position angles instead of
        using Radiance internal sun position calculation (for that use gendaylit function)
        If material type is known, pass it in to get
        reflectance info.  if material type isn't known, material_info.list is returned
        
        Parameters
        ----------
        metdata : ``MetObj``
            MetObj object with 8760 list of dni, dhi, ghi and location
        timeindex : int
            Index from 0 to 8759 of EPW timestep
        debug : bool
            Flag to print output of sky DHI and DNI

        Returns
        -------
        skyname : str
            Sets as a self.skyname and returns filename of sky in /skies/ directory. 
            If errors exist, such as DNI = 0 or sun below horizon, this skyname is None

        """
        import warnings
 
        if metdata is None:
            try:
                metdata = self.metdata
            except:
                print('usage: pass metdata, or run after running' +
                      'readWeatherfile(), readEPW() or readTMY()') 
                return

        if type(timeindex)== MetObj:  # check for deprecated usage of gendaylit
            warnings.warn('passed MetObj into timeindex position - proper ' +
                          'usage: gendaylit(timeindex, metdata) ')
            return
        
        ground = self.ground
        
        locName = metdata.city
        dni = metdata.dni[timeindex]
        dhi = metdata.dhi[timeindex]
        ghi = metdata.ghi[timeindex]
        elev = metdata.elevation
        lat = metdata.latitude
        lon = metdata.longitude

        # Assign Albedos
        try:
            if ground.ReflAvg.shape == metdata.dni.shape:
                groundindex = timeindex  
            elif self.ground.ReflAvg.shape[0] == 1: # just 1 entry
                groundindex = 0
            else:
                warnings.warn("Shape of ground Albedos and TMY data do not match.")
                return
        except:
            print('usage: make sure to run setGround() before gendaylit()')
            return

        if debug is True:
            print('Sky generated with Gendaylit, with DNI: %0.1f, DHI: %0.1f' % (dni, dhi))
            print("Datetime TimeIndex", metdata.datetime[timeindex])



        #Time conversion to correct format and offset.
        #datetime = metdata.sunrisesetdata['corrected_timestamp'][timeindex]
        #Don't need any of this any more. Already sunrise/sunset corrected and offset by appropriate interval

        # get solar position zenith and azimuth based on site metadata
        #solpos = pvlib.irradiance.solarposition.get_solarposition(datetimetz,lat,lon,elev)
        solpos = metdata.solpos.iloc[timeindex]
        sunalt = float(solpos.elevation)
        # Radiance expects azimuth South = 0, PVlib gives South = 180. Must substract 180 to match.
        sunaz = float(solpos.azimuth)-180.0

        sky_path = 'skies'

        if dhi <= 0:
            self.skyfiles = [None]
            return None
        # We should already be filtering for elevation >0. But just in case...
        if sunalt <= 0:
            sunalt = np.arcsin((ghi-dhi)/(dni+.001))*180/np.pi # reverse engineer elevation from ghi, dhi, dni
            print('Warning: negative sun elevation at '+
                  '{}.  '.format(metdata.datetime[timeindex])+
                  'Re-calculated elevation: {:0.2}'.format(sunalt))

        # Note - -W and -O1 option is used to create full spectrum analysis in units of Wm-2
         #" -L %s %s -g %s \n" %(dni/.0079, dhi/.0079, self.ground.ReflAvg) + \
        skyStr = ("# start of sky definition for daylighting studies\n" + \
            "# location name: " + str(locName) + " LAT: " + str(lat)
            +" LON: " + str(lon) + " Elev: " + str(elev) + "\n"
            "# Sun position calculated w. PVLib\n" + \
            "!gendaylit -ang %s %s" %(sunalt, sunaz)) + \
            " -W %s %s -g %s -O 1 \n" %(dni, dhi, ground.ReflAvg[groundindex]) + \
            "skyfunc glow sky_mat\n0\n0\n4 1 1 1 0\n" + \
            "\nsky_mat source sky\n0\n0\n4 0 0 1 180\n" + \
            ground._makeGroundString(index=groundindex, cumulativesky=False)

        time = metdata.datetime[timeindex]
        filename = str(time)[5:-12].replace('-','_').replace(' ','_')

        skyname = os.path.join(sky_path,"sky2_%s_%s_%s.rad" %(lat, lon, filename))

        skyFile = open(skyname, 'w')
        skyFile.write(skyStr)
        skyFile.close()

        self.skyfiles = [skyname]

        return skyname

    def gendaylit2manual(self, dni, dhi, sunalt, sunaz):
        """
        Sets and returns sky information using gendaylit.
        Uses user-provided data for sun position and irradiance.
        
        .. warning::
            Currently half an hour offset is programed on timestamp, for wheater files.
     
        Parameters
        ------------
        dni: int or float
           Direct Normal Irradiance (DNI) value, in W/m^2
        dhi : int or float
           Diffuse Horizontal Irradiance (DHI) value, in W/m^2 
        sunalt : int or float
           Sun altitude (degrees) 
        sunaz : int or float
           Sun azimuth (degrees) 

        Returns
        -------
        skyname : string
           Filename of sky in /skies/ directory
        """
        
        #TODO:
        # #DocumentationCheck
        # Is the half hour warning thing still Valid
        #
        # Documentation note: "if material type is known, pass it in to get
        # reflectance info.  if material type isn't known, material_info.list is returned"
        # I don't think this function is doing that still? Maybe just delete this lines?
        
        print('Sky generated with Gendaylit 2 MANUAL, with DNI: %0.1f, DHI: %0.1f' % (dni, dhi))

        sky_path = 'skies'

        if sunalt <= 0 or dhi <= 0:
            self.skyfiles = [None]
            return None
        
                # Assign Albedos
        try:
            if self.ground.ReflAvg.shape[0] == 1: # just 1 entry
                groundindex = 0
            else:
                print("Ambiguous albedo entry, Set albedo to single value "
                      "in setGround()")
                return
        except:
            print('usage: make sure to run setGround() before gendaylit()')
            return
        
        
        # Note: -W and -O1 are used to create full spectrum analysis in units of Wm-2       
         #" -L %s %s -g %s \n" %(dni/.0079, dhi/.0079, self.ground.ReflAvg) + \
        skyStr =   ("# start of sky definition for daylighting studies\n" + \
            "# Manual inputs of DNI, DHI, SunAlt and SunAZ into Gendaylit used \n" + \
            "!gendaylit -ang %s %s" %(sunalt, sunaz)) + \
            " -W %s %s -g %s -O 1 \n" %(dni, dhi, self.ground.ReflAvg[groundindex]) + \
            "skyfunc glow sky_mat\n0\n0\n4 1 1 1 0\n" + \
            "\nsky_mat source sky\n0\n0\n4 0 0 1 180\n" + \
            self.ground._makeGroundString(index=groundindex, cumulativesky=False)

        skyname = os.path.join(sky_path, "sky2_%s.rad" %(self.name))

        skyFile = open(skyname, 'w')
        skyFile.write(skyStr)
        skyFile.close()

        self.skyfiles = [skyname]

        return skyname

    def genCumSky(self, epwfile=None, startdt=None, enddt=None, savefile=None):
        """ 
        Generate Skydome using gencumsky. 
        
        .. warning::
            gencumulativesky.exe is required to be installed,
            which is not a standard radiance distribution.
            You can find the program in the bifacial_radiance distribution directory
            in \Lib\site-packages\bifacial_radiance\data
            
        .. deprecated:: 0.3.2
            startdatetime and enddatetime inputs are deprecated and should not be used.
            Use :func:`readWeatherFile(filename, starttime='MM_DD_HH', endtime='MM_DD_HH')` 
            to limit gencumsky simulations instead.

        Parameters
        ------------
        epwfile : str
            Filename of the .epw file to read in (-E mode) or 2-column csv (-G mode).
           
        startdatetime : datetime.datetime(Y,M,D,H,M,S) object
            Only M,D,H selected. default: (0,1,1,0)
        enddatetime : datetime.datetime(Y,M,D,H,M,S) object
            Only M,D,H selected. default: (12,31,24,0)
        savefile : string
            If savefile is None, defaults to "cumulative"
            
        Returns
        -------
        skyname : str
            Filename of the .rad file containing cumulativesky info
        """
        
        # #TODO:  error checking and auto-install of gencumulativesky.exe
        import datetime
        
        if epwfile is None:
            epwfile = self.epwfile
        if epwfile.endswith('epw'):
            filetype = '-E'  # EPW file input into gencumulativesky *DEPRECATED
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
        cmd = "gencumulativesky +s1 -h 0 -a %s -o %s -m %s %s " %(lat, lon, float(timeZone)*15, filetype) +\
            "-time %s %s -date %s %s %s %s %s" % (startdt.hour, enddt.hour+1,
                                                  startdt.month, startdt.day,
                                                  enddt.month, enddt.day,
                                                  epwfile)
        '''
        cmd = (f"gencumulativesky +s1 -h 0 -a {lat} -o {lon} -m "
               f"{float(timeZone)*15} {filetype} -time {startdt.hour} "
               f"{enddt.hour+1} -date {startdt.month} {startdt.day} "
               f"{enddt.month} {enddt.day} {epwfile}" )
               
        with open(savefile+".cal","w") as f:
            _,err = _popen(cmd, None, f)
            if err is not None:
                print(err)

        # Assign Albedos
        try:
            groundstring = self.ground._makeGroundString(cumulativesky=True)
        except:
            raise Exception('Error: ground reflection not defined.  '
                            'Run RadianceObj.setGround() first')
            return
        


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
            groundstring
            
        skyname = os.path.join(sky_path, savefile+".rad")

        skyFile = open(skyname, 'w')
        skyFile.write(skyStr)
        skyFile.close()

        self.skyfiles = [skyname]#, 'SunFile.rad' ]

        return skyname

    def set1axis(self, metdata=None, axis_azimuth=180, limit_angle=45,
                 angledelta=5, backtrack=True, gcr=1.0 / 3, cumulativesky=True,
                 fixed_tilt_angle=None):
        """
        Set up geometry for 1-axis tracking.  Pull in tracking angle details from
        pvlib, create multiple 8760 metdata sub-files where datetime of met data
        matches the tracking angle.  Returns 'trackerdict' which has keys equal to
        either the tracker angles (gencumsky workflow) or timestamps (gendaylit hourly
        workflow)

        Parameters
        ------------
        cumulativesky : bool
            [True] Wether individual csv files are
            created with constant tilt angle for the cumulativesky approach.
            if false, the gendaylit tracking approach must be used.
        metdata : :py:class:`~bifacial_radiance.MetObj` 
            Meterological object to set up geometry. Usually set automatically by
            `bifacial_radiance` after running :py:class:`bifacial_radiance.readepw`. 
            Default = self.metdata
        axis_azimuth : numeric
            Orientation axis of tracker torque tube. Default North-South (180 deg)
        limit_angle : numeric
            Limit angle (+/-) of the 1-axis tracker in degrees. Default 45
        backtrack : bool
            Whether backtracking is enabled (default = True)
        gcr : float
            Ground coverage ratio for calculation backtracking. Defualt [1.0/3.0] 
        angledelta : numeric
            Degree of rotation increment to parse irradiance bins. Default 5 degrees.
            (0.4 % error for DNI).  Other options: 4 (.25%), 2.5 (0.1%).
            Note: the smaller the angledelta, the more simulations must be run.
        fixed_tilt_angle : numeric
            If passed, this changes to a fixed tilt
            simulation where each hour uses fixed_tilt_angle 
            and axis_azimuth as the tilt and azimuth

        Returns
        -------
        trackerdict : dictionary 
            Keys represent tracker tilt angles (gencumsky) or timestamps (gendaylit)
            and list of csv metfile, and datetimes at that angle
            trackerdict[angle]['csvfile';'surf_azm';'surf_tilt';'UTCtime']
            - or -
            trackerdict[time]['tracker_theta';'surf_azm';'surf_tilt']
        """

        # Documentaiton check:
        # Removed         Internal variables
        # -------
        # metdata.solpos          dataframe with solar position data
        # metdata.surface_azimuth list of tracker azimuth data
        # metdata.surface_tilt    list of tracker surface tilt data
        # metdata.tracker_theta   list of tracker tilt angle
        
        if metdata == None:
            metdata = self.metdata

        if metdata == {}:
            raise Exception("metdata doesnt exist yet.  "+
                            "Run RadianceObj.readWeatherFile() ")


        #backtrack = True   # include backtracking support in later version
        #gcr = 1.0/3.0       # default value - not used if backtrack = False.


        # get 1-axis tracker angles for this location, rounded to nearest 'angledelta'
        trackerdict = metdata._set1axis(cumulativesky=cumulativesky,
                                       axis_azimuth=axis_azimuth,
                                       limit_angle=limit_angle,
                                       angledelta=angledelta,
                                       backtrack=backtrack,
                                       gcr=gcr,
                                       fixed_tilt_angle=fixed_tilt_angle
                                       )
        self.trackerdict = trackerdict
        self.cumulativesky = cumulativesky

        return trackerdict

    def gendaylit1axis(self, metdata=None, trackerdict=None, startdate=None,
                       enddate=None, debug=False, hpc=False):
        """
        1-axis tracking implementation of gendaylit.
        Creates multiple sky files, one for each time of day.

        Parameters
        ------------
        metdata
            Output from readEPW or readTMY.  Needs to have RadianceObj.set1axis() run on it first.
        startdate : str 
            Starting point for hourly data run. Optional parameter string 
            'MM/DD' or 'MM_DD' or 'MM/DD/HH' or 'MM/DD/HH' format
        enddate : str
            Ending date for hourly data run. Optional parameter string 
            'MM/DD' or 'MM_DD' or 'MM/DD/HH' or 'MM/DD/HH' format
        trackerdict : dictionary
            Dictionary with keys for tracker tilt angles (gencumsky) or timestamps (gendaylit)

        Warning: If you're passing trackerdicts without 00 hour, and using startdate
        and enddate of 'MM/DD' or 'MM_HH' it will not trim the trackerdict; pass an hour
        that you know is available in the trackerdict to trim properly. This will be 
        improved in a future release thank you.
        
        Returns
        -------
        Updated trackerdict dictionary 
            Dictionary with keys for tracker tilt angles (gencumsky) or timestamps (gendaylit)
            with the additional dictionary value ['skyfile'] added

        """
        
        #import dateutil.parser as parser # used to convert startdate and enddate
        import re

        if metdata is None:
            metdata = self.metdata
        if trackerdict is None:
            try:
                trackerdict = self.trackerdict
            except AttributeError:
                print('No trackerdict value passed or available in self')

        try:
            metdata.tracker_theta  # this may not exist
        except AttributeError:
            print("metdata.tracker_theta doesn't exist. Run RadianceObj.set1axis() first")

        # look at start and end date if they're passed.  Otherwise don't worry about it.
        # compare against metdata.datetime because this isn't necessarily an 8760!
        temp = pd.to_datetime(metdata.datetime)
        temp2 = temp.month*10000+temp.day*100+temp.hour
        try:
            match1 = re.split('_|/',startdate) 
            matchval = int(match1[0])*10000+int(match1[1])*100
            if len(match1)>2:
                matchval = matchval + int(match1[2])
            startindex = temp2.to_list().index(matchval)
        except: # catch ValueError (not in list) and AttributeError (startdate = None)
            startindex = 0
        try:
            match1 = re.split('_|/',enddate) 
            matchval = int(match1[0])*10000+int(match1[1])*100
            if len(match1)>2:
                matchval = matchval + int(match1[2])
            endindex = temp2.to_list().index(matchval)
        except: # catch ValueError (not in list) and AttributeError 
            endindex = len(metdata.datetime)

        if hpc is True:
            startindex = 0
            endindex = len(metdata.datetime)

        if debug is False:
            print('Creating ~%d skyfiles.  Takes 1-2 minutes'%((endindex-startindex)/2))
        count = 0  # counter to get number of skyfiles created, just for giggles

        trackerdict2={}
        for i in range(startindex,endindex+1):
            try:
                time = metdata.datetime[i]
            except IndexError:  #out of range error
                break  # 
            filename = str(time)[5:-12].replace('-','_').replace(' ','_')
            self.name = filename

            #check for GHI > 0
            #if metdata.ghi[i] > 0:
            if (metdata.ghi[i] > 0) & (~np.isnan(metdata.tracker_theta[i])):  
                skyfile = self.gendaylit(metdata=metdata,timeindex=i, debug=debug)
                # trackerdict2 reduces the dict to only the range specified.
                trackerdict2[filename] = trackerdict[filename]  
                trackerdict2[filename]['skyfile'] = skyfile
                count +=1

        print('Created {} skyfiles in /skies/'.format(count))
        self.trackerdict = trackerdict2
        return trackerdict2

    def genCumSky1axis(self, trackerdict=None):
        """
        1-axis tracking implementation of gencumulativesky.
        Creates multiple .cal files and .rad files, one for each tracker angle.
        > Deprecated on 0.3.2 : startdt and enddt inputs are no longer available.
        > Use :func:`readWeatherFile(filename, starttime='MM_DD_HH', endtime='MM_DD_HH')` 
        > to limit gencumsky simulations instead.
        
        
        Parameters
        ------------
        trackerdict : dictionary
            Trackerdict generated as output by RadianceObj.set1axis()
        startdt : *DEPRECATED*
            deprecated    
        enddt : *DEPRECATED*
            deprecated
            
        Returns
        -------
        trackerdict : dictionary
            Trackerdict dictionary with new entry trackerdict.skyfile  
            Appends 'skyfile'  to the 1-axis dict with the location of the sky .radfile

        """
        
        if trackerdict == None:
            try:
                trackerdict = self.trackerdict
            except AttributeError:
                print('No trackerdict value passed or available in self')

        for theta in sorted(trackerdict):  
            # call gencumulativesky with a new .cal and .rad name
            csvfile = trackerdict[theta]['csvfile']
            savefile = '1axis_%s'%(theta)  #prefix for .cal file and skies\*.rad file
            skyfile = self.genCumSky(epwfile=csvfile, savefile=savefile)
            trackerdict[theta]['skyfile'] = skyfile
            print('Created skyfile %s'%(skyfile))
        # delete default skyfile (not strictly necessary)
        self.skyfiles = None
        self.trackerdict = trackerdict
        return trackerdict


    def makeOct(self, filelist=None, octname=None, hpc=False):
        """
        Combine everything together into a .oct file

        Parameters
        ----------
        filelist : list 
            Files to include.  otherwise takes self.filelist
        octname : str
            filename (without .oct extension)
        hpc : bool
            Default False. Activates a wait period in case one of the files for
            making the oct is still missing.

        Returns
        -------
        octname : str
            filename of .oct file in root directory including extension
        err : str
            Error message returned from oconv (if any)
        """
        
        if filelist is None:
            filelist = self.getfilelist()
        if octname is None:
            octname = self.name

        debug = False
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
                #Filesky is being saved as 'none', so it crashes !
                while not os.path.exists(file):
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
        with open('%s.oct' % (octname), "w") as f:
            _,err = _popen(cmd, None, f)
            #TODO:  exception handling for no sun up
            if err is not None:
                if err[0:5] == 'error':
                    raise Exception(err[7:])

        #use rvu to see if everything looks good. 
        # use cmd for this since it locks out the terminal.
        #'rvu -vf views\side.vp -e .01 monopanel_test.oct'
        print("Created %s.oct" % (octname))
        self.octfile = '%s.oct' % (octname)
        return '%s.oct' % (octname)

    def makeOct1axis(self, trackerdict=None, singleindex=None, customname=None, hpc=False):
        """
        Combine files listed in trackerdict into multiple .oct files

        Parameters
        ------------
        trackerdict 
            Output from :py:class:`~bifacial_radiance.RadianceObj.makeScene1axis`
        singleindex : str
            Single index for trackerdict to run makeOct1axis in single-value mode.
        customname : str 
            Custom text string added to the end of the OCT file name.
        hpc : bool
            Default False. Activates a wait period in case one of the files for
            making the oct is still missing.

        Returns
        -------
        trackerdict
            Append 'octfile'  to the 1-axis dict with the location of the scene .octfile
        """

        if customname is None:
            customname = ''

        if trackerdict is None:
            try:
                trackerdict = self.trackerdict
            except AttributeError:
                print('No trackerdict value passed or available in self')
        if singleindex is None:   # loop through all values in the tracker dictionary
            indexlist = trackerdict.keys()
        else:  # just loop through one single index in tracker dictionary
            indexlist = [singleindex]

        print('\nMaking {} octfiles in root directory.'.format(indexlist.__len__()))
        for index in sorted(indexlist):  # run through either entire key list of trackerdict, or just a single value
            try:
                filelist = self.materialfiles + [trackerdict[index]['skyfile'], trackerdict[index]['radfile']]
                octname = '1axis_%s%s'%(index, customname)
                trackerdict[index]['octfile'] = self.makeOct(filelist, octname, hpc)
            except KeyError as e:
                print('Trackerdict key error: {}'.format(e))

        return trackerdict


    def makeModule(self, name=None, x=None, y=None, z=None, bifi=1, modulefile=None, text=None, customtext='',
                   torquetube=False, diameter=0.1, tubetype='Round', material='Metal_Grey',
                   xgap=0.01, ygap=0.0, zgap=0.1, numpanels=1, rewriteModulefile=True,
                   axisofrotationTorqueTube=False, cellLevelModuleParams=None,  
                   orientation=None, glass=False, torqueTubeMaterial=None):
        """
        Add module details to the .JSON module config file module.json
        makeModule is in the `RadianceObj` class because this is defined before a `SceneObj` is.

        Module definitions assume that the module .rad file is defined
        with zero tilt, centered along the x-axis and y-axis for the center
        of rotation of the module (+X/2, -X/2, +Y/2, -Y/2 on each side).
        Tip: to define a module that is in 'portrait' mode, y > x. 

        Parameters
        ------------
        name : str
            Input to name the module type
        x : numeric
            Width of module along the axis of the torque tube or racking structure. (meters).
        y : numeric
            Length of module (meters)
        bifi : numeric
            Bifaciality of the panel (not currently used). Between 0 (monofacial) 
            and 1, default 1.
        modulefile : str
            Existing radfile location in \objects.  Otherwise a default value is used
        text : str
            Text used in the radfile to generate the module
        customtext : str
            Added-text used in the radfile to generate any
            extra details in the racking/module. Does not overwrite
            generated module (unlike "text"), but adds to it at the end.
        rewriteModulefile : bool
            Default True. Will rewrite module file each time makeModule is run.
        torquetube : bool
            This variable defines if there is a torque tube or not.
        diameter : float
            Tube diameter in meters. For square,
            For Square, diameter means the length of one of the
            square-tube side.  For Hex, diameter is the distance
            between two vertices (diameter of the circumscribing circle)
        tubetype : str
            Options: 'Square', 'Round' (default), 'Hex' or 'Oct'. Tube cross section
        material : str
            Options: 'Metal_Grey' or 'black'. Material for the torque tube.
        numpanels : int
            Number of modules arrayed in the Y-direction. e.g.
            1-up or 2-up, etc. (supports any number for carport/Mesa simulations)
        xgap : float
            Panel space in X direction. Separation between modules in a row.
        ygap : float
            Gap between modules arrayed in the Y-direction if any.
        zgap : float
            Distance behind the modules in the z-direction to the edge of the tube (m)
        cellLevelModuleParams : dict
            Dictionary with input parameters for creating a cell-level module.
            See details below for keys needed.
        axisofrotationTorqueTube : bool
            Default False. IF true, creates geometry
            so center of rotation is at the center of the torquetube, with
            an offsetfromaxis equal to half the torquetube diameter + the zgap.
            If there is no torquetube (torquetube=False), offsetformaxis
            will equal the zgap.

        Notes
        -----
        For creating a cell-level module, the following input parameters have 
        to be in ``cellLevelModuleParams``:
        
        ================   ====================================================
        Keys : type        Description
        ================   ====================================================  
        numcellsx : int    Number of cells in the X-direction within the module
        numcellsy : int    Number of cells in the Y-direction within the module
        xcell : float      Width of each cell (X-direction) in the module
        ycell : float      Length of each cell (Y-direction) in the module
        xcellgap : float   Spacing between cells in the X-direction
        ycellgap : float   Spacing between cells in the Y-direction
        ================   ====================================================  

        '"""

        # #TODO: add transparency parameter, make modules with non-zero opacity
        # #DocumentationCheck: this Todo seems to besolved by doing cell-level modules
        # and printing the packaging facotr
        
        
        # #TODO: refactor this module to streamline it and accept moduleDict input
        # #DocumentationCheck : do we still need to do this Todo?

        import json
        
        
        if name is None:
            print("usage:  makeModule(name,x,y, bifi = 1, modulefile = '\objects\*.rad', "+
                  "torquetube=False, diameter = 0.1 (torque tube dia.), "+
                  "tubetype = 'Round' (or 'square', 'hex'), material = "+
                  "'Metal_Grey' (or 'black'), zgap = 0.1 (module offset)"+
                  "numpanels = 1 (# of panels in portrait), ygap = 0.05 "+
                  "(slope distance between panels when arrayed), "+
                  "rewriteModulefile = True (or False)")
            print("Optional: cellLevelModule={} (create cell-level module by "+
                  " passing in dictionary with keys 'numcellsx'6 (#cells in "+
                  "X-dir.), 'numcellsy', 'xcell' (cell size in X-dir. in meters),"+
                  "'ycell', 'xcellgap' (spacing between cells in X-dir.), 'ycellgap'")
            print("You can also override module_type info by passing 'text'"+
                  "variable, or add on at the end for racking details with "+
                  "'customtext'. See function definition for more details")

            return

        
        #replace whitespace with underlines. what about \n and other weird characters?
        name2 = str(name).strip().replace(' ', '_')        

        if modulefile is None:
            modulefile = os.path.join('objects', name2 + '.rad')
            print("\nModule Name:", name2)

        if rewriteModulefile is True:
            if os.path.isfile(modulefile):
                print(f'Pre-existing .rad file {modulefile} '
                      'will be overwritten')
                os.remove(modulefile)

        if orientation is not None:
            print('\n\n WARNING: Orientation format has been deprecated since '+
                  'version 0.2.4. If you want to flip your modules, on '+
                  'makeModule switch the x and y values. X value is the size '+
                  'of the panel along the row, so for a "landscape" panel x '+
                  'should be > than y.\n\n')
            
        if torqueTubeMaterial is not None:
            material = torqueTubeMaterial
        #aliases for equations below
        diam = diameter
        Ny = numpanels
        cc = 0
        import math

        # Defaults for rotating system around module
        offsetfromaxis = 0      # Module Offset

        # Update values for rotating system around torque tube.
        if axisofrotationTorqueTube == True:
            if torquetube is True:
                offsetfromaxis = np.round(zgap + diam/2.0,8)
                tto = 0
            else:
                offsetfromaxis = zgap
                tto = 0                
        #TODO: replace these with functions
       
        # Adding the option to replace the module thickess
        if z is None:
            z = 0.020
            
        if text is None:
            
            if not cellLevelModuleParams:
                try:
                    text = '! genbox black {} {} {} {} '.format(name2,x, y, z)
                    text +='| xform -t {} {} {} '.format(-x/2.0,
                                            (-y*Ny/2.0)-(ygap*(Ny-1)/2.0),
                                            offsetfromaxis)
                    text += '-a {} -t 0 {} 0'.format(Ny, y+ygap)
                    packagingfactor = 100.0

                except NameError as err: # probably because no x or y passed
                    raise Exception('makeModule variable {} and cellLevelModule'+
                                    'Params is None.  One or the other must'+
                                    ' be specified.'.format(err.args[0]))
            else:
                c = cellLevelModuleParams
                x = c['numcellsx']*c['xcell'] + (c['numcellsx']-1)*c['xcellgap']
                y = c['numcellsy']*c['ycell'] + (c['numcellsy']-1)*c['ycellgap']

                #center cell -
                if c['numcellsx'] % 2 == 0:
                    cc = c['xcell']/2.0
                    print("Module was shifted by {} in X to avoid sensors on air".format(cc))

                text = '! genbox black cellPVmodule {} {} {} | '.format(c['xcell'], c['ycell'], z)
                text +='xform -t {} {} {} '.format(-x/2.0 + cc,
                                 (-y*Ny / 2.0)-(ygap*(Ny-1) / 2.0),
                                 offsetfromaxis)
                text += '-a {} -t {} 0 0 '.format(c['numcellsx'], c['xcell'] + c['xcellgap'])
                text += '-a {} -t 0 {} 0 '.format(c['numcellsy'], c['ycell'] + c['ycellgap'])
                text += '-a {} -t 0 {} 0'.format(Ny, y+ygap)

                # OPACITY CALCULATION
                packagingfactor = np.round((c['xcell']*c['ycell']*c['numcellsx']*c['numcellsy'])/(x*y), 2)
                print("This is a Cell-Level detailed module with Packaging "+
                      "Factor of {} %".format(packagingfactor))

            if torquetube is True:
                if tubetype.lower() == 'square':
                    if axisofrotationTorqueTube == False:
                        tto = -zgap-diam/2.0
                    text += '\r\n! genbox {} tube1 {} {} {} '.format(material,
                                          x+xgap, diam, diam)
                    text += '| xform -t {} {} {}'.format(-(x+xgap)/2.0+cc,
                                        -diam/2.0, -diam/2.0+tto)

                elif tubetype.lower() == 'round':
                    if axisofrotationTorqueTube == False:
                        tto = -zgap-diam/2.0
                    text += '\r\n! genrev {} tube1 t*{} {} '.format(material, x+xgap, diam/2.0)
                    text += '32 | xform -ry 90 -t {} {} {}'.format(-(x+xgap)/2.0+cc, 0, tto)

                elif tubetype.lower() == 'hex':
                    radius = 0.5*diam

                    if axisofrotationTorqueTube == False:
                        tto = -radius*math.sqrt(3.0)/2.0-zgap

                    text += '\r\n! genbox {} hextube1a {} {} {} | xform -t {} {} {}'.format(
                            material, x+xgap, radius, radius*math.sqrt(3),
                            -(x+xgap)/2.0+cc, -radius/2.0, -radius*math.sqrt(3.0)/2.0+tto) #ztran -radius*math.sqrt(3.0)-tto


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
                    raise Exception("Incorrect torque tube type.  "+
                                    "Available options: 'square' or 'round'."+
                                    "  Value entered: {}".format(tubetype))

            if glass: 
                    edge = 0.005                     
                    text = text+'\r\n! genbox stock_glass {} {} {} {} '.format(name2+'_Glass',x+edge, y+edge, z+edge)
                    text +='| xform -t 0 {} 0 ' . format(-edge/2.0)
                    text +='| xform -t {} {} {} '.format(-x/2.0-edge/2.0 + cc,
                                            (-y*Ny/2.0)-(ygap*(Ny-1)/2.0),
                                            offsetfromaxis - 0.5*edge + 0.5*z)
                    text += '-a {} -t 0 {} 0'.format(Ny, y+ygap)
                

                
            text += customtext  # For adding any other racking details at the module level that the user might want.

        

        moduleDict = {'x':x,
                      'y':y,
                      'z':z,
                      'scenex': x+xgap,
                      'sceney': np.round(y*Ny + ygap*(Ny-1), 8),
                      'scenez': np.round(zgap + diam / 2.0, 8),
                      'numpanels':Ny,
                      'bifi':bifi,
                      'text':text,
                      'modulefile':modulefile,
                      'offsetfromaxis':offsetfromaxis, #<- this may not be consistent if the module is re-loaded from the JSON later since 'axisofrotationTorqueTube' isn't kept track of..
                      'xgap':xgap,
                      'ygap':ygap,
                      'zgap':zgap,
                      'cellModule':cellLevelModuleParams,
                      'torquetube':{'bool':torquetube,
                                    'diameter':diameter,
                                    'tubetype':tubetype,
                                    'material':material
                              }
                      }
 

        filedir = os.path.join(DATA_PATH, 'module.json') 
        with open(filedir) as configfile:
            data = json.load(configfile)


        data.update({name:moduleDict})
        with open(os.path.join(DATA_PATH, 'module.json') ,'w') as configfile:
            json.dump(data, configfile, indent=4, sort_keys=True)

        print('Module {} updated in module.json'.format(name))

        self.moduleDict = moduleDict

        return moduleDict


    def makeCustomObject(self, name=None, text=None):
        """
        Function for development and experimenting with extraneous objects in the scene.
        This function creates a `name.rad` textfile in the objects folder
        with whatever text that is passed to it.
        It is up to the user to pass the correct radiance format.
        
        For example, to create a box at coordinates 0,0 (with its bottom surface
        on the plane z=0):
            
        .. code-block:
        
            name = 'box'
            text='! genbox black PVmodule 0.5 0.5 0.5 | xform -t -0.25 -0.25 0'

        Parameters
        ----------
        name : str
            String input to name the module type
        text : str
            Text used in the radfile to generate the module
        
        """

        customradfile = os.path.join('objects', '%s.rad'%(name)) # update in 0.2.3 to shorten radnames
        # py2 and 3 compatible: binary write, encode text first
        with open(customradfile, 'wb') as f:
            f.write(text.encode('ascii'))

        print("\nCustom Object Name", customradfile)
        self.customradfile = customradfile
        return customradfile


    def printModules(self):
        # print available module types by creating a dummy SceneObj
        temp = SceneObj()
        modulenames = temp.readModule()
        print('Available module names: {}'.format([str(x) for x in modulenames]))
        return modulenames
    
    def makeScene(self, moduletype=None, sceneDict=None, hpc=False):
        """
        Create a SceneObj which contains details of the PV system configuration including
        tilt, row pitch, height, nMods per row, nRows in the system...

        Parameters
        ----------
        moduletype : str
            String name of module created with makeModule()
        sceneDict : dictionary
            Dictionary with keys: `tilt`, `clearance_height`*, `pitch`,
            `azimuth`, `nMods`, `nRows`, `hub_height`*, `height`*
            * height deprecated from sceneDict. For makeScene (fixed systems)
            if passed it is assumed it reffers to clearance_height.
            `clearance_height` recommended for fixed_tracking systems.
            `hub_height` can also be passed as a possibility.
        hpc : bool
            Default False. For makeScene, it adds the full path
            of the objects folder where the module . rad file is saved.

        Returns
        -------
        SceneObj 
            'scene' with configuration details
            
        """
        
        if moduletype is None:
            print('makeScene(moduletype, sceneDict, nMods, nRows).  '+\
                  'Available moduletypes: monopanel, simple_panel' )
            #TODO: read in config file to identify available module types
            return
        self.scene = SceneObj(moduletype)

        if sceneDict is None:
            print('makeScene(moduletype, sceneDict, nMods, nRows).  '+\
                  'sceneDict inputs: .tilt .clearance_height .pitch .azimuth')
            return self.scene

        if 'orientation' in sceneDict:
            if sceneDict['orientation'] == 'landscape':
                raise Exception('\n\n ERROR: Orientation format has been '+
                                'deprecated since version 0.2.4. If you want '+
                                'to flip your modules, on makeModule switch '+
                                'the x and y values. X value is the size of '+
                                'the panel along the row, so for a "landscape"'+
                                'panel x should be > than y.\n\n')
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
                    print("sceneDict Warning: Passed 'clearance_height', "+
                           "'hub_height', and 'height' into makeScene. For "+
                           "makeScene fixed tilt routine, using 'clearance_"+
                           "height' and removing 'hub_height' and 'height' "+
                           "(deprecated) from sceneDict")
                    del sceneDict['height']
                    del sceneDict['hub_height']
                else:
                    print("sceneDict Warning: Passed 'height' and 'clearance_"+
                          "height'. Using 'clearance_height' and deprecating 'height'")
                    del sceneDict['height']
            else:
                if 'hub_height' in sceneDict:
                    print("sceneDict Warning: Passed 'hub_height' and 'height'"+
                          "into makeScene. Using 'hub_height' and removing 'height' from sceneDict.")
                    del sceneDict['height']
                else:
                    print("sceneDict Warning: Passed 'height' to makeScene()."+
                          " We are assuming this is 'clearance_height'."+
                          "Renaming and deprecating height.")
                    sceneDict['clearance_height']=sceneDict['height']
                    del sceneDict['height']
        else:
            if 'clearance_height' in sceneDict:
                if 'hub_height' in sceneDict:
                    print("sceneDict Warning: Passed 'clearance_height' and"+
                           " 'hub_height' into makeScene. For this fixed tilt"+
                           "routine, using 'clearance_height' and removing 'hub_height' from sceneDict")
                    del sceneDict['hub_height']
            else:
                if 'hub_height' not in sceneDict:
                    print("ERROR: Issue with sceneDict. No 'clearance_height'"+
                          ", 'hub_height' nor 'height' (deprecated) passed")
                    return

        self.nMods = sceneDict['nMods']
        self.nRows = sceneDict['nRows']
        self.sceneRAD = self.scene._makeSceneNxR(moduletype=moduletype,
                                                sceneDict=sceneDict,
                                                hpc=hpc)

        if 'appendRadfile' not in sceneDict:
            appendRadfile = False
        else:
            appendRadfile = sceneDict['appendRadfile']

        if appendRadfile:
            debug = False
            try:
                self.radfiles.append(self.sceneRAD)
                if debug:
                    print( "Radfile APPENDED!")
            except:
                #TODO: Manage situation where radfile was created with
                #appendRadfile to False first....
                self.radfiles=[]
                self.radfiles.append(self.sceneRAD)
                if debug:
                    print( "Radfile APPENDAGE created!")
        else:
            self.radfiles = [self.sceneRAD]
        return self.scene

    def appendtoScene(self, radfile=None, customObject=None, text=''):
        """
        Appends to the `Scene radfile` in folder `\objects` the text command in Radiance
        lingo created by the user.
        Useful when using addCustomObject to the scene.

        Parameters
        ----------
        radfile: str
            Directory and name of where .rad scene file is stored
        customObject : str
            Directory and name of custom object .rad file is stored
        text : str 
            Command to be appended to the radfile. Do not leave empty spaces
            at the end.

        Returns
        -------
        Nothing, the radfile must already be created and assigned when running this.
        
        """
        
        #TODO: Add a custom name and replace radfile name

        # py2 and 3 compatible: binary write, encode text first
        text2 = '\n' + text + ' ' + customObject
        
        debug = False
        if debug:
            print (text2)

        with open(radfile, 'a+') as f:
            f.write(text2)


    def makeScene1axis(self, trackerdict=None, moduletype=None, sceneDict=None,
                       cumulativesky=None, hpc=False):
        """
        Creates a SceneObj for each tracking angle which contains details of the PV
        system configuration including row pitch, hub_height, nMods per row, nRows in the system...

        Parameters
        ------------
        trackerdict
            Output from GenCumSky1axis
        moduletype : str
            Name of module created with makeModule()
        sceneDict : 
            Dictionary with keys:`tilt`, `hub_height`, `pitch`, `azimuth`
        cumulativesky : bool
            Defines if sky will be generated with cumulativesky or gendaylit.
        nMods : int
            DEPRECATED. int number of modules per row (default = 20).
            If included it will be assigned to the sceneDict
        nRows: int
            DEPRECATED. int number of rows in system (default = 7).
            If included it will be assigned to the sceneDict
        hpc :  bool
            Default False. For makeScene, it adds the full path
            of the objects folder where the module . rad file is saved.

        Returns
        --------
        trackerdict 
            Append the following keys
                'radfile'
                    directory where .rad scene file is stored
                'scene'
                    SceneObj for each tracker theta
                'clearance_height'
                    Calculated ground clearance based on
                    `hub height`, `tilt` angle and overall collector width `sceney`
                
        """
        
        # #DocumentationCheck
        # #TODO
        # nMods and nRows were deprecated various versions before.
        # Removed them as inputs now. 
        
        import math

        if sceneDict is None:
            print('usage: makeScene1axis(moduletype, sceneDict, nMods, nRows).'+
                  'sceneDict inputs: .hub_height .azimuth .nMods .nRows'+
                  'and .pitch or .gcr')
            return

        # If no nRows or nMods assigned on deprecated variable or dictionary,
        # assign default.
        if 'nRows' not in sceneDict:
            sceneDict['nRows'] = 7
        if 'nMods' not in sceneDict:
            sceneDict['nMods'] = 20

        if trackerdict is None:
            try:
                trackerdict = self.trackerdict
            except AttributeError:
                print('No trackerdict value passed or available in self')

        if cumulativesky is None:
            try:
                # see if cumulativesky = False was set earlier,
                # e.g. in RadianceObj.set1axis
                cumulativesky = self.cumulativesky
            except AttributeError:
                # default cumulativesky = true to maintain backward compatibility.
                cumulativesky = True

        if moduletype is None:
            print('usage:  makeScene1axis(trackerdict, moduletype, '+
                  'sceneDict, nMods, nRows). ')
            self.printModules() #print available module types
            return


        if 'orientation' in sceneDict:
            if sceneDict['orientation'] == 'landscape':
                raise Exception('\n\n ERROR: Orientation format has been '+
                                'deprecated since version 0.2.4. If you want'+
                                ' to flip your modules, on makeModule switch'+
                                'the x and y values. X value is the size of'+
                                ' the panel along the row, so for a '+
                                '"landscape" panel x should be > than y.\n\n')

        if 'hub_height' in sceneDict:
            if 'height' in sceneDict:
                if 'clearance_height' in sceneDict:
                    print("sceneDict Warning: 'hub_height', 'clearance_height'"+
                          ", and 'height' are being passed. Removing 'height'"+
                          " (deprecated) and 'clearance_height' from sceneDict"+
                          " for this tracking routine")
                    del sceneDict['clearance_height']
                    del sceneDict['height']
                else:
                    print("sceneDict Warning: 'height' is being deprecated. Using 'hub_height'")
                    del sceneDict['height']
            else:
                if 'clearance_height' in sceneDict:
                    print("sceneDict Warning: 'hub_height' and 'clearance_height'"+
                          " are being passed. Using 'hub_height' for tracking "+
                          "routine and removing 'clearance_height' from sceneDict")
                    del sceneDict['clearance_height']
        else: # if no hub_height is passed
            if 'height' in sceneDict:
                if 'clearance_height' in sceneDict:
                    print("sceneDict Warning: 'clearance_height and 'height' "+
                          "(deprecated) are being passed. Renaming 'height' "+
                          "as 'hub_height' and removing 'clearance_height' "+
                          "from sceneDict for this tracking routine")
                    sceneDict['hub_height']=sceneDict['height']
                    del sceneDict['clearance_height']
                    del sceneDict['height']
                else:
                    print("sceneDict Warning: 'height' is being deprecated. "+
                          "Renaming as 'hub_height'")
                    sceneDict['hub_height']=sceneDict['height']
                    del sceneDict['height']
            else: # If no hub_height nor height is passed
                if 'clearance_height' in sceneDict:
                    print("sceneDict Warning: Passing 'clearance_height' to a "+
                          "tracking routine. Assuming this is really 'hub_height' and renaming.")
                    sceneDict['hub_height']=sceneDict['clearance_height']
                    del sceneDict['clearance_height']
                else:
                    print ("sceneDict Error! no argument in sceneDict found "+
                           "for 'hub_height', 'height' nor 'clearance_height'. "+
                           "Exiting routine.")
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
                radname = '1axis%s_'%(theta,)

                # Calculating clearance height for this theta.
                height = hubheight - 0.5* math.sin(abs(theta) * math.pi / 180) \
                        * scene.sceney + scene.offsetfromaxis \
                        * math.sin(abs(theta)*math.pi/180)
                # Calculate the ground clearance height based on the hub height. Add abs(theta) to avoid negative tilt angle errors
                trackerdict[theta]['clearance_height'] = height

                try:
                    sceneDict2 = {'tilt':trackerdict[theta]['surf_tilt'],
                                  'pitch':sceneDict['pitch'],
                                  'clearance_height':trackerdict[theta]['clearance_height'],
                                  'azimuth':trackerdict[theta]['surf_azm'],
                                  'nMods': sceneDict['nMods'],
                                  'nRows': sceneDict['nRows'],
                                  'modulez': scene.moduleDict['z']}
                except KeyError:
                    #maybe gcr is passed, not pitch
                    sceneDict2 = {'tilt':trackerdict[theta]['surf_tilt'],
                                  'gcr':sceneDict['gcr'],
                                  'clearance_height':trackerdict[theta]['clearance_height'],
                                  'azimuth':trackerdict[theta]['surf_azm'],
                                  'nMods': sceneDict['nMods'],
                                  'nRows': sceneDict['nRows'],
                                  'modulez': scene.moduleDict['z']}

                radfile = scene._makeSceneNxR(moduletype=moduletype,
                                             sceneDict=sceneDict2,
                                             radname=radname,
                                             hpc=hpc)
                trackerdict[theta]['radfile'] = radfile
                trackerdict[theta]['scene'] = scene

            print('{} Radfiles created in /objects/'.format(trackerdict.__len__()))

        else:  #gendaylit workflow
            print('\nMaking ~%s .rad files for gendaylit 1-axis workflow (this takes a minute..)' % (len(trackerdict)))
            count = 0
            for time in trackerdict:
                scene = SceneObj(moduletype)

                if trackerdict[time]['surf_azm'] >= 180:
                    trackerdict[time]['surf_azm'] = trackerdict[time]['surf_azm']-180
                    trackerdict[time]['surf_tilt'] = trackerdict[time]['surf_tilt']*-1
                theta = trackerdict[time]['theta']
                radname = '1axis%s_'%(time,)

                # Calculating clearance height for this time.
                height = hubheight - 0.5* math.sin(abs(theta) * math.pi / 180) \
                        * scene.sceney + scene.offsetfromaxis \
                        * math.sin(abs(theta)*math.pi/180)

                if trackerdict[time]['ghi'] > 0:
                    trackerdict[time]['clearance_height'] = height
                    try:
                        sceneDict2 = {'tilt':trackerdict[time]['surf_tilt'],
                                      'pitch':sceneDict['pitch'],
                                      'clearance_height': trackerdict[time]['clearance_height'],
                                      'azimuth':trackerdict[time]['surf_azm'],
                                      'nMods': sceneDict['nMods'],
                                      'nRows': sceneDict['nRows'],
                                      'modulez': scene.moduleDict['z']}
                    except KeyError:
                        #maybe gcr is passed instead of pitch
                        sceneDict2 = {'tilt':trackerdict[time]['surf_tilt'],
                                      'gcr':sceneDict['gcr'],
                                      'clearance_height': trackerdict[time]['clearance_height'],
                                      'azimuth':trackerdict[time]['surf_azm'],
                                      'nMods': sceneDict['nMods'],
                                      'nRows': sceneDict['nRows'],
                                      'modulez': scene.moduleDict['z']}

                    radfile = scene._makeSceneNxR(moduletype=moduletype,
                                                 sceneDict=sceneDict2,
                                                 radname=radname,
                                                 hpc=hpc)
                    trackerdict[time]['radfile'] = radfile
                    trackerdict[time]['scene'] = scene
                    count+=1
            print('{} Radfiles created in /objects/'.format(count))

        self.trackerdict = trackerdict
        self.nMods = sceneDict['nMods']  #assign nMods and nRows to RadianceObj
        self.nRows = sceneDict['nRows']
        self.hub_height = hubheight
        
        return trackerdict#self.scene


    def analysis1axis(self, trackerdict=None, singleindex=None, accuracy='low',
                      customname=None, modWanted=None, rowWanted=None, sensorsy=9, hpc=False):
        """
        Loop through trackerdict and runs linescans for each scene and scan in there.

        Parameters
        ----------------
        trackerdict 
        singleindex : str
            For single-index mode, just the one index we want to run (new in 0.2.3).
            Example format '11_06_14' for November 6 at 2 PM
        accuracy : str
            'low' or 'high', resolution option used during _irrPlot and rtrace
        customname : str
            Custom text string to be added to the file name for the results .CSV files
        modWanted : int 
            Module to be sampled. Index starts at 1.
        rowWanted : int
            Row to be sampled. Index starts at 1. (row 1)
        sensorsy : int 
            Sampling resolution for the irradiance across the collector width.

        Returns
        -------
        trackerdict with new keys:
            
            'AnalysisObj'  : analysis object for this tracker theta
            'Wm2Front'     : list of front Wm-2 irradiances, len=sensorsy
            'Wm2Back'      : list of rear Wm-2 irradiances, len=sensorsy
            'backRatio'    : list of rear irradiance ratios, len=sensorsy
        RadianceObj with new appended values: 
            'Wm2Front'     : np Array with front irradiance cumulative
            'Wm2Back'      : np Array with rear irradiance cumulative
            'backRatio'    : np Array with rear irradiance ratios
        """
        
        import warnings

        if customname is None:
            customname = ''

        if trackerdict == None:
            try:
                trackerdict = self.trackerdict
            except AttributeError:
                print('No trackerdict value passed or available in self')

        if singleindex is None:  # run over all values in trackerdict
            trackerkeys = sorted(trackerdict.keys())
        else:                   # run in single index mode.
            trackerkeys = [singleindex]

        if modWanted == None:
            modWanted = round(self.nMods / 1.99)
        if rowWanted == None:
            rowWanted = round(self.nRows / 1.99)

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
                frontscan, backscan = analysis.moduleAnalysis(scene=scene, modWanted=modWanted, rowWanted=rowWanted, sensorsy=sensorsy)
                analysis.analysis(octfile=octfile,name=name,frontscan=frontscan,backscan=backscan,accuracy=accuracy, hpc=hpc)                
                trackerdict[index]['AnalysisObj'] = analysis
            except Exception as e: # problem with file. TODO: only catch specific error types here.
                warnings.warn('Index: {}. Problem with file. Error: {}. Skipping'.format(index,e), Warning)
                return

            #combine cumulative front and back irradiance for each tracker angle
            try:  #on error, trackerdict[index] is returned empty
                trackerdict[index]['Wm2Front'] = analysis.Wm2Front
                trackerdict[index]['Wm2Back'] = analysis.Wm2Back
                trackerdict[index]['backRatio'] = analysis.backRatio
            except AttributeError as  e:  # no key Wm2Front.
                warnings.warn('Index: {}. Trackerdict key not found: {}. Skipping'.format(index,e), Warning)
                return

            if np.sum(frontWm2) == 0:  # define frontWm2 the first time through
                frontWm2 =  np.array(analysis.Wm2Front)
                backWm2 =  np.array(analysis.Wm2Back)
            else:
                frontWm2 +=  np.array(analysis.Wm2Front)
                backWm2 +=  np.array(analysis.Wm2Back)
            print('Index: {}. Wm2Front: {}. Wm2Back: {}'.format(index,
                  np.mean(analysis.Wm2Front), np.mean(analysis.Wm2Back)))

        if np.sum(self.Wm2Front) == 0:
            self.Wm2Front = frontWm2   # these are accumulated over all indices passed in.
            self.Wm2Back = backWm2
        else:
            self.Wm2Front += frontWm2   # these are accumulated over all indices passed in.
            self.Wm2Back += backWm2
        self.backRatio = backWm2/(frontWm2+.001)

        # Save compiled results using _saveresults
        if singleindex is None:
        
            print ("Saving a cumulative-results file in the main simulation folder." +
                   "This adds up by sensor location the irradiance over all hours " +
                   "or configurations considered." +
                   "\nWarning: This file saving routine does not clean results, so "+
                   "if your setup has ygaps, or 2+modules or torque tubes, doing "+
                   "a deeper cleaning and working with the individual results "+
                   "files in the results folder is highly suggested.")
            cumfilename = 'cumulative_results_%s.csv'%(customname)
            if self.cumulativesky is True: 
                frontcum = pd.DataFrame()
                rearcum = pd.DataFrame()
                temptrackerdict = trackerdict[0.0]['AnalysisObj']
                frontcum ['x'] = temptrackerdict.x
                frontcum ['y'] = temptrackerdict.y
                frontcum ['z'] = temptrackerdict.z
                frontcum ['mattype'] = temptrackerdict.mattype
                frontcum ['Wm2'] = self.Wm2Front
                rearcum ['x'] = temptrackerdict.x
                rearcum ['y'] = temptrackerdict.x
                rearcum ['z'] = temptrackerdict.rearZ
                rearcum ['mattype'] = temptrackerdict.rearMat
                rearcum ['Wm2'] = self.Wm2Back
                cumanalysisobj = AnalysisObj()
                print ("\nSaving Cumulative results" )
                cumanalysisobj._saveResultsCumulative(frontcum, rearcum, savefile=cumfilename)
            else: # trackerkeys are day/hour/min, and there's no easy way to find a 
                # tilt of 0, so making a fake linepoint object for tilt 0 
                # and then saving.
                try:
                    cumscene = trackerdict[trackerkeys[0]]['scene']
                    cumscene.sceneDict['tilt']=0
                    cumscene.sceneDict['clearance_height'] = self.hub_height
                    cumanalysisobj = AnalysisObj()
                    frontscan, backscan = cumanalysisobj.moduleAnalysis(scene=cumscene, modWanted=modWanted, rowWanted=rowWanted, sensorsy = sensorsy)
                    x,y,z = cumanalysisobj._linePtsArray(frontscan)
                    x,y,rearz = cumanalysisobj._linePtsArray(backscan)
        
                    frontcum = pd.DataFrame()
                    rearcum = pd.DataFrame()
                    frontcum ['x'] = x
                    frontcum ['y'] = y
                    frontcum ['z'] = z
                    frontcum ['mattype'] = trackerdict[trackerkeys[0]]['AnalysisObj'].mattype
                    frontcum ['Wm2'] = self.Wm2Front
                    rearcum ['x'] = x
                    rearcum ['y'] = y
                    rearcum ['z'] = rearz
                    rearcum ['mattype'] = trackerdict[trackerkeys[0]]['AnalysisObj'].rearMat
                    rearcum ['Wm2'] = self.Wm2Back
                    print ("\nSaving Cumulative results" )
                    cumanalysisobj._saveResultsCumulative(frontcum, rearcum, savefile=cumfilename)            
                except:
                    print("Not able to save a cumulative result for this simulation.")
        return trackerdict


# End RadianceObj definition

class GroundObj:
    """
    Class to set and return details for the ground surface materials and reflectance.
    If 1 albedo value is passed, it is used as default.
    If 3 albedo values are passed, they are assigned to each of the three wavelength placeholders (RGB),
    
    If material type is known, it is used to get reflectance info.  
    if material type isn't known, material_info.list is returned

    Parameters
    ------------
    materialOrAlbedo : numeric or str
        If number between 0 and 1 is passed, albedo input is assumed and assigned.    
        If string is passed with the name of the material desired. e.g. 'litesoil',
        properties are searched in `material_file`.
        Default Material names to choose from: litesoil, concrete, white_EPDM, 
        beigeroof, beigeroof_lite, beigeroof_heavy, black, asphalt
    material_file : str
        Filename of the material information. Default `ground.rad`

    Returns
    -------
    material_info.normval : numeric
        Normalized color value
    material_info.ReflAvg : numeric
        Average reflectance
    material_info.names : list 
        List of material names in case of wrong/empty materialorAlbedo option passed.
    """

    # #DocumentationCheck  : not really returning material_info.normval but self?
    
    def __init__(self, materialOrAlbedo=None, material_file=None):
        import warnings
        from numbers import Number
        
        self.normval = None
        self.ReflAvg = None
        self.Rrefl = None
        self.Grefl = None
        self.Brefl = None

        self.ground_type = 'custom'        

        if material_file is None:
            material_file = 'ground.rad'
            
        self.material_file = material_file           
        if materialOrAlbedo is None: # Case where it's none.
            print('\nInput albedo 0-1, or string from GroundObj.printGroundMaterials().'
            '\nAlternatively, run setGround after readWeatherData()'
            'and setGround will read metdata.albedo if availalbe')
            return
            
        if isinstance(materialOrAlbedo, str) :
            self.ground_type = materialOrAlbedo  
            # Return the RGB albedo for material ground_type
            materialOrAlbedo = self.printGroundMaterials(self.ground_type)
            
        # Check for double and int. 
        if isinstance(materialOrAlbedo, Number):
            materialOrAlbedo = np.array([[materialOrAlbedo, 
                                          materialOrAlbedo, materialOrAlbedo]])
        
        if isinstance(materialOrAlbedo, list):
            materialOrAlbedo = np.asarray(materialOrAlbedo)
        
        # By this point, materialOrAlbedo should be a np.ndarray:
        if isinstance(materialOrAlbedo, np.ndarray):

            if materialOrAlbedo.ndim == 0:
            # numpy array of one single value, i.e. np.array(0.62)
            # after this if, np.array([0.62])
                materialOrAlbedo = materialOrAlbedo.reshape([1])
                
            if materialOrAlbedo.ndim == 1:
            # If np.array is ([0.62]), this repeats it so at the end it's
            # np.array ([0.62, 0.62, 0.62])
                materialOrAlbedo = np.repeat(np.array([materialOrAlbedo]), 
                                             3, axis=1).reshape(
                                                     len(materialOrAlbedo),3)
            
            if (materialOrAlbedo.ndim == 2) & (materialOrAlbedo.shape[1] > 3): 
                    warnings.warn("Radiance only raytraces 3 wavelengths at "
                                  "a time. Trimming albedo np.array input to "
                                  "3 wavelengths.")
                    materialOrAlbedo = materialOrAlbedo[:,0:3]
        # By this point we should have np.array of dim=2 and shape[1] = 3.        
        # Check for invalid values
        if (materialOrAlbedo > 1).any() or (materialOrAlbedo < 0).any():
            print('Warning: albedo values greater than 1 or less than 0. '
                  'Constraining to [0..1]')
            materialOrAlbedo = materialOrAlbedo.clip(min=0, max=1)
        try:
            self.Rrefl = materialOrAlbedo[:,0]
            self.Grefl = materialOrAlbedo[:,1]
            self.Brefl = materialOrAlbedo[:,2]
            self.normval = _normRGB(materialOrAlbedo[:,0],materialOrAlbedo[:,1],
                                    materialOrAlbedo[:,2])
            self.ReflAvg = np.round(np.mean(materialOrAlbedo, axis=1),4)
            print(f'Loading albedo, {self.ReflAvg.__len__()} value(s), '
                  f'{self._nonzeromean(self.ReflAvg):0.3f} avg\n'
                  f'{self.ReflAvg[self.ReflAvg != 0].__len__()} nonzero albedo values.')
        except IndexError as e:
            print('albedo.shape should be 3 column (N x 3)')
            raise e
    
    def printGroundMaterials(self, materialString=None):
        """
        printGroundMaterials(materialString=None)
        
        input: None or materialString.  If None, return list of acceptable
        material types from ground.rad.  If valid string, return RGB albedo
        of the material type selected.
        """
        
        import warnings
        material_path = 'materials'
        
        f = open(os.path.join(material_path, self.material_file))
        keys = [] #list of material key names
        Rreflall = []; Greflall=[]; Breflall=[] #RGB material reflectance  
        temp = f.read().split()
        f.close()
        #return indices for 'plastic' definition
        index = _findme(temp,'plastic')
        for i in index:
            keys.append(temp[i+1])# after plastic comes the material name
            Rreflall.append(float(temp[i+5]))#RGB reflectance comes a few more down the list
            Greflall.append(float(temp[i+6]))
            Breflall.append(float(temp[i+7]))
        
        if materialString is not None:
            try:
                index = _findme(keys,materialString)[0]
            except IndexError:
                warnings.warn(f'Error - materialString not in '
                              '{self.material_file}: {materialString}')
            return(np.array([[Rreflall[index], Greflall[index], Breflall[index]]]))
        else:
            return(keys)
            
    def _nonzeromean(self, val):
        '''  array mean excluding zero. return zero if everything's zero'''
        tempmean = np.nanmean(val)
        if tempmean > 0:
            tempmean = np.nanmean(val[val !=0])
        return tempmean     
        
    def _makeGroundString(self, index=0, cumulativesky=False):
        '''
        create string with ground reflectance parameters for use in 
        gendaylit and gencumsky.
        
        Parameters
        -----------
        index : integer
            Index of time for time-series albedo. Default 0
        cumulativesky:  Boolean
            If true, set albedo to average of time series values.

        Returns
        -------
        groundstring:  text with albedo details to append to sky.rad in
                       gendaylit
        '''
         
        
        try:  
            if cumulativesky is True:
                Rrefl = self._nonzeromean(self.Rrefl) 
                Grefl = self._nonzeromean(self.Grefl) 
                Brefl = self._nonzeromean(self.Brefl)
                normval = _normRGB(Rrefl, Grefl, Brefl)
            else:
                Rrefl = self.Rrefl[index]
                Grefl = self.Grefl[index]
                Brefl = self.Brefl[index]
                normval = _normRGB(Rrefl, Grefl, Brefl)

            # Check for all zero albedo case
            if normval == 0:
                normval = 1
            
            groundstring = ( f'\nskyfunc glow ground_glow\n0\n0\n4 ' 
                f'{Rrefl/normval} {Grefl/normval} {Brefl/normval} 0\n' 
                '\nground_glow source ground\n0\n0\n4 0 0 -1 180\n' 
                f'\nvoid plastic {self.ground_type}\n0\n0\n5 '
                f'{Rrefl:0.3f} {Grefl:0.3f} {Brefl:0.3f} 0 0\n'
                f"\n{self.ground_type} ring groundplane\n" 
                '0\n0\n8\n0 0 -.01\n0 0 1\n0 100' )
        except IndexError as err:
            print(f'Index {index} passed to albedo with only '
                  f'{self.Rrefl.__len__()} values.'   )
            raise err
        return groundstring

        

class SceneObj:
    '''
    scene information including PV module type, bifaciality, array info
    pv module orientation defaults: Azimuth = 180 (south)
    pv module origin: z = 0 bottom of frame. y = 0 lower edge of frame. 
    x = 0 vertical centerline of module

    scene includes module details (x,y,bifi, sceney (collector_width), scenex)
    '''
    def __init__(self, moduletype=None):
        ''' initialize SceneObj
        '''
        modulenames = self.readModule()
        # should sceneDict be initialized here? This is set in _makeSceneNxR
        if moduletype is None:
            #print('Usage: SceneObj(moduletype)\nNo module type selected. 
            #   Available module types: {}'.format(modulenames))
            return
        else:
            if moduletype in modulenames:
                # read in module details from configuration file.
                self.moduleDict = self.readModule(name = moduletype)
            else:
                print('incorrect panel type selection')
                return




    def readModule(self, name=None):
        """
        Read in available modules in module.json.  If a specific module name is
        passed, return those details into the SceneObj. Otherwise 
        return available module list.

        Parameters
        -----------
        name : str
            Name of module to be read

        Returns
        -------
        moduleDict : dictionary
            self.scenex : (float)
                Overall module width including xgap.
            self.sceney : (float)
                Overall module(s) height including ygaps along the collector width (CW),
        list of modulenames if name is not passed in.

        """

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
            self.z = moduleDict['z']
            self.bifi = moduleDict['bifi']  # panel bifaciality. Not used yet
            if 'scenex' in moduleDict:
                self.scenex = moduleDict['scenex']
            else:
                self.scenex = moduleDict['x']
            if 'sceney' in moduleDict:
                self.sceney = moduleDict['sceney']
            else:
                self.sceney = moduleDict['y']
            if 'offsetfromaxis' in moduleDict:
                self.offsetfromaxis = moduleDict['offsetfromaxis']
            else:
                self.offsetfromaxis = 0
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

    def _makeSceneNxR(self, moduletype=None, sceneDict=None, radname=None, hpc=False):
        """
        Arrange module defined in :py:class:`bifacial_radiance.SceneObj` into a N x R array.
        Returns a :py:class:`bifacial_radiance.SceneObj` which contains details 
        of the PV system configuration including `tilt`, `row pitch`, `hub_height`
        or `clearance_height`, `nMod`s per row, `nRows` in the system.

        The returned scene has (0,0) coordinates centered at the module at the
        center of the array. For 5 rows, that is row 3, for 4 rows, that is
        row 2 also (rounds down). For 5 modules in the row, that is module 3,
        for 4 modules in the row, that is module 2 also (rounds down)

        Parameters
        ------------
        moduletype: str 
            Name of module created with :py:class:`~bifacial_radiance.RadianceObj.makeModule`.
        sceneDict : dictionary 
            Dictionary of scene parameters.
                clearance_height : numeric
                    (meters). 
                pitch : numeric
                    Separation between rows
                tilt : numeric 
                    Valid input ranges -90 to 90 degrees
                axis_azimuth : numeric 
                    A value denoting the compass direction along which the
                    axis of rotation lies. Measured in decimal degrees East
                    of North. [0 to 180) possible.
                    If azimuth is passed, a warning is given and Axis Azimuth and
                    tilt are re-calculated.
                nMods : int 
                    Number of modules per row (default = 20)
                nRows : int 
                    Number of rows in system (default = 7)
        radname : str
            String for name for radfile.
        hpc : bool
            Default False. For makeScene, it adds the full path
            of the objects folder where the module .rad file is saved.

        Returns
        -------
        radfile : str
             Filename of .RAD scene in /objects/
        scene : :py:class:`~bifacial_radiance.SceneObj `
             Returns a `SceneObject` 'scene' with configuration details

        """

        #Cleanup Should this still be here?
        if moduletype is None:
            print('makeScene(moduletype, sceneDict, nMods, nRows).'
                  'Available moduletypes: monopanel, simple_panel' )
            #TODO: read in config file to identify available module types
            return
        self.scene = SceneObj(moduletype)   #is this needed?

        if sceneDict is None:
            print('makeScene(moduletype, sceneDict, nMods, nRows).  sceneDict'
                  ' inputs: .tilt .azimuth .nMods .nRows' 
                  ' AND .tilt or .gcr ; AND .hub_height or .clearance_height')


        if 'orientation' in sceneDict:
            if sceneDict['orientation'] == 'landscape':
                raise Exception('\n\n ERROR: Orientation format has been '
                                'deprecated since version 0.2.4. If you want '
                                'to flip your modules, on makeModule switch '
                                'the x and y values. X value is the size of '
                                'the panel along the row, so for a "landscape'
                                ' panel x should be > than y.\n\n')

        if 'azimuth' not in sceneDict:
            sceneDict['azimuth'] = 180

        if 'axis_tilt' not in sceneDict:
            sceneDict['axis_tilt'] = 0

        if 'originx' not in sceneDict:
            sceneDict['originx'] = 0

        if 'originy' not in sceneDict:
            sceneDict['originy'] = 0

        if radname is None:
            radname =  str(self.moduletype).strip().replace(' ', '_')

        # loading variables
        tilt = sceneDict['tilt']
        azimuth = sceneDict['azimuth']
        nMods = sceneDict['nMods']
        nRows = sceneDict['nRows']
        axis_tilt = sceneDict['axis_tilt']
        originx = sceneDict ['originx']
        originy = sceneDict['originy']

        # hub_height, clearance_height and height logic.
        # this routine uses hub_height to move the panels up so it's important 
        # to have a value for that, either obtianing from clearance_height 
        # (if coming from makeScene) or from hub_height itself.
        # it is assumed htat if no clearnace_height or hub_height is passed,
        # hub_height = height.

        if 'height' in sceneDict:
            if 'clearance_height' in sceneDict:
                if 'hub_height' in sceneDict:
                    print("Warning: Passed 'height' (deprecated), "
                          "'clearance_height', and 'hub_height'. Removing "
                          "'height' and 'clearance_height' and using "
                          "'hub_height' for scene generation")
                    hubheight = sceneDict['hub_height']
                    del sceneDict['clearance_height']
                    del sceneDict['height']
                else:
                    print("Warning: Passed 'height'(deprecated) and 'clearance"
                          "_height'. Removing 'height'")
                    del sceneDict['height']
                    hubheight = (sceneDict['clearance_height'] + 
                        0.5* np.sin(abs(tilt) * np.pi / 180) *  self.sceney - 
                        self.offsetfromaxis*np.sin(abs(tilt)*np.pi/180) )
            else:
                if 'hub_height' in sceneDict:
                    print("Warning: Passed 'height'(deprecated) and 'hub_"
                          "height'. Removing 'height'")
                    hubheight = sceneDict['hub_height']
                    del sceneDict['height']
                else:
                    print("Warning: 'height' is being deprecated. Assuming "
                          "height passed is hub_height")
                    hubheight = sceneDict['hub_height']
                    sceneDict['hub_height']=sceneDict['height']
                    del sceneDict['height']
        else:
            if 'hub_height' in sceneDict:
                if 'clearance_height' in sceneDict:
                    print("Warning: Passed 'hub_height' and 'clearance_height"
                          "'. Proceeding with 'hub_height' and removing "
                          "'clearance_height' from dictionary")
                    hubheight = sceneDict['hub_height']
                    del sceneDict['clearance_height']
                else:
                    hubheight = sceneDict['hub_height']
            else:
                if 'clearance_height' in sceneDict:
                    hubheight = (sceneDict['clearance_height'] + 
                        0.5* np.sin(abs(tilt) * np.pi / 180) *  self.sceney 
                        - self.offsetfromaxis*np.sin(abs(tilt)*np.pi/180) )
                else:
                    print("ERROR with sceneDict: No hub_height, clearance_"
                           "height or height (depr.) passed! Exiting routine.")
                    return



        # this is clearance_height, used for the title.
        height = hubheight - 0.5* np.sin(abs(tilt) * np.pi / 180) \
            * self.sceney + self.offsetfromaxis*np.sin(abs(tilt)*np.pi/180)

        try: 
            if sceneDict['pitch'] >0:
                pitch = sceneDict['pitch'] 
            else:
                raise Exception('default to gcr')
            
        except:

            if 'gcr' in sceneDict:
                pitch = np.round(self.sceney/sceneDict['gcr'],3)
            else:
                raise Exception('No valid `pitch` or `gcr` in sceneDict')



        ''' INITIALIZE VARIABLES '''
        text = '!xform '

        text += '-rx %s -t %s %s %s ' %(tilt, 0, 0, hubheight)
        
        # create nMods-element array along x, nRows along y. 1cm module gap.
        text += '-a %s -t %s 0 0 -a %s -t 0 %s 0 ' %(nMods, self.scenex, nRows, pitch)

        # azimuth rotation of the entire shebang. Select the row to scan here based on y-translation.
        # Modifying so center row is centered in the array. (i.e. 3 rows, row 2. 4 rows, row 2 too)
        # Since the array is already centered on row 1, module 1, we need to increment by Nrows/2-1 and Nmods/2-1

        text += (f'-i 1 -t {-self.scenex*(round(nMods/1.999)*1.0-1)} '
                 f'{-pitch*(round(nRows / 1.999)*1.0-1)} 0 -rz {180-azimuth} '
                 f'-t {originx} {originy} 0 ' )
        
        #axis tilt only working for N-S trackers
        if axis_tilt != 0 and azimuth == 90:  
            print("Axis_Tilt is still under development. The scene will be "
                  "created with the proper axis tilt, and the tracking angle"
                  "will consider the axis_tilt, but the sensors for the "
                  "analysis might not fall in the correct surfaces unless you"
                  " manually position them for this version. Sorry! :D ")
                  
            text += (f'-rx {axis_tilt} -t 0 0 %s ' %(
                self.scenex*(round(nMods/1.99)*1.0-1)*np.sin(
                        axis_tilt * np.pi/180) ) )

        filename = (f'{radname}_C_{height:0.5f}_rtr_{pitch:0.5f}_tilt_{tilt:0.5f}_'
                    f'{nMods}modsx{nRows}rows_origin{originx},{originy}.rad' )
        
        if hpc:
            text += os.path.join(os.getcwd(), self.modulefile) 
            radfile = os.path.join(os.getcwd(), 'objects', filename) 
        else:
            text += os.path.join(self.modulefile)
            radfile = os.path.join('objects',filename ) 

        # py2 and 3 compatible: binary write, encode text first
        with open(radfile, 'wb') as f:
            f.write(text.encode('ascii'))

        self.gcr = self.sceney / pitch
        self.text = text
        self.radfiles = radfile
        self.sceneDict = sceneDict
#        self.hub_height = hubheight
        return radfile
    
    def showModule(self, name):
        """ 
        Method to call objview on a module called 'name' and render it 
        (visualize it).
        
        Parameters
        ----------
        name : str
            Name of module to be rendered.
        
        """
        
        moduleDict = self.readModule(name)
        modulefile = moduleDict['modulefile']
        
        cmd = 'objview %s %s' % (os.path.join('materials', 'ground.rad'),
                                         modulefile)
        _,err = _popen(cmd,None)
        if err is not None:
            print('Error: {}'.format(err))
            print('possible solution: install radwinexe binary package from '
                  'http://www.jaloxa.eu/resources/radiance/radwinexe.shtml'
                  ' into your RADIANCE binaries path')
            return
    
    def showScene(self):
        """ 
        Method to call objview on the scene included in self
            
        """
        cmd = 'objview %s %s' % (os.path.join('materials', 'ground.rad'),
                                         self.radfiles)
        print('Rendering scene. This may take a moment...')
        _,err = _popen(cmd,None)
        if err is not None:
            print('Error: {}'.format(err))
            print('possible solution: install radwinexe binary package from '
                  'http://www.jaloxa.eu/resources/radiance/radwinexe.shtml'
                  ' into your RADIANCE binaries path')
            return
# end of SceneObj

class MetObj:
    """
    Meteorological data from EPW file.

    Initialize the MetObj from tmy data already read in. 
    
    Parameters
    -----------
    tmydata : DataFrame
        TMY3 output from :py:class:`~bifacial_radiance.RadianceObj.readTMY` or 
        from :py:class:`~bifacial_radiance.RadianceObj.readEPW`.
    metadata : Dictionary
        Metadata output from output from :py:class:`~bifacial_radiance.RadianceObj.readTMY`` 
        or from :py:class:`~bifacial_radiance.RadianceObj.readEPW`.
    label : str
        label : str
        'left', 'right', or 'center'. For data that is averaged, defines if the
        timestamp refers to the left edge, the right edge, or the center of the
        averaging interval, for purposes of calculating sunposition. For
        example, TMY3 data is right-labeled, so 11 AM data represents data from
        10 to 11, and sun position should be calculated at 10:30 AM.  Currently
        SAM and PVSyst use left-labeled interval data and NSRDB uses centered.

    """

    def __init__(self, tmydata, metadata, label = 'right'):

        import pytz
        import pvlib
        #import numpy as np

        #  location data.  so far needed:
        # latitude, longitude, elevation, timezone, city
        self.latitude = metadata['latitude']; lat=self.latitude
        self.longitude = metadata['longitude']; lon=self.longitude
        self.elevation = metadata['altitude']; elev=self.elevation
        self.timezone = metadata['TZ']
        try:
            self.city = metadata['Name'] # readepw version
        except KeyError:
            self.city = metadata['city'] # pvlib version
        #self.location.state_province_region = metadata['State'] # unecessary
        self.datetime = tmydata.index.tolist() # this is tz-aware.
        self.ghi = np.array(tmydata.GHI)
        self.dhi = np.array(tmydata.DHI)
        self.dni = np.array(tmydata.DNI)
        self.albedo = np.array(tmydata.Alb)
        
        #v0.2.5: initialize MetObj with solpos, sunrise/set and corrected time
        datetimetz = pd.DatetimeIndex(self.datetime)
        try:  # make sure the data is tz-localized.
            datetimetz = datetimetz.tz_localize(pytz.FixedOffset(self.timezone*60))#  use pytz.FixedOffset (in minutes)
        except TypeError:  # data is tz-localized already. Just put it in local time.
            datetimetz = datetimetz.tz_convert(pytz.FixedOffset(self.timezone*60))
        #check for data interval. default 1h.
        try:
            interval = datetimetz[1]-datetimetz[0]
        except IndexError:
            interval = pd.Timedelta('1h') # ISSUE: if 1 datapoint is passed, are we sure it's hourly data?
            print ("WARNING: TMY interval was unable to be defined, so setting it to 1h.")

        if label.lower() == 'center':
            print("Calculating Sun position for center labeled data, at exact timestamp in input Weather File")
            sunup= pvlib.irradiance.solarposition.sun_rise_set_transit_spa(datetimetz, lat, lon) #new for pvlib >= 0.6.1
            sunup['corrected_timestamp'] = datetimetz
        else:
            if interval== pd.Timedelta('1h'):

                if label.lower() == 'right':
                    print("Calculating Sun position for Metdata that is right-labeled ", 
                          "with a delta of -30 mins. i.e. 12 is 11:30 sunpos")
                    sunup= pvlib.irradiance.solarposition.sun_rise_set_transit_spa(datetimetz, lat, lon) #new for pvlib >= 0.6.1
                    sunup['minutedelta']= int(interval.seconds/2/60) # default sun angle 30 minutes before timestamp
                    # vector update of minutedelta at sunrise
                    sunrisemask = sunup.index.hour-1==sunup['sunrise'].dt.hour
                    sunup['minutedelta'].mask(sunrisemask,np.floor((60-(sunup['sunrise'].dt.minute))/2),inplace=True)
                    # vector update of minutedelta at sunset
                    sunsetmask = sunup.index.hour-1==sunup['sunset'].dt.hour
                    sunup['minutedelta'].mask(sunsetmask,np.floor((60-(sunup['sunset'].dt.minute))/2),inplace=True)
                    # save corrected timestamp
                    sunup['corrected_timestamp'] = sunup.index-pd.to_timedelta(sunup['minutedelta'], unit='m')
        
                elif label.lower() == 'left':        
                    print("Calculating Sun position for Metdata that is left-labeled ",
                          "with a delta of +30 mins. i.e. 12 is 12:30 sunpos.")
                    sunup= pvlib.irradiance.solarposition.sun_rise_set_transit_spa(datetimetz, lat, lon) 
                    sunup['minutedelta']= int(interval.seconds/2/60) # default sun angle 30 minutes after timestamp
                    # vector update of minutedelta at sunrise
                    sunrisemask = sunup.index.hour==sunup['sunrise'].dt.hour
                    sunup['minutedelta'].mask(sunrisemask,np.ceil((60+sunup['sunrise'].dt.minute)/2),inplace=True)
                    # vector update of minutedelta at sunset
                    sunsetmask = sunup.index.hour==sunup['sunset'].dt.hour
                    sunup['minutedelta'].mask(sunsetmask,np.ceil((60+sunup['sunset'].dt.minute)/2),inplace=True)
                    # save corrected timestamp
                    sunup['corrected_timestamp'] = sunup.index+pd.to_timedelta(sunup['minutedelta'], unit='m')
                else: raise ValueError('Error: invalid weather label passed. Valid inputs: right, left or center')
            else:
                minutedelta = int(interval.seconds/2/60)
                print("Interval in weather data is less than 1 hr, calculating Sun position with a delta of -",minutedelta)
                print("If you want no delta for sunposition, run simulation with input variable label='center'")
                #datetimetz=datetimetz-pd.Timedelta(minutes = minutedelta)   # This doesn't check for Sunrise or Sunset
                #sunup= pvlib.irradiance.solarposition.get_sun_rise_set_transit(datetimetz, lat, lon) # deprecated in pvlib 0.6.1
                sunup= pvlib.irradiance.solarposition.sun_rise_set_transit_spa(datetimetz, lat, lon) #new for pvlib >= 0.6.1
                sunup['corrected_timestamp'] = sunup.index-pd.Timedelta(minutes = minutedelta)
    
        self.solpos = pvlib.irradiance.solarposition.get_solarposition(sunup['corrected_timestamp'],lat,lon,elev)
        self.sunrisesetdata=sunup

    def _set1axis(self, cumulativesky=True, axis_azimuth=180, limit_angle=45,
                 angledelta=None, backtrack=True, gcr = 1.0/3.0, axis_tilt = 0,
                 fixed_tilt_angle=None):
        """
        Set up geometry for 1-axis tracking cumulativesky.  Solpos data
        already stored in `metdata.solpos`. Pull in tracking angle details from
        pvlib, create multiple 8760 metdata sub-files where datetime of met
        data matches the tracking angle.

        Parameters
        ------------
        cumulativesky : bool
            Whether individual csv files are created
            with constant tilt angle for the cumulativesky approach.
            if false, the gendaylit tracking approach must be used.
        axis_azimuth : numerical
            orientation axis of tracker torque tube. Default North-South (180 deg)
            For fixed tilt simulations (angledelta=0) this is the orientation azimuth
        limit_angle : numerical
            +/- limit angle of the 1-axis tracker in degrees. Default 45
            For fixed tilt simulations (angledelta=0) this is the tilt angle
        angledelta : numerical
            Degree of rotation increment to parse irradiance bins.
            Default 5 degrees (0.4 % error for DNI).
            Other options: 4 (.25%), 2.5 (0.1%).
            (the smaller the angledelta, the more simulations)
        fixed_tilt_angle : numerical
            Optional use. this changes to a fixed
            tilt simulation where each hour uses fixed_tilt_angle and
            axis_azimuth as the tilt and azimuth

        Returns
        -------
        trackerdict : dictionary 
            Keys for tracker tilt angles and
            list of csv metfile, and datetimes at that angle
            trackerdict[angle]['csvfile';'surf_azm';'surf_tilt';'UTCtime']
            Note: this output is mostly used for the cumulativesky approach.
        metdata.solpos : dataframe
            Pandas dataframe with output from pvlib solar position for each timestep
        metdata.sunrisesetdata :
            Pandas dataframe with sunrise, sunset and adjusted time data.
        metdata.tracker_theta : list
            Tracker tilt angle from pvlib for each timestep
        metdata.surface_tilt : list
            Tracker surface tilt angle from pvlib for each timestep
        metdata.surface_azimuth : list
            Tracker surface azimuth angle from pvlib for each timestep
        """

        # #DocumentationCheck : trackerdict Note of output still valid? I don't think so
          # Also -- is that metdata.solpos and sunrisesetdata properly documented as a return of this function?
          
        #axis_tilt = 0       # only support 0 tilt trackers for now
        self.cumulativesky = cumulativesky   # track whether we're using cumulativesky or gendaylit

        if (cumulativesky is True) & (angledelta is None):
            angledelta = 5  # round angle to 5 degrees for cumulativesky

        # get 1-axis tracker angles for this location,
        # round to nearest 'angledelta'
        trackingdata = self._getTrackingAngles(axis_azimuth,
                                               limit_angle,
                                               angledelta,
                                               axis_tilt = axis_tilt,
                                               backtrack = backtrack,
                                               gcr = gcr,
                                               fixed_tilt_angle=fixed_tilt_angle)

        # get list of unique rounded tracker angles
        theta_list = trackingdata.dropna()['theta_round'].unique()

        if cumulativesky is True:
            # create a separate metfile for each unique tracker theta angle.
            # return dict of filenames and details
            trackerdict = self._makeTrackerCSV(theta_list,trackingdata)
        else:
            # trackerdict uses timestamp as keys. return azimuth
            # and tilt for each timestamp
            times = [str(i)[5:-12].replace('-','_').replace(' ','_') for i in self.datetime]
            #trackerdict = dict.fromkeys(times)
            trackerdict = {}
            for i,time in enumerate(times) :
                # remove NaN tracker theta from trackerdict
                if (self.ghi[i] > 0) & (~np.isnan(self.tracker_theta[i])):
                    trackerdict[time] = {
                                        'surf_azm':self.surface_azimuth[i],
                                        'surf_tilt':self.surface_tilt[i],
                                        'theta':self.tracker_theta[i],
                                        'ghi':self.ghi[i],
                                        'dhi':self.dhi[i]
                                        }

        return trackerdict


    def _getTrackingAngles(self, axis_azimuth=180, limit_angle=45,
                           angledelta=None, axis_tilt=0, backtrack=True,
                           gcr = 1.0/3.0, fixed_tilt_angle=None):
        '''
        Helper subroutine to return 1-axis tracker tilt and azimuth data.

        Parameters
        ----------
        same as pvlib.tracking.singleaxis, plus:
        angledelta : degrees
            Angle to round tracker_theta to.  This is for
            cumulativesky simulations. Other input options: None (no 
            rounding of tracker angle) 
        fixed_tilt_angle : (Optional) degrees
            This changes to a fixed tilt simulation where each hour uses fixed_tilt_angle 
            and axis_azimuth as the tilt and azimuth

        Returns
        -------
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
        import pvlib
        #import numpy as np
        #import pandas as pd
        
        solpos = self.solpos
        
        #New as of 0.3.2:  pass fixed_tilt_angle and switches to FIXED TILT mode

        if fixed_tilt_angle is not None:
            # fixed tilt system with tilt = fixed_tilt_angle and
            # azimuth = axis_azimuth
            pvsystem = pvlib.pvsystem.PVSystem(fixed_tilt_angle,axis_azimuth) 
            # trackingdata keys: 'tracker_theta', 'aoi', 'surface_azimuth', 'surface_tilt'
            trackingdata = pd.DataFrame({'tracker_theta':limit_angle,
                                         'aoi':pvsystem.get_aoi(
                                                 solpos['zenith'], 
                                                 solpos['azimuth']),
                                         'surface_azimuth':axis_azimuth,
                                         'surface_tilt':limit_angle})
        else:
            # get 1-axis tracker tracker_theta, surface_tilt and surface_azimuth
            trackingdata = pvlib.tracking.singleaxis(solpos['zenith'],
                                                     solpos['azimuth'],
                                                     axis_tilt,
                                                     axis_azimuth,
                                                     limit_angle,
                                                     backtrack,
                                                     gcr)
            
        # save tracker tilt information to metdata.tracker_theta,
        # metdata.surface_tilt and metdata.surface_azimuth
        self.tracker_theta = np.round(trackingdata['tracker_theta'],2).tolist()
        self.surface_tilt = np.round(trackingdata['surface_tilt'],2).tolist()
        self.surface_azimuth = np.round(trackingdata['surface_azimuth'],2).tolist()
        # undo the  timestamp offset put in by solpos.
        #trackingdata.index = trackingdata.index + pd.Timedelta(minutes = 30)
        # It may not be exactly 30 minutes any more...
        trackingdata.index = self.sunrisesetdata.index  #this has the original time data in it

        # round tracker_theta to increments of angledelta for use in cumulativesky
        def _roundArbitrary(x, base=angledelta):
            # round to nearest 'base' value.
            # mask NaN's to avoid rounding error message
            return base * (x.dropna()/float(base)).round()

        if angledelta == 0:
            raise ZeroDivisionError('Angledelta = 0. Use None instead')
        elif angledelta is None: # don't round theta
            trackingdata['theta_round'] = trackingdata['tracker_theta']
        else:  # round theta
            trackingdata['theta_round'] = \
                _roundArbitrary(trackingdata['tracker_theta'], angledelta)

        return trackingdata

    def _makeTrackerCSV(self, theta_list, trackingdata):
        '''
        Create multiple new irradiance csv files with data for each unique
        rounded tracker angle. Return a dictionary with the new csv filenames
        and other details, Used for cumulativesky tracking

        Parameters
        -----------
        theta_list : array
             Array of unique tracker angle values

        trackingdata : Pandas 
             Pandas Series with hourly tracker angles from
             :pvlib.tracking.singleaxis

        Returns
        --------
        trackerdict : dictionary
              keys: *theta_round tracker angle  (default: -45 to +45 in
                                                 5 degree increments).
              sub-array keys:
                  *datetime:  array of datetime strings in this group of angles
                  *count:  number of datapoints in this group of angles
                  *surf_azm:  tracker surface azimuth during this group of angles
                  *surf_tilt:  tilt angle average during this group of angles
                  *csvfile:  name of csv met data file saved in /EPWs/
        '''

        dt = pd.to_datetime(self.datetime)

        trackerdict = dict.fromkeys(theta_list)

        for theta in sorted(trackerdict):  
            trackerdict[theta] = {}
            csvfile = os.path.join('EPWs', '1axis_{}.csv'.format(theta))
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
            for g, d, time in zip(self.ghi, self.dhi,
                                  dt.strftime('%Y-%m-%d %H:%M:%S')):

                # is this time included in a particular theta_round angle?
                if time in datetimetemp:
                    ghi_temp.append(g)
                    dhi_temp.append(d)
                else:
                    # mask out irradiance at this time, since it
                    # belongs to a different bin
                    ghi_temp.append(0.0)
                    dhi_temp.append(0.0)
            # save in 2-column GHI,DHI format for gencumulativesky -G
            savedata = pd.DataFrame({'GHI':ghi_temp, 'DHI':dhi_temp},
                                    index = self.datetime).tz_localize(None)
            # Fill partial year. Requires 2001 measurement year.
            if savedata.__len__() != 8760:
                savedata.loc[pd.to_datetime('2001-01-01 0:0:0')]=0
                savedata.loc[pd.to_datetime('2001-12-31 23:0:0')]=0
                savedata = savedata.resample('1h').asfreq(fill_value=0)
            print('Saving file {}, # points: {}'.format(
                  trackerdict[theta]['csvfile'], datetimetemp.__len__()))

            savedata.to_csv(csvfile,
                            index=False,
                            header=False,
                            sep=' ',
                            columns=['GHI','DHI'])


        return trackerdict


class AnalysisObj:
    """
    Analysis class for performing raytrace to obtain irradiance measurements
    at the array, as well plotting and reporting results    
    """
    
    def __init__(self, octfile=None, name=None):
        self.octfile = octfile
        self.name = name

    def makeImage(self, viewfile, octfile=None, name=None, hpc=False):
        """
        Makes a visible image (rendering) of octfile, viewfile
        """
        
        import time

        if octfile is None:
            octfile = self.octfile
        if name is None:
            name = self.name
        #TODO: update this for cross-platform compatibility w/ os.path.join
        #JSS
        if hpc is True:
            time_to_wait = 10
            time_counter = 0
            filelist = [octfile, "views/"+viewfile]
            for file in filelist:
                while not os.path.exists(file):
                    time.sleep(1)
                    time_counter += 1
                    if time_counter > time_to_wait:break

        print('Generating visible render of scene')
        #TODO: update this for cross-platform compatibility w os.path.join
        os.system("rpict -dp 256 -ar 48 -ms 1 -ds .2 -dj .9 -dt .1 "+
                  "-dc .5 -dr 1 -ss 1 -st .1 -ab 3  -aa .1 "+
                  "-ad 1536 -as 392 -av 25 25 25 -lr 8 -lw 1e-4 -vf views/"
                  +viewfile+ " " + octfile +
                  " > images/"+name+viewfile[:-3] +".hdr")

    def makeFalseColor(self, viewfile, octfile=None, name=None):
        """
        Makes a false-color plot of octfile, viewfile
        
        .. note::
            For Windows requires installation of falsecolor.exe,
            which is part of radwinexe-5.0.a.8-win64.zip found at
            http://www.jaloxa.eu/resources/radiance/radwinexe.shtml
        """
        #TODO: error checking for installation of falsecolor.exe 
        
        if octfile is None:
            octfile = self.octfile
        if name is None:
            name = self.name

        print('Generating scene in WM-2. This may take some time.')
        #TODO: update and test this for cross-platform compatibility using os.path.join
        cmd = "rpict -i -dp 256 -ar 48 -ms 1 -ds .2 -dj .9 -dt .1 "+\
              "-dc .5 -dr 1 -ss 1 -st .1 -ab 3  -aa .1 -ad 1536 -as 392 " +\
              "-av 25 25 25 -lr 8 -lw 1e-4 -vf views/"+viewfile + " " + octfile

        WM2_out,err = _popen(cmd,None)
        if err is not None:
            print('Error: {}'.format(err))
            return

        # determine the extreme maximum value to help with falsecolor autoscale
        extrm_out,err = _popen("pextrem",WM2_out.encode('latin1'))
        # cast the pextrem string as a float and find the max value
        WM2max = max(map(float,extrm_out.split()))
        print('Saving scene in false color')
        #auto scale false color map
        if WM2max < 1100:
            cmd = "falsecolor -l W/m2 -m 1 -s 1100 -n 11"
        else:
            cmd = "falsecolor -l W/m2 -m 1 -s %s"%(WM2max,)
        with open(os.path.join("images","%s%s_FC.hdr"%(name,viewfile[:-3]) ),"w") as f:
            data,err = _popen(cmd,WM2_out.encode('latin1'),f)
            if err is not None:
                print(err)
                print('possible solution: install radwinexe binary package from '
                      'http://www.jaloxa.eu/resources/radiance/radwinexe.shtml')

    def _linePtsArray(self, linePtsDict):
        """
        Helper function to just print the x y and z values in an array format,
        just like they will show in the .csv result files.
        
        """
        xstart = linePtsDict['xstart']
        ystart = linePtsDict['ystart']
        zstart = linePtsDict['zstart']
        xinc = linePtsDict['xinc']
        yinc = linePtsDict['yinc']
        zinc = linePtsDict['zinc']
        Nx = int(linePtsDict['Nx'])
        Ny = int(linePtsDict['Ny'])
        Nz = int(linePtsDict['Nz'])

        x = []
        y = []
        z = []

        for iz in range(0,Nz):
            for iy in range(0,Ny):
                x . append(xstart+iy*xinc)
                y . append(ystart+iy*yinc)
                z . append(zstart+iy*zinc)

        return x, y, z
        
    def _linePtsMakeDict(self, linePtsDict):
        a = linePtsDict
        linepts = self._linePtsMake3D(a['xstart'],a['ystart'],a['zstart'],
                                a['xinc'], a['yinc'], a['zinc'],
                                a['Nx'],a['Ny'],a['Nz'],a['orient'])
        return linepts

    def _linePtsMake3D(self, xstart, ystart, zstart, xinc, yinc, zinc,
                      Nx, Ny, Nz, orient):
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
            for iy in range(0,Ny):
                ypos = ystart+iy*yinc
                xpos = xstart+iy*xinc
                zpos = zstart+iy*zinc
                linepts = linepts + str(xpos) + ' ' + str(ypos) + \
                          ' '+str(zpos) + ' ' + orient + " \r"
        return(linepts)

    def _irrPlot(self, octfile, linepts, mytitle=None, plotflag=None,
                   accuracy='low', hpc=False):
        """
        (plotdict) = _irrPlot(linepts,title,time,plotflag, accuracy)
        irradiance plotting using rtrace
        pass in the linepts structure of the view along with a title string
        for the plots.  note that the plots appear in a blocking way unless
        you call pylab magic in the beginning.

        Parameters
        ------------
        octfile : string
            Filename and extension of .oct file
        linepts : 
            Output from :py:class:`bifacial_radiance.AnalysisObj._linePtsMake3D`
        mytitle : string
            Title to append to results files
        plotflag : Boolean
            Include plot of resulting irradiance
        accuracy : string
            Either 'low' (default - faster) or 'high'
            (better for low light)
        hpc : boolean, default False. Waits for octfile for a
            Longer time if parallel processing.

        Returns
        -------
        out : dictionary
            out.x,y,z  - coordinates of point
            .r,g,b     - r,g,b values in Wm-2
            .Wm2            - equal-weight irradiance
            .mattype        - material intersected
            .title      - title passed in
        """
        
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
            print('_irrPlot accuracy options: "low" or "high"')
            return({})



        temp_out,err = _popen(cmd,linepts.encode())
        if err is not None:
            if err[0:5] == 'error':
                raise Exception(err[7:])
            else:
                print(err)

        # when file errors occur, temp_out is None, and err message is printed.
        if temp_out is not None:
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
                import matplotlib.pyplot as plt
                plt.figure()
                plt.plot(out['Wm2'])
                plt.ylabel('Wm2 irradiance')
                plt.xlabel('variable')
                plt.title(mytitle)
                plt.show()
        else:
            out = None   # return empty if error message.

        return(out)

    def _saveResults(self, data, reardata=None, savefile=None, RGB = False):
        """
        Function to save output from _irrPlot
        If rearvals is passed in, back ratio is saved

        Returns
        --------
        savefile : str
            If set to None, will write to default .csv filename in results folder.
        """

        if savefile is None:
            savefile = data['title'] + '.csv'
        # make dataframe from results
        
        if RGB:
            data_sub = {key:data[key] for key in ['x', 'y', 'z', 'r', 'g', 'b', 'Wm2', 'mattype']}
            self.R = data['R']
            self.G = data['G']
            self.B = data['B']
            self.x = data['x']
            self.y = data['y']
            self.z = data['z']
            self.mattype = data['mattype']
        else:
            data_sub = {key:data[key] for key in ['x', 'y', 'z', 'Wm2', 'mattype']}
            self.x = data['x']
            self.y = data['y']
            self.z = data['z']
            self.mattype = data['mattype']
            
        if reardata is not None:
            self.rearX = reardata['x']
            self.rearY = reardata['y']
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
            
            if RGB:
                self.rearR = reardata['r']
                data_sub['rearR'] = self.rearR
                self.rearG = reardata['g']
                data_sub['rearG'] = self.rearG
                self.rearB = reardata['b']
                data_sub['rearB'] = self.rearB
                
                df = pd.DataFrame.from_dict(data_sub)
                df.to_csv(os.path.join("results", savefile), sep = ',',
                          columns = ['x','y','z','rearZ','mattype','rearMat',
                                     'Wm2Front','Wm2Back','Back/FrontRatio', 'R','G','B', 'rearR','rearG','rearB'],
                                     index = False) # new in 0.2.3

            else:
                df = pd.DataFrame.from_dict(data_sub)
                df.to_csv(os.path.join("results", savefile), sep = ',',
                          columns = ['x','y','z','rearZ','mattype','rearMat',
                                     'Wm2Front','Wm2Back','Back/FrontRatio'],
                                     index = False) # new in 0.2.3

        else:
            if RGB:
                df = pd.DataFrame.from_dict(data_sub)
                df.to_csv(os.path.join("results", savefile), sep = ',',
                          columns = ['x','y','z', 'mattype','Wm2', 'R', 'G', 'B'], index = False)
            else:
                df = pd.DataFrame.from_dict(data_sub)
                df.to_csv(os.path.join("results", savefile), sep = ',',
                          columns = ['x','y','z', 'mattype','Wm2'], index = False)
                
        print('Saved: %s'%(os.path.join("results", savefile)))
        return os.path.join("results", savefile)

    def _saveResultsCumulative(self, data, reardata=None, savefile=None):
        """
        TEMPORARY FUNCTION -- this is a fix to save ONE cumulative results csv
        in the main working folder for when doing multiple entries in a 
        tracker dict.
        
        Returns
        --------
        savefile : str
            If set to None, will write to default .csv filename in results folder.
        """

        if savefile is None:
            savefile = data['title'] + '.csv'
        # make dataframe from results
        data_sub = {key:data[key] for key in ['x', 'y', 'z', 'Wm2', 'mattype']}
        self.x = data['x']
        self.y = data['y']
        self.z = data['z']
        self.mattype = data['mattype']
        #TODO: data_sub front values don't seem to be saved to self.
        if reardata is not None:
            self.rearX = reardata['x']
            self.rearY = reardata['y']
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
            df.to_csv(savefile, sep = ',',
                      columns = ['x','y','z','rearZ','mattype','rearMat',
                                 'Wm2Front','Wm2Back','Back/FrontRatio'],
                                 index = False) # new in 0.2.3

        else:
            df = pd.DataFrame.from_dict(data_sub)
            df.to_csv(savefile, sep = ',',
                      columns = ['x','y','z', 'mattype','Wm2'], index = False)

        print('Saved: %s'%(savefile))
        return (savefile)

    def moduleAnalysis(self, scene, modWanted=None, rowWanted=None,
                       sensorsy=9.0, frontsurfaceoffset=0.001, backsurfaceoffset=0.001, debug=False):
        """
        This function defines the scan points to be used in the 
        :py:class:`~bifacial_radiance.AnalysisObj.analysis` function,
        to perform the raytrace through Radiance function `rtrace`

        Parameters
        ------------
        scene : ``SceneObj``
            Generated with :py:class:`~bifacial_radiance.RadianceObj.makeScene`.
        modWanted : int
            Module wanted to sample. If none, defaults to center module (rounding down)
        rowWanted : int
            Row wanted to sample. If none, defaults to center row (rounding down)
        sensorsy : int
            Number of 'sensors' or scanning points along the collector width 
            (CW) of the module(s)
        debug : bool
            Activates various print statemetns for debugging this function.

        Returns
        -------
        frontscan : dictionary
            Scan dictionary for module's front side. Used to pass into 
            :py:class:`~bifacial_radiance.AnalysisObj.analysis` function
        backscan : dictionary 
            Scan dictionary for module's back side. Used to pass into 
            :py:class:`~bifacial_radiance.AnalysisObj.analysis` function

        """

        # Height:  clearance height for fixed tilt systems, or torque tube
        #           height for single-axis tracked systems.
        #   Single axis tracked systems will consider the offset to calculate the final height.

        if sensorsy >0:
            sensorsy = sensorsy * 1.0
        else:
            raise Exception('input sensorsy must be numeric >0')

        dtor = np.pi/180.0

        # Internal scene parameters are stored in scene.sceneDict. Load these into local variables
        sceneDict = scene.sceneDict
        #moduleDict = scene.moduleDict  # not needed?


        azimuth = sceneDict['azimuth']
        tilt = sceneDict['tilt']
        nMods = sceneDict['nMods']
        nRows = sceneDict['nRows']
        originx = sceneDict['originx']
        originy = sceneDict['originy']

       # offset = moduleDict['offsetfromaxis']
        offset = scene.offsetfromaxis
        sceney = scene.sceney
        scenex = scene.scenex

        ## Check for proper input variables in sceneDict
        if 'pitch' in sceneDict:
            pitch = sceneDict['pitch']
        elif 'gcr' in sceneDict:
            pitch = sceney / sceneDict['gcr']
        else:
            raise Exception("Error: no 'pitch' or 'gcr' passed in sceneDict" )
        
        if 'axis_tilt' in sceneDict:
            axis_tilt = sceneDict['axis_tilt']
        else:
            axis_tilt = 0

        if 'z' in scene.moduleDict:
            modulez = scene.moduleDict['z']
        else:
            print ("Module's z not set on sceneDict internal dictionary. Setting to default")
            modulez = 0.02
            
        if frontsurfaceoffset is None:
            frontsurfaceoffset = 0.001
        if backsurfaceoffset is None:
            backsurfaceoffset = 0.001
        
        # The Sensor routine below needs a "hub-height", not a clearance height.
        # The below complicated check checks to see if height (deprecated) is passed,
        # and if clearance_height or hub_height is passed as well.

        # height internal variable defined here is equivalent to hub_height.
        if 'hub_height' in sceneDict:
            height = sceneDict['hub_height']

            if 'height' in sceneDict:
                print ("sceneDict warning: 'height' is deprecated, using "
                       "'hub_height' and deleting 'height' from sceneDict.")
                del sceneDict['height']

            if 'clearance_height' in sceneDict:
                print ("sceneDict warning: 'hub_height' and 'clearance_height"
                       "' passed to moduleAnalysis(). Using 'hub_height' "
                       "instead of 'clearance_height'")
        else:
            if 'clearance_height' in sceneDict:
                height = sceneDict['clearance_height'] + 0.5* \
                    np.sin(abs(tilt) * np.pi / 180) * \
                    sceney - offset*np.sin(abs(tilt)*np.pi/180)

                if 'height' in sceneDict:
                    print("sceneDict warning: 'height' is deprecated, using"
                          " 'clearance_height' for moduleAnalysis()")
                    del sceneDict['height']
            else:
                if 'height' in sceneDict:
                    print("sceneDict warning: 'height' is deprecated. "
                          "Assuming this was clearance_height that was passed"
                          " as 'height' and renaming it in sceneDict for "
                          "moduleAnalysis()")
                    height = (sceneDict['height'] + 0.5* np.sin(abs(tilt) * 
                                      np.pi / 180) * sceney - offset * 
                                      np.sin(abs(tilt)*np.pi/180) )
                else:
                    print("Isue with moduleAnalysis routine. No hub_height "
                          "or clearance_height passed (or even deprecated "
                          "height!)")

        if debug:
            print("For debug:\n hub_height, Azimuth, Tilt, nMods, nRows, "
                  "Pitch, Offset, SceneY, SceneX")
            print(height, azimuth, tilt, nMods, nRows,
                  pitch, offset, sceney, scenex)

        if modWanted == 0:
            print( " FYI Modules and Rows start at index 1. "
                  "Reindexing to modWanted 1"  )
            modWanted = modWanted+1  # otherwise it gives results on Space.

        if rowWanted ==0:
            print( " FYI Modules and Rows start at index 1. "
                  "Reindexing to rowWanted 1"  )
            rowWanted = rowWanted+1

        if modWanted is None:
            modWanted = round(nMods / 1.99)
        if rowWanted is None:
            rowWanted = round(nRows / 1.99)

        if debug is True:
            print( f"Sampling: modWanted {modWanted}, rowWanted {rowWanted} "
                  "out of {nMods} modules, {nRows} rows" )

        x0 = (modWanted-1)*scenex - (scenex*(round(nMods/1.99)*1.0-1))
        y0 = (rowWanted-1)*pitch - (pitch*(round(nRows / 1.99)*1.0-1))

        x1 = x0 * np.cos ((180-azimuth)*dtor) - y0 * np.sin((180-azimuth)*dtor)
        y1 = x0 * np.sin ((180-azimuth)*dtor) + y0 * np.cos((180-azimuth)*dtor)
        z1 = 0

        if axis_tilt != 0 and azimuth == 90:
            print ("fixing height for axis_tilt")
            #TODO check might need to do half a module more?
            z1 = (modWanted-1)*scenex * np.sin(axis_tilt*dtor)

        # Edge of Panel
        x2 = (sceney/2.0) * np.cos((tilt)*dtor) * np.sin((azimuth)*dtor)
        y2 = (sceney/2.0) * np.cos((tilt)*dtor) * np.cos((azimuth)*dtor)
        z2 = -(sceney/2.0) * np.sin(tilt*dtor)


        # Axis of rotation Offset (if offset is not 0) for the front of the module
        x3 = (offset + modulez + frontsurfaceoffset) * np.sin(tilt*dtor) * np.sin((azimuth)*dtor)
        y3 = (offset + modulez + frontsurfaceoffset) * np.sin(tilt*dtor) * np.cos((azimuth)*dtor)
        z3 = (offset + modulez + frontsurfaceoffset) * np.cos(tilt*dtor)

        # Axis of rotation Offset, for the back of the module 
        x4 = (offset - backsurfaceoffset) * np.sin(tilt*dtor) * np.sin((azimuth)*dtor)
        y4 = (offset - backsurfaceoffset) * np.sin(tilt*dtor) * np.cos((azimuth)*dtor)
        z4 = (offset - backsurfaceoffset) * np.cos(tilt*dtor)

        xstartfront = x1 + x2 + x3 + originx
        xstartback = x1 + x2 + x4 + originx

        ystartfront = y1 + y2 + y3 + originy
        ystartback = y1 + y2 + y4 + originy

        zstartfront = height + z1 + z2 + z3
        zstartback = height + z1 + z2 + z4

        xinc = -(sceney/(sensorsy + 1.0)) * np.cos((tilt)*dtor) * np.sin((azimuth)*dtor)
        yinc = -(sceney/(sensorsy + 1.0)) * np.cos((tilt)*dtor) * np.cos((azimuth)*dtor)
        zinc = (sceney/(sensorsy + 1.0)) * np.sin(tilt*dtor)

        if debug is True:
            print("Azimuth", azimuth)
            print("Coordinate Center Point of Desired Panel before azm rotation", x0, y0)
            print("Coordinate Center Point of Desired Panel after azm rotation", x1, y1)
            print("Edge of Panel", x2, y2, z2)
            print("Offset Shift", x3, y3, z3)
            print("Final Start Coordinate Front", xstartfront, ystartfront, zstartfront)
            print("Increase Coordinates", xinc, yinc, zinc)
        
        #NEW: adjust orientation of scan depending on tilt & azimuth
        zdir = np.cos((tilt)*dtor)
        ydir = np.sin((tilt)*dtor) * np.cos((azimuth)*dtor)
        xdir = np.sin((tilt)*dtor) * np.sin((azimuth)*dtor)
        front_orient = '%0.3f %0.3f %0.3f' % (-xdir, -ydir, -zdir)
        back_orient = '%0.3f %0.3f %0.3f' % (xdir, ydir, zdir)
    

        frontscan = {'xstart': xstartfront+xinc, 'ystart': ystartfront+yinc,
                     'zstart': zstartfront + zinc,
                     'xinc':xinc, 'yinc': yinc,
                     'zinc':zinc , 'Nx': 1, 'Ny':sensorsy, 'Nz':1, 'orient':front_orient }
        backscan = {'xstart':xstartback+xinc, 'ystart': ystartback+yinc,
                     'zstart': zstartback + zinc,
                     'xinc':xinc, 'yinc': yinc,
                     'zinc':zinc, 'Nx': 1, 'Ny':sensorsy, 'Nz':1, 'orient':back_orient }

        return frontscan, backscan

    def analysis(self, octfile, name, frontscan, backscan, plotflag=False, accuracy='low', hpc = False):
        """
        General analysis function, where linepts are passed in for calling the
        raytrace routine :py:class:`~bifacial_radiance.AnalysisObj._irrPlot` 
        and saved into results with 
        :py:class:`~bifacial_radiance.AnalysisObj._saveResults`.
        
        This function can also pass in the linepts structure of the view 
        along with a title string for the plots note that the plots appear in 
        a blocking way unless you call pylab magic in the beginning 

        Parameters
        ------------
        name : string 
            Name to append to output files
        octfile : string
            Filename and extension of .oct file
        frontscan : scene.frontscan object
            Object with the sensor location information for the 
            front of the module
        backscan : scene.backscan object
            Object with the sensor location information for the 
            rear side of the module
        plotflag : boolean
            Include plot of resulting irradiance
        accuracy : string 
            Either 'low' (default - faster) or 'high' (better for low light)

        Returns
        -------
         File saved in `\\results\\irr_name.csv`

        """

        if octfile is None:
            print('Analysis aborted - no octfile \n')
            return None, None
        linepts = self._linePtsMakeDict(frontscan)
        frontDict = self._irrPlot(octfile, linepts, name+'_Front',
                                    plotflag=plotflag, accuracy=accuracy, hpc = hpc)

        #bottom view.
        linepts = self._linePtsMakeDict(backscan)
        backDict = self._irrPlot(octfile, linepts, name+'_Back',
                                   plotflag=plotflag, accuracy=accuracy, hpc = hpc)
        # don't save if _irrPlot returns an empty file.
        if frontDict is not None:
            self._saveResults(frontDict, backDict,'irr_%s.csv'%(name) )

        return frontDict, backDict
    
def runJob(daydate):
    """
    Routine for the HPC, assigns each daydate to a different node and 
    performs all the bifacial radiance tasks.        
    
    Parameters
    ------------
    daydate : string 
         'MM_dd' corresponding to month_day i.e. '02_17' February 17th.
         
    """
    
    try:
        slurm_nnodes = int(os.environ['SLURM_NNODES'])
    except KeyError:
        print("Slurm environment not set. Are you running this in a job?")
        slurm_nnodes = 1 # Doing this instead of the exit allows it to run when not in slurm at regular speed for when you are testing stuff.
        #exit(1)

    print("entering runJob on node %s" % slurm_nnodes)
    
    demo.readEPW(epwfile=epwfile, hpc=hpc, daydate=daydate)

    print("1. Read EPW Finished")
    
    trackerdict = demo.set1axis(cumulativesky=cumulativesky,
                                axis_azimuth=axis_azimuth,
                                limit_angle=limit_angle,
                                angledelta=angledelta,
                                backtrack=backtrack,
                                gcr=gcr)
    
    print("2. set1axis Done")
    
    trackerdict = demo.gendaylit1axis(hpc=hpc)

    print("3. Gendalyit1axis Finished")
    
    #cdeline comment: previous version passed trackerdict into makeScene1axis.. 
    demo.makeScene1axis(moduletype=moduletype, sceneDict=sceneDict,
                        cumulativesky = cumulativesky, hpc = hpc)

    print("4. MakeScene1axis Finished")

    demo.makeOct1axis(trackerdict, hpc=True)

    trackerdict = demo.analysis1axis(trackerdict,
                                     modWanted=modWanted,
                                     rowWanted=rowWanted,
                                     sensorsy=sensorsy, customname=daydate)
    print("5. Finished ", daydate)


def quickExample(testfolder=None):
    """
    Example of how to run a Radiance routine for a simple rooftop bifacial system

    """

    import bifacial_radiance
    
    if testfolder == None:
        testfolder = bifacial_radiance.main._interactive_directory(
            title = 'Select or create an empty directory for the Radiance tree')

    demo = bifacial_radiance.RadianceObj('simple_panel',path = testfolder)  # Create a RadianceObj 'object'

    #    A=load_inputvariablesfile()

    # input albedo number or material name like 'concrete'.
    # To see options, run setGround without any input.
    demo.setGround(0.62)
    try:
        epwfile = demo.getEPW(37.5,-77.6) # pull TMY data for any global lat/lon
    except ConnectionError: # no connection to automatically pull data
        pass

    metdata = demo.readEPW(epwfile) # read in the EPW weather data from above
    #metdata = demo.readTMY() # select a TMY file using graphical picker
    # Now we either choose a single time point, or use cumulativesky for the entire year.
    cumulativeSky = True
    if cumulativeSky:
        demo.genCumSky(demo.epwfile) # entire year.
    else:
        demo.gendaylit(metdata=metdata, timeindex=4020)  # Noon, June 17th


    # create a scene using panels in landscape at 10 deg tilt, 1.5m pitch. 0.2 m ground clearance
    moduletype = 'test'
    moduleDict = demo.makeModule(name = moduletype, x = 1.59, y = 0.95 )
    sceneDict = {'tilt':10,'pitch':1.5,'clearance_height':0.2,
                 'azimuth':180, 'nMods': 20, 'nRows': 7}
    #makeScene creates a .rad file with 20 modules per row, 7 rows.
    scene = demo.makeScene(moduletype=moduletype, sceneDict=sceneDict)
    # makeOct combines all of the ground, sky and object files into .oct file.
    octfile = demo.makeOct(demo.getfilelist())

    # return an analysis object including the scan dimensions for back irradiance
    analysis = bifacial_radiance.AnalysisObj(octfile, demo.name)
    frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=9)
    analysis.analysis(octfile, demo.name, frontscan, backscan)
    # bifacial ratio should be 12.8% - 12.9% !
    print('Annual bifacial ratio average:  %0.3f' %(
            sum(analysis.Wm2Back) / sum(analysis.Wm2Front) ) )

    return analysis
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
import warnings
#from input import *

# Mutual parameters across all processes
#daydate=sys.argv[1]


global DATA_PATH # path to data files including module.json.  Global context
#DATA_PATH = os.path.abspath(pkg_resources.resource_filename('bifacial_radiance', 'data/') )
DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

def _findme(lst, a): #find string match in a list. script from stackexchange
    return [i for i, x in enumerate(lst) if x == a]

def _missingKeyWarning(dictype, missingkey, newvalue): # prints warnings 
    if type(newvalue) is bool:
        valueunit = ''
    else:
        valueunit = 'm'
    print("Warning: {} Dictionary Parameters passed, but {} is missing. ".format(dictype, missingkey))        
    print("Setting it to default value of {} {} to continue\n".format(newvalue, valueunit))

def _normRGB(r, g, b): #normalize by each color for human vision sensitivity
    return r*0.216+g*0.7152+b*0.0722

def _popen(cmd, data_in, data_out=PIPE):
    """
    Helper function subprocess.popen replaces os.system
    - gives better input/output process control
    usage: pass <data_in> to process <cmd> and return results
    based on rgbeimage.py (Thomas Bleicher 2010)
    """
    if type(cmd) == str:
        cmd = str(cmd) # gets rid of unicode oddities
        shell=True
    else:
        shell=False

    p = Popen(cmd, bufsize=-1, stdin=PIPE, stdout=data_out, stderr=PIPE, shell=shell) #shell=True required for Linux? quick fix, but may be security concern
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

def _modDict(originaldict, moddict, relative=False):
    '''
    Compares keys in originaldict with moddict and updates values of 
    originaldict to moddict if existing.
    
    Parameters
    ----------
    originaldict : dictionary
        Original dictionary calculated, for example frontscan or backscan dictionaries.
    moddict : dictionary
        Modified dictinoary, for example modscan['xstart'] = 0 to change position of x.
    relative : Bool
        if passing modscanfront and modscanback to modify dictionarie of positions,
        this sets if the values passed to be updated are relative or absolute. 
        Default is absolute value (relative=False)
            
    Returns
    -------
    originaldict : dictionary
        Updated original dictionary with values from moddict.
    '''
    newdict = originaldict.copy()

    for key in moddict:
        try:
            if relative:
                newdict[key] = moddict[key] + newdict[key]
            else:
                newdict[key] = moddict[key]
        except:
            print("Wrong key in modified dictionary")
    
    return newdict

def _heightCasesSwitcher(sceneDict, preferred='hub_height', nonpreferred='clearance_height'):
        """
        
        Parameters
        ----------
        sceneDict : dictionary
            Dictionary that might contain more than one way of defining height for 
            the array: `clearance_height`, `hub_height`, `height`*
            * height deprecated from sceneDict. This function helps choose
            * which definition to use.  
        preferred : str, optional
            When sceneDict has hub_height and clearance_height, or it only has height,
            it will leave only the preferred option.. The default is 'hub_height'.
        nonpreferred : TYPE, optional
            When sceneDict has hub_height and clearance_height, 
            it wil ldelete this nonpreferred option. The default is 'clearance_height'.
    
        Returns
        -------
        sceneDict : TYPE
            Dictionary now containing the appropriate definition for system height. 
        use_clearanceheight : Bool
            Helper variable to specify if dictionary has only clearancehet for
            use inside `makeScene1axis`. Will get deprecated once that internal
            function is streamlined.
    
        """
        # TODO: When we update to python 3.9.0, this could be a Switch Cases (Structural Pattern Matching):
    
            
        heightCases = '_'
        if 'height' in sceneDict:
            heightCases = heightCases+'height__'
        if 'clearance_height' in sceneDict:
            heightCases = heightCases+'clearance_height__'
        if 'hub_height' in sceneDict:
            heightCases = heightCases+'hub_height__'
        
        use_clearanceheight = False
        # CASES:
        if heightCases == '_height__':
            print("sceneDict Warning: 'height' is being deprecated. "+
                                  "Renaming as "+preferred)
            sceneDict[preferred]=sceneDict['height']
            del sceneDict['height']
        
        elif heightCases == '_clearance_height__':
            #print("Using clearance_height.")
            use_clearanceheight = True
            
        elif heightCases == '_hub_height__':
            #print("Using hub_height.'")
            pass
        elif heightCases == '_height__clearance_height__':  
            print("sceneDict Warning: 'clearance_height and 'height' "+
                  "(deprecated) are being passed. removing 'height' "+
                  "from sceneDict for this tracking routine")
            del sceneDict['height']
            use_clearanceheight = True
                            
        elif heightCases == '_height__hub_height__':     
            print("sceneDict Warning: 'height' is being deprecated. Using 'hub_height'")
            del sceneDict['height']
        
        elif heightCases == '_height__clearance_height__hub_height__':       
            print("sceneDict Warning: 'hub_height', 'clearance_height'"+
                  ", and 'height' are being passed. Removing 'height'"+
                  " (deprecated) and "+ nonpreferred+ ", using "+preferred)
            del sceneDict[nonpreferred]
        
        elif heightCases == '_clearance_height__hub_height__':  
            print("sceneDict Warning: 'hub_height' and 'clearance_height'"+
                  " are being passed. Using "+preferred+
                  " and removing "+ nonpreferred)
            del sceneDict[nonpreferred]
    
        else: 
            print ("sceneDict Error! no argument in sceneDict found "+
                   "for 'hub_height', 'height' nor 'clearance_height'. "+
                   "Exiting routine.")
            
        return sceneDict, use_clearanceheight

def _is_leap_and_29Feb(s): # Removes Feb. 29 if it a leap year.
    return (s.index.year % 4 == 0) & \
           ((s.index.year % 100 != 0) | (s.index.year % 400 == 0)) & \
           (s.index.month == 2) & (s.index.day == 29)

def _subhourlydatatoGencumskyformat(gencumskydata, label='right'):
    # Subroutine to resample, pad, remove leap year and get data in the
    # 8760 hourly format
    # for saving the temporary files for gencumsky in _saveTempTMY and
    # _makeTrackerCSV
    

    #Resample to hourly. Gencumsky wants right-labeled data.
    gencumskydata = gencumskydata.resample('60T', closed='right', label='right').mean()       
    
    if label == 'left': #switch from left to right labeled by adding an hour
        gencumskydata.index = gencumskydata.index + pd.to_timedelta('1H')
                     

    # Padding
    tzinfo = gencumskydata.index.tzinfo
    padstart = pd.to_datetime('%s-%s-%s %s:%s' % (gencumskydata.index.year[0],1,1,1,0 ) ).tz_localize(tzinfo)
    padend = pd.to_datetime('%s-%s-%s %s:%s' % (gencumskydata.index.year[0]+1,1,1,0,0) ).tz_localize(tzinfo)
    gencumskydata.iloc[0] = 0  # set first datapt to zero to forward fill w zeros
    gencumskydata.iloc[-1] = 0  # set last datapt to zero to forward fill w zeros
    # check if index exists. I'm sure there is a way to do this backwards.
    if any(gencumskydata.index.isin([padstart])):
        print("Data starts on Jan. 01")
    else:
        gencumskydata=gencumskydata.append(pd.DataFrame(index=[padstart]))
    if any(gencumskydata.index.isin([padend])):
        print("Data ends on Dec. 31st")
    else:
        gencumskydata=gencumskydata.append(pd.DataFrame(index=[padend]))
    gencumskydata.loc[padstart]=0
    gencumskydata.loc[padend]=0
    gencumskydata=gencumskydata.sort_index() 
    # Fill empty timestamps with zeros
    gencumskydata = gencumskydata.resample('60T').asfreq().fillna(0)
    # Mask leap year
    leapmask =  ~(_is_leap_and_29Feb(gencumskydata))
    gencumskydata = gencumskydata[leapmask]

    if (gencumskydata.index.year[-1] == gencumskydata.index.year[-2]+1) and len(gencumskydata)>8760:
        gencumskydata = gencumskydata[:-1]
    return gencumskydata
    # end _subhourlydatatoGencumskyformat        
    

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
    def __repr__(self):
        return str(self.__dict__)  
    def __init__(self, name=None, path=None, hpc=False):
        '''
        initialize RadianceObj with path of Radiance materials and objects,
        as well as a basename to append to

        Parameters
        ----------
        name: string, append temporary and output files with this value
        path: location of Radiance materials and objects
        hpc:  Keeps track if User is running simulation on HPC so some file 
              reading routines try reading a bit longer and some writing 
              routines (makeModule) that overwrite themselves are inactivated.

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
        self.hpc = hpc           # HPC simulation is being run. Some read/write functions are modified
        
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

    #def setHPC(self, hpc=True):
    #    self.hpc = hpc
        
    def addMaterial(self, material, Rrefl, Grefl, Brefl, materialtype='plastic', 
                    specularity=0, roughness=0, material_file=None, comment=None, rewrite=True):
        """
        Function to add a material in Radiance format. 


        Parameters
        ----------
        material : str
            DESCRIPTION.
        Rrefl : str
            Reflectivity for first wavelength, or 'R' bin.
        Grefl : str
            Reflecstrtivity for second wavelength, or 'G' bin.
        Brefl : str
            Reflectivity for third wavelength, or 'B' bin.
        materialtype : str, optional
            Type of material. The default is 'plastic'. Others can be mirror,
            trans, etc. See RADIANCe documentation. 
        specularity : str, optional
            Ratio of reflection that is specular and not diffuse. The default is 0.
        roughness : str, optional
            This is the microscopic surface roughness: the more jagged the 
            facets are, the rougher it is and more blurry reflections will appear.
        material_file : str, optional
            DESCRIPTION. The default is None.
        comment : str, optional
            DESCRIPTION. The default is None.
        rewrite : str, optional
            DESCRIPTION. The default is True.

        Returns
        -------
        None. Just adds the material to the material_file specified or the 
        default in ``materials\ground.rad``.

        References:
            See examples of documentation for more materialtype details.
            http://www.jaloxa.eu/resources/radiance/documentation/docs/radiance_tutorial.pdf page 10
     
            Also, you can use https://www.jaloxa.eu/resources/radiance/colour_picker.shtml 
            to have a sense of how the material would look with the RGB values as 
            well as specularity and roughness.

            To understand more on reflectivity, specularity and roughness values
            https://thinkmoult.com/radiance-specularity-and-roughness-value-examples.html
            
        """
        if material_file is None:
            material_file = 'ground.rad'    
    
        matfile = os.path.join('materials', material_file)
        
        with open(matfile, 'r') as fp:
            buffer = fp.readlines()
                
        # search buffer for material matching requested addition
        found = False
        for i in buffer:
            if materialtype and material in i:
                loc = buffer.index(i)
                found = True
                break
        if found:
            if rewrite:            
                print('Material exists, overwriting...\n')
                if comment is None:
                    pre = loc - 1
                else:
                    pre = loc - 2            
                # commit buffer without material match
                with open(matfile, 'w') as fp:
                    for i in buffer[0:pre]:
                        fp.write(i)
                    for i in buffer[loc+4:]:
                        fp.write(i)
        if (found and rewrite) or (not found):
            # append -- This will create the file if it doesn't exist
            file_object = open(matfile, 'a')
            file_object.write("\n\n")
            if comment is not None:
                file_object.write("#{}".format(comment))
            file_object.write("\nvoid {} {}".format(materialtype, material))
            if materialtype == 'glass':
                file_object.write("\n0\n0\n3 {} {} {}".format(Rrefl, Grefl, Brefl))
            else:
                file_object.write("\n0\n0\n5 {} {} {} {} {}".format(Rrefl, Grefl, Brefl, specularity, roughness))
            file_object.close()
            print('Added material {} to file {}'.format(material, material_file))
        if (found and not rewrite):
            print('Material already exists\n')

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
            print ("\n Warning: For cumulativesky simulations, exporting the "
                   "TrackerDict requires reindex = False. Setting reindex = "
                   "False and proceeding")
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
      
        
    def readWeatherFile(self, weatherFile=None, starttime=None, 
                        endtime=None, label=None, source=None,
                        coerce_year=None, tz_convert_val=None):
        """
        Read either a EPW or a TMY file, calls the functions 
        :py:class:`~bifacial_radiance.readTMY` or
        :py:class:`~bifacial_radiance.readEPW` 
        according to the weatherfile extention.
        
        Parameters
        ----------
        weatherFile : str
            File containing the weather information. EPW, TMY or solargis accepted.
        starttime : str
            Limited start time option in 'YYYY-mm-dd_HHMM' or 'mm_dd_HH' format
        endtime : str
            Limited end time option in 'YYYY-mm-dd_HHMM' or 'mm_dd_HH' format
        daydate : str  DEPRECATED
            For single day in 'MM/DD' or MM_DD format.  Now use starttime and 
            endtime set to the same date.
        label : str
            'left', 'right', or 'center'. For data that is averaged, defines if
            the timestamp refers to the left edge, the right edge, or the 
            center of the averaging interval, for purposes of calculating 
            sunposition. For example, TMY3 data is right-labeled, so 11 AM data 
            represents data from 10 to 11, and sun position is calculated 
            at 10:30 AM.  Currently SAM and PVSyst use left-labeled interval 
            data and NSRDB uses centered.
        source : str
            To help identify different types of .csv files. If None, it assumes
            it is a TMY3-style formated data. Current options: 'TMY3', 
            'solargis', 'EPW'
        coerce_year : int
            Year to coerce weather data to in YYYY format, ie 2021. 
            If more than one year of data in the  weather file, year is NOT coerced.
        tz_convert_val : int 
            Convert timezone to this fixed value, following ISO standard 
            (negative values indicating West of UTC.)
        """
        #from datetime import datetime
        import warnings
        
        if weatherFile is None:
            if hasattr(self,'epwfile'):
                weatherFile = self.epwfile
            else:
                try:
                    weatherFile = _interactive_load('Select EPW or TMY3 climate file')
                except:
                    raise Exception('Interactive load failed. Tkinter not supported'+
                                    'on this system. Try installing X-Quartz and reloading')
        if coerce_year is not None:
            coerce_year = int(coerce_year)
            if str(coerce_year).__len__() != 4:
                warnings.warn('Incorrect coerce_year. Setting to None')
                coerce_year = None
                
        
        def _parseTimes(t, hour, coerce_year):
            '''
            parse time input t which could be string mm_dd_HH or YYYY-mm-dd_HHMM
            or datetime.datetime object.  Return pd.datetime object.  Define
            hour as hour input if not passed directly.
            '''
            import re
            
            if type(t) == str:
                try:
                    tsplit = re.split('-|_| ', t)
                    
                    #mm_dd format
                    if tsplit.__len__() == 2 and t.__len__() == 5: 
                        if coerce_year is None:
                                coerce_year = 2021 #default year. 
                        tsplit.insert(0,str(coerce_year))
                        tsplit.append(str(hour).rjust(2,'0')+'00')
                        
                    #mm_dd_hh or YYYY_mm_dd format
                    elif tsplit.__len__() == 3 :
                        if tsplit[0].__len__() == 2:
                            if coerce_year is None:
                                coerce_year = 2021 #default year. 
                            tsplit.insert(0,str(coerce_year))
                        elif tsplit[0].__len__() == 4:
                            tsplit.append(str(hour).rjust(2,'0')+'00')
                            
                    #YYYY-mm-dd_HHMM  format
                    if tsplit.__len__() == 4 and tsplit[0].__len__() == 4:
                        t_out = pd.to_datetime(''.join(tsplit).ljust(12,'0') ) 
                    
                    else:
                        raise Exception(f'incorrect time string passed {t}.'
                                        'Valid options: mm_dd, mm_dd_HH, '
                                        'mm_dd_HHMM, YYYY-mm-dd_HHMM')  
                except Exception as e:
                    # Error for incorrect string passed:
                    raise(e)
            else:  #datetime or timestamp
                try:
                    t_out = pd.to_datetime(t)
                except pd.errors.ParserError:
                    print('incorrect time object passed.  Valid options: '
                          'string or datetime.datetime or pd.timeIndex. You '
                          f'passed {type(t)}.')
            return t_out, coerce_year
        # end _parseTimes
        
        def _tz_convert(metdata, metadata, tz_convert_val):
            """
            convert metdata to a different local timzone.  Particularly for 
            SolarGIS weather files which are returned in UTC by default.
            ----------
            tz_convert_val : int
                Convert timezone to this fixed value, following ISO standard 
                (negative values indicating West of UTC.)
            Returns: metdata, metadata  
            """
            import pytz
            if (type(tz_convert_val) == int) | (type(tz_convert_val) == float):
                metadata['TZ'] = tz_convert_val
                metdata = metdata.tz_convert(pytz.FixedOffset(tz_convert_val*60))
            return metdata, metadata
        # end _tz_convert

        if source is None:
    
            if weatherFile[-3:].lower() == 'epw':
                source = 'EPW'
            else:
                print('Warning: CSV file passed for input. Assuming it is TMY3'+
                      'style format') 
                source = 'TMY3'
            if label is None:
                label = 'right' # EPW and TMY are by deffault right-labeled.

        if source.lower() == 'solargis':
            if label is None:
                label = 'center'
            metdata, metadata = self._readSOLARGIS(weatherFile, label=label)

        if source.lower() =='epw':
            metdata, metadata = self._readEPW(weatherFile, label=label)

        if source.lower() =='tmy3':
            metdata, metadata = self._readTMY(weatherFile, label=label)
        
        metdata, metadata = _tz_convert(metdata, metadata, tz_convert_val)
        tzinfo = metdata.index.tzinfo
        tempMetDatatitle = 'metdata_temp.csv'

        # Parse the start and endtime strings. 
        if starttime is not None:
            starttime, coerce_year = _parseTimes(starttime, 1, coerce_year)
            starttime = starttime.tz_localize(tzinfo)
        if endtime is not None:
            endtime, coerce_year = _parseTimes(endtime, 23, coerce_year)
            endtime = endtime.tz_localize(tzinfo)
        '''
        #TODO: do we really need this check?
        if coerce_year is not None and starttime is not None:
            if coerce_year != starttime.year or coerce_year != endtime.year:
                print("Warning: Coerce year does not match requested sampled "+
                      "date(s)'s years. Setting Coerce year to None.")
                coerce_year = None
        '''        

        tmydata_trunc = self._saveTempTMY(metdata, filename=tempMetDatatitle, 
                                          starttime=starttime, endtime=endtime, 
                                          coerce_year=coerce_year,
                                          label=label)

        if tmydata_trunc.__len__() > 0:
            self.metdata = MetObj(tmydata_trunc, metadata, label = label)
        else:
            self.metdata = None
            raise Exception('Weather file returned zero points for the '
                  'starttime / endtime  provided')
        
        
        return self.metdata

    def _saveTempTMY(self, tmydata, filename=None, starttime=None, endtime=None, 
                     coerce_year=None, label=None):
        '''
        private function to save part or all of tmydata into /EPWs/ for use 
        in gencumsky -G mode and return truncated  tmydata. Gencumsky 8760
        starts with Jan 1, 1AM and ends Dec 31, 2400
        
        starttime:  tz-localized pd.TimeIndex
        endtime:    tz-localized pd.TimeIndex
        
        returns: tmydata_truncated  : subset of tmydata based on start & end
        '''
        
        
        if filename is None:
            filename = 'temp.csv'
              
                           
        gencumskydata = None
        gencumdict = None
        if len(tmydata) == 8760: 
            print("8760 line in WeatherFile. Assuming this is a standard hourly"+
                  " WeatherFile for the year for purposes of saving Gencumulativesky"+
                  " temporary weather files in EPW folder.")
            if coerce_year is None and starttime is not None:
                coerce_year = starttime.year
            # SILVANA:  If user doesn't pass starttime, and doesn't select
            # coerce_year, then do we really need to coerce it?
            elif coerce_year is None:
                coerce_year = 2021                
            print(f"Coercing year to {coerce_year}")
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                tmydata.index.values[:] = tmydata.index[:] + pd.DateOffset(year=(coerce_year))
                # Correcting last index to next year.
                tmydata.index.values[-1] = tmydata.index[-1] + pd.DateOffset(year=(coerce_year+1))
        
            # FilterDates
            filterdates = None
            if starttime is not None and endtime is not None:
                starttime
                filterdates = (tmydata.index >= starttime) & (tmydata.index <= endtime)
            else:
                if starttime is not None:
                    filterdates = (tmydata.index >= starttime)
                if endtime is not None:
                    filterdates = (tmydata.index <= endtime)
            
            if filterdates is not None:
                print("Filtering dates")
                tmydata[~filterdates] = 0
        
            gencumskydata = tmydata.copy()
            
        else:
            if len(tmydata.index.year.unique()) == 1:
                if coerce_year:
                    # TODO: check why subhourly data still has 0 entries on the next day on _readTMY3
                    # in the meantime, let's make Silvana's life easy by just deletig 0 entries
                    tmydata = tmydata[~(tmydata.index.hour == 0)] 
                    print(f"Coercing year to {coerce_year}")
                    # TODO: this coercing shows a python warning. Turn it off or find another method? bleh.
                    tmydata.index.values[:] = tmydata.index[:] + pd.DateOffset(year=(coerce_year))
        
                # FilterDates
                filterdates = None
                if starttime is not None and endtime is not None:
                    filterdates = (tmydata.index >= starttime) & (tmydata.index <= endtime)
                else:
                    if starttime is not None:
                        filterdates = (tmydata.index >= starttime)
                    if endtime is not None:
                        filterdates = (tmydata.index <= endtime)
                
                if filterdates is not None:
                    print("Filtering dates")
                    tmydata[~filterdates] = 0
        
                gencumskydata = tmydata.copy()
                gencumskydata = _subhourlydatatoGencumskyformat(gencumskydata, 
                                                                label=label)
        
            else:
                if coerce_year:
                    print("More than 1 year of data identified. Can't do coercing")
                
                # Check if years are consecutive
                l = list(tmydata.index.year.unique())
                if l != list(range(min(l), max(l)+1)):
                    print("Years are not consecutive. Won't be able to use Gencumsky"+
                          " because who knows what's going on with this data.")
                else:
                    print("Years are consecutive. For Gencumsky, make sure to select"+
                          " which yearly temporary weather file you want to use"+
                          " else they will all get accumulated to same hour/day")
                    
                    # FilterDates
                    filterdates = None
                    if starttime is not None and endtime is not None:
                        filterdates = (tmydata.index >= starttime) & (tmydata.index <= endtime)
                    else:
                        if starttime is not None:
                            filterdates = (tmydata.index >= starttime)
                        if endtime is not None:
                            filterdates = (tmydata.index <= endtime)
                    
                    if filterdates is not None:
                        print("Filtering dates")
                        tmydata = tmydata[filterdates] # Reducing years potentially
        
                    # Checking if filtering reduced to just 1 year to do usual savin.
                    if len(tmydata.index.year.unique()) == 1:
                        gencumskydata = tmydata.copy()
                        gencumskydata = _subhourlydatatoGencumskyformat(gencumskydata,
                                                                        label=label)

                    else:
                        gencumdict = [g for n, g in tmydata.groupby(pd.Grouper(freq='Y'))]
                        
                        for ii in range(0, len(gencumdict)):
                            gencumskydata = gencumdict[ii]
                            gencumskydata = _subhourlydatatoGencumskyformat(gencumskydata,
                                                                            label=label)
                            gencumdict[ii] = gencumskydata
                        
                        gencumskydata = None # clearing so that the dictionary style can be activated.
        
        
        # Let's save files in EPWs folder for Gencumsky     
        if gencumskydata is not None:
            csvfile = os.path.join('EPWs', filename)
            print('Saving file {}, # points: {}'.format(csvfile, gencumskydata.__len__()))
            gencumskydata.to_csv(csvfile, index=False, header=False, sep=' ', columns=['GHI','DHI'])
            self.gencumsky_metfile = csvfile
        
        if gencumdict is not None:
            self.gencumsky_metfile = []
            for ii in range (0, len(gencumdict)):
                gencumskydata = gencumdict[ii]
                newfilename = filename.split('.')[0]+'_year_'+str(ii)+'.csv'
                csvfile = os.path.join('EPWs', newfilename)
                print('Saving file {}, # points: {}'.format(csvfile, gencumskydata.__len__()))
                gencumskydata.to_csv(csvfile, index=False, header=False, sep=' ', columns=['GHI','DHI'])
                self.gencumsky_metfile.append(csvfile)

        return tmydata

        
    def _readTMY(self, tmyfile=None, label = 'right', coerce_year=None):
        '''
        use pvlib to read in a tmy3 file.
        Note: pvlib 0.7 does not currently support sub-hourly files. Until
        then, use _readTMYdate() to create the index

        Parameters
        ------------
        tmyfile : str
            Filename of tmy3 to be read with pvlib.tmy.readtmy3
        label : str
            'left', 'right', or 'center'. For data that is averaged, defines if
            the timestamp refers to the left edge, the right edge, or the 
            center of the averaging interval, for purposes of calculating 
            sunposition. For example, TMY3 data is right-labeled, so 11 AM data 
            represents data from 10 to 11, and sun position is calculated 
            at 10:30 AM.  Currently SAM and PVSyst use left-labeled interval 
            data and NSRDB uses centered.
        coerce_year : int
            Year to coerce to. Default is 2021. 
        
        Returns
        -------
        metdata - MetObj collected from TMY3 file
        '''
        def _convertTMYdate(data, meta):
            ''' requires pvlib 0.8, updated to handle subhourly timestamps '''
            # get the date column as a pd.Series of numpy datetime64
            data_ymd = pd.to_datetime(data['Date (MM/DD/YYYY)'])
            # shift the time column so that midnite is 00:00 instead of 24:00
            shifted_hour = data['Time (HH:MM)'].str[:2].astype(int) % 24
            minute = data['Time (HH:MM)'].str[3:].astype(int) 
            # shift the dates at midnite so they correspond to the next day
            data_ymd[shifted_hour == 0] += datetime.timedelta(days=1)
            # NOTE: as of pandas>=0.24 the pd.Series.array has a month attribute, but
            # in pandas-0.18.1, only DatetimeIndex has month, but indices are immutable
            # so we need to continue to work with the panda series of dates `data_ymd`
            data_index = pd.DatetimeIndex(data_ymd)
            # use indices to check for a leap day and advance it to March 1st
            leapday = (data_index.month == 2) & (data_index.day == 29)
            data_ymd[leapday] += datetime.timedelta(days=1)
            # shifted_hour is a pd.Series, so use pd.to_timedelta to get a pd.Series of
            # timedeltas
            # NOTE: as of pvlib-0.6.3, min req is pandas-0.18.1, so pd.to_timedelta
            # unit must be in (D,h,m,s,ms,us,ns), but pandas>=0.24 allows unit='hour'
            data.index = (data_ymd + pd.to_timedelta(shifted_hour, unit='h') +
                         pd.to_timedelta(minute, unit='min') )

            data = data.tz_localize(int(meta['TZ'] * 3600))
            
            return data
        
        
        import pvlib

        #(tmydata, metadata) = pvlib.tmy.readtmy3(filename=tmyfile) #pvlib<=0.6
        (tmydata, metadata) = pvlib.iotools.tmy.read_tmy3(filename=tmyfile,
                                                          coerce_year=coerce_year) 
        
        try:
            tmydata = _convertTMYdate(tmydata, metadata) 
        except KeyError:
            print('PVLib >= 0.8.0 is required for sub-hourly data input')


        return tmydata, metadata

    def _readEPW(self, epwfile=None, label = 'right', coerce_year=None):
        """
        Uses readepw from pvlib>0.6.1 but un-do -1hr offset and
        rename columns to match TMY3: DNI, DHI, GHI, DryBulb, Wspd
    
        Parameters
        ------------
        epwfile : str
            Direction and filename of the epwfile. If None, opens an interactive
            loading window.
        label : str
            'left', 'right', or 'center'. For data that is averaged, defines if
            the timestamp refers to the left edge, the right edge, or the 
            center of the averaging interval, for purposes of calculating 
            sunposition. For example, TMY3 data is right-labeled, so 11 AM data 
            represents data from 10 to 11, and sun position is calculated 
            at 10:30 AM.  Currently SAM and PVSyst use left-labeled interval 
            data and NSRDB uses centered.
        coerce_year : int
            Year to coerce data to.
        
        """
        
        import pvlib
        #import re
        
        '''
        NOTE: In PVLib > 0.6.1 the new epw.read_epw() function reads in time 
        with a default -1 hour offset.  This is reflected in our existing
        workflow. 
        '''
        #(tmydata, metadata) = readepw(epwfile) #
        (tmydata, metadata) = pvlib.iotools.epw.read_epw(epwfile, 
                                                         coerce_year=coerce_year) #pvlib>0.6.1
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

        return tmydata, metadata


    def _readSOLARGIS(self, filename=None, label='center'):
        """
        Read solarGIS data file which is timestamped in UTC.
        rename columns to match TMY3: DNI, DHI, GHI, DryBulb, Wspd
        Timezone is always returned as UTC. Use tz_convert in readWeatherFile
        to manually convert to local time
    
        Parameters
        ------------
        filename : str
            filename of the solarGIS file. 
        label : str
            'left', 'right', or 'center'. For data that is averaged, defines if
            the timestamp refers to the left edge, the right edge, or the 
            center of the averaging interval. SolarGis default style is center,
            unless user requests a right label. 
       
        """
        # file format: anything with # preceding is in the header
        header = []; lat = None; lon = None; elev = None; name = None
        with open(filename, 'r') as result:
            for line in result:
                if line.startswith('#'):
                    header.append(line)
                    if line.startswith('#Latitude:'):
                        lat = line[11:]
                    if line.startswith('#Longitude:'):
                        lon = line[12:]
                    if line.startswith('#Elevation:'):
                        elev = line[12:17]
                    if line.startswith('#Site name:'):
                        name = line[12:-1]
                else:
                    break
        metadata = {'latitude':float(lat),
                    'longitude':float(lon),
                    'altitude':float(elev),
                    'Name':name,
                    'TZ':0.0}
        # read in remainder of data
        data = pd.read_csv(filename,skiprows=header.__len__(), delimiter=';')

        # rename different field parameters to match output from 
        # pvlib.tmy.readtmy: DNI, DHI, DryBulb, Wspd
        data.rename(columns={'DIF':'DHI',
                             'TEMP':'DryBulb',
                             'WS':'Wspd',
                             }, inplace=True)    

        # Generate index from Date (DD.HH.YYYY) and Time
        data.index = pd.to_datetime(data.Date + ' ' +  data.Time, 
                                    dayfirst=True, utc=True,
                                    infer_datetime_format = True)

        
        return data, metadata


    def getSingleTimestampTrackerAngle(self, metdata, timeindex, gcr=None, 
                                       azimuth=180, axis_tilt=0, 
                                       limit_angle=45, backtrack=True):
        """
        Helper function to calculate a tracker's angle for use with the 
        fixed tilt routines of bifacial_radiance. It calculates tracker angle for
        sun position at the timeindex passed (no left or right time offset, 
        label = 'center')
        
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
        azimuth : float or int
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
                                             axis_tilt, azimuth,
                                             limit_angle, backtrack, gcr)
        
        tracker_theta = float(np.round(trackingdata['tracker_theta'],2))
        tracker_theta = tracker_theta*-1 # bifacial_radiance uses East (morning) theta as positive
            
        return tracker_theta


    def gendaylit(self, timeindex, metdata=None, debug=False):
        """
        Sets and returns sky information using gendaylit.
        Uses PVLIB for calculating the sun position angles instead of
        using Radiance internal sun position calculation (for that use gendaylit function)
        
        Parameters
        ----------
        timeindex : int
            Index from 0 to ~4000 of the MetObj (daylight hours only)
        metdata : ``MetObj``
            MetObj object with list of dni, dhi, ghi and location
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
                print('usage: pass metdata, or run after running ' +
                      'readWeatherfile() ') 
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
        #filename = str(time)[2:-9].replace('-','_').replace(' ','_').replace(':','_')
        filename = time.strftime('%Y-%m-%d_%H%M')
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
            This generates the sky at the sun altitude&azimuth provided, make 
            sure it is the right position relative to how the weather data got
            created and read (i.e. label right, left or center).
            
     
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

    def genCumSky(self, gencumsky_metfile=None, savefile=None):
        """ 
        Generate Skydome using gencumsky. 
        
        .. warning::
            gencumulativesky.exe is required to be installed,
            which is not a standard radiance distribution.
            You can find the program in the bifacial_radiance distribution directory
            in \Lib\site-packages\bifacial_radiance\data
            
 
        Use :func:`readWeatherFile(filename, starttime='YYYY-mm-dd_HHMM', endtime='YYYY-mm-dd_HHMM')` 
        to limit gencumsky simulations instead.

        Parameters
        ------------
        gencumsky_metfile : str
            Filename with path to temporary created meteorological file usually created
            in EPWs folder. This csv file has no headers, no index, and two
            space separated columns with values for GHI and DNI for each hour 
            in the year, and MUST have 8760 entries long otherwise gencumulativesky.exe cries. 
        savefile : string
            If savefile is None, defaults to "cumulative"
            
        Returns
        --------
        skyname : str
            Filename of the .rad file containing cumulativesky info
            
        """
        
        # TODO:  error checking and auto-install of gencumulativesky.exe
        # TODO: add check if readWeatherfile has not be done
        # TODO: check if it fails if gcc module has been loaded? (common hpc issue)
        
        #import datetime
        
        if gencumsky_metfile is None:
            gencumsky_metfile = self.gencumsky_metfile
            if isinstance(gencumsky_metfile, str):
                print("Loaded ", gencumsky_metfile)
                
        if isinstance(gencumsky_metfile, list):
            print("There are more than 1 year of gencumsky temporal weather file saved."+
                  "You can pass which file you want with gencumsky_metfile input. Since "+
                  "No year was selected, defaulting to using the first year of the list")
            gencumsky_metfile = gencumsky_metfile[0] 
            print("Loaded ", gencumsky_metfile)


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
                                                  gencumsky_metfile)
        '''
        cmd = (f"gencumulativesky +s1 -h 0 -a {lat} -o {lon} -m "
               f"{float(timeZone)*15} -G {gencumsky_metfile}" )
               
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

    def set1axis(self, metdata=None, azimuth=180, limit_angle=45,
                 angledelta=5, backtrack=True, gcr=1.0 / 3, cumulativesky=True,
                 fixed_tilt_angle=None, useMeasuredTrackerAngle=False,
                 axis_azimuth=None):
        """
        Set up geometry for 1-axis tracking.  Pull in tracking angle details from
        pvlib, create multiple 8760 metdata sub-files where datetime of met data
        matches the tracking angle.  Returns 'trackerdict' which has keys equal to
        either the tracker angles (gencumsky workflow) or timestamps (gendaylit hourly
        workflow)

        Parameters
        ------------
         metdata : :py:class:`~bifacial_radiance.MetObj` 
            Meterological object to set up geometry. Usually set automatically by
            `bifacial_radiance` after running :py:class:`bifacial_radiance.readepw`. 
            Default = self.metdata
        azimuth : numeric
            Orientation axis of tracker torque tube. Default North-South (180 deg).
            For fixed-tilt configuration, input is fixed azimuth (180 is south)
        limit_angle : numeric
            Limit angle (+/-) of the 1-axis tracker in degrees. Default 45
        angledelta : numeric
            Degree of rotation increment to parse irradiance bins. Default 5 degrees.
            (0.4 % error for DNI).  Other options: 4 (.25%), 2.5 (0.1%).
            Note: the smaller the angledelta, the more simulations must be run.
        backtrack : bool
            Whether backtracking is enabled (default = True)
        gcr : float
            Ground coverage ratio for calculation backtracking. Defualt [1.0/3.0] 
        cumulativesky : bool
            [True] Wether individual csv files are
            created with constant tilt angle for the cumulativesky approach.
            if false, the gendaylit tracking approach must be used.
        fixed_tilt_angle : numeric
            If passed, this changes to a fixed tilt simulation where each hour 
            uses fixed_tilt_angle and axis_azimuth as the tilt and azimuth
        useMeasuredTrackerAngle: Bool
            If True, and data for tracker angles has been passed by being included
            in the WeatherFile object (column name 'Tracker Angle (degrees)'),
            then tracker angles will be set to these values instead of being calculated.
            NOTE that the value for azimuth passed to set1axis must be surface 
            azimuth in the morning and not the axis_azimuth 
            (i.e. for a N-S HSAT, azimuth = 90).
        axis_azimuth : numeric
            DEPRECATED.  returns deprecation warning. Pass the tracker 
            axis_azimuth through to azimuth input instead.


        Returns
        -------
        trackerdict : dictionary 
            Keys represent tracker tilt angles (gencumsky) or timestamps (gendaylit)
            and list of csv metfile, and datetimes at that angle
            trackerdict[angle]['csvfile';'surf_azm';'surf_tilt';'UTCtime']
            - or -
            trackerdict[time]['tracker_theta';'surf_azm';'surf_tilt']
        """

        # Documentation check:
        # Removed         Internal variables
        # -------
        # metdata.solpos          dataframe with solar position data
        # metdata.surface_azimuth list of tracker azimuth data
        # metdata.surface_tilt    list of tracker surface tilt data
        # metdata.tracker_theta   list of tracker tilt angle
        import warnings
        
        if metdata == None:
            metdata = self.metdata

        if metdata == {}:
            raise Exception("metdata doesnt exist yet.  "+
                            "Run RadianceObj.readWeatherFile() ")

        if axis_azimuth:
            azimuth = axis_azimuth
            warnings.warn("axis_azimuth is deprecated in set1axis; use azimuth "
                          "input instead.", DeprecationWarning)
            
        #backtrack = True   # include backtracking support in later version
        #gcr = 1.0/3.0       # default value - not used if backtrack = False.


        # get 1-axis tracker angles for this location, rounded to nearest 'angledelta'
        trackerdict = metdata._set1axis(cumulativesky=cumulativesky,
                                       azimuth=azimuth,
                                       limit_angle=limit_angle,
                                       angledelta=angledelta,
                                       backtrack=backtrack,
                                       gcr=gcr,
                                       fixed_tilt_angle=fixed_tilt_angle,
                                       useMeasuredTrackerAngle=useMeasuredTrackerAngle
                                       )
        self.trackerdict = trackerdict
        self.cumulativesky = cumulativesky

        return trackerdict

    def gendaylit1axis(self, metdata=None, trackerdict=None, startdate=None,
                       enddate=None, debug=False):
        """
        1-axis tracking implementation of gendaylit.
        Creates multiple sky files, one for each time of day.

        Parameters
        ------------
        metdata
            MetObj output from readWeatherFile.  Needs to have 
            RadianceObj.set1axis() run on it first.
        startdate : str 
            DEPRECATED, does not do anything now.
            Recommended to downselect metdata when reading Weather File.
        enddate : str
            DEPRECATED, does not do anything now.
            Recommended to downselect metdata when reading Weather File.
        trackerdict : dictionary
            Dictionary with keys for tracker tilt angles (gencumsky) or timestamps (gendaylit)
        
        Returns
        -------
        Updated trackerdict dictionary 
            Dictionary with keys for tracker tilt angles (gencumsky) or timestamps (gendaylit)
            with the additional dictionary value ['skyfile'] added

        """
        
        if metdata is None:
            metdata = self.metdata
        if trackerdict is None:
            try:
                trackerdict = self.trackerdict
            except AttributeError:
                print('No trackerdict value passed or available in self')

        if startdate is not None or enddate is not None:
            print("Deprecation Warning: gendyalit1axis no longer downselects"+
                  " entries by stardate and enddate. Downselect your data"+
                  " when loading with readWeatherFile")
            return
            
        try:
            metdata.tracker_theta  # this may not exist
        except AttributeError:
            print("metdata.tracker_theta doesn't exist. Run RadianceObj.set1axis() first")

        if debug is False:
            print('Creating ~%d skyfiles. '%(len(trackerdict.keys())))
        count = 0  # counter to get number of skyfiles created, just for giggles

        trackerdict2={}
        for i in range(0, len(trackerdict.keys())):
            try:
                time = metdata.datetime[i]
            except IndexError:  #out of range error
                break  # 
            #filename = str(time)[5:-12].replace('-','_').replace(' ','_')
            filename = time.strftime('%Y-%m-%d_%H%M')
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

        Use :func:`readWeatherFile` to limit gencumsky simulations
        
        
        Parameters
        ------------
        trackerdict : dictionary
            Trackerdict generated as output by RadianceObj.set1axis()
            
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
            skyfile = self.genCumSky(gencumsky_metfile=csvfile, savefile=savefile)
            trackerdict[theta]['skyfile'] = skyfile
            print('Created skyfile %s'%(skyfile))
        # delete default skyfile (not strictly necessary)
        self.skyfiles = None
        self.trackerdict = trackerdict
        return trackerdict


    def makeOct(self, filelist=None, octname=None):
        """
        Combine everything together into a .oct file

        Parameters
        ----------
        filelist : list 
            Files to include.  otherwise takes self.filelist
        octname : str
            filename (without .oct extension)


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
        if self.hpc :
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

        #cmd = 'oconv ' + ' '.join(filelist)
        filelist.insert(0,'oconv')
        with open('%s.oct' % (octname), "w") as f:
            _,err = _popen(filelist, None, f)
            #TODO:  exception handling for no sun up
            if err is not None:
                if err[0:5] == 'error':
                    raise Exception(err[7:])
                if err[0:7] == 'message':
                    warnings.warn(err[9:], Warning)
                    

        #use rvu to see if everything looks good. 
        # use cmd for this since it locks out the terminal.
        #'rvu -vf views\side.vp -e .01 monopanel_test.oct'
        print("Created %s.oct" % (octname))
        self.octfile = '%s.oct' % (octname)
        return '%s.oct' % (octname)

    def makeOct1axis(self, trackerdict=None, singleindex=None, customname=None):
        """
        Combine files listed in trackerdict into multiple .oct files

        Parameters
        ------------
        trackerdict 
            Output from :py:class:`~bifacial_radiance.RadianceObj.makeScene1axis`
        singleindex : str
            Single index for trackerdict to run makeOct1axis in single-value mode,
            format 'YYYY-MM-DD_HHMM'.
        customname : str 
            Custom text string added to the end of the OCT file name.

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
                trackerdict[index]['octfile'] = self.makeOct(filelist, octname)
            except KeyError as e:
                print('Trackerdict key error: {}'.format(e))

        return trackerdict

    
    def makeModule(self, name=None, x=None, y=None, z=None,  modulefile=None, 
                 text=None, customtext='',  xgap=0.01, ygap=0.0, 
                 zgap=0.1, numpanels=1, rewriteModulefile=True, 
                 glass=False, modulematerial=None, bifi=1,  **kwargs):
        """
        pass module generation details into ModuleObj(). See ModuleObj() 
        docstring for more details
        """
        from bifacial_radiance import ModuleObj

        if name is None:
            print("usage:  makeModule(name,x,y,z, modulefile = '\objects\*.rad', "+
                  " zgap = 0.1 (module offset)"+
                  "numpanels = 1 (# of panels in portrait), ygap = 0.05 "+
                  "(slope distance between panels when arrayed), "+
                  "rewriteModulefile = True (or False), bifi = 1")
            print("You can also override module_type info by passing 'text'"+
                  "variable, or add on at the end for racking details with "+
                  "'customtext'. See function definition for more details")
            print("Optional: tubeParams={} (torque tube details including "
                  "diameter (torque tube dia. in meters), tubetype='Round' "
                  "(or 'square', 'hex'), material='Metal_Grey' (or 'black')"
                  ", axisofrotation=True (does scene rotate around tube)")
            print("Optional: cellModule={} (create cell-level module by "+
                  " passing in dictionary with keys 'numcellsx'6 (#cells in "+
                  "X-dir.), 'numcellsy', 'xcell' (cell size in X-dir. in meters),"+
                  "'ycell', 'xcellgap' (spacing between cells in X-dir.), 'ycellgap'")
            print("Optional: omegaParams={} (create the support structure omega by "+
                  "passing in dictionary with keys 'omega_material' (the material of "+
                  "omega), 'mod_overlap'(the length of the module adjacent piece of"+
                  " omega that overlaps with the module),'x_omega1', 'y_omega' (ideally same"+
                  " for all the parts of omega),'z_omega1', 'x_omega2' (X-dir length of the"+
                  " vertical piece), 'x_omega3', z_omega3")

            return
        
        """
        # TODO: check for deprecated torquetube and axisofrotationTorqueTube in
          kwargs.  
        """
        if 'tubeParams' in kwargs:
            tubeParams = kwargs.pop('tubeParams')
        else:
            tubeParams = None
        if 'torquetube' in kwargs:
            torquetube = kwargs.pop('torquetube')
            print("\nWarning: boolean input `torquetube` passed into makeModule"
                  ". Starting in v0.4.0 this boolean parameter is deprecated."
                  " Use module.addTorquetube() with `visible` parameter instead.")
            if tubeParams:
                tubeParams['visible'] =  torquetube
            elif (tubeParams is None) & (torquetube is True):
                tubeParams = {'visible':True} # create default TT
            
        if 'axisofrotationTorqueTube' in kwargs:
            axisofrotation = kwargs.pop('axisofrotationTorqueTube')
            print("\nWarning: input boolean `axisofrotationTorqueTube` passed "
                "into makeModule. Starting in v0.4.0 this boolean parameter is"
                " deprecated. Use module.addTorquetube() with `axisofrotation`"
                "parameter instead.")
            if tubeParams:  #this kwarg only does somehting if there's a TT.
                tubeParams['axisofrotation'] = axisofrotation
        
        if self.hpc:  # trigger HPC simulation in ModuleObj
            kwargs['hpc']=True
            
        self.module = ModuleObj(name=name, x=x, y=y, z=z, bifi=bifi, modulefile=modulefile,
                   text=text, customtext=customtext, xgap=xgap, ygap=ygap, 
                   zgap=zgap, numpanels=numpanels, 
                   rewriteModulefile=rewriteModulefile, glass=glass, 
                   modulematerial=modulematerial, tubeParams=tubeParams,
                   **kwargs)
        return self.module
    
    
    
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
        # print available module types from ModuleObj
        from bifacial_radiance import ModuleObj
        modulenames = ModuleObj().readModule()
        print('Available module names: {}'.format([str(x) for x in modulenames]))
        return modulenames
    
    def makeScene(self, module=None, sceneDict=None, radname=None,
                  moduletype=None):
        """
        Create a SceneObj which contains details of the PV system configuration including
        tilt, row pitch, height, nMods per row, nRows in the system...

        Parameters
        ----------
        module : str or ModuleObj
            String name of module created with makeModule()
        sceneDict : dictionary
            Dictionary with keys: `tilt`, `clearance_height`*, `pitch`,
            `azimuth`, `nMods`, `nRows`, `hub_height`*, `height`*
            * height deprecated from sceneDict. For makeScene (fixed systems)
            if passed it is assumed it reffers to clearance_height.
            `clearance_height` recommended for fixed_tracking systems.
            `hub_height` can also be passed as a possibility.
        radname : str
            Gives a custom name to the scene file. Useful when parallelizing.
        moduletype: DEPRECATED. use the `module` kwarg instead.
        
        Returns
        -------
        SceneObj 
            'scene' with configuration details
            
        """
        if moduletype is not None:
            module = moduletype
            print("Warning:  input `moduletype` is deprecated. Use kwarg "
                  "`module` instead")
        if module is None:
            try:
                module = self.module
                print(f'Using last saved module, name: {module.name}')
            except AttributeError:
                print('makeScene(module, sceneDict, nMods, nRows).  '+\
                          'Available moduletypes: ' )
                self.printModules() #print available module types
                return
        self.scene = SceneObj(module)
        self.scene.hpc = self.hpc  #pass HPC mode from parent

        if sceneDict is None:
            print('makeScene(moduletype, sceneDict, nMods, nRows).  '+\
                  'sceneDict inputs: .tilt .clearance_height .pitch .azimuth')
            return self.scene

        if 'azimuth' not in sceneDict:
            sceneDict['azimuth'] = 180

        if 'nRows' not in sceneDict:
            sceneDict['nRows'] = 7

        if 'nMods' not in sceneDict:
            sceneDict['nMods'] = 20

        # Fixed tilt routine
        # Preferred: clearance_height,
        # If only height is passed, it is assumed to be clearance_height.
        
        sceneDict, use_clearanceheight  = _heightCasesSwitcher(sceneDict, 
                                                                preferred='clearance_height', 
                                                                nonpreferred='hub_height')
        
        self.nMods = sceneDict['nMods']
        self.nRows = sceneDict['nRows']
        self.sceneRAD = self.scene._makeSceneNxR(sceneDict=sceneDict,
                                                 radname=radname)

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
                #appendRadfile to False first..
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



    
    def makeScene1axis(self, trackerdict=None, module=None, sceneDict=None,
                       cumulativesky=None, moduletype=None):
        """
        Creates a SceneObj for each tracking angle which contains details of the PV
        system configuration including row pitch, hub_height, nMods per row, nRows in the system...

        Parameters
        ------------
        trackerdict
            Output from GenCumSky1axis
        module : str or ModuleObj
            Name or ModuleObj created with makeModule()
        sceneDict : 
            Dictionary with keys:`tilt`, `hub_height`, `pitch`, `azimuth`
        cumulativesky : bool
            Defines if sky will be generated with cumulativesky or gendaylit.
        moduletype: DEPRECATED. use the `module` kwarg instead.

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
        
        import math

        if sceneDict is None:
            print('usage: makeScene1axis(module, sceneDict, nMods, nRows).'+
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


        if moduletype is not None:
            module = moduletype
            print("Warning:  input `moduletype` is deprecated. Use kwarg "
                  "`module` instead")
        if module is None:
            try:
                module = self.module
                print(f'Using last saved module, name: {module.name}')
            except AttributeError:
                print('usage:  makeScene1axis(trackerdict, module, '+
                      'sceneDict, nMods, nRows). ')
                self.printModules() #print available module types
                return

        if 'orientation' in sceneDict:
            raise Exception('\n\n ERROR: Orientation format has been '
                'deprecated since version 0.2.4. If you want to flip your '
                'modules, on makeModule switch the x and y values.\n\n')
       
        # 1axis routine
        # Preferred hub_height
        sceneDict, use_clearanceheight = _heightCasesSwitcher(sceneDict, 
                                                        preferred='hub_height', 
                                                        nonpreferred='clearance_height')

        if use_clearanceheight:
            simplefix = 0
            hubheight = sceneDict['clearance_height'] # Not really, but this is the fastest 
            # to make it work with the simplefix as below the actual clearnace height
            # gets calculated and the 0 sets the cosine correction to 0. 
            # TODO CLEAN THIS UP.
            
        else:
            #the hub height is the tracker height at center of rotation.
            hubheight = sceneDict['hub_height']
            simplefix = 1

        if cumulativesky is True:        # cumulativesky workflow
            print('\nMaking .rad files for cumulativesky 1-axis workflow')
            for theta in trackerdict:
                scene = SceneObj(module)
                if trackerdict[theta]['surf_azm'] >= 180:
                    trackerdict[theta]['surf_azm'] = trackerdict[theta]['surf_azm']-180
                    trackerdict[theta]['surf_tilt'] = trackerdict[theta]['surf_tilt']*-1
                radname = '1axis%s_'%(theta,)

                # Calculating clearance height for this theta.
                height = hubheight - simplefix*0.5* math.sin(abs(theta) * math.pi / 180) \
                        * scene.module.sceney + scene.module.offsetfromaxis \
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
                                  'modulez': scene.module.z}
                except KeyError:
                    #maybe gcr is passed, not pitch
                    sceneDict2 = {'tilt':trackerdict[theta]['surf_tilt'],
                                  'gcr':sceneDict['gcr'],
                                  'clearance_height':trackerdict[theta]['clearance_height'],
                                  'azimuth':trackerdict[theta]['surf_azm'],
                                  'nMods': sceneDict['nMods'],
                                  'nRows': sceneDict['nRows'],
                                  'modulez': scene.module.z}

                radfile = scene._makeSceneNxR(sceneDict=sceneDict2,
                                             radname=radname)
                trackerdict[theta]['radfile'] = radfile
                trackerdict[theta]['scene'] = scene

            print('{} Radfiles created in /objects/'.format(trackerdict.__len__()))

        else:  #gendaylit workflow
            print('\nMaking ~%s .rad files for gendaylit 1-axis workflow (this takes a minute..)' % (len(trackerdict)))
            count = 0
            for time in trackerdict:
                scene = SceneObj(module)

                if trackerdict[time]['surf_azm'] >= 180:
                    trackerdict[time]['surf_azm'] = trackerdict[time]['surf_azm']-180
                    trackerdict[time]['surf_tilt'] = trackerdict[time]['surf_tilt']*-1
                theta = trackerdict[time]['theta']
                radname = '1axis%s_'%(time,)

                # Calculating clearance height for this time.
                height = hubheight - simplefix*0.5* math.sin(abs(theta) * math.pi / 180) \
                        * scene.module.sceney + scene.module.offsetfromaxis \
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
                                      'modulez': scene.module.z}
                    except KeyError:
                        #maybe gcr is passed instead of pitch
                        sceneDict2 = {'tilt':trackerdict[time]['surf_tilt'],
                                      'gcr':sceneDict['gcr'],
                                      'clearance_height': trackerdict[time]['clearance_height'],
                                      'azimuth':trackerdict[time]['surf_azm'],
                                      'nMods': sceneDict['nMods'],
                                      'nRows': sceneDict['nRows'],
                                      'modulez': scene.module.z}

                    radfile = scene._makeSceneNxR(sceneDict=sceneDict2,
                                                 radname=radname)
                    trackerdict[time]['radfile'] = radfile
                    trackerdict[time]['scene'] = scene
                    count+=1
            print('{} Radfiles created in /objects/'.format(count))

        self.trackerdict = trackerdict
        self.nMods = sceneDict['nMods']  #assign nMods and nRows to RadianceObj
        self.nRows = sceneDict['nRows']
        self.hub_height = hubheight
        
        return trackerdict


    def analysis1axis(self, trackerdict=None, singleindex=None, accuracy='low',
                      customname=None, modWanted=None, rowWanted=None, 
                      sensorsy=9, sensorsx=1,  
                      modscanfront = None, modscanback = None, relative=False, 
                      debug=False ):
        """
        Loop through trackerdict and runs linescans for each scene and scan in there.

        Parameters
        ----------------
        trackerdict 
        singleindex : str
            For single-index mode, just the one index we want to run (new in 0.2.3).
            Example format '21_06_14_12_30' for 2021 June 14th 12:30 pm
        accuracy : str
            'low' or 'high', resolution option used during _irrPlot and rtrace
        customname : str
            Custom text string to be added to the file name for the results .CSV files
        modWanted : int 
            Module to be sampled. Index starts at 1.
        rowWanted : int
            Row to be sampled. Index starts at 1. (row 1)
        sensorsy : int or list 
            Number of 'sensors' or scanning points along the collector width 
            (CW) of the module(s). If multiple values are passed, first value
            represents number of front sensors, second value is number of back sensors
        sensorsx : int or list 
            Number of 'sensors' or scanning points along the length, the side perpendicular 
            to the collector width (CW) of the module(s) for the back side of the module. 
            If multiple values are passed, first value represents number of 
            front sensors, second value is number of back sensors.
        modscanfront : dict
            dictionary with one or more of the following key: xstart, ystart, zstart, 
            xinc, yinc, zinc, Nx, Ny, Nz, orient. All of these keys are ints or 
            floats except for 'orient' which takes x y z values as string 'x y z'
            for example '0 0 -1'. These values will overwrite the internally
            calculated frontscan dictionary for the module & row selected. If modifying 
            Nx, Ny or Nz, make sure to modify on modscanback to avoid issues on 
            results writing stage. 
        modscanback : dict
            dictionary with one or more of the following key: xstart, ystart, zstart, 
            xinc, yinc, zinc, Nx, Ny, Nz, orient. All of these keys are ints or 
            floats except for 'orient' which takes x y z values as string 'x y z'
            for example '0 0 -1'. These values will overwrite the internally
            calculated frontscan dictionary for the module & row selected.  If modifying 
            Nx, Ny or Nz, make sure to modify on modscanback to avoid issues on 
            results writing stage. 
        relative : Bool
            if passing modscanfront and modscanback to modify dictionarie of positions,
            this sets if the values passed to be updated are relative or absolute. 
            Default is absolute value (relative=False)
        debug : Bool
            Activates internal printing of the function to help debugging.
 

        Returns
        -------
        trackerdict with new keys:
            
            'AnalysisObj'  : analysis object for this tracker theta
            'Wm2Front'     : list of front Wm-2 irradiances, len=sensorsy_back
            'Wm2Back'      : list of rear Wm-2 irradiances, len=sensorsy_back
            'backRatio'    : list of rear irradiance ratios, len=sensorsy_back
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
                frontscanind, backscanind = analysis.moduleAnalysis(scene=scene, modWanted=modWanted, 
                                                rowWanted=rowWanted, 
                                                sensorsy=sensorsy, 
                                                sensorsx=sensorsx, 
                                                modscanfront=modscanfront, modscanback=modscanback,
                                                relative=relative, debug=debug)
                analysis.analysis(octfile=octfile,name=name,frontscan=frontscanind,backscan=backscanind,accuracy=accuracy)                
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
        self.backRatio = np.mean(backWm2)/np.mean(frontWm2+.001)

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
                temptrackerdict = trackerdict[list(trackerdict)[0]]['AnalysisObj']
                #temptrackerdict = trackerdict[0.0]['AnalysisObj']
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
                    frontscancum, backscancum = cumanalysisobj.moduleAnalysis(scene=cumscene, modWanted=modWanted, 
                                                rowWanted=rowWanted, 
                                                sensorsy=sensorsy, 
                                                sensorsx=sensorsx,
                                                modscanfront=modscanfront, modscanback=modscanback,
                                                relative=relative, debug=debug)
                    x,y,z = cumanalysisobj._linePtsArray(frontscancum)
                    x,y,rearz = cumanalysisobj._linePtsArray(backscancum)
        
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


    def calculatePerformanceModule(self, CECMod, glassglass=False, bifacialityfactor=None):
        '''
        Loops through all results in trackerdict and calculates performance using
        PVLib. Cell temperature is calculated

        Parameters
        ----------
        CECMod : Dict
            Dictionary with CEC Module PArameters for the module selected. Must 
            contain at minimum  alpha_sc, a_ref, I_L_ref, I_o_ref, R_sh_ref,
            R_s, Adjust
        glassglass : boolean, optional
            If True, module packaging is set to glass-glass for thermal 
            coefficients for module temperature calculation. Else it is
            assumes it is a glass-polymer package.
        bifacialityfactor : float, optional
            bifaciality factor to be used on calculations, range 0 to 1. If 
            not passed, it uses the module object's stored bifaciality factor.
        
        Returns
        -------
        trackerdict 
            Trackerdict with effective irradiance and Power Output for the module.

        '''
        
        from bifacial_radiance import performance
        
        trackerdict = self.trackerdict

        keys = list(trackerdict.keys())
       
        # Search for module object bifaciality
        if bifacialityfactor is None:
            bifacialityfactor = trackerdict[keys[0]]['scene'].module.bifi
            print("Bifaciality factor of module stored is ", bifacialityfactor)

        effective_irradiance = []
        temp_air = []
        wind_speed = []
            
        for key in keys:
            frontirrad = trackerdict[key]['AnalysisObj'].Wm2Front
            backirrad = trackerdict[key]['AnalysisObj'].Wm2Back
            eff_irrad = np.mean(frontirrad)+np.mean(backirrad)*bifacialityfactor
            effective_irradiance.append(eff_irrad)
            trackerdict[key]['effective_irradiance'] = eff_irrad
            temp_air.append(trackerdict[key]['temp_air'])
            wind_speed.append(trackerdict[key]['wind_speed'])
       
        performanceModdata= pd.DataFrame(zip(wind_speed, temp_air, effective_irradiance), 
                                         columns=('wind_speed', 'temp_air', 'effective_irradiance'))
        pout = performance.calculatePerformance(
                    effective_irradiance = performanceModdata.effective_irradiance, 
                    CECMod=CECMod, 
                    temp_air=performanceModdata.temp_air, 
                    wind_speed=performanceModdata.wind_speed)


        ii = 0
        for key in keys:        
            trackerdict[key]['Pout_module'] = pout[ii]
            ii +=1

        self.trackerdict = trackerdict
        
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

    """
   
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
            print('\nInput albedo 0-1, or string from ground.printGroundMaterials().'
            '\nAlternatively, run setGround after readWeatherData()'
            'and setGround will read metdata.albedo if available')
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
                warnings.warn('Error - materialString not in '
                              f'{self.material_file}: {materialString}')
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
    def __repr__(self):
        return str(self.__dict__)
    def __init__(self, module=None):
        ''' initialize SceneObj
        '''
        from bifacial_radiance import ModuleObj
        # should sceneDict be initialized here? This is set in _makeSceneNxR
        if module is None:
            return
        elif type(module) == str:
            self.module = ModuleObj(name=module)


        elif type(module) == ModuleObj: # try moduleObj
            self.module = module

        #self.moduleDict = self.module.getDataDict()
        #self.scenex = self.module.scenex
        #self.sceney = self.module.sceney
        #self.offsetfromaxis = self.moduleDict['offsetfromaxis']
        #TODO: get rid of these 4 values
        
        self.modulefile = self.module.modulefile
        self.hpc = False  #default False.  Set True by makeScene after sceneobj created.


    def _makeSceneNxR(self, modulename=None, sceneDict=None, radname=None):
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
        modulename: str 
            Name of module created with :py:class:`~bifacial_radiance.RadianceObj.makeModule`.
        sceneDict : dictionary 
            Dictionary of scene parameters.
                clearance_height : numeric
                    (meters). 
                pitch : numeric
                    Separation between rows
                tilt : numeric 
                    Valid input ranges -90 to 90 degrees
                azimuth : numeric 
                    A value denoting the compass direction along which the
                    axis of rotation lies. Measured in decimal degrees East
                    of North. [0 to 180) possible.
                nMods : int 
                    Number of modules per row (default = 20)
                nRows : int 
                    Number of rows in system (default = 7)
        radname : str
            String for name for radfile.


        Returns
        -------
        radfile : str
             Filename of .RAD scene in /objects/
        scene : :py:class:`~bifacial_radiance.SceneObj `
             Returns a `SceneObject` 'scene' with configuration details

        """

        if modulename is None:
            modulename = self.module.name

        if sceneDict is None:
            print('makeScene(modulename, sceneDict, nMods, nRows).  sceneDict'
                  ' inputs: .tilt .azimuth .nMods .nRows' 
                  ' AND .tilt or .gcr ; AND .hub_height or .clearance_height')


        if 'orientation' in sceneDict:
            raise Exception('\n\n ERROR: Orientation format has been '
                'deprecated since version 0.2.4. If you want to flip your '
                'modules, on makeModule switch the x and y values.\n\n')

        if 'azimuth' not in sceneDict:
            sceneDict['azimuth'] = 180

        if 'axis_tilt' not in sceneDict:
            sceneDict['axis_tilt'] = 0

        if 'originx' not in sceneDict:
            sceneDict['originx'] = 0

        if 'originy' not in sceneDict:
            sceneDict['originy'] = 0

        if radname is None:
            radname =  str(self.module.name).strip().replace(' ', '_')

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
        # it is assumed that if no clearance_height or hub_height is passed,
        # hub_height = height.

        
        sceneDict, use_clearanceheight  = _heightCasesSwitcher(sceneDict, preferred='hub_height', 
                                                     nonpreferred='clearance_height')
        
        if use_clearanceheight :
            hubheight = sceneDict['clearance_height'] + 0.5* np.sin(abs(tilt) * np.pi / 180) \
            * self.module.sceney - self.module.offsetfromaxis*np.sin(abs(tilt)*np.pi/180)

            title_clearance_height = sceneDict['clearance_height'] 
        else:
            hubheight = sceneDict['hub_height'] 
            # this calculates clearance_height, used for the title
            title_clearance_height = sceneDict['hub_height'] - 0.5* np.sin(abs(tilt) * np.pi / 180) \
            * self.module.sceney + self.module.offsetfromaxis*np.sin(abs(tilt)*np.pi/180)

        try: 
            if sceneDict['pitch'] >0:
                pitch = sceneDict['pitch'] 
            else:
                raise Exception('default to gcr')
            
        except:

            if 'gcr' in sceneDict:
                pitch = np.round(self.module.sceney/sceneDict['gcr'],3)
            else:
                raise Exception('No valid `pitch` or `gcr` in sceneDict')



        ''' INITIALIZE VARIABLES '''
        text = '!xform '

        text += '-rx %s -t %s %s %s ' %(tilt, 0, 0, hubheight)
        
        # create nMods-element array along x, nRows along y. 1cm module gap.
        text += '-a %s -t %s 0 0 -a %s -t 0 %s 0 ' %(nMods, self.module.scenex, nRows, pitch)

        # azimuth rotation of the entire shebang. Select the row to scan here based on y-translation.
        # Modifying so center row is centered in the array. (i.e. 3 rows, row 2. 4 rows, row 2 too)
        # Since the array is already centered on row 1, module 1, we need to increment by Nrows/2-1 and Nmods/2-1

        text += (f'-i 1 -t {-self.module.scenex*(round(nMods/1.999)*1.0-1)} '
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
                self.module.scenex*(round(nMods/1.99)*1.0-1)*np.sin(
                        axis_tilt * np.pi/180) ) )

        filename = (f'{radname}_C_{title_clearance_height:0.5f}_rtr_{pitch:0.5f}_tilt_{tilt:0.5f}_'
                    f'{nMods}modsx{nRows}rows_origin{originx},{originy}.rad' )
        
        if self.hpc:
            text += f'"{os.path.join(os.getcwd(), self.modulefile)}"' 
            radfile = os.path.join(os.getcwd(), 'objects', filename) 
        else:
            text += os.path.join(self.modulefile)
            radfile = os.path.join('objects',filename ) 

        # py2 and 3 compatible: binary write, encode text first
        with open(radfile, 'wb') as f:
            f.write(text.encode('ascii'))

        self.gcr = self.module.sceney / pitch
        self.text = text
        self.radfiles = radfile
        self.sceneDict = sceneDict
#        self.hub_height = hubheight
        return radfile
    
   
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
        
        #First prune all GHI = 0 timepoints.  New as of 0.4.0
        # TODO: is this a good idea?  This changes default behavior...
        tmydata = tmydata[tmydata.GHI > 0]

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
        try:
            self.albedo = np.array(tmydata.Alb)
        except AttributeError: # no TMY albedo data
            self.albedo = None
        
        # Try and retrieve dewpoint and pressure
        try:
            self.dewpoint = np.array(tmydata['temp_dew'])
        except KeyError:
            self.dewpoint = None

        try:
            self.pressure = np.array(tmydata['atmospheric_pressure'])
        except KeyError:
            self.pressure = None

        try:
            self.temp_air = np.array(tmydata['temp_air'])
        except KeyError:
            self.temp_air = None

        if self.temp_air is None:
            try:
                self.temp_air = np.array(tmydata['DryBulb'])
            except KeyError:
                self.temp_air = None

        try:
            self.wind_speed = np.array(tmydata['wind_speed'])
        except KeyError:
            self.wind_speed = None
        
        if self.wind_speed is None:
            try:
                self.wind_speed = np.array(tmydata['Wspd'])
            except KeyError:
                self.wind_speed = None
            
        # Try and retrieve TrackerAngle
        try:
            self.meastracker_angle = np.array(tmydata['Tracker Angle (degrees)'])
        except KeyError:
            self.meastracker_angle= None
            
            
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
        # TODO:  Refactor this into a subfunction. first calculate minutedelta 
        # based on label and interval (-30, 0, +30, +7.5 etc) then correct all.        
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
                print("Interval in weather data is less than 1 hr, calculating"
                      f" Sun position with a delta of -{minutedelta} minutes.")
                print("If you want no delta for sunposition, use "
                      "readWeatherFile( label='center').")
                #datetimetz=datetimetz-pd.Timedelta(minutes = minutedelta)   # This doesn't check for Sunrise or Sunset
                #sunup= pvlib.irradiance.solarposition.get_sun_rise_set_transit(datetimetz, lat, lon) # deprecated in pvlib 0.6.1
                sunup= pvlib.irradiance.solarposition.sun_rise_set_transit_spa(datetimetz, lat, lon) #new for pvlib >= 0.6.1
                sunup['corrected_timestamp'] = sunup.index-pd.Timedelta(minutes = minutedelta)
    
        self.solpos = pvlib.irradiance.solarposition.get_solarposition(sunup['corrected_timestamp'],lat,lon,elev)
        self.sunrisesetdata=sunup
        self.label = label


    def _set1axis(self, azimuth=180, limit_angle=45, angledelta=None, 
                  backtrack=True, gcr=1.0/3.0, cumulativesky=True, 
                  fixed_tilt_angle=None, axis_tilt=0, useMeasuredTrackerAngle=False):

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
        azimuth : numerical
            orientation axis of tracker torque tube. Default North-South (180 deg)
            For fixed tilt simulations  this is the orientation azimuth
        limit_angle : numerical
            +/- limit angle of the 1-axis tracker in degrees. Default 45
        angledelta : numerical
            Degree of rotation increment to parse irradiance bins.
            Default 5 degrees (0.4 % error for DNI).
            Other options: 4 (.25%), 2.5 (0.1%).
            (the smaller the angledelta, the more simulations)
        backtrack : bool
            Whether backtracking is enabled (default = True)
        gcr : float
            Ground coverage ratio for calculation backtracking. Defualt [1.0/3.0] 
        axis_tilt : float
            Tilt of the axis. While it can be considered for the tracking calculation,
            the scene geometry creation of the trackers does not support tilte
            axis_trackers yet (but can be done manuallyish. See Tutorials)
        fixed_tilt_angle : numeric
            If passed, this changes to a fixed tilt simulation where each hour
            uses fixed_tilt_angle and azimuth as the tilt and azimuth

        Returns
        -------
        trackerdict : dictionary 
            Keys for tracker tilt angles and
            list of csv metfile, and datetimes at that angle
            trackerdict[angle]['csvfile';'surf_azm';'surf_tilt';'UTCtime']
        metdata.solpos : dataframe
            Dataframe with output from pvlib solar position for each timestep
        metdata.sunrisesetdata :
            Pandas dataframe with sunrise, sunset and adjusted time data.
        metdata.tracker_theta : list
            Tracker tilt angle from pvlib for each timestep
        metdata.surface_tilt : list
            Tracker surface tilt angle from pvlib for each timestep
        metdata.surface_azimuth : list
            Tracker surface azimuth angle from pvlib for each timestep
        """
          
        #axis_tilt = 0       # only support 0 tilt trackers for now
        self.cumulativesky = cumulativesky   # track whether we're using cumulativesky or gendaylit

        if (cumulativesky is True) & (angledelta is None):
            angledelta = 5  # round angle to 5 degrees for cumulativesky

        # get 1-axis tracker angles for this location,
        # round to nearest 'angledelta'
        if self.meastracker_angle is not None and useMeasuredTrackerAngle is True:
            print("Tracking Data: Reading from provided Tracker Angles")
        elif self.meastracker_angle is None and useMeasuredTrackerAngle is True:
            useMeasuredTrackerAngle = False
            print("Warning: Using Measured Tracker Angles was specified but DATA"+
                  " for trackers has not yet been assigned. "+
                  " Assign it by making it a column on your Weatherdata File "+
                  "named 'Tracker Angle (degrees)' and run ReadWeatherFile again")

        trackingdata = self._getTrackingAngles(azimuth,
                                               limit_angle,
                                               angledelta,
                                               axis_tilt = axis_tilt,
                                               backtrack = backtrack,
                                               gcr = gcr,
                                               fixed_tilt_angle=fixed_tilt_angle,
                                               useMeasuredTrackerAngle=useMeasuredTrackerAngle)

        # get list of unique rounded tracker angles
        theta_list = trackingdata.dropna()['theta_round'].unique()

        if cumulativesky is True:
            # create a separate metfile for each unique tracker theta angle.
            # return dict of filenames and details
            trackerdict = self._makeTrackerCSV(theta_list,trackingdata)
        else:
            # trackerdict uses timestamp as keys. return azimuth
            # and tilt for each timestamp
            #times = [str(i)[5:-12].replace('-','_').replace(' ','_') for i in self.datetime]
            times = [i.strftime('%Y-%m-%d_%H%M') for i in self.datetime]
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
                                        'dhi':self.dhi[i],
                                        'temp_air':self.temp_air[i],
                                        'wind_speed':self.wind_speed[i]
                                        }

        return trackerdict


    def _getTrackingAngles(self, azimuth=180, limit_angle=45,
                           angledelta=None, axis_tilt=0, backtrack=True,
                           gcr = 1.0/3.0, fixed_tilt_angle=None,
                           useMeasuredTrackerAngle=False):
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
            This changes to a fixed tilt simulation where each hour uses 
            fixed_tilt_angle and azimuth as the tilt and azimuth

        Returns
        -------
        DataFrame with the following columns:
            * tracker_theta: The rotation angle of the tracker.
                tracker_theta = 0 is horizontal, and positive rotation angles 
                are clockwise.
            * aoi: The angle-of-incidence of direct irradiance onto the
                rotated panel surface.
            * surface_tilt: The angle between the panel surface and the earth
                surface, accounting for panel rotation.
            * surface_azimuth: The azimuth of the rotated panel, determined by
                projecting the vector normal to the panel's surface to the 
                earth's  surface.
            * 'theta_round' : tracker_theta rounded to the nearest 'angledelta'
            If no angledelta is specified, it is rounded to the nearest degree.
        '''
        import pvlib
        import warnings
        from pvlib.irradiance import aoi 
        #import numpy as np
        #import pandas as pd
        
        solpos = self.solpos
        
        #New as of 0.3.2:  pass fixed_tilt_angle and switches to FIXED TILT mode

        if fixed_tilt_angle is not None:
            # system with fixed tilt = fixed_tilt_angle 
            surface_tilt=fixed_tilt_angle
            surface_azimuth=azimuth 
            # trackingdata keys: 'tracker_theta', 'aoi', 'surface_azimuth', 'surface_tilt'
            trackingdata = pd.DataFrame({'tracker_theta':fixed_tilt_angle,
                                         'aoi':aoi(surface_tilt, surface_azimuth,
                                                   solpos['zenith'], 
                                                   solpos['azimuth']),
                                         'surface_azimuth':azimuth,
                                         'surface_tilt':fixed_tilt_angle})
        elif useMeasuredTrackerAngle:           
            # tracked system
            surface_tilt=self.meastracker_angle
            surface_azimuth=azimuth

            trackingdata = pd.DataFrame({'tracker_theta':self.meastracker_angle,
                                         'aoi':aoi(surface_tilt, surface_azimuth,
                                                   solpos['zenith'], 
                                                   solpos['azimuth']),
                                         'surface_azimuth':azimuth,
                                         'surface_tilt':abs(self.meastracker_angle)})


        else:
            # get 1-axis tracker tracker_theta, surface_tilt and surface_azimuth
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=RuntimeWarning)
                trackingdata = pvlib.tracking.singleaxis(solpos['zenith'],
                                                     solpos['azimuth'],
                                                     axis_tilt,
                                                     azimuth,
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
            return base * (x/float(base)).round()

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
            # Fill partial year. Requires 2021 measurement year.
            savedata = _subhourlydatatoGencumskyformat(savedata, 
                                                       label=self.label)
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
    at the array, as well plotting and reporting results.
    """
    def __repr__(self):
        return str(self.__dict__)    
    def __init__(self, octfile=None, name=None, hpc=False):
        """
        Initialize AnalysisObj by pointing to the octfile.  Scan information
        is defined separately by passing scene details into AnalysisObj.moduleAnalysis()
        
        Parameters
        ------------
        octfile : string
            Filename and extension of .oct file
        name    :
        hpc     : boolean, default False. Waits for octfile for a
                  longer time if parallel processing.
        """

        self.octfile = octfile
        self.name = name
        self.hpc = hpc

    def makeImage(self, viewfile, octfile=None, name=None):
        """
        Makes a visible image (rendering) of octfile, viewfile
        """
        
        import time

        if octfile is None:
            octfile = self.octfile
        if name is None:
            name = self.name

        #TODO: update this for cross-platform compatibility w/ os.path.join
        if self.hpc :
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
        sx_xinc = linePtsDict['sx_xinc']
        sx_yinc = linePtsDict['sx_yinc']
        sx_zinc = linePtsDict['sx_zinc']
        Nx = int(linePtsDict['Nx'])
        Ny = int(linePtsDict['Ny'])
        Nz = int(linePtsDict['Nz'])

        x = []
        y = []
        z = []

        for iz in range(0,Nz):
            for ix in range(0,Nx):
                for iy in range(0,Ny):
                    x . append(xstart+iy*xinc+ix*sx_xinc)
                    y . append(ystart+iy*yinc+ix*sx_yinc)
                    z . append(zstart+iy*zinc+ix*sx_zinc)

        return x, y, z
        
    def _linePtsMakeDict(self, linePtsDict):
        a = linePtsDict
        linepts = self._linePtsMake3D(a['xstart'],a['ystart'],a['zstart'],
                            a['xinc'], a['yinc'], a['zinc'],
                            a['sx_xinc'], a['sx_yinc'], a['sx_zinc'],
                            a['Nx'],a['Ny'],a['Nz'],a['orient'])
        return linepts

    def _linePtsMake3D(self, xstart, ystart, zstart, xinc, yinc, zinc,
                       sx_xinc, sx_yinc, sx_zinc,
                      Nx, Ny, Nz, orient):
        #create linepts text input with variable x,y,z.
        #If you don't want to iterate over a variable, inc = 0, N = 1.

        linepts = ""
        # make sure Nx, Ny, Nz are ints.
        Nx = int(Nx)
        Ny = int(Ny)
        Nz = int(Nz)


        for iz in range(0,Nz):
            for ix in range(0,Nx):
                for iy in range(0,Ny):
                    xpos = xstart+iy*xinc+ix*sx_xinc
                    ypos = ystart+iy*yinc+ix*sx_yinc
                    zpos = zstart+iy*zinc+ix*sx_zinc
                    linepts = linepts + str(xpos) + ' ' + str(ypos) + \
                          ' '+str(zpos) + ' ' + orient + " \r"
        return(linepts)

    def _irrPlot(self, octfile, linepts, mytitle=None, plotflag=None,
                   accuracy='low'):
        """
        (plotdict) = _irrPlot(linepts,title,time,plotflag, accuracy)
        irradiance plotting using rtrace
        pass in the linepts structure of the view along with a title string
        for the plots.  

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

        
        if self.hpc :
            import time
            time_to_wait = 10
            time_counter = 0
            while not os.path.exists(octfile):
                time.sleep(1)
                time_counter += 1
                if time_counter > time_to_wait:
                    print('Warning: OCTFILE NOT FOUND')
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

    def _saveResults(self, data=None, reardata=None, savefile=None, RGB = False):
        """
        Function to save output from _irrPlot
        If rearvals is passed in, back ratio is saved
        If data = None then only reardata is saved.
    
        Returns
        --------
        savefile : str
            If set to None, will write to default .csv filename in results folder.
        """

        if savefile is None:
            savefile = data['title'] + '.csv'
        
        if data is None and reardata is not None: # only rear data is passed.
            data = reardata
            reardata = None
            # run process like normal but swap labels at the end
            rearswapflag = True  
        else:
            rearswapflag = False
            
        # make savefile dataframe and set self.attributes
        
        if RGB:
            data_sub = {key:data[key] for key in ['x', 'y', 'z', 'mattype', 'Wm2','r', 'g', 'b' ]}
        else:
            data_sub = {key:data[key] for key in ['x', 'y', 'z', 'mattype','Wm2' ]}
            
        df = pd.DataFrame(data_sub)
        df = df.rename(columns={'Wm2':'Wm2Front'})
        
        if reardata is not None:
            df.insert(3, 'rearZ', reardata['z'])
            df.insert(5, 'rearMat', reardata['mattype'])
            df.insert(7, 'Wm2Back',  reardata['Wm2'])
            # add 1mW/m2 to avoid dividebyzero
            df.insert(8, 'Back/FrontRatio',  df['Wm2Back'] / (df['Wm2Front']+.001))
            df['backRatio'] = df['Back/FrontRatio']
            df['rearX'] = reardata['x']
            df['rearY'] = reardata['y']
            if RGB:
                df['rearR'] = reardata['r']
                df['rearG'] = reardata['g']
                df['rearB'] = reardata['b']
                #df = df[['x','y','z','rearZ','mattype','rearMat',
                #                    'Wm2Front','Wm2Back','Back/FrontRatio',
                #                    'r','g','b', 'rearR','rearG','rearB']]
            #else:
                #df = df[['x','y','z','rearZ','mattype','rearMat',
                #                     'Wm2Front','Wm2Back','Back/FrontRatio']]

        #else:
        #    if RGB:
        #        df = df[['x','y','z', 'mattype','Wm2Front', 'r', 'g', 'b']]
        #
        #    else:
        #        df = df[['x','y','z', 'mattype','Wm2Front']]
                
        # rename columns if only rear data was originally passed
        if rearswapflag:
            df = df.rename(columns={'Wm2Front':'Wm2Back','mattype':'rearMat'})
        # set attributes of analysis to equal columns of df
        for col in df.columns:
            setattr(self, col, list(df[col]))    
        # only save a subset
        df = df.drop(columns=['rearX','rearY','backRatio'], errors='ignore')
        df.to_csv(os.path.join("results", savefile), sep = ',',
                           index = False)


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
                       sensorsy=9, sensorsx=1, 
                       frontsurfaceoffset=0.001, backsurfaceoffset=0.001, 
                       modscanfront=None, modscanback=None, relative=False, 
                       debug=False):
        
        """
        Handler function that decides how to handle different number of front
        and back sensors. If number for front sensors is not provided or is 
        the same as for the back, _moduleAnalysis
        is called only once. Else it is called twice to get the different front
        and back dictionary. 
                  
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
        sensorsy : int or list 
            Number of 'sensors' or scanning points along the collector width 
            (CW) of the module(s). If multiple values are passed, first value
            represents number of front sensors, second value is number of back sensors
        sensorsx : int or list 
            Number of 'sensors' or scanning points along the length, the side perpendicular 
            to the collector width (CW) of the module(s) for the back side of the module. 
            If multiple values are passed, first value represents number of 
            front sensors, second value is number of back sensors.
        debug : bool
            Activates various print statemetns for debugging this function.
        modscanfront : dict
            Dictionary to modify the fronstcan values established by this routine 
            and set a specific value. Keys possible are 'xstart', 'ystart', 'zstart',
            'xinc', 'yinc', 'zinc', 'Nx', 'Ny', 'Nz', and 'orient'. If modifying 
            Nx, Ny or Nz, make sure to modify on modscanback to avoid issues on 
            results writing stage. All of these keys are ints or 
            floats except for 'orient' which takes x y z values as string 'x y z'
            for example '0 0 -1'. These values will overwrite the internally
            calculated frontscan dictionary for the module & row selected.
        modscanback: dict
            Dictionary to modify the backscan values established by this routine 
            and set a specific value. Keys possible are 'xstart', 'ystart', 'zstart',
            'xinc', 'yinc', 'zinc', 'Nx', 'Ny', 'Nz', and 'orient'. If modifying 
            Nx, Ny or Nz, make sure to modify on modscanback to avoid issues on 
            results writing stage. All of these keys are ints or 
            floats except for 'orient' which takes x y z values as string 'x y z'
            for example '0 0 -1'. These values will overwrite the internally
            calculated frontscan dictionary for the module & row selected.    
        relative : Bool
            if passing modscanfront and modscanback to modify dictionarie of positions,
            this sets if the values passed to be updated are relative or absolute. 
            Default is absolute value (relative=False)
   
        
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
        
        def _checkSensors(sensors):
            # Checking Sensors input data for list or tuple
            if (type(sensors)==tuple or type(sensors)==list):
                try:
                    sensors_back = sensors[1]
                    sensors_front = sensors[0]
                except IndexError: # only 1 value passed??
                    sensors_back = sensors_front = sensors[0]
            elif (type(sensors)==int or type(sensors)==float):
                # Ensure sensors are positive int values.
                if int(sensors) < 1:
                    raise Exception('input sensorsy must be numeric >0')
                sensors_back = sensors_front = int(sensors)
            else:
                print('Warning: invalid value passed for sensors. Setting = 1')
                sensors_back = sensors_front = 1
            return sensors_front, sensors_back
            
        sensorsy_front, sensorsy_back = _checkSensors(sensorsy)
        sensorsx_front, sensorsx_back = _checkSensors(sensorsx)
        
        if (sensorsx_back != sensorsx_front) or (sensorsy_back != sensorsy_front):
            sensors_diff = True
        else:
            sensors_diff = False
          
        dtor = np.pi/180.0

        # Internal scene parameters are stored in scene.sceneDict. Load these into local variables
        sceneDict = scene.sceneDict

        azimuth = sceneDict['azimuth']
        tilt = sceneDict['tilt']
        nMods = sceneDict['nMods']
        nRows = sceneDict['nRows']
        originx = sceneDict['originx']
        originy = sceneDict['originy']

       # offset = moduleDict['offsetfromaxis']
        offset = scene.module.offsetfromaxis
        sceney = scene.module.sceney
        scenex = scene.module.scenex

        # x needed for sensorsx>1 case
        x = scene.module.x
        
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

        if hasattr(scene.module,'z'):
            modulez = scene.module.z
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

        sceneDict, use_clearanceheight  = _heightCasesSwitcher(sceneDict, 
                                                               preferred = 'hub_height',
                                                               nonpreferred = 'clearance_height')
        
        if use_clearanceheight :
            height = sceneDict['clearance_height'] + 0.5* \
                np.sin(abs(tilt) * np.pi / 180) * \
                sceney - offset*np.sin(abs(tilt)*np.pi/180)
        else:
            height = sceneDict['hub_height']


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

        #Adjust orientation of scan depending on tilt & azimuth
        zdir = np.cos((tilt)*dtor)
        ydir = np.sin((tilt)*dtor) * np.cos((azimuth)*dtor)
        xdir = np.sin((tilt)*dtor) * np.sin((azimuth)*dtor)
        front_orient = '%0.3f %0.3f %0.3f' % (-xdir, -ydir, -zdir)
        back_orient = '%0.3f %0.3f %0.3f' % (xdir, ydir, zdir)
    
        #IF cellmodule:
        #TODO: Add check for sensorsx_back
        #temp = scene.moduleDict.get('cellModule') #error-free way to query it
        #if ((temp is not None) and
        if ((getattr(scene.module, 'cellModule', None)) and
            (sensorsy_back == scene.module.cellModule.numcellsy)):
            ycell = scene.module.cellModule.ycell
            xinc_back = -((sceney - ycell ) / (scene.module.cellModule.numcellsy-1)) * np.cos((tilt)*dtor) * np.sin((azimuth)*dtor)
            yinc_back = -((sceney - ycell) / (scene.module.cellModule.numcellsy-1)) * np.cos((tilt)*dtor) * np.cos((azimuth)*dtor)
            zinc_back = ((sceney - ycell) / (scene.module.cellModule.numcellsy-1)) * np.sin(tilt*dtor)
            firstsensorxstartfront = xstartfront - scene.module.cellModule.ycell/2 * np.cos((tilt)*dtor) * np.sin((azimuth)*dtor)
            firstsensorxstartback = xstartback  - ycell/2 * np.cos((tilt)*dtor) * np.sin((azimuth)*dtor)
            firstsensorystartfront = ystartfront - ycell/2 * np.cos((tilt)*dtor) * np.cos((azimuth)*dtor)
            firstsensorystartback = ystartback - ycell/2 * np.cos((tilt)*dtor) * np.cos((azimuth)*dtor)
            firstsensorzstartfront = zstartfront + ycell/2 * np.sin(tilt*dtor)
            firstsensorzstartback = zstartback + ycell/2  * np.sin(tilt*dtor)
            xinc_front = xinc_back
            yinc_front = yinc_back
            zinc_front = zinc_back
            
            sx_xinc_front = 0.0
            sx_yinc_front = 0.0
            sx_zinc_front = 0.0
            sx_xinc_back = 0.0
            sx_yinc_back = 0.0
            sx_zinc_back = 0.0
        
            if (sensorsx_back != 1.0):
                print("Warning: Cell-level module analysis for sensorsx > 1 not "+
                      "fine-tuned yet. Use at own risk, some of the x positions "+
                      "might fall in spacing between cells.")
        else:        
            xinc_back = -(sceney/(sensorsy_back + 1.0)) * np.cos((tilt)*dtor) * np.sin((azimuth)*dtor)
            yinc_back = -(sceney/(sensorsy_back + 1.0)) * np.cos((tilt)*dtor) * np.cos((azimuth)*dtor)
            zinc_back = (sceney/(sensorsy_back + 1.0)) * np.sin(tilt*dtor)
            
            
            if sensors_diff:
                xinc_front = -(sceney/(sensorsy_front + 1.0)) * np.cos((tilt)*dtor) * np.sin((azimuth)*dtor)
                yinc_front = -(sceney/(sensorsy_front + 1.0)) * np.cos((tilt)*dtor) * np.cos((azimuth)*dtor)
                zinc_front = (sceney/(sensorsy_front + 1.0)) * np.sin(tilt*dtor)
                
            else:
                xinc_front = xinc_back
                yinc_front = yinc_back
                zinc_front = zinc_back
                
            firstsensorxstartfront = xstartfront+xinc_front
            firstsensorxstartback = xstartback+xinc_back
            firstsensorystartfront = ystartfront+yinc_front
            firstsensorystartback = ystartback+yinc_back
            firstsensorzstartfront = zstartfront + zinc_front
            firstsensorzstartback = zstartback + zinc_back
        
            ## Correct positions for sensorsx other than 1
            # TODO: At some point, this equations can include the case where 
            # sensorsx = 1, and cleanup the original position calculation to place
            # firstsensorxstartback before this section on edge not on center.
            # will save some multiplications and division but well, it works :)
            
            if sensorsx_back > 1.0:
                sx_xinc_back = -(x/(sensorsx_back*1.0+1)) * np.cos((azimuth)*dtor)
                sx_yinc_back = (x/(sensorsx_back*1.0+1)) * np.sin((azimuth)*dtor)
                # Not needed unless axis_tilt != 0, which is not a current option
                sx_zinc_back = 0.0 #       
                
                firstsensorxstartback = firstsensorxstartback + (x/2.0) * np.cos((azimuth)*dtor) + sx_xinc_back
                firstsensorystartback = firstsensorystartback - (x/2.0) * np.sin((azimuth)*dtor) + sx_yinc_back
                # firstsensorzstartback Not needed unless axis_tilt != 0, which is not a current option
                #firstsensorxstartfront = firstsensorxstartback
                #firstsensorystartfront = firstsensorystartback                
            else:
                sx_xinc_back = 0.0
                sx_yinc_back = 0.0
                sx_zinc_back = 0.0
            
            if sensorsx_front > 1.0:
                sx_xinc_front = -(x/(sensorsx_front*1.0+1)) * np.cos((azimuth)*dtor)
                sx_yinc_front = (x/(sensorsx_front*1.0+1)) * np.sin((azimuth)*dtor)
                # Not needed unless axis_tilt != 0, which is not a current option
                sx_zinc_front = 0.0 # 
                
                firstsensorxstartfront = firstsensorxstartfront + (x/2.0) * np.cos((azimuth)*dtor) + sx_xinc_back
                firstsensorystartfront = firstsensorystartfront - (x/2.0) * np.sin((azimuth)*dtor) + sx_yinc_back

                # firstsensorzstartback Not needed unless axis_tilt != 0, which is not a current option
            else:
                sx_xinc_front = 0.0
                sx_yinc_front = 0.0
                sx_zinc_front = 0.0
                
                
        if debug is True:
            print("Azimuth", azimuth)
            print("Coordinate Center Point of Desired Panel before azm rotation", x0, y0)
            print("Coordinate Center Point of Desired Panel after azm rotation", x1, y1)
            print("Edge of Panel", x2, y2, z2)
            print("Offset Shift", x3, y3, z3)
            print("Final Start Coordinate Front", xstartfront, ystartfront, zstartfront)
            print("Increase Coordinates", xinc_front, yinc_front, zinc_front)
        
        frontscan = {'xstart': firstsensorxstartfront, 'ystart': firstsensorystartfront,
                     'zstart': firstsensorzstartfront,
                     'xinc':xinc_front, 'yinc': yinc_front, 'zinc':zinc_front,
                     'sx_xinc':sx_xinc_front, 'sx_yinc':sx_yinc_front,
                     'sx_zinc':sx_zinc_front, 
                     'Nx': sensorsx_front, 'Ny':sensorsy_front, 'Nz':1, 'orient':front_orient }
        backscan = {'xstart':firstsensorxstartback, 'ystart': firstsensorystartback,
                     'zstart': firstsensorzstartback,
                     'xinc':xinc_back, 'yinc': yinc_back, 'zinc':zinc_back,
                     'sx_xinc':sx_xinc_back, 'sx_yinc':sx_yinc_back,
                     'sx_zinc':sx_zinc_back, 
                     'Nx': sensorsx_back, 'Ny':sensorsy_back, 'Nz':1, 'orient':back_orient }

        if modscanfront is not None:
            frontscan2 = _modDict(originaldict=frontscan, moddict=modscanfront, relative=relative)
        else:
            frontscan2 = frontscan.copy()
        if modscanback is not None:
            backscan2 = _modDict(originaldict=backscan, moddict=modscanback, relative=relative)
        else:
            backscan2 = backscan.copy()   
                
        return frontscan2, backscan2 
      
    def analyzeRow(self, octfile, scene, rowWanted=None, name=None, 
                   sensorsy=None, sensorsx=None ):
        '''
        Function to Analyze every module in the row. 

        Parameters
        ----------
        octfile : string
            Filename and extension of .oct file
        scene : ``SceneObj``
            Generated with :py:class:`~bifacial_radiance.RadianceObj.makeScene`.
        rowWanted : int
            Row wanted to sample. If none, defaults to center row (rounding down)
        sensorsy : int or list 
            Number of 'sensors' or scanning points along the collector width 
            (CW) of the module(s). If multiple values are passed, first value
            represents number of front sensors, second value is number of back sensors
        sensorsx : int or list 
            Number of 'sensors' or scanning points along the length, the side perpendicular 
            to the collector width (CW) of the module(s) for the back side of the module. 
            If multiple values are passed, first value represents number of 
            front sensors, second value is number of back sensors.

        Returns
        -------
        df_row : dataframe
            Dataframe with all values sampled for the row.

        '''
        #allfront = []
        #allback = []
        
        nMods = scene.sceneDict['nMods']
        
        if rowWanted == None:
            rowWanted = round(self.nRows / 1.99)
        df_dict_row = {}
        row_keys = ['x','y','z','rearZ','mattype','rearMat','Wm2Front','Wm2Back','Back/FrontRatio']
        dict_row = df_dict_row.fromkeys(row_keys)
        df_row = pd.DataFrame(dict_row, index = [j for j in range(nMods)])
        
        for i in range (nMods):
            temp_dict = {}
            frontscan, backscan = self.moduleAnalysis(scene, sensorsy=sensorsy, 
                                        sensorsx=sensorsx, modWanted = i+1, 
                                        rowWanted = rowWanted) 
            allscan = self.analysis(octfile, name+'_Module_'+str(i), frontscan, backscan) 
            front_dict = allscan[0]
            back_dict = allscan[1]
            temp_dict['x'] = front_dict['x']
            temp_dict['y'] = front_dict['y']
            temp_dict['z'] = front_dict['z']
            temp_dict['rearZ'] = back_dict['z']
            temp_dict['mattype'] = front_dict['mattype']
            temp_dict['rearMat'] = back_dict['mattype']
            temp_dict['Wm2Front'] = front_dict['Wm2']
            temp_dict['Wm2Back'] = back_dict['Wm2']
            temp_dict['Back/FrontRatio'] = list(np.array(front_dict['Wm2'])/np.array(back_dict['Wm2']))
            df_row.iloc[i] = temp_dict
            #allfront.append(front)
        return df_row

    def analysis(self, octfile, name, frontscan, backscan,
                 plotflag=False, accuracy='low', RGB=False):
        """
        General analysis function, where linepts are passed in for calling the
        raytrace routine :py:class:`~bifacial_radiance.AnalysisObj._irrPlot` 
        and saved into results with 
        :py:class:`~bifacial_radiance.AnalysisObj._saveResults`.

        
        Parameters
        ------------
        octfile : string
            Filename and extension of .oct file
        name : string 
            Name to append to output files
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
        RGB : Bool
            If the raytrace is a spectral raytrace and information for the three channe
            wants to be saved, set RGB to True.

            
        Returns
        -------
         File saved in `\\results\\irr_name.csv`

        """

        if octfile is None:
            print('Analysis aborted - no octfile \n')
            return None, None
        linepts = self._linePtsMakeDict(frontscan)
        frontDict = self._irrPlot(octfile, linepts, name+'_Front',
                                    plotflag=plotflag, accuracy=accuracy)

        #bottom view.
        linepts = self._linePtsMakeDict(backscan)
        backDict = self._irrPlot(octfile, linepts, name+'_Back',
                                   plotflag=plotflag, accuracy=accuracy)
        # don't save if _irrPlot returns an empty file.
        if frontDict is not None:
            if len(frontDict['Wm2']) != len(backDict['Wm2']):
                self.Wm2Front = np.mean(frontDict['Wm2'])
                self.Wm2Back = np.mean(backDict['Wm2'])
                self.backRatio = self.Wm2Back / (self.Wm2Front + .001)
                self._saveResults(frontDict, reardata=None, savefile='irr_%s.csv'%(name+'_Front'), RGB=RGB)
                self._saveResults(data=None, reardata=backDict, savefile='irr_%s.csv'%(name+'_Back'), RGB=RGB)
            else:
                self._saveResults(frontDict, backDict,'irr_%s.csv'%(name), RGB=RGB)

        return frontDict, backDict


def quickExample(testfolder=None):
    """
    Example of how to run a Radiance routine for a simple rooftop bifacial system

    """

    import bifacial_radiance
    
    if testfolder == None:
        testfolder = bifacial_radiance.main._interactive_directory(
            title = 'Select or create an empty directory for the Radiance tree')

    demo = bifacial_radiance.RadianceObj('simple_panel', path=testfolder)  # Create a RadianceObj 'object'

    #    A=load_inputvariablesfile()

    # input albedo number or material name like 'concrete'.
    # To see options, run setGround without any input.
    demo.setGround(0.62)
    try:
        epwfile = demo.getEPW(lat=40.01667, lon=-105.25) # pull TMY data for any global lat/lon
    except ConnectionError: # no connection to automatically pull data
        pass

    metdata = demo.readWeatherFile(epwfile, coerce_year=2001) # read in the EPW weather data from above
    #metdata = demo.readTMY() # select a TMY file using graphical picker
    # Now we either choose a single time point, or use cumulativesky for the entire year.
    cumulativeSky = False
    if cumulativeSky:
        demo.genCumSky() # entire year.
    else:
        timeindex = metdata.datetime.index(pd.to_datetime('2001-06-17 12:0:0 -7'))
        demo.gendaylit(metdata=metdata, timeindex=timeindex)  # Noon, June 17th


    # create a scene using panels in landscape at 10 deg tilt, 1.5m pitch. 0.2 m ground clearance
    moduletype = 'test-module'
    module = demo.makeModule(name=moduletype, x=1.59, y=0.95 )
    sceneDict = {'tilt':10,'pitch':1.5,'clearance_height':0.2,
                 'azimuth':180, 'nMods': 10, 'nRows': 3}
    #makeScene creates a .rad file with 10 modules per row, 3 rows.
    scene = demo.makeScene(module=module, sceneDict=sceneDict)
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



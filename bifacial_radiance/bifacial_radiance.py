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
0.0.5:  1-axis tracking draft
0.0.4:  Include configuration file module.json and custom module configuration
0.0.3:  Arbitrary NxR number of modules and rows for SceneObj 
0.0.2:  Adjustable azimuth angle other than 180
0.0.1:  Initial stable release
'''

#start in pylab space to enable plotting
#get_ipython().magic(u'pylab')
import os, datetime
import matplotlib.pyplot as plt  
import pandas as pd
import numpy as np #already imported with above pylab magic
#from IPython.display import Image
from subprocess import Popen, PIPE  # replacement for os.system()
#import shlex

import pkg_resources
global DATA_PATH # path to data files including module.json.  Global context
DATA_PATH = pkg_resources.resource_filename('bifacial_radiance', 'data/') 


def _findme(lst, a): #find string match in a list. found this nifty script on stackexchange
    return [i for i, x in enumerate(lst) if x==a]


def _normRGB(r,g,b): #normalize by weight of each color for human vision sensitivity
    return r*0.216+g*0.7152+b*0.0722

def _popen(cmd, data_in, data_out=PIPE):
    """
    Helper function subprocess.popen replaces os.system 
    - gives better input/output process control
    usage: pass <data_in> to process <cmd> and return results
    from rgbeimage.py (Thomas Bleicher 2010)
    """
    cmd = str(cmd) # get's rid of unicode oddities
    #p = Popen(shlex.split(cmd), bufsize=-1, stdin=PIPE, stdout=data_out, stderr=PIPE)
    p = Popen(cmd, bufsize=-1, stdin=PIPE, stdout=data_out, stderr=PIPE)
    data, err = p.communicate(data_in)
    if err:
        return 'message: '+err.strip()
    if data:
        return data



        

class RadianceObj:
    '''
    RadianceObj:  top level class to work on radiance objects, keep track of filenames, 
    sky values, PV module configuration etc.

    
    values:
        basename    : text to append to output files
        filelist    : list of Radiance files to create oconv
        nowstr      : current date/time string
        path        : working directory with Radiance materials and objects
        TODO:  populate this more
    functions:
        __init__   : initialize the object
        _setPath    : change the working directory
        TODO:  populate this more
    
    '''
    
    def __init__(self, basename=None, path=None):
        '''
        Description
        -----------
        initialize RadianceObj with path of Radiance materials and objects,
        as well as a basename to append to 
    
        Parameters
        ----------
        basename: string, append temporary and output files with this value
        path: location of Radiance materials and objects
    
        Returns
        -------
        none
        '''

        self.metdata = {}        # data from epw met file
        self.data = {}           # data stored at each timestep
        self.path = ""             # path of working directory
        self.basename = ""         # basename to append
        #self.filelist = []         # list of files to include in the oconv
        self.materialfiles = []    # material files for oconv
        self.skyfiles = []          # skyfiles for oconv
        self.radfiles = []      # scene rad files for oconv
        self.octfile = []       #octfile name for analysis
                

        now = datetime.datetime.now()
        self.nowstr = str(now.date())+'_'+str(now.hour)+str(now.minute)+str(now.second)
        
        ''' DEFAULTS '''
        #TODO:  check if any of these defaults are necessary
        #self.material_path = "materials"      # directory of materials data. default 'materials'
        #self.sky_path = 'skies'         # directory of sky data. default 'skies'
        #TODO: check if lat/lon/epwfile should be defined in the meteorological object instead
        self.latitude = 40.02           # default - Boulder
        self.longitude = -105.25        # default - Boulder
        self.epwfile = 'USA_CO_Boulder.724699_TMY2.epw'  # default - Boulder
        
        
        if basename is None:
            self.basename = self.nowstr
        else:
            self.basename = basename
        #self.__name__ = self.basename  #optional info
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
        except:
            print('Path doesn''t exist: %s' % (path)) 
        
        # check for path in the new Radiance directory:
        def _checkPath(path):  # create the file structure if it doesn't exist
            if not os.path.exists(path):
                os.makedirs(path)
                print('Making path: '+path)
                
        _checkPath('images/'); _checkPath('objects/');  _checkPath('results/'); _checkPath('skies/'); 
        # if materials directory doesn't exist, populate it with ground.rad
        # figure out where pip installed support files. 
        from shutil import copy2 

        if not os.path.exists('materials/'):  #copy ground.rad to /materials
            os.makedirs('materials/') 
            print('Making path: materials/')

            copy2(os.path.join(DATA_PATH,'ground.rad'),'materials')
        # if views directory doesn't exist, create it with two default views - side.vp and front.vp
        if not os.path.exists('views/'):
            os.makedirs('views/')
            with open('views/side.vp', 'wb') as f:
                f.write('rvu -vtv -vp -10 1.5 3 -vd 1.581 0 -0.519234 -vu 0 0 1 -vh 45 -vv 45 -vo 0 -va 0 -vs 0 -vl 0') 
            with open('views/front.vp', 'wb') as f:
                f.write('rvu -vtv -vp 0 -3 5 -vd 0 0.894427 -0.894427 -vu 0 0 1 -vh 45 -vv 45 -vo 0 -va 0 -vs 0 -vl 0') 

    def getfilelist(self):
        ''' return concat of matfiles, radfiles and skyfiles
        '''
        return self.materialfiles + self.skyfiles + self.radfiles
    
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
        
    def returnMaterialFiles(self, material_path = None):
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
        
    def setGround(self, material = None, material_file = None):
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
        
        path_to_save = 'EPWs\\' # create a directory and write the name of directory here
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
        print 'Getting weather file: ' + name,
        r = requests.get(url,verify = False, headers = hdr)
        if r.ok:
            with open(path_to_save + name, 'wb') as f:
                f.write(r.text)
            print ' ... OK!'
        else:
            print ' connection error status code: %s' %( r.status_code)
            r.raise_for_status()
        
        self.epwfile = 'EPWs\\'+name
        return 'EPWs\\'+name
    
    def getEPW_all():
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
     
        path_to_save = 'EPWs\\' # create a directory and write the name of directory here
        if not os.path.exists(path_to_save):
            os.makedirs(path_to_save)
        r = requests.get('https://github.com/NREL/EnergyPlus/raw/develop/weather/master.geojson', verify = False)
        data = r.json()
    
        for location in data['features']:
            match = re.search(r'href=[\'"]?([^\'" >]+)', location['properties']['epw'])
            if match:
                url = match.group(1)
                name = url[url.rfind('/') + 1:]
                print name
                r = requests.get(url,verify = False)
                if r.ok:
                    with open(path_to_save + name, 'wb') as f:
                        f.write(r.text)
                else:
                    print ' connection error status code: %s' %( r.status_code)
        print 'done!'    
    
            
    def readEPW(self,epwfile=None):
        '''
        use pyepw to read in a epw file.  
        pyepw installation info:  pip install pyepw
        documentation: https://github.com/rbuffat/pyepw
        
        Parameters
        ------------
        epwfile:  filename of epw

        Returns
        -------
        metdata - MetObj collected from epw file
        '''
        if epwfile is None:
            epwfile = self.epwfile
        try:
            from pyepw.epw import EPW
        except:
            print('Error: pyepw not installed.  try pip install pyepw')
        epw = EPW()
        epw.read(epwfile)
        
        self.metdata = MetObj(epw)
        self.epwfile = epwfile
        return self.metdata
        
    def gendaylit(self, metdata, timeindex):
        '''
        sets and returns sky information using gendaylit.  if material type is known, pass it in to get
        reflectance info.  if material type isn't known, material_info.list is returned
        Note - -W and -O1 option is used to create full spectrum analysis in units of Wm-2
        Parameters
        ------------
        metdata:  MetObj object with 8760 list of dni, dhi, ghi and location
        timeindex: index from 0 to 8759 of EPW timestep
        
        Returns
        -------
        skyname:   filename of sky in /skies/ directory
        
        '''
        locName = metdata.location.city
        month = metdata.datetime[timeindex].month
        day = metdata.datetime[timeindex].day
        hour = metdata.datetime[timeindex].hour
        minute = metdata.datetime[timeindex].minute
        timeZone = metdata.location.timezone
        dni = metdata.dni[timeindex]
        dhi = metdata.dhi[timeindex]
        
        sky_path = 'skies'

         #" -L %s %s -g %s \n" %(dni/.0079, dhi/.0079, self.ground.ReflAvg) + \
        skyStr =   ("# start of sky definition for daylighting studies\n"  
            "# location name: " + str(locName) + " LAT: " + str(metdata.location.latitude) 
            +" LON: " + str(metdata.location.longitude) + "\n"
            "!gendaylit %s %s %s" %(month,day,hour+minute/60.0) ) + \
            " -a %s -o %s" %(metdata.location.latitude, metdata.location.longitude) +\
            " -m %s" % (float(timeZone)*15) +\
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
         
        skyname = os.path.join(sky_path,"sky_%s.rad" %(self.basename))
            
        skyFile = open(skyname, 'w')
        skyFile.write(skyStr)
        skyFile.close()
        
        self.skyfiles = [skyname ]
        
        return skyname
        
    def genCumSky(self,epwfile = None, startdt = None, enddt = None, savefile = None):
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
        lat = self.metdata.location.latitude
        lon = self.metdata.location.longitude
        timeZone = self.metdata.location.timezone
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
            err = _popen(cmd,None,f)
            if err is not None:
                print err

            
        
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

        skyname = os.path.join(sky_path,savefile+".rad" )
        
        skyFile = open(skyname, 'w')
        skyFile.write(skyStr)
        skyFile.close()
        
        self.skyfiles = [skyname]#, 'SunFile.rad' ]
        
        return skyname
        
    def genCumSky1axis(self, trackerdict):
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
        
        for theta in trackerdict:
            # call gencumulativesky with a new .cal and .rad name
            csvfile = trackerdict[theta]['csvfile']
            savefile = '1axis_%s'%(theta)  #prefix for .cal file and skies\*.rad file
            skyfile = self.genCumSky(epwfile = csvfile,  savefile = savefile)
            trackerdict[theta]['skyfile'] = skyfile
            print('Created skyfile %s'%(skyfile))
        # delete default skyfile (not strictly necessary)
        self.skyfiles = None
        
        return trackerdict
        
        
    def makeOct(self,filelist=None,octname = None):
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
            octname = self.basename
            
        
        #os.system('oconv '+ ' '.join(filelist) + ' > %s.oct' % (octname))
        
        cmd = 'oconv '+ ' '.join(filelist)
        with open('%s.oct' % (octname),"w") as f:
            err = _popen(cmd,None,f)
            #TODO:  exception handling for no sun up
            if err is not None:
                if err[0:5] == 'error':
                    raise Exception, err[7:]
        
        #use rvu to see if everything looks good. use cmd for this since it locks out the terminal.
        #'rvu -vf views\CUside.vp -e .01 monopanel_test.oct'
        print("created %s.oct" % (octname)),
        self.octfile = '%s.oct' % (octname)
        return '%s.oct' % (octname)
        
    def makeOct1axis(self,trackerdict):
        ''' 
        combine files listed in trackerdict into multiple .oct files
        
        Parameters
        ------------
        trackerdict:  Output from makeScene1axis
        
        Returns: 
        -------
        trackerdict:  append 'octfile'  to the 1-axis dict with the location of the scene .octfile
        '''
        for theta in trackerdict:
            filelist = self.materialfiles + [trackerdict[theta]['skyfile'] , trackerdict[theta]['radfile']]
            octname = '1axis_%s'%(theta)
            trackerdict[theta]['octfile'] = self.makeOct(filelist,octname)
         
        return trackerdict
    """
    def analysis(self, octfile = None, basename = None):
        '''
        default to AnalysisObj.PVSCanalysis(self.octfile, self.basename)
        Not sure how wise it is to have RadianceObj.analysis - perhaps this is best eliminated entirely?
        Most analysis is not done on the PVSC scene any more...  eliminate this and update example notebook?
        '''
        if octfile is None:
            octfile = self.octfile
        if basename is None:
            basename = self.basename
        
        analysis_obj = AnalysisObj(octfile, basename)
        analysis_obj.PVSCanalysis(octfile, basename)
         
        return analysis_obj
    """
    def makeModule(self,name=None,x=1,y=1,bifi=1,orientation='portrait',modulefile = None,text = None):
        '''
        add module details to the .JSON module config file module.json
        This needs to be in the RadianceObj class because this is defined before a SceneObj is.
        
        TODO: add transparency parameter, make modules with non-zero opacity
        
        Parameters
        ------------
        name: string input to name the module type
        
        module configuration dictionary inputs:
        x       # width of module (meters).
        y       # height of module (meters).
        bifi    # bifaciality of the panel (not currently used)
        orientation  #default orientation of the scene (portrait or landscape)
        modulefile   # existing radfile location in \objects.  Otherwise a default value is used
        text = ''    # generation text

        
        Returns: None
        -------
        
        '''
        if name is None:
            print('usage:  makeModule(name,x,y)')
        
        import json
        if modulefile is None:
            #replace whitespace with underlines. what about \n and other weird characters?
            name2 = str(name).strip().replace(' ', '_')
            modulefile = 'objects\\' + name2 + '.rad'
        if text is None:
            text = '! genbox black PVmodule {} {} 0.02 | xform -t {} 0 0'.format(x, y, -x/2.0)
        moduledict = {'x':x,
                      'y':y,
                      'bifi':bifi,
                      'orientation':orientation,
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
        
    def printModules(self):
        # print available module types by creating a dummy SceneObj
        temp = SceneObj('simple_panel')
        modulenames = temp.readModule()
        print('Available module names: {}'.format([str(x) for x in modulenames]))
 
        
    def makeScene(self, moduletype=None, sceneDict=None, nMods = 20, nRows = 7):
        '''
        return a SceneObj which contains details of the PV system configuration including 
        tilt, orientation, row pitch, height, nMods per row, nRows in the system...

        '''
        if moduletype is None:
            print('makeScene(moduletype, sceneDict, nMods, nRows).  Available moduletypes: monopanel, simple_panel' ) #TODO: read in config file to identify available module types
            return
        self.scene = SceneObj(moduletype)
        
        if sceneDict is None:
            print('makeScene(moduletype, sceneDict, nMods, nRows).  sceneDict inputs: .tilt .height .pitch .azimuth')

        if sceneDict.has_key('orientation') is False:
            sceneDict['orientation'] = 'portrait'
        if sceneDict.has_key('azimuth') is False:
            sceneDict['azimuth'] = 180
        self.sceneRAD = self.scene.makeSceneNxR(sceneDict['tilt'],sceneDict['height'],sceneDict['pitch'],sceneDict['orientation'],sceneDict['azimuth'], nMods = nMods, nRows = nRows)
        self.radfiles = [self.sceneRAD]
        
        return self.scene
    
    def makeScene1axis(self, trackerdict, moduletype=None, sceneDict=None, nMods = 20, nRows = 7):
        '''
        create a SceneObj for each tracking angle which contains details of the PV 
        system configuration including orientation, row pitch, hub height, nMods per row, nRows in the system...
        
        Parameters
        ------------
        trackerdict: output from GenCumSky1axis
        
        Returns
        -----------
        trackerdict: append the following keys :
            'radfile': directory where .rad scene file is stored
            'scene' : SceneObj for each tracker theta
            'ground_clearance' : calculated ground clearance based on hub height, tilt angle and module length
        '''
        import math
        
        if moduletype is None:
            print('makeScene1axis(trackerdict, moduletype, sceneDict, nMods, nRows).  Available moduletypes: monopanel, simple_panel' ) #TODO: read in config file to identify available module types
            return
        
        if sceneDict is None:
            print('makeScene(moduletype, sceneDict, nMods, nRows).  sceneDict inputs: .tilt .height .pitch .azimuth')

        if sceneDict.has_key('orientation') is False:
            sceneDict['orientation'] = 'portrait'
        
        

        for theta in trackerdict:
            scene = SceneObj(moduletype)
            surf_azm = trackerdict[theta]['surf_azm']
            surf_tilt = trackerdict[theta]['surf_tilt']
            radname = '1axis%s'%(theta,)
            hubheight = sceneDict['height'] #the hub height is the tracker height at center of rotation.
            if sceneDict['orientation'] == 'portrait':
                module_y = scene.y
            elif sceneDict['orientation'] == 'landscape':
                module_y = scene.x
            # Calculate the ground clearance height based on the hub height
            height = hubheight - 0.5* math.sin(theta * math.pi / 180) * module_y
            radfile = scene.makeSceneNxR(surf_tilt, height,sceneDict['pitch'],orientation = sceneDict['orientation'], azimuth = surf_azm, nMods = nMods, nRows = nRows, radname = radname)
            trackerdict[theta]['radfile'] = radfile
            trackerdict[theta]['scene'] = scene
            trackerdict[theta]['ground_clearance'] = height


        return trackerdict#self.scene
    
    def analysis1axis(self, trackerdict):
        '''
        loop through trackerdict and run linescans for each scene and scan in there.
        
        Parameters
        ----------------
        trackerdict
        
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
        frontWm2 = np.empty(9) # container for tracking front irradiance across module chord
        backWm2 = np.empty(9) # container for tracking rear irradiance across module chord
        for theta in trackerdict:
            basename = '1axis_%s'%(theta)
            octfile = trackerdict[theta]['octfile']
            analysis = AnalysisObj(octfile,basename)            
            frontscan = trackerdict[theta]['scene'].frontscan
            backscan = trackerdict[theta]['scene'].backscan
            basename = '1axis_%s'%(theta,)
            analysis.analysis(octfile,basename,frontscan,backscan)
            trackerdict[theta]['AnalysisObj'] = analysis
            #TODO:  combine cumulative front and back irradiance for each tracker angle
            trackerdict[theta]['Wm2Front'] = analysis.Wm2Front
            trackerdict[theta]['Wm2Back'] = analysis.Wm2Back
            trackerdict[theta]['backRatio'] = analysis.backRatio
            frontWm2 = frontWm2 + np.array(analysis.Wm2Front)
            backWm2 = backWm2 + np.array(analysis.Wm2Back)

        self.Wm2Front = frontWm2
        self.Wm2Back = backWm2
        self.backRatio = backWm2/(frontWm2+.001) 
        
        return trackerdict
            
# End RadianceObj definition
        
class GroundObj:
    '''
    details for the ground surface and reflectance
    '''
       
    def __init__(self, materialOrAlbedo= None, material_file = None):
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
    pv module orientation defaults: portrait orientation. Azimuth = 180 (south)
    pv module origin: z = 0 bottom of frame. y = 0 lower edge of frame. x = 0 vertical centerline of module
    
    scene includes module details (x,y,bifi,orientation)
    '''
    def __init__(self,moduletype=None):
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
  
       


    def readModule(self,name = None):
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
            self.orientation = moduledict['orientation'] #default orientation of the scene
                    #create new .RAD file
            if not os.path.isfile(radfile):
                with open(radfile, 'wb') as f:
                    f.write(moduledict['text'])
            #if not os.path.isfile(radfile):
            #    raise Exception('Error: module file not found {}'.format(radfile))
            self.modulefile = radfile
            
            return moduledict
        else:
            print('Error: module name {} doesnt exist'.format(name))
            return {}
    
    def makeSceneNxR(self, tilt, height, pitch, orientation = None, azimuth = 180, nMods = 20, nRows = 7, radname = None):
        '''
        arrange module defined in SceneObj into a N x R array
        Valid input ranges: Tilt 0-90 degrees.  Azimuth 45-315 degrees
        
        
                Parameters
        ------------
        radname: (string) default name to save radfile. If none, use moduletype by default
        
        Returns
        -------
        radfile: (string) filename of .RAD scene in /objects/
        
        '''

        if orientation is None:
            orientation = 'portrait'
        if radname is None:
            radname =  str(self.moduletype).strip().replace(' ', '_')# remove whitespace
        # assign inputs
        self.tilt = tilt
        self.height = height
        self.pitch = pitch
        self.orientation = orientation
        self.azimuth = azimuth
        ''' INITIALIZE VARIABLES '''
        dtor = np.pi/180
        text = '!xform '

        if orientation == 'landscape':  # transform for landscape
            text += '-rz -90 -t %s %s 0 '%(-self.y/2, self.x/2)
            tempx = self.x; tempy = self.y
            self.x = tempy; self.y = tempx

        text += '-rx %s -t 0 0 %s ' %(tilt, height)
        # create nMods-element array along x, nRows along y
        text += '-a %s -t %s 0 0 -a %s -t 0 %s 0 ' %(nMods, self.x+ 0.01, nRows, pitch)
        
        # azimuth rotation of the entire shebang
        text += '-i 1 -t %s %s 0 -rz %s ' %(-self.x*int(nMods/2), -pitch* int(nRows/2), 180-azimuth) #was *4
        
        text += self.modulefile
        # save the .RAD file
        
        radfile = 'objects\\%s_%s_%s_%sx%s.rad'%(radname,height,pitch, nMods, nRows)
        with open(radfile, 'wb') as f:
            f.write(text)
        

        # define the 9-point front and back scan. if tilt < 45  else scan z
        if tilt < 45: #scan along y facing up/down.
            if -45 <= (azimuth-180) <= 45:  # less than 45 deg rotation in z. still scan y
                self.frontscan = {'xstart':0, 'ystart':  0.1*self.y * np.cos(tilt*dtor) / np.cos((azimuth-180)*dtor), 
                             'zstart': height + self.y *np.sin(tilt*dtor) + 1,
                             'xinc':0, 'yinc': 0.1* self.y * np.cos(tilt*dtor) / np.cos((azimuth-180)*dtor), 
                             'zinc':0 , 'Nx': 1, 'Ny':9, 'Nz':1, 'orient':'0 0 -1' }
                self.backscan = {'xstart':0, 'ystart':  0.1*self.y * np.cos(tilt*dtor) / np.cos((azimuth-180)*dtor), 
                             'zstart': 0.01,
                             'xinc':0, 'yinc': 0.1* self.y * np.cos(tilt*dtor) / np.cos((azimuth-180)*dtor), 
                             'zinc':0 , 'Nx': 1, 'Ny':9, 'Nz':1, 'orient':'0 0 1' }
                             
            elif 45 < abs(azimuth-180) < 135:  # greater than 45 deg rotation in z. scan x instead
                self.frontscan = {'xstart':0.1*self.y * np.cos(tilt*dtor) / np.sin((azimuth-180)*dtor), 'ystart':  0, 
                             'zstart': height + self.y *np.sin(tilt*dtor) + 1,
                             'xinc':0.1* self.y * np.cos(tilt*dtor) / np.sin((azimuth-180)*dtor), 'yinc': 0, 
                             'zinc':0 , 'Nx': 9, 'Ny':1, 'Nz':1, 'orient':'0 0 -1' }
                self.backscan = {'xstart':0.1*self.y * np.cos(tilt*dtor) / np.sin((azimuth-180)*dtor), 'ystart':  0, 
                             'zstart': 0.01,
                             'xinc':0.1* self.y * np.cos(tilt*dtor) / np.sin((azimuth-180)*dtor), 'yinc': 0, 
                             'zinc':0 , 'Nx': 9, 'Ny':1, 'Nz':1, 'orient':'0 0 1' }
            else: # invalid azimuth (?)
                print('\n\nERROR: invalid azimuth. Value must be between 45 and 315. Value entered: %s\n\n' % (azimuth,))
                return
        else: # scan along z
            self.frontscan = {'xstart':0, 'ystart': 0 , 
                         'zstart': height + 0.1* self.y *np.sin(tilt*dtor),
                         'xinc':0, 'yinc': 0, 
                         'zinc':0.1* self.y * np.sin(tilt*dtor), 'Nx': 1, 'Ny':1, 'Nz':9, 'orient':'%s %s 0'%(-1*np.sin(azimuth*dtor), -1*np.cos(azimuth*dtor)) }
            self.backscan = {'xstart':self.y * -1*np.sin(azimuth*dtor), 'ystart': self.y * -1*np.cos(azimuth*dtor), 
                         'zstart': height + 0.1* self.y *np.sin(tilt*dtor),
                         'xinc':0, 'yinc':0, 
                         'zinc':0.1* self.y * np.sin(tilt*dtor), 'Nx': 1, 'Ny':1, 'Nz':9, 'orient':'%s %s 0'%(np.sin(azimuth*dtor), np.cos(azimuth*dtor)) }
        
        self.gcr = self.y / pitch
        self.text = text
        self.radfile = radfile
        return radfile
            
    def makeScene10x3(self, tilt, height, pitch, orientation = None, azimuth = 180):
        '''
        arrange module defined in SceneObj into a 10 x 3 array
        Valid input ranges: Tilt 0-90 degrees.  Azimuth 45-315 degrees
        
        Use the new makeSceneNxR routine

        '''
        radfile = self.makeSceneNxR(tilt=tilt, height=height, pitch=pitch, orientation = orientation, azimuth = azimuth, nMods = 10, nRows = 3)
        return radfile


        
            
class MetObj:
    '''
    meteorological data from EPW file

    '''
    def __init__(self,epw):
        ''' initialize MetObj from passed in epwdata from pyepw.epw
        '''
        self.location = epw.location
        
        wd = epw.weatherdata
        
        
        self.datetime = [datetime.datetime(
                                1990,x.month,x.day,x.hour-1)
                                for x in wd                        
                                ]
        self.ghi = [x.global_horizontal_radiation for x in wd]
        self.dhi = [x.diffuse_horizontal_radiation for x in wd]        
        self.dni = [x.direct_normal_radiation for x in wd]  
        self.ghl = [x.global_horizontal_illuminance for x in wd]
        self.dhl = [x.diffuse_horizontal_illuminance for x in wd]        
        self.dnl = [x.direct_normal_illuminance for x in wd] 
        self.epw_raw = epw
 
    def set1axis(self, axis_azimuth = 180, limit_angle = 45, angledelta = 5):
        '''
        Set up geometry for 1-axis tracking.  Pull in tracking angle details from 
        pvlib, create multiple 8760 metdata sub-files where datetime of met data 
        matches the tracking angle. 
        
        Parameters
        ------------
        axis_azimuth         # orientation axis of tracker torque tube. Default North-South (180 deg)
        limit_angle      # +/- limit angle of the 1-axis tracker in degrees. Default 45 
        angledelta      # degree of rotation increment to parse irradiance bins. Default 5 degrees
                        #  (0.4 % error for DNI).  Other options: 4 (.25%), 2.5 (0.1%).  
                        #  Note: the smaller the angledelta, the more simulations must be run
        Returns
        -------
        trackerdict      dictionary with keys for tracker tilt angles and list of csv metfile, and datetimes at that angle
                         trackerdict[angle]['csvfile';'surf_azm';'surf_tilt';'UTCtime']
        '''

        axis_tilt = 0       # only support 0 tilt trackers for now
        backtrack = False   # include backtracking support in later version
        gcr = 2.0/7.0       # default value - not used if backtrack = False.

        
        # get 1-axis tracker angles for this location, rounded to nearest 'angledelta'
        trackingdata = self._getTrackingAngles(axis_azimuth, limit_angle, angledelta, axis_tilt = 0, backtrack = False, gcr = 2.0/7.0 )
        
        # get list of unique rounded tracker angles
        theta_list = trackingdata.dropna()['theta_round'].unique() 
        # create a separate metfile for each unique tracker theta angle. return dict of filenames and details 
        trackerdict = self._makeTrackerCSV(theta_list,trackingdata)

        return trackerdict
    
    
    def _getTrackingAngles(self,axis_azimuth = 180, limit_angle = 45, angledelta = 5, axis_tilt = 0, backtrack = False, gcr = 2.0/7.0 ):  # return tracker angle data for the system
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
            
            lat = self.location.latitude
            lon = self.location.longitude
            elev = self.location.elevation
            datetime = pd.to_datetime(self.datetime)
            tz = self.location.timezone
            datetimetz = datetime.tz_localize(pytz.FixedOffset(tz*60))  # either use pytz.FixedOffset (in minutes) or 'Etc/GMT+5'
            
            # get solar position zenith and azimuth based on site metadata
            # TODO:  compare against bifacial_vf sun.hrSolarPos
            # TODO:  should we use a solar position  30 minutes prior to the stated datetime to account for hour ending irradiance averages???
            solpos = pvlib.irradiance.solarposition.get_solarposition(datetimetz,lat,lon,elev)
            # get 1-axis tracker tracker_theta, surface_tilt and surface_azimuth        
            trackingdata = pvlib.tracking.singleaxis(solpos['zenith'], solpos['azimuth'], axis_tilt, axis_azimuth, limit_angle, backtrack, gcr)
            # round tracker_theta to increments of angledelta
            
            def _roundArbitrary(x, base = angledelta):
            # round to nearest 'base' value.
            # mask NaN's to avoid rounding error message
                return base * (x.dropna()/float(base)).round()
            trackingdata['theta_round'] = _roundArbitrary(trackingdata['tracker_theta'])
            
            return trackingdata    

    def _makeTrackerCSV(self,theta_list,trackingdata):
        '''
        Create multiple new irradiance csv files with data for each unique rounded tracker angle.
        Return a dictionary with the new csv filenames and other details
        
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
              *csvfile:  name of csv met data file saved in \\EPWs\\
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
            savedata.to_csv(csvfile,index = False, header = False, sep = ' ')


        return trackerdict
    

class AnalysisObj:
    '''
    Analysis class for plotting and reporting
    '''
    def __init__(self, octfile=None, basename=None):
        self.octfile = octfile
        self.basename = basename
        
    def makeImage(self, viewfile, octfile=None, basename=None):
        'make visible image of octfile, viewfile'
        
        if octfile is None:
            octfile = self.octfile
        if basename is None:
            basename = self.basename
        print('generating visible render of scene')
        os.system("rpict -dp 256 -ar 48 -ms 1 -ds .2 -dj .9 -dt .1 -dc .5 -dr 1 -ss 1 -st .1 -ab 3  -aa .1 "+ 
                  "-ad 1536 -as 392 -av 25 25 25 -lr 8 -lw 1e-4 -vf views/"+viewfile+ " " + octfile +
                  " > images/"+basename+viewfile[:-3] +".hdr")
        
    def makeFalseColor(self, viewfile, octfile=None, basename=None):
        '''make false-color plot of octfile, viewfile
        Note: for Windows requires installation of falsecolor.exe, which is part of
        radwinexe-5.0.a.8-win64.zip found at http://www.jaloxa.eu/resources/radiance/radwinexe.shtml
        TODO: error checking for installation of falsecolor.exe with download suggestion
        '''
        if octfile is None:
            octfile = self.octfile
        if basename is None:
            basename = self.basename   
        
        print('generating scene in WM-2')    
        cmd = "rpict -i -dp 256 -ar 48 -ms 1 -ds .2 -dj .9 -dt .1 -dc .5 -dr 1 -ss 1 -st .1 -ab 3  -aa " +\
                  ".1 -ad 1536 -as 392 -av 25 25 25 -lr 8 -lw 1e-4 -vf views/"+viewfile + " " + octfile
        WM2_out = _popen(cmd,None)
        # determine the extreme maximum value to help with falsecolor autoscale
        extrm_out = _popen("pextrem",WM2_out)
        WM2max = max(map(float,extrm_out.split())) # cast the pextrem string as a float and find the max value
        print('saving scene in false color') 
        #auto scale false color map
        if WM2max < 1100:
            cmd = "falsecolor -l W/m2 -m 1 -s 1100 -n 11" 
        else:
            cmd = "falsecolor -l W/m2 -m 1 -s %s"%(WM2max,) 
        with open("images/%s%s_FC.hdr"%(basename,viewfile[:-3]),"w") as f:
            err = _popen(cmd,WM2_out,f)
            if err is not None:
                print err
                print( 'possible solution: install radwinexe binary package from '
                      'http://www.jaloxa.eu/resources/radiance/radwinexe.shtml')
        
    def linePtsMakeDict(self,linePtsDict):
        a = linePtsDict
        linepts = self.linePtsMake3D(a['xstart'],a['ystart'],a['zstart'],
                                a['xinc'], a['yinc'], a['zinc'],
                                a['Nx'],a['Ny'],a['Nz'],a['orient'])
        return linepts
        
    def linePtsMake3D(self,xstart,ystart,zstart,xinc,yinc,zinc,Nx,Ny,Nz,orient):
        #linePtsMake(xpos,ypos,zstart,zend,Nx,Ny,Nz,dir)
        #create linepts text input with variable x,y,z. 
        #If you don't want to iterate over a variable, inc = 0, N = 1.
        
        #now create our own matrix - 3D nested Z,Y,Z
        linepts = ""
        for iz in range(0,Nz):
            zpos = zstart+iz*zinc
            for iy in range(0,Ny):
                ypos = ystart+iy*yinc
                for ix in range(0,Nx):
                    xpos = xstart+ix*xinc
                    linepts = linepts + str(xpos) + ' ' + str(ypos) + ' '+str(zpos) + ' ' + orient + " \r"
        return(linepts)
    
    def irrPlotNew(self,octfile,linepts, mytitle = None,plotflag = None):
        '''
        (plotdict) = irrPlotNew(linepts,title,time,plotflag)
        irradiance plotting using rtrace
        pass in the linepts structure of the view along with a title string for the plots
        note that the plots appear in a blocking way unless you call pylab magic in the beginning.
        
        Parameters
        ------------
        octfile     - filename and extension of .oct file
        linepts     - output from linePtsMake3D
        mytitle     - title to append to results files
        
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
        
        keys = ['Wm2','x','y','z','r','g','b','mattype']
        out = {key: [] for key in keys}
        #out = dict.fromkeys(['Wm2','x','y','z','r','g','b','mattype','title'])
        out['title'] = mytitle    
        print 'linescan in process: ' + mytitle
        #rtrace ambient values set for 'very accurate':
        #cmd = "rtrace -i -ab 5 -aa .08 -ar 512 -ad 2048 -as 512 -h -oovs "+ octfile
        #rtrace optimized for faster scans: (ab2, others 96 is too coarse)
        cmd = "rtrace -i -ab 2 -aa .1 -ar 256 -ad 2048 -as 256 -h -oovs "+ octfile
        temp_out = _popen(cmd,linepts)
        if temp_out is not None:
            if temp_out[0:5] == 'error':
                raise Exception, temp_out[7:]
            else:
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
        
        return(out)   
    
    def saveResults(self, data, reardata = None, savefile = None):
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
            self.Wm2Front = data_sub.pop('Wm2')
            data_sub['Wm2Front'] = self.Wm2Front
            self.Wm2Back = reardata['Wm2']
            data_sub['Wm2Back'] = self.Wm2Back
            self.backRatio = [x/(y+.001) for x,y in zip(reardata['Wm2'],data['Wm2'])] # add 1mW/m2 to avoid dividebyzero
            data_sub['Back/FrontRatio'] = self.backRatio
            df = pd.DataFrame.from_dict(data_sub)
            df.to_csv(os.path.join("results", savefile), sep = ',',columns = ['x','y','z','mattype','Wm2Front','Wm2Back','Back/FrontRatio'], index = False)
        else:
            df = pd.DataFrame.from_dict(data_sub)
            df.to_csv(os.path.join("results", savefile), sep = ',', columns = ['x','y','z','mattype','Wm2'], index = False)
            
        print('saved: %s'%(os.path.join("results", savefile)))
        return os.path.join("results", savefile)
      
    def PVSCanalysis(self, octfile, basename):
        # analysis of octfile results based on the PVSC architecture.
        # usable for \objects\PVSC_4array.rad
        # PVSC front view. iterate x = 0.1 to 4 in 26 increments of 0.15. z = 0.9 to 2.25 in 9 increments of .15
        #x = 3.2 - middle of east panel
        
        frontScan = {'xstart':3.2, 'ystart': -0.1,'zstart': 0.9,'xinc':0, 'yinc': 0,
                     'zinc':0.15, 'Nx': 1, 'Ny':1, 'Nz':10, 'orient':'0 1 0' }
        rearScan = {'xstart':3.2, 'ystart': 3,'zstart': 0.9,'xinc':0, 'yinc': 0,
                     'zinc':0.15, 'Nx': 1, 'Ny':1, 'Nz':10, 'orient':'0 -1 0' }    
        self.analysis(octfile, basename, frontScan, rearScan)

    def G173analysis(self, octfile, basename):
        # analysis of octfile results based on the G173 architecture.
        # usable for \objects\monopanel_G173_ht_1.0.rad
        # top view. centered at z = 10 y = -.1 to 1.5 in 10 increments of .15
       
        frontScan = {'xstart':0.15, 'ystart': -0.1,'zstart': 10,'xinc':0, 'yinc': 0.15,
                     'zinc':0, 'Nx': 1, 'Ny':10, 'Nz':1, 'orient':'0 0 -1' }
        rearScan = {'xstart':0.15, 'ystart': -0.1,'zstart': 0,'xinc':0, 'yinc': 0.15,
                     'zinc':0, 'Nx': 1, 'Ny':10, 'Nz':1, 'orient':'0 0 1' }  
        self.analysis(octfile, basename, frontScan, rearScan)
        
        
    def analysis(self, octfile, basename, frontscan, backscan, plotflag = False):
        # general analysis where linescan is passed in
        linepts = self.linePtsMakeDict(frontscan)
        frontDict = self.irrPlotNew(octfile,linepts,basename+'_Front',plotflag)        
      
        #bottom view. 
        linepts = self.linePtsMakeDict(backscan)
        backDict = self.irrPlotNew(octfile,linepts,basename+'_Back',plotflag)
        self.saveResults(frontDict, backDict,'irr_%s.csv'%(basename) )


if __name__ == "__main__":
    '''
    Example of how to run a Radiance routine for a simple bifacial system

    '''

    import easygui  # this is only required if you want a graphical directory picker  
    #testfolder = r'C:\Users\cdeline\Documents\Python Scripts\TestFolder'  #point to an empty directory or existing Radiance directory
    testfolder = easygui.diropenbox(msg = 'Select or create an empty directory for the Radiance tree',title='Browse for empty Radiance directory')
    demo = RadianceObj('simple_panel',testfolder)  # Create a RadianceObj 'object'
    demo.setGround(0.62) # input albedo number or material name like 'concrete'.  To see options, run this without any input.
    try:
        epwfile = demo.getEPW(37.5,-77.6) # pull TMY data for any global lat/lon
    except:
        pass
        
    metdata = demo.readEPW('EPWs\\USA_VA_Richmond.Intl.AP.724010_TMY.epw') # read in the weather data
    # Now we either choose a single time point, or use cumulativesky for the entire year. 
    fullYear = True
    if fullYear:
        demo.genCumSky(demo.epwfile) # entire year.
    else:
        demo.gendaylit(metdata,4020)  # Noon, June 17th
        
    # create a scene using panels in landscape at 10 deg tilt, 1.5m pitch. 0.2 m ground clearance
    sceneDict = {'tilt':10,'pitch':1.5,'height':0.2,'orientation':'landscape','azimuth':180}  
    scene = demo.makeScene('simple_panel',sceneDict, nMods = 20, nRows = 7) #makeScene creates a .rad file with 20 modules per row, 7 rows.
    octfile = demo.makeOct(demo.getfilelist())  # makeOct combines all of the ground, sky and object files into a .oct file.
    analysis = AnalysisObj(octfile, demo.basename)  # return an analysis object including the scan dimensions for back irradiance
    analysis.analysis(octfile, demo.basename, scene.frontscan, scene.backscan)  # compare the back vs front irradiance  
    print('Annual bifacial ratio: %0.3f - %0.3f' %(min(analysis.backRatio), np.mean(analysis.backRatio)) )

  

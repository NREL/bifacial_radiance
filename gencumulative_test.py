'''
Created on 7/5/2016 - based on G173_journal_height

@author: cdeline

gencumulative_test.py - attempt to develop some structure that enables gencumulativesky to be leveraged

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
        return 'error: '+err.strip()
    if data:
        return data


        
# start developing the class

class RadianceObj:
    '''
    RadianceObj:  top level class to work on radiance objects, keep track of filenames, 
    sky values, PV module configuration etc.
    
    bibliography examples: rgbeimage.py (Thomas Bleicher) and honeybee
    
    values:
        basename    : text to append to output files
        filelist    : list of Radiance files to create oconv
        nowstr      : current date/time string
        path        : working directory with Radiance materials and objects
        
    functions:
        __init__   : initialize the object
        _setPath    : change the working directory
        
    
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
        self.filelist = []         # list of files to include in the oconv
        now = datetime.datetime.now()
        self.nowstr = str(now.date())+'_'+str(now.hour)+str(now.minute)+str(now.second)
        
        ''' DEFAULTS '''
        #TODO:  check if any of these defaults are necessary
        self.material_path = "materials"      # directory of materials data. default 'materials'
        self.sky_path = 'skies'         # directory of sky data. default 'skies'
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
        
        self.returnMaterialFiles()  # load files in the /material/ directory

    def _setPath(self, path):
        '''
        setPath - move path and working directory
        '''
        self.path = path
        
        print('path = '+ path)
        try:
            os.chdir(self.path)
        except:
            print('Path doesnt exist: %s' % (path)) 

       
      
    
    def returnOctFiles(self):
        '''
        return files in the root directory with .oct extension
        
        Returns
        -------
        oct_files : list of .oct files
        
        '''
        oct_files = [f for f in os.listdir(self.path) if f.endswith('.oct')]
        self.oct_files = oct_files
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
        if material_path is not None:
            self.material_path = material_path

        material_files = [f for f in os.listdir(os.path.join(self.path,self.material_path)) if f.endswith('.rad')]
        self.material_files = material_files
        self.filelist = self.filelist + [os.path.join(self.material_path,f) for f in self.material_files]
        return material_files
        
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
        timeZone = metdata.location.timezone
        dni = metdata.dni[timeindex]
        dhi = metdata.dhi[timeindex]
         #" -L %s %s -g %s \n" %(dni/.0079, dhi/.0079, self.ground.ReflAvg) + \
        skyStr =   ("# start of sky definition for daylighting studies\n"  
            "# location name: " + str(locName) + " LAT: " + str(metdata.location.latitude) 
            +" LON: " + str(metdata.location.longitude) + "\n"
            "!gendaylit %s %s %s" %(month,day,hour) ) + \
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
            "\n%s ring groundplane\n" % (self.ground.ground_type) +\
            '0\n0\n8\n0 0 -.01\n0 0 1\n0 100'
         
        skyname = os.path.join(self.sky_path,"sky_%s.rad" %(self.basename))
            
        skyFile = open(skyname, 'w')
        skyFile.write(skyStr)
        skyFile.close()
        
        self.filelist = self.filelist + [skyname ]
        
        return skyname
        
    def genCumSky(self,epwfile, startdt = None, enddt = None):
        ''' genCumSky
        
        skydome using gencumsky.  note: gencumulativesky.exe is required to be installed,
        which is not a standard radiance distribution.
        TODO:  error checking and auto-install of gencumulativesky.exe    
        
        Parameters
        ------------
        epwfile             - filename of the .epw file to read in
        hour                - tuple start, end hour of day. default (0,24)
        startdatetime       - datetime.datetime(Y,M,D,H,M,S) object. Only M,D,H selected. default: (0,1,1,0)
        enddatetime         - datetime.datetime(Y,M,D,H,M,S) object. Only M,D,H selected. default: (12,31,24,0)
        
        Returns
        -------
        skyname - filename of the .rad file containing cumulativesky info
        '''
        if startdt is None:
            startdt = datetime.datetime(2001,1,1,0)
        if enddt is None:
            enddt = datetime.datetime(2001,12,31,23)
        
        lat = self.metdata.location.latitude
        lon = self.metdata.location.longitude
        timeZone = self.metdata.location.timezone
        '''
        cmd = "gencumulativesky +s1 -h 0 -a %s -o %s -m %s -E " %(lat, lon, float(timeZone)*15) +\
            "-time %s %s -date 6 17 6 17 %s > cumulative.cal" % (epwfile)     
        print cmd
        os.system(cmd)
        '''
        cmd = "gencumulativesky +s1 -h 0 -a %s -o %s -m %s -E " %(lat, lon, float(timeZone)*15) +\
            "-time %s %s -date %s %s %s %s %s" % (startdt.hour, enddt.hour+1, 
                                                  startdt.month, startdt.day, 
                                                  enddt.month, enddt.day,
                                                  epwfile) 

        with open("cumulative.cal","w") as f:
            err = _popen(cmd,None,f)
            if err is not None:
                print err

            
        
        skyStr = "#Cumulative Sky Definition\n" +\
            "void brightfunc skyfunc\n" + \
            "2 skybright " + "cumulative.cal" + "\n" + \
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
            "\n%s ring groundplane\n" % (self.ground.ground_type) +\
            "0\n0\n8\n0 0 -.01\n0 0 1\n0 100" 



        skyname = os.path.join(self.sky_path,"cumulativesky.rad" )
        
        skyFile = open(skyname, 'w')
        skyFile.write(skyStr)
        skyFile.close()
        
        self.filelist = self.filelist + [skyname]#, 'SunFile.rad' ]
        
        return skyname
        
        
        
    def makeOct(self,filelist=None,octname = None):
        ''' 
        combine everything together into a .oct file
        
        Parameters
        ------------
        filelist:  overload files to include.  otherwise takes self.filelist
        octname:   filename (without .oct extension)
        
        Returns
        -------
        octname:   filename of .oct file in root directory including extension
        
        '''
        if filelist is None:
            filelist = self.filelist
        if octname is None:
            octname = self.basename
            
        
        #os.system('oconv '+ ' '.join(filelist) + ' > %s.oct' % (octname))
        
        cmd = 'oconv '+ ' '.join(filelist)
        with open('%s.oct' % (octname),"w") as f:
            err = _popen(cmd,None,f)
            if err is not None:
                print err
        
        
        #use rvu to see if everything looks good. use cmd for this since it locks out the terminal.
        #'rvu -vf views\CUside.vp -e .01 monopanel_test.oct'
        print("created %s.oct" % (octname))
        self.octfile = '%s.oct' % (octname)
        return '%s.oct' % (octname)
        
    def analysis(self, octfile = None, basename = None):
        '''
        default to AnalysisObj.PVSCanalysis(self.octfile, self.basename)
        
        '''
        if octfile is None:
            octfile = self.octfile
        if basename is None:
            basename = self.basename
        
        analysis_obj = AnalysisObj(octfile, basename)
        analysis_obj.PVSCanalysis(octfile, basename)
         
        return analysis_obj
    
    def makeScene(self, moduletype=None, sceneDict=None):
        '''
        return a SceneObj
        '''
        if moduletype is None:
            print('makeScene(moduletype, sceneDict).  Available moduletypes: monopanel' )
            return
        self.scene = SceneObj(moduletype)
        
        if sceneDict is None:
            print('makeScene(moduletype, sceneDict).  sceneDict inputs: .tilt .height .pitch')

        if sceneDict.has_key('orientation') is False:
            sceneDict['orientation'] = 'portrait'
        self.sceneRAD = self.scene.makeScene10x3(sceneDict['tilt'],sceneDict['height'],sceneDict['pitch'],sceneDict['orientation'])
        self.filelist += [self.sceneRAD]
        
        return self.scene
        
class GroundObj:
    '''
    details for the ground surface and reflectance
    '''
       
    def __init__(self, material = None, material_file = None):
        '''
        sets and returns ground materials information.  if material type is known, pass it in to get
        reflectance info.  if material type isn't known, material_info.list is returned
        
        Parameters
        ------------
        material      - if known, the name of the material desired. e.g. 'litesoil'
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
        
        material_path = 'materials'

        if material_file is None:
            material_file = 'ground.rad'
        
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

        if material is not None:
            # if material isn't specified, return list of material options
            index = _findme(keys,material)[0]
            #calculate avg reflectance of the material and normalized color using NormRGB function
            self.normval = _normRGB(Rrefl[index],Grefl[index],Brefl[index])
            self.ReflAvg = (Rrefl[index]+Grefl[index]+Brefl[index])/3
            self.ground_type = keys[index]
            self.Rrefl = Rrefl[index]
            self.Grefl = Grefl[index]            
            self.Brefl = Brefl[index]

        else:
            print('ground material names to choose from:'+str(keys))
            return None
            
        '''
        #material names to choose from: litesoil, concrete, white_EPDM, beigeroof, beigeroof_lite, beigeroof_heavy, black, asphalt
        #NOTE! delete inter.amb and .oct file if you change materials !!!
        
        '''
class SceneObj:
    '''
    scene information including PV module type, bifaciality, array info
    pv module orientation defaults: portrait orientation
    pv module origin: z = 0 bottom of frame. y = 0 lower edge of frame. x = 0 vertical centerline of module
    
    scene includes module details (x,y,bifi,orientation)
    '''
    def __init__(self,moduletype=None):
        ''' initialize SceneObj
        '''
        if moduletype is None:
            moduletype = 'simple_panel'
        self.moduletype = moduletype
        
        if moduletype == 'monopanel' or 'simple_panel':
            self.x = 0.95  # width of module.
            self.y = 1.59 # height of module.
            self.bifi = 1  # bifaciality of the panel
            self.orientation = 'portrait' #default orientation of the scene
            self.modulefile = 'objects\\monopanel_1.rad'
        if moduletype == 'simple_panel':  #next module type
            radfile = 'objects\\simple_panel.rad'
            if not os.path.isfile(radfile):
                with open(radfile, 'wb') as f:
                    f.write('!genbox Color_I11 PVmodule 0.95 1.59 0.02 | xform -t -0.475 0 0 ')    
            self.modulefile = radfile
        else:
            print('incorrect panel type selection')
            return
            
    def makeScene10x3(self, tilt, height, pitch, orientation = None):
        '''
        arrange module defined in SceneObj into a 10 x 3 array
        
        TODO: include support for non-south azimuths
        
        '''
        if orientation is None:
            orientation = 'portrait'
        # assign inputs
        self.tilt = tilt
        self.height = height
        self.pitch = pitch
        self.orientation = orientation
        ''' INITIALIZE VARIABLES '''
        dtor = np.pi/180
        text = '!xform '

        if orientation == 'landscape':  # transform for landscape
            text += '-rz -90 -t %s %s 0 '%(-self.y/2, self.x/2)
            tempx = self.x; tempy = self.y
            self.x = tempy; self.y = tempx

        text += '-rx %s -t 0 0 %s ' %(tilt, height)
        # create 10-element array along x, 3 along y
        text += '-a 10 -t %s 0 0 -a 3 -t 0 %s 0 ' %(self.x+ 0.01, pitch)
        
        text += self.modulefile
        # save the .RAD file
        
        radfile = 'objects\\%s_%s_%s_10x3.rad'%(self.moduletype,height,pitch)
        with open(radfile, 'wb') as f:
            f.write(text)
        

        # define the 3-point front and back scan. if tilt < 45  else scan z
        if tilt < 45: #scan along y facing up/down.
            self.frontscan = {'xstart':(self.x )*4, 'ystart': pitch + 0.1*self.y * np.cos(tilt*dtor), 
                         'zstart': height + self.y *np.sin(tilt*dtor) + 1,
                         'xinc':0, 'yinc': 0.4* self.y * np.cos(tilt*dtor), 
                         'zinc':0 , 'Nx': 1, 'Ny':3, 'Nz':1, 'orient':'0 0 -1' }
            self.backscan = {'xstart':(self.x )*4, 'ystart': pitch + 0.1*self.y * np.cos(tilt*dtor), 
                         'zstart': 0,
                         'xinc':0, 'yinc': 0.4* self.y * np.cos(tilt*dtor), 
                         'zinc':0 , 'Nx': 1, 'Ny':3, 'Nz':1, 'orient':'0 0 1' }
        else: # scan along z
            self.frontscan = {'xstart':(self.x + 0.01)*4, 'ystart': pitch , 
                         'zstart': height + 0.1* self.y *np.sin(tilt*dtor),
                         'xinc':0, 'yinc': 0, 
                         'zinc':0.4* self.y * np.sin(tilt*dtor), 'Nx': 1, 'Ny':1, 'Nz':3, 'orient':'0 1 0' }
            self.backscan = {'xstart':(self.x + 0.01)*4, 'ystart': pitch + self.y * np.cos(tilt*dtor), 
                         'zstart': height + 0.1* self.y *np.sin(tilt*dtor),
                         'xinc':0, 'yinc':0, 
                         'zinc':0.4* self.y * np.sin(tilt*dtor), 'Nx': 1, 'Ny':3, 'Nz':1, 'orient':'0 -1 0' }
        
        self.gcr = self.y / pitch
        
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
 
class AnalysisObj:
    '''
    Analysis class for plotting and reporting
    '''
    def __init__(self, octfile, basename):
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
        
        print('saving scene in false color') 
        #TODO:  auto scale false color map
        cmd = "falsecolor -l W/m2 -m 1 -s 1100 -n 11" 
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
        # pulled from Hansen_PVSC_journal
        
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
            #write to echo, simpler than making a temp file. rtrace ambient values set for 'very accurate'
        #os.system("echo " + linepts + " | rtrace -i -ab 5 -aa .08 -ar 512 -ad 2048 -as 512 -h -oovs "+ octfile +
        #          " > results\irr_"+mytitle+".csv")
        print 'linescan in process: ' + mytitle
        cmd = "rtrace -i -ab 5 -aa .08 -ar 512 -ad 2048 -as 512 -h -oovs "+ octfile
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
            self.backRatio = [x/y for x,y in zip(reardata['Wm2'],data['Wm2'])]
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
    demo = RadianceObj('G173gencumsky_3.0m')  
    demo.setGround('litesoil')
    metdata = demo.readEPW(r'USA_CO_Boulder.724699_TMY2.epw')
    # sky data for index 4010 - 4028 (June 17)  
    #demo.gendaylit(metdata,4020)
    demo.genCumSky(r'USA_CO_Boulder.724699_TMY2.epw')
    octfile = demo.makeOct(demo.filelist + ['objects\\monopanel_G173_ht_3.0.rad'])
    analysis = AnalysisObj(octfile, demo.basename)
    analysis.G173analysis(octfile, demo.basename)
    
    demo2 = RadianceObj('G173gendaylit_3.0m')  
    demo2.setGround('litesoil')
    metdata = demo2.readEPW(r'USA_CO_Boulder.724699_TMY2.epw')
    # sky data for index 4010 - 4028 (June 17)  
    demo2.gendaylit(metdata,4020)
    #demo.genCumSky(r'USA_CO_Boulder.724699_TMY2.epw')
    octfile = demo2.makeOct(demo.filelist + ['objects\\monopanel_G173_ht_3.0.rad'])
    analysis2 = AnalysisObj(octfile, demo2.basename)
    analysis2.G173analysis(octfile, demo2.basename)

    pvscdemo = RadianceObj('PVSC_gencumsky')  
    pvscdemo.setGround('litesoil')
    epwfile = pvscdemo.getEPW(40,-105)
    metdata = pvscdemo.readEPW(epwfile)
    # sky data for index 4010 - 4028 (June 17)  
    #demo.gendaylit(metdata,4020)
    start = datetime.datetime(2000,6,17,12)
    end = datetime.datetime(2000,6,17,13)
    pvscdemo.genCumSky(r'USA_CO_Boulder.724699_TMY2.epw', start, end)
    octfile = pvscdemo.makeOct(pvscdemo.filelist + ['objects\\PVSC_4array.rad'])
    pvscdemo.analysis(octfile, pvscdemo.basename)

    pvscdemo = RadianceObj('PVSC_gendaylit')  
    pvscdemo.setGround('litesoil')
    metdata = pvscdemo.readEPW(r'USA_CO_Boulder.724699_TMY2.epw')
    # sky data for index 4010 - 4028 (June 17)  
    pvscdemo.gendaylit(metdata,4020)
    #pvscdemo.genCumSky(r'USA_CO_Boulder.724699_TMY2.epw',datetime.datetime(2000,6,17,0), datetime.datetime(2000,6,17,23))
    octfile = pvscdemo.makeOct(pvscdemo.filelist + ['objects\\PVSC_4array.rad'])
    analysis = pvscdemo.analysis(octfile, pvscdemo.basename)
    analysis.makeImage('PVSCfront.vp')
    '''
    demo = RadianceObj('simple_panel')  
    #TODO:   update setGround to handle arbitrary albedo values
    demo.setGround('greyroof') # 0.62 albedo - need to update ground.rad with this entry.
    #demo.getEPW(37.5,-77.6) #can't run this within NREL firewall.  BOO
    metdata = demo.readEPW('EPWs\\USA_VA_Richmond.Intl.AP.724010_TMY.epw')
    # sky data for index 4010 - 4028 (June 17)  
    #demo.gendaylit(metdata,4020)
    demo.genCumSky(demo.epwfile)
    # create a scene using monopanel in landscape at 10 deg tilt, 1.5m pitch
    sceneDict = {'tilt':10,'pitch':1.5,'height':0.2,'orientation':'landscape'}
    scene = demo.makeScene('simple_panel',sceneDict)
    octfile = demo.makeOct(demo.filelist)
    analysis = AnalysisObj(octfile, demo.basename)
    analysis.analysis(octfile, demo.basename, scene.frontscan, scene.backscan)    
    print('Annual bifacial ratio: %s - %s' %(min(analysis.backRatio), np.mean(analysis.backRatio)) )




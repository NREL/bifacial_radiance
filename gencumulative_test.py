'''
Created on 7/5/2016 - based on G173_journal_height

@author: cdeline
G173 radiance script - look at a single module above light soil background
G173 Heightv2: use Illum mode -L for gendaylit.  this matches much closer to broadband POA,  due to spectral cutoff.
G173 rowspacing: investigate multiple modules adjacent to the single one, then multiple sequential rows

gencumulative_test.py - attempt to develop some structure that enables gencumulativesky to be leveraged

'''
#start in pylab space to enable plotting
#get_ipython().magic(u'pylab')
import sys, os, datetime
import matplotlib.pyplot as plt  #already imported with above pylab magic
import numpy as np #already imported with above pylab magic
from IPython.display import Image

def _findme(lst, a): #find string match in a list. found this nifty script on stackexchange
    return [i for i, x in enumerate(lst) if x==a]


def _normRGB(r,g,b): #normalize by weight of each color for human vision sensitivity
    return r*0.216+g*0.7152+b*0.0722

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
        self.material_path = "materials"      # directory of materials data. default 'materials'
        self.sky_path = 'skies'         # directory of sky data. default 'skies'
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
        
        self.returnMaterialFiles()  # look for files in the /material/ directory

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

       
    def _linePtsMake3D(self,xstart,ystart,zstart,xinc,yinc,zinc,Nx,Ny,Nz,orient):
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
    def _irrPlotTime(self,octfile,linepts,mytitle,time,plotflag):
        #(xval,yval,zval,Wm2,mattype) = irrPlot(linepts,title,time,plotflag)
        #irradiance plotting, show absolute and relative irradiance front and backside for various configurations.
        #pass in the linepts structure of the view along with a title string for the plots
        #note that the plots appear in a blocking way unless you call pylab magic in the beginning.
        #add time of day
        #
        # pulled from HansenPVSC_journal
        
        #get current date
        #nowstr = str(datetime.datetime.now().date())
        
        if time is None:
            time = ""
        
        #write to line.pts or do it through echo.
        #use echo, simpler than making a temp file. rtrace ambient values set for 'very accurate'
        os.system("echo " + linepts + " | rtrace -i -ab 5 -aa .08 -ar 512 -ad 2048 -as 512 -h -oovs "+ octfile +
                  " > results\irr_"+mytitle+time+".csv")
    
        #response is in rgb irradiances. output in lux: 179*(.265*$4+.670*$5+.065*$6). Lux = 0.0079 W/m^2
        
        #try it for normal incidence view, see if it changes any.  No - as long as you're hitting the right objects. -oovs helps to identify what you're actually looking at.
        #note that the -av 25 25 25 parameter doesn't change the measured irradiance any.
        #normal incidence for 37 tilt is +/- 0.602Y 0.799Z.  Not really necessary, which is a good thing since this complicates things.
        #return_code = os.system("rtrace -i -ab 3 -aa .1 -ar 48 -ad 1536 -as 392 -af inter.amb -av 25 25 25 -h -oovs  MonoPanel.oct < data\line_normal.pts > results\irr_normal.csv")
        
        #f = open(direc_name + 'results\\irr.csv')
        
        #try to read in the .csv file and plot it!!!
        #read in data\irr.csv.  column list: x,y,z,R,G,B.  This isn't really working like I wanted to...
        #with open(direc_name + 'results\\irr.csv') as f:
        f = open('results/irr_'+mytitle+time+'.csv')   # or direc_name
        
    
        xval = []; yval = []; zval = [];RGB = [[]];lux = [];Wm2 = []
        mattype = []
        #line = f.readline()
        for line in f:
            temp = line.split('\t') #split by tab separtion
            xval.append(float(temp[0]))
            yval.append(float(temp[1]))
            zval.append(float(temp[2]))
            lux.append(179*(0.265*float(temp[3])+.670*float(temp[4])+.065*float(temp[5])))
            Wm2.append(0.0079*lux[lux.__len__()-1])
            mattype.append(temp[6])
        f.close()
        
        if plotflag == 1:
            plt.figure()
            plt.plot(Wm2)
            plt.ylabel('Wm2 irradiance')
            plt.xlabel('variable')
            plt.title(mytitle)
            plt.show()
    
        return(xval,yval,zval,Wm2,mattype)     
        
    
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
        
    def readEPW(self,epwfile):
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
        from pyepw.epw import EPW
        epw = EPW()
        epw.read(epwfile)
        
        self.metdata = MetObj(epw)
        
        return self.metdata
        
    def gendaylit(self, metdata, timeindex):
        '''
        sets and returns sky information using gendaylit.  if material type is known, pass it in to get
        reflectance info.  if material type isn't known, material_info.list is returned
        
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
        
        skyStr =   ("# start of sky definition for daylighting studies\n"  
            "# location name: " + str(locName) + " LAT: " + str(metdata.location.latitude) 
            +" LON: " + str(metdata.location.longitude) + "\n"
            "!gendaylit %s %s %s" %(month,day,hour) ) + \
            " -a %s -o %s" %(metdata.location.latitude, metdata.location.longitude) +\
            " -m %s" % (float(timeZone)*15) +\
            " -L %s %s -g %s\n" %(dni/.0079, dhi/.0079, self.ground.ReflAvg) + \
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
        
    def genCumSky(self,epwfile):
        ''' genCumSky
        
        skydome using gencumsky
        
        Usage: GenCumulativeSky [-d] [+s1|+s2] [-a latitude] [-o longitude] [-l] [-m sta
        ndard meridian] [-h hourshift] [-G|-B|-E] <climate file>
        (Note: longitude +ve East of Greenwich)
        
                -d      Ignore diffuse irradiance
                +s1     Use "smeared sun" approach (default)
                +s2     Use "binned sun" approach
                -l      Output luminance instead of radiance
                -r      Output radiance/179000 (ensures that units in the Radiance Image
         Viewer are in kWhm-2)
                -p      Output radiance/1000 (ensures that units in the Radiance RGB dat
        a file  are in kWhm-2)
                -G      File format is col1=global irradiance (W/m2), col2=diffuse irrad
        iance (W/m2)
                -B      File format is col1=direct horizontal irradiance (W/m2), col2=di
        ffuse irradiance (W/m2)
                -E      File format is an energyplus weather file (*.epw) The gprogram u
        ses the global irradiance (W/m2) and diffuse irradiance (W/m2) data columns.
                        In combination with '-E' the considered time interval can be spe
        cified:
                        -time <start time of day> <end time of day>
                        -date mm_start dd_start mm_end dd_end (if start-date after end-d
        ate then the winter interval is considered)
        
        Parameters
        ------------

        
        
        Returns
        -------


        '''
        lat = self.metdata.location.latitude
        lon = self.metdata.location.longitude
        timeZone = self.metdata.location.timezone
        
        cmd = "gencumulativesky +s2 -h -0.5 -a %s -o %s -m %s -E " %(lat, lon, float(timeZone)*15) +\
            "-time 12 14 -date 6 17 6 17 %s > cumulative.cal" % (epwfile) 
            
        print cmd
        os.system(cmd)
        
        #Generate the .cal file with the irradiance sky dome (lookup table)
        #os.system('gencumulativesky +s1 -a 38.5 -o 121.5 -m 120 -E -date 03 21 03 21 USA_CA_Sacramento.724835_TMY2.epw > cumulativesky_day.cal')
        
        
        skyStr = "#Cumulative Sky Definition\n" +\
            "\n%s ring groundplane\n" % (self.ground.ground_type) +\
            "0\n0\n8\n0 0 -.01\n0 0 1\n0 100" 
        '''
            "void brightfunc skyfunc\n" + \
            "2 skybright " + "cumulative.cal" + "\n" + \
            "0\n" + \
            "0\n" + \
            "skyfunc glow sky_glow\n" + \
            "0\n" + \
            "0\n" + \
            "4 1 1 1 0\n" + \
            "sky_glow source sky\n" + \
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
        '''
        skyname = os.path.join(self.sky_path,"cumulativesky.rad" )
        
        skyFile = open(skyname, 'w')
        skyFile.write(skyStr)
        skyFile.close()
        
        self.filelist = self.filelist + [skyname, 'SunFile.rad' ]
        
        return skyname
        
        ''' debugging
        
        here's what compiled:
            
            #Generate the .cal file with the irradiance sky dome (lookup table)
            os.system('gencumulativesky +s1 -a 38.5 -o 121.5 -m 120 -E -date 03 21 03 21 USA_CA_Sacramento.724835_TMY2.epw > cumulativesky_day.cal')
            
            f = open('skies\\cumulativesky.rad','w')
            #Write the cal file into the rad file
            f.write('void brightfunc skyfunc\n')
            f.write('2 skybright cumulativesky_day.cal\n')
            f.write('0\n')
            f.write('0')
            f.close()
            
            #Octree as before
            os.system('oconv materials\\ground.rad materials\\MonoPanel_mtl.rad skies\\cumulativesky.rad skies\\outside'+basename0+'.rad objects\\monopanel_'+basename0+'.rad > monopanel_'+basename+'.oct')
            
                        
                    
        ''' 
        
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
            
        
        os.system('oconv '+ ' '.join(filelist) + ' > %s.oct' % (octname))
        
        #use rvu to see if everything looks good. use cmd for this since it locks out the terminal.
        #'rvu -vf views\CUside.vp -e .01 monopanel_test.oct'
        print("created %s.oct" % (octname))
        self.octfile = '%s.oct' % (octname)
        return '%s.oct' % (octname)
        
    def analysis(self, octfile,basename):
        # analysis of octfile results based on the PVSC architecture.
        # todo for the future: maybe offload all of this stuff into a separate object?
        # PVSC front view. iterate x = 0.1 to 4 in 26 increments of 0.15. z = 0.9 to 2.25 in 9 increments of .15
        #linePtsMake3D(xstart,ystart,zstart,xinc,yinc,zinc,Nx,Ny,Nz,dir):
        #x = 3.2 - middle of east panel
        linepts = self._linePtsMake3D(3.2,-0.1,0.8,0,0,0.15,1,1,11,'0 1 0')
        
        plotflag = 0
        (xval,yval,zval,Wm2top,mattypetop) = self._irrPlotTime(octfile,linepts,basename+'_Front',None,plotflag)
        
    
        #back view. iterate x = 0.1 to 4 in 26 increments of 0.15. z = 0.9 to 2.25 in 9 increments of .15
        linepts = self._linePtsMake3D(3.2,3,0.8,0,0,.15,1,1,11,'0 -1 0')
        
        (xval,yval,zval,Wm2bottom,mattypebottom) = self._irrPlotTime(octfile,linepts,basename+'_Back',None,plotflag)
        
        
        # read results
        f = open('results/irr_'+basename+'_Front'+'.csv')   
        temp = f.read().splitlines()
        f.close()
        f = open('results/irr_'+basename+'_Back'+'.csv')  
        temp2 = f.read().splitlines()
        f.close()
        #open new file in write mode
        f = open('results/modified/irr_'+basename+'Front'+'.txt','w') 
        f2 = open('results/modified/irr_'+basename+'Back'+'.txt','w') 
        #tab separated header
        f.write('X\tY\tZ\tR\tG\tB\tObject\tLux\tWm^-2\tBack/FrontRatio\n')
        f2.write('X\tY\tZ\tR\tG\tB\tObject\tLux\tWm^-2\tBack/FrontRatio\n')
        #write each line in temp and append Lux, W/m2 and Fraction
        #Lux = 179*(0.265*R+0.67*G+0.065*B)
        #Wm2 = Lux *0.0079
        for j,newline in enumerate(temp):
            templine = newline.split('\t')
            temp2line = temp2[j].split('\t')
            Lux = 179*(0.265*float(templine[3])+0.67*float(templine[4])+0.065*float(templine[5]))
            Lux2 = 179*(0.265*float(temp2line[3])+0.67*float(temp2line[4])+0.065*float(temp2line[5]))
                       
            f.write(newline+str(Lux)+'\t'+str(Lux*0.0079)+'\t'+str(Lux2/Lux)+'\n')
            f2.write(temp2[j]+str(Lux2)+'\t'+str(Lux2*0.0079)+'\t'+str(Lux2/Lux)+'\n')
        f.close()
        f2.close()

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
    
    
if __name__ == "__main__":
    demo = RadianceObj('PVSC_gendaylit_EPDM')  
    demo.setGround('white_EPDM')
    metdata = demo.readEPW(r'USA_CO_Boulder.724699_TMY2.epw')
    # sky data for index 4010 - 4028 (June 17)  
    demo.gendaylit(metdata,4020)
    #demo.genCumSky(r'USA_CO_Boulder.724699_TMY2.epw')
    octfile = demo.makeOct(demo.filelist + ['objects\\PVSC_4array.rad'])
    demo.analysis(octfile, demo.basename)
    
    demo2 = RadianceObj('PVSC_gencumsky_EPDM')  
    demo2.setGround('white_EPDM')
    metdata = demo2.readEPW(r'USA_CO_Boulder.724699_TMY2.epw')
    # sky data for index 4010 - 4028 (June 17)  
    #demo.gendaylit(metdata,4020)
    demo2.genCumSky(r'USA_CO_Boulder.724699_TMY2.epw')
    octfile = demo2.makeOct(demo2.filelist + ['objects\\PVSC_4array.rad'])
    demo2.analysis(octfile, demo2.basename)
    







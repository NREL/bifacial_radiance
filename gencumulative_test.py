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

       
    def _linePtsMake(xstart,ystart,zstart,xend,yend,zend,Ns,dir):
        '''
        linePtsMake(xpos,ypos,zstart,zend,Nz,dir)
        create linepts text input with variable x,y,z.
        line.pts matrix subroutine is used for returning trace values from the scene
        '''
        xinc = float(xend-xstart)/(Ns-1) #x increment
        yinc = float(yend-ystart)/(Ns-1) #y increment
        zinc = float(zend-zstart)/(Ns-1) #z increment
        #now create our own matrix
        linepts = ""
        for index in range(0,Ns):
            xpos = xstart+index*xinc
            ypos = ystart+index*yinc
            zpos = zstart+index*zinc
            linepts = linepts + str(xpos) + ' ' + str(ypos) + ' '+str(zpos) + ' ' + dir + " \r"
        return(linepts)
    

    
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
        material_info = {}
        material_info['normval'] = ''
        material_info['ReflAvg'] = ''
        material_info['ground_type'] = ''
        
        if self.material_path is None:
            self.material_path = 'materials'
        if material_file is None:
            material_file = 'ground.rad'
        
        f = open(os.path.join(self.path,self.material_path,material_file)) 
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
        
        material_info['names'] = keys

        if material is not None:
            # if material isn't specified, return list of material options
            index = _findme(keys,material)[0]
            #calculate avg reflectance of the material and normalized color using NormRGB function
            material_info['normval'] = _normRGB(Rrefl[index],Grefl[index],Brefl[index])
            material_info['ReflAvg'] = (Rrefl[index]+Grefl[index]+Brefl[index])/3
            material_info['ground_type'] = keys[index]
            self.ground_type = keys[index]
            self.ground_reflAvg = material_info['ReflAvg']
        else:
            print('ground material names to choose from:'+str(keys))
            
        return material_info
        '''
        #material names to choose from: litesoil, concrete, white_EPDM, beigeroof, beigeroof_lite, beigeroof_heavy, black, asphalt
        #NOTE! delete inter.amb and .oct file if you change materials !!!
        
        '''
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
        import datetime
        epw = EPW()
        epw.read(epwfile)
        
        metdata = MetObj(epw)
        
        return metdata
        
    def setSky(self):
        '''
        sets and returns sky information.  if material type is known, pass it in to get
        reflectance info.  if material type isn't known, material_info.list is returned
        
        Parameters
        ------------
        
        
        
        Returns
        -------

        
        '''
        #G173 sky. based on SMARTS: 896.5 DNI, 100.13 DHI, 41.76 elevation . To match GHI = 697 and POA = 1000 drop to 38 degrees
        #os.system('gendaylit -ang 53 0 -W 1050 115 -g ' + str(ReflAvg) + ' > skies/' +basename0 +'sky.rad')
        #os.system('gendaylit -ang 53 0 -W 1095 90 -g ' + str(ReflAvg) + ' > skies/' +basename0 +'sky.rad')
        os.system('gendaylit -ang 41.76 0 -L ' + str(890/0.0079) + ' '+ str(99.3/0.0079) +' -g ' + str(ReflAvg) + ' > skies/' +basename +'sky.rad') #luminance = 900/0.0079 100/0.0079
        #note: -g option defines the ground reflectance (0:1). 0.2 default
        #note: gendaymtx is a time series of sky views. this may be useful later 
        #details on defining the sky and ground glow: http://www.radiance-online.org/pipermail/radiance-general/2003-October/001056.html
        #now the ground and sky definitions. create new outside .rad file based on outside_def.rad
        f = open('skies\\outside_def.rad')  #this file should be READ ONLY - it's a partial file that is appended to here
        temp = f.read()
        f.close()
        
        f = open('skies\\outside'+basename+'.rad','w')
        f.write(temp)
        f.write('\nskyfunc glow ground_glow\n0\n0\n4 '+ str(Rrefl[index]/normval) + ' ' + str(Grefl[index]/normval) + ' ' + str(Brefl[index]/normval) +' 0\n')
        f.write('\nground_glow source ground\n0\n0\n4 0 0 -1 180\n')
        f.write('\n'+keys[index] + ' ring groundplane\n0\n0\n8\n0 0 -.01\n0 0 1\n0 100')
        f.close()

''' Honeybee_generate climate based sky.py
        
def date2Hour(month, day, hour):
    # fix the end day
    numOfDays = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    # dd = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    JD = numOfDays[int(month)-1] + int(day)
    return (JD - 1) * 24 + hour

def getRadiationValues(epw_file, HOY):
    epwfile = open(epw_file,"r")
    for lineCount, line in enumerate(epwfile):
        if lineCount == int(HOY + 8 - 1):
            dirRad = (float(line.split(',')[14]))
            difRad = (float(line.split(',')[15]))
    return dirRad, difRad

def RADDaylightingSky(epwFileAddress, locName, lat, long, timeZone, hour, day, month,  north = 0):
    
    dirNrmRad, difHorRad = getRadiationValues(epwFileAddress, date2Hour(month, day, hour))
    
    print "Direct: " + `dirNrmRad` + "| Diffuse: " + `difHorRad`
    
    return  "# start of sky definition for daylighting studies\n" + \
            "# location name: " + locName + " LAT: " + lat + "\n" + \
            "!gendaylit " + `month` + ' ' + `day` + ' ' + `hour` + \
            " -a " + lat + " -o " + `-float(long)` + " -m " + `-float(timeZone) * 15` + \
            " -W " + `dirNrmRad` + " " + `difHorRad` + " -O " + `outputType` + \
            " | xform -rz " + str(north) + "\n" + \
            "skyfunc glow sky_mat\n" + \
            "0\n" + \
            "0\n" + \
            "4\n" + \
            "1 1 1 0\n" + \
            "sky_mat source sky\n" + \
            "0\n" + \
            "0\n" + \
            "4\n" + \
            "0 0 1 180\n" + \
            "skyfunc glow ground_glow\n" + \
            "0\n" + \
            "0\n" + \
            "4\n" + \
            "1 .8 .5 0\n" + \
            "ground_glow source ground\n" + \
            "0\n" + \
            "0\n" + \
            "4\n" + \
            "0 0 -1 180\n"
skyStr = RADDaylightingSky(weatherFile, newLocName, lat, lngt, timeZone, hour, day, month, math.degrees(northAngle))
    
skyFile = open(outputFile, 'w')
skyFile.write(skyStr)
skyFile.close()

return outputFile , `day` + "_" + `month` + "@" + ('%.2f'%hour).replace(".", "")
'''
''' honeybee_generate cumulative sky

    def cumSkystr(calFile):
        #from honeybee
        skyStr = "#Cumulative Sky Definition\n" + \
                 "void brightfunc skyfunc\n" + \
                 "2 skybright " + calFile + "\n" + \
                 "0\n" + \
                 "0\n" + \
                 "skyfunc glow sky_glow\n" + \
                 "0\n" + \
                 "0\n" + \
                 "4 1 1 1 0\n" + \
                 "sky_glow source sky\n" + \
                 "0\n" + \
                 "0\n" + \
                 "4 0 0 1 180\n"
        return skyStr
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
    demo = RadianceObj('test')  
    demo.setGround('litesoil')
    metdata = demo.readEPW(r'USA_CO_Boulder.724699_TMY2.epw')
    import pyplot
    pyplot.plot(metdata.datetime,metdata.ghi)
        
'''

# Now we're going to xform to define the CU Boulder scene. save it as monopanel_1.rad


f = open('objects\\monopanel_' +basename + '.rad','w')   # or direc_name

#CU boulder system - first row of modules - module is 1612mm x 974mm. monopanel_1 starts in portrait. 10 degree tilt. 
#14" (35.56cm) off the ground. 12" (30.5cm) inter-row spacing
#use the xform command.  first rotate 90 to get into landscape. then tilt 10. then translate +z = .3566. 
#then array 6x in x direction and 4x in y direction.
f.writelines('!xform -rz 90 -rx 10 -t 0 0 0.3556 -a 6 -t 1.62 0 0 -a 4 -t 0 1.279 0 objects\\monopanel_1.rad') #modules 14" from ground
#f.writelines('!xform -rz 90 -rx 10 -t 0 0 0.254 -a 6 -t 1.62 0 0 -a 4 -t 0 1.279 0 objects\\monopanel_1.rad') #module height 10" instead of 14"
f.close()


# In[ ]:

Image("images\\monopanel_CU_raw.PNG")


# image of the above:
# ![monopanel_CU](C:\Users\cdeline\Documents\!Work\Bifacial\Radiance\Scenes\MonoPanel\images\monopanel_CU_raw.PNG)
# Now define the sun condition and sky/ground

# In[14]:


#write out to a new .rad file for G173 sky and ground




# In[ ]:




# In[17]:

#G173 sky. based on SMARTS: 896.5 DNI, 100.13 DHI, 41.76 elevation . To match GHI = 697 and POA = 1000 drop to 38 degrees
#os.system('gendaylit -ang 53 0 -W 1050 115 -g ' + str(ReflAvg) + ' > skies/' +basename0 +'sky.rad')
#os.system('gendaylit -ang 53 0 -W 1095 90 -g ' + str(ReflAvg) + ' > skies/' +basename0 +'sky.rad')
os.system('gendaylit -ang 41.76 0 -L ' + str(890/0.0079) + ' '+ str(99.3/0.0079) +' -g ' + str(ReflAvg) + ' > skies/' +basename +'sky.rad') #luminance = 900/0.0079 100/0.0079
#note: -g option defines the ground reflectance (0:1). 0.2 default
#note: gendaymtx is a time series of sky views. this may be useful later 
#details on defining the sky and ground glow: http://www.radiance-online.org/pipermail/radiance-general/2003-October/001056.html
#now the ground and sky definitions. create new outside .rad file based on outside_def.rad
f = open('skies\\outside_def.rad')  #this file should be READ ONLY - it's a partial file that is appended to here
temp = f.read()
f.close()

f = open('skies\\outside'+basename+'.rad','w')
f.write(temp)
f.write('\nskyfunc glow ground_glow\n0\n0\n4 '+ str(Rrefl[index]/normval) + ' ' + str(Grefl[index]/normval) + ' ' + str(Brefl[index]/normval) +' 0\n')
f.write('\nground_glow source ground\n0\n0\n4 0 0 -1 180\n')
f.write('\n'+keys[index] + ' ring groundplane\n0\n0\n8\n0 0 -.01\n0 0 1\n0 100')
f.close()


# In[36]:

#now combine everything together into a .oct file

#os.system('oconv materials\\ground.rad materials\\MonoPanel_mtl.rad skies\\'+basename+'sky.rad skies\\outside'+basename+'.rad objects\\monopanel_'+basename+'.rad > monopanel_'+basename+'.oct')
os.system('oconv materials/ground.rad materials/MonoPanel_mtl.rad skies/'+basename+'sky.rad skies/outside'+basename+'.rad objects/monopanel_'+basename+'.rad > monopanel_'+basename+'.oct')
#use rvu to see if everything looks good. use cmd for this since it locks out the terminal.
#'rvu -vf views\CUside.vp -e .01 monopanel_test.oct'


# The next block shows some image generation.
# ![monopanel_CU](C:/Users/cdeline/Documents/!Work/Bifacial/Radiance/Scenes/MonoPanel/images/monopanel_CU_raw.PNG)

# ## Now do the same using _popenPipeCmd
# 

# In[10]:

from subprocess import Popen, PIPE
import shlex
import shutil

#def _popenPipeCmd(self, cmd, data_in, data_out=PIPE):
def _popenPipeCmd(cmd, data_in, data_out=PIPE):
    """pass <data_in> to process <cmd> and return results"""
    cmd = str(cmd) # get's rid of unicode oddities
    p = Popen(shlex.split(cmd), bufsize=-1, stdin=PIPE, stdout=data_out, stderr=PIPE)
    data, err = p.communicate(data_in)
    if err:
        raise Exception, err.strip()
    if data:
        return data


# In[91]:

#skies/tempsky.rad
cmd = 'gendaylit -ang 41.76 0 -L ' + str(890/0.0079) + ' '+ str(99.3/0.0079) +' -g ' + str(ReflAvg) 
sky0 = _popenPipeCmd(cmd, None)
#print sky0

#skies/outsidetemp.rad
f = open('skies\\outside_def.rad')  #this file should be READ ONLY - it's a partial file that is appended to here
sky1 = f.read()
f.close()
sky1=sky1+'\nskyfunc glow ground_glow\n0\n0\n4 '+ str(Rrefl[index]/normval) + ' ' + str(Grefl[index]/normval) + ' ' + str(Brefl[index]/normval) +' 0\n'
sky1 = sky1+'\nground_glow source ground\n0\n0\n4 0 0 -1 180\n'
sky1 = sky1+'\n'+keys[index] + ' ring groundplane\n0\n0\n8\n0 0 -.01\n0 0 1\n0 100'
print sky1


# In[97]:

cmd = "oconv materials/ground.rad materials/MonoPanel_mtl.rad skies/%ssky.rad objects/monopanel_%s.rad"%(basename,basename)
octfile = _popenPipeCmd(cmd, None, open('popen_test1.oct','w'))   


# In[74]:

#combine everything together into a .oct file from individual files
print 'oconv materials/ground.rad materials/MonoPanel_mtl.rad skies/'+basename+'sky.rad skies/outside'+basename+'.rad objects/monopanel_'+basename+'.rad > monopanel_'+basename+'.oct'
cmd = "oconv materials/ground.rad materials/MonoPanel_mtl.rad skies/%ssky.rad skies/outside%s.rad objects/monopanel_%s.rad"%(basename,basename,basename)
filelist = ['materials/ground.rad', 'materials/MonoPanel_mtl.rad', "skies/%ssky.rad"%(basename), "skies/outside%s.rad"%(basename), "objects/monopanel_%s.rad"%(basename)]
filelist.insert(0,'oconv')
cmd3 = ' '.join(filelist)


# In[78]:

#f = open('popen_test.oct','w')
octfile = _popenPipeCmd(cmd3, None, open('popen_test.oct','w'))                                                                   
#f.close()
#os.system('oconv materials\\ground.rad materials\\MonoPanel_mtl.rad skies\\'+basename+'sky.rad skies\\outside'+basename+'.rad objects\\monopanel_'+basename+'.rad > monopanel_'+basename+'.oct')


# 

# In[ ]:




# In[ ]:

print ReflAvg
Image("images/CUside.hdr")


# irrPlot subroutine - plot each frontside or backside view scan of irradiance. not quite updated here yet

# In[7]:

def irrPlot(linepts,mytitle,plotflag):
    #(xval,yval,zval,Wm2,mattype) = irrPlot(linepts,title,plotflag)
    #irradiance plotting, show absolute and relative irradiance front and backside for various configurations.
    #pass in the linepts structure of the view along with a title string for the plots
    #note that the plots appear in a blocking way unless you call pylab magic in the beginning.
    
    #get current date
    #now = datetime.datetime.now()
    #nowstr = str(now.date())+'_'+str(now.hour)+str(now.minute)+str(now.second)
    nowstr = str(datetime.datetime.now().date())
    #write to line.pts or do it through echo.
    #use echo, simpler than making a temp file. rtrace ambient values set for 'very accurate'. 
    os.system("echo " + linepts + " | rtrace -i -ab 5 -aa .08 -ar 512 -ad 2048 -as 512  -h -oovs               monopanel_"+basename+".oct  > results\irr_"+mytitle+nowstr+".csv")

    #response is in rgb irradiances. output in lux: 179*(.265*$4+.670*$5+.065*$6). Lux = 0.0079 W/m^2
    
    #try it for normal incidence view, see if it changes any.  No - as long as you're hitting the right objects. -oovs helps to identify what you're actually looking at.
    #note that the -av 25 25 25 parameter doesn't change the measured irradiance any.
    #normal incidence for 37 tilt is +/- 0.602Y 0.799Z.  Not really necessary, which is a good thing since this complicates things.
    #return_code = os.system("rtrace -i -ab 3 -aa .1 -ar 48 -ad 1536 -as 392 -af inter.amb -av 25 25 25 -h -oovs  MonoPanel.oct < data\line_normal.pts > results\irr_normal.csv")
    
    #f = open(direc_name + 'results\\irr.csv')
    
    #try to read in the .csv file and plot it!!!
    #read in data\irr.csv.  column list: x,y,z,R,G,B.  This isn't really working like I wanted to...
    #with open(direc_name + 'results\\irr.csv') as f:
    f = open('results/irr_'+mytitle+nowstr+'.csv')   # or direc_name
    

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
        figure()
        plot(Wm2)
        ylabel('Wm2 irradiance')
        xlabel('variable')
        title(mytitle)
        show()
    
    


    return(xval,yval,zval,Wm2,mattype)


# Make a line scan of top and bottom.  This creates a new filename every day you run it.

# In[7]:

for i2 in [1,3,5,9,17]:
    i = i2
    basename = basename0+'_'+str(i)

    xpos = 0.1+(i2-1)/2; 
    #linepts = linePtsMake(xpos,0,6,xpos,2,6,50,'0 0 -1') #top view looking down. rowspace and backrow option.
    linepts = linePtsMake(xpos,3.23,6,xpos,5.23,6,50,'0 0 -1') #top view looking down. front&back option
    plotflag = 0
    (xval,yval,zval,Wm2top,mattypetop) = irrPlot(linepts,basename+'top',plotflag)

    #linepts = linePtsMake(xpos,0,0.1,xpos,2,0.1,50,'0 0 1') #bottom view looking up. rowspace and backrow option.
    linepts = linePtsMake(xpos,3.23,0.1,xpos,5.23,0.1,50,'0 0 1') #bottom view looking up. front&back option
    (xval,yval,zval,Wm2bottom,mattypebottom) = irrPlot(linepts,basename+'bottom',plotflag)
    #get ratios of back vs front irradiance. only if material type is 'solar cell'
    backfrac = []; yplot = []; Wm2top_clean = []; Wm2bottom_clean = []
    for t,b,mat,y in zip(Wm2top,Wm2bottom,mattypetop,yval):
        if mat.find('PVmodule') > 0:
            backfrac.append(b/t)
            Wm2top_clean.append(t)
            Wm2bottom_clean.append(b)
            yplot.append(y)
    figure()
    plot(yplot,backfrac)
    ylabel('Backside vs frontside irradiance')
    xlabel('X distance (m)')
    title('Backside vs frontside irradiance, '+basename)

    figure()
    plot(yval,Wm2top)
    plot(yval,Wm2bottom)
    ylabel('Irradiance (W/m^2)')
    xlabel('X distance (m)')
    title('Frontside and backside irradiance, '+basename)
    show()


# In[8]:

#modify .csv files to append header, add total lux, W/m^2 and back/front ratio
#start with the header
nowstr = str(datetime.datetime.now().date())
for i2 in [1,3,5,9,17]:

    f = open("results\irr_"+basename0+'_'+str(i2)+'top'+nowstr+".csv") 
    temp = f.read().splitlines()
    f.close()
    f = open("results\irr_"+basename0+'_'+str(i2)+'bottom'+nowstr+".csv") 
    temp2 = f.read().splitlines()
    f.close()
    #open new file in write mode
    f = open('results/modified/irr_'+basename0+'_'+str(i2)+'top'+nowstr+'.txt','w')
    f2 = open('results/modified/irr_'+basename0+'_'+str(i2)+'bottom'+nowstr+'.txt','w')
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


'''




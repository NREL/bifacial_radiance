#!/usr/bin/env python
# coding: utf-8

# ## Separating Frontscan and Backscan for different number of Sensors

# The key ideas here are:
# 
# - Functions like moduleAnalysis() returns two identically structured dictionaries that contain the keys like xstart, ystart, zstart, xinc, yinc, zinc, Nx, Ny, Nz, orientation. For the function arguments like sensorsy or sensorsx, there is an assumption that those will be equal for both the front and back surface.
# 
# - We need to develop a separate function, pretty much functionally parallel with moduleAnalysis() to bring out the frontscan and backscan separately.....may be two distinct functions with distinct arguments for frontscan() and backscan()
# 
# - The new functions will have variables passed on as arguments which can be different for front and back

# In[1]:


import bifacial_radiance
import numpy as np
import os
from pathlib import Path

testfolder = str(Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP')


# In[2]:


demo = bifacial_radiance.RadianceObj('ScanSeparate', testfolder) 


# In[3]:


x = 2
y = 1
xgap = 0.02
ygap = 0.15
zgap = 0.10
numpanels = 1
offsetfromaxis = True
Ny = numpanels
axisofrotationTorqueTube = True
frameParams = None
omegaParams = None
diam = 0.1


# In[4]:


module_type = 'TEST'
nMods = 3
nRows = 2
sceneDict = {'tilt':0, 'pitch':6, 'clearance_height':3,'azimuth':90, 'nMods': nMods, 'nRows': nRows} 


# In[5]:


demo.setGround(0.2)
epwfile = demo.getEPW(lat = 37.5, lon = -77.6)
metdata = demo.readWeatherFile(epwfile, coerce_year = 2021)
demo.gendaylit(4020)


# In[6]:


demo.makeModule(name=module_type,x=x, y=y, torquetube = True, 
                    diameter = diam, xgap = xgap, ygap = ygap, zgap = zgap, 
                    numpanels = Ny, omegaParams=None,
                    axisofrotationTorqueTube=axisofrotationTorqueTube)


# In[7]:


scene = demo.makeScene(module_type,sceneDict)
octfile = demo.makeOct()
analysis = bifacial_radiance.AnalysisObj()  # return an analysis object including the scan dimensions for back irradiance


# In[9]:


name = 'ModuleScanTest'
rowWanted = 1
modWanted = 2
sensorsy = 2
sensorsx = 3


# In[10]:


sensors_diff = True
sensorsx_back = 3
sensorsy_back = 3


# In[12]:


frontscan, backscan = analysis.moduleAnalysis(scene, modWanted=None, rowWanted=None,
                       sensorsy=9.0, sensorsx=1.0, frontsurfaceoffset=0.001, backsurfaceoffset=0.001, 
                       modscanfront=None, modscanback=None, debug=False, sensors_diff = sensors_diff, 
                       sensorsy_back=sensorsy_back, sensorsx_back=sensorsx_back)


# In[13]:


frontscan


# In[14]:


backscan


# In[18]:


frontDict, backDict = analysis.analysis(octfile = octfile, name = name, frontscan = frontscan, backscan = backscan)


# In[19]:


frontDict


# In[20]:


backDict


# In[21]:


len(frontDict['Wm2'])


# In[22]:


len(backDict['Wm2'])


# In[ ]:


linepts = analysis._linePtsMakeDict(front_dict)


# In[ ]:


linepts


# In[ ]:


hpc = False
accuracy = 'low'
plotflag = None
frontDict = analysis._irrPlot(octfile, linepts, name+'_Front',
                                    plotflag=plotflag, accuracy=accuracy, hpc = hpc)


# In[ ]:


frontDict


# In[ ]:


#bottom view.
linepts = analysis._linePtsMakeDict(back_dict)
backDict = analysis._irrPlot(octfile, linepts, name+'_Back',
                                   plotflag=plotflag, accuracy=accuracy, hpc = hpc)


# In[ ]:


backDict


# In[ ]:


data = frontDict
data_sub = {key:data[key] for key in ['x', 'y', 'z', 'r', 'g', 'b', 'Wm2', 'mattype']}


# In[ ]:


data_sub


# In[ ]:


data_back = backDict


# In[ ]:


data_sub_back = {key:data_back[key] for key in ['x', 'y', 'z', 'r', 'g', 'b', 'Wm2', 'mattype']}


# In[ ]:


data_sub_back


# In[ ]:


frontDict


# In[ ]:


frontscan_test = analysis._irrPlot(octfile = octfile, linepts = linepts)


# In[ ]:


analysis._saveResults(frontscan_test)


# In[ ]:


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
        self.R = data['r']
        self.G = data['g']
        self.B = data['b']
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
            df.reindex(columns=['x','y','z','rearZ','mattype','rearMat',
                                'Wm2Front','Wm2Back','Back/FrontRatio',
                                'R','G','B', 'rearR','rearG','rearB'])
            df.to_csv(os.path.join("results", savefile), sep = ',',
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


# In[ ]:


def module_analysis(as is, sensormismatch = None):
    if sensormismatch is not None:
        do differently for front and back
        name_front, name_back
        # will need different inputs for sensorsy_front, sensorsx_front, sensorsy_back, sensorsX_back
        # This will create two different dictionaries for frontscan and backscan
    return frontscan, backscan #as dictionary

def analysis:
    if len(frontscan_[key] != len(backscan.keys()):
        linepts_front = 
        linepts_back = 
        frontDict = _irrPlot(linepts_front,...)
        backDict = _irrPlot(linepts_back,...)
        
        saveResults(data = frontDict, reardata = None, savefile = name_front)
        saveResults(data = backDict, reardata = None, savefile = name_back)
        
        


# In[ ]:





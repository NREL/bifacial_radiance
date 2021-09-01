#!/usr/bin/env python
# coding: utf-8

# ## Making Analysis Function for Row

# In[1]:


import bifacial_radiance


# In[5]:


import os
from pathlib import Path

testfolder = str(Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP')


# In[6]:


demo = bifacial_radiance.RadianceObj('SimRowScan', testfolder) 


# In[7]:


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


# In[8]:


module_type = 'TEST'
nMods = 5
nRows = 4
sceneDict = {'tilt':0, 'pitch':30, 'clearance_height':3,'azimuth':90, 'nMods': nMods, 'nRows': nRows} 


# In[9]:


demo.setGround(0.2)
epwfile = demo.getEPW(lat = 37.5, lon = -77.6)
metdata = demo.readWeatherFile(epwfile, coerce_year = 2021)
demo.gendaylit(4020)


# In[10]:


demo.makeModule(name=module_type,x=x, y=y, torquetube = True, 
                    diameter = diam, xgap = xgap, ygap = ygap, zgap = zgap, 
                    numpanels = Ny, frameParams=frameParams, omegaParams=omegaParams,
                    axisofrotationTorqueTube=axisofrotationTorqueTube)


# In[11]:


scene = demo.makeScene(module_type,sceneDict)
octfile = demo.makeOct()
analysis = bifacial_radiance.AnalysisObj()  # return an analysis object including the scan dimensions for back irradiance
#frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=1) # Gives us the dictionaries with coordinates


# In[12]:


rowWanted = 2
modWanted = 2
name = 'ScanTest'
sensorsy = 2
#frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=sensorsy, modWanted = modWanted, rowWanted = rowWanted)


# In[13]:


rowscan = analysis.analyzeRow(name = name, scene = scene, sensorsy = sensorsy, rowWanted = rowWanted, nMods = nMods, octfile = octfile)


# In[14]:


rowscan


# In[ ]:





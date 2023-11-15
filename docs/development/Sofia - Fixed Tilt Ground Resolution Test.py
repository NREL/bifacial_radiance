#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
from pathlib import Path

testfolder = str(Path().resolve().parent / 'TEMP' /  'sofia')

if not os.path.exists(testfolder):
    os.makedirs(testfolder)
    
print ("Your simulation will be stored in %s" % testfolder)


# In[2]:


import bifacial_radiance as br
import numpy as np
import pandas as pd


# In[3]:


# This information helps with debugging and getting support :)
import sys, platform
print("Working on a ", platform.system(), platform.release())
print("Python version ", sys.version)
print("Pandas version ", pd.__version__)
print("bifacial_radiance version ", br.__version__)


# In[4]:


simulationname = 'tutorial_1'

# Location:
lat = 39.7407 # ° N, 
lon = -105.1686 # ° W


# Scene Parameters:
azimuth_ang=90 # Facing south
tilt = 30 # tilt.

# MakeModule Parameters
moduletype='test-module'
numpanels = 1  # AgriPV site has 3 modules along the y direction
module_x = 2 # m
module_y = 1 # m. slope we will measure
sensorsy=2
sensorsground=5

# SceneDict Parameters
pitch = 6 # m
albedo = 0.2  #'grass'     # ground albedo
clearance_height = 0.5 # m  
nMods = 4 # six modules per row.
nRows = 3  # 3 row


# In[5]:


demo = br.RadianceObj(simulationname,path = testfolder)  
demo.setGround(albedo) 
epwfile = demo.getEPW(lat, lon) # NJ lat/lon 40.0583° N, 74.4057


# In[6]:


module=demo.makeModule(name=moduletype,x=module_x,y=module_y)


# In[7]:


#Valid options: mm_dd, mm_dd_HH, mm_dd_HHMM, YYYY-mm-dd_HHMM
metdata = demo.readWeatherFile(epwfile, coerce_year=2021, starttime='2021-06-01', endtime='2021-06-30')


# In[12]:


demo.genCumSky()  
#demo.gendaylit(timeindex=0)  


# In[13]:


sceneDict = {'tilt':tilt,'pitch': pitch,'clearance_height':clearance_height,'azimuth':azimuth_ang, 
             'nMods': nMods, 'nRows': nRows}  
scene = demo.makeScene(module=moduletype, sceneDict=sceneDict) 


# In[14]:


octfile = demo.makeOct()


# If desired, you can view the Oct file at this point:
# 
# ***rvu -vf views\front.vp -e .01 tutorial_1.oct***

# In[15]:


analysis = br.AnalysisObj(octfile, demo.name)  
frontscan, backscan, groundscan = analysis.moduleAnalysis(scene, sensorsy=sensorsy, sensorsground=sensorsground)


# In[16]:


analysis.analysis(octfile, simulationname+"_groundscan_East", groundscan, backscan)  # compare the back vs front irradiance  


# In[ ]:


# Loop for sensorsground and see resolution effect 


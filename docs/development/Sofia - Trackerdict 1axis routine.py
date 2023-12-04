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
lat = 40.0583  # NJ
lon = -74.4057  # NJ

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


#Valid options: mm_dd, mm_dd_HH, mm_dd_HHMM, YYYY-mm-dd_HHMM
metdata = demo.readWeatherFile(epwfile, coerce_year=2021, starttime='2021-06-01', endtime='2021-06-30_23')


# Couple measurements:
# * hub_height = 1.5 m
# * pitch = 5.7 m
# * modules are in 1-up portrait
# * Field size is 10 rows x 20 modules
# * Module are 2x1 m
# * Pyranometers start 16in off east-way from the center of row 7, module 14
#     
# Suggestions:
# * Do an hourly simulation. To calculate the tracker angle, look at the function and documentation of [`getSingleTimestampTrackerAngle`](https://bifacial-radiance.readthedocs.io/en/latest/generated/bifacial_radiance.RadianceObj.getSingleTimestampTrackerAngle.html#bifacial_radiance.RadianceObj.getSingleTimestampTrackerAngle)
# 

# In[7]:


# -- establish tracking angles
hub_height = 1.5 # m
pitch = 5.7 # m
sazm = 180  # Tracker axis azimuth
fixed_tilt_angle = None
gcr = 2 / pitch
cumulativesky = True

trackerParams = {'limit_angle':50,
             'angledelta':30, # 
             'backtrack':True,
             'gcr':gcr,
             'cumulativesky':cumulativesky,
             'azimuth': sazm,
             'fixed_tilt_angle': fixed_tilt_angle
             }


# In[17]:


trackerdict = demo.set1axis(**trackerParams)


# In[18]:


if cumulativesky:
    demo.genCumSky1axis()
else:
    demo.gendaylit1axis()


# In[19]:


sceneDict = {'pitch':pitch, 
             'hub_height': hub_height,
             'nMods': 5,
             'nRows': 2,
             'tilt': fixed_tilt_angle,  
             'sazm': sazm
             }


# In[20]:


trackerdict = demo.makeScene1axis(module=moduletype,sceneDict=sceneDict)
trackerdict = demo.makeOct1axis()


# In[21]:


demo.trackerdict.keys()


# In[23]:


trackerdict = demo.analysis1axis(customname = 'Module',
                                   sensorsy=2, modWanted=2,
                                   rowWanted=1) #sensorsground=2)


# In[ ]:


600


# In[ ]:


## Loop for sensrosground = 1, 2, 3, 5, 10, 20, 30,50,100,150,200,250,300, 400, 500



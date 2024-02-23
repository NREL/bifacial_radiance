#!/usr/bin/env python
# coding: utf-8

# # A1
# * GCR = 0.25
# * Albedo = 0.2
# * Hub Height = 1.5
# * Configuration = 1-Up portrait
# * Ground surface = Horizontal
# ***
# * For a GCR of 0.25 the pitch is 9.536m
# * 1-up Portrait: 5 rows, each with 25 modules
# * Torque tube diameter = 15 cm. (round)
# * Maximum tracker rotation angle = 55 deg
# * Backtracking is enabled
# * Location: Albuquerque, New Mexico USA (35.05°, -106.54°)

# In[1]:


import os
from pathlib import Path

testfolder = 'Scenarios/A1'

if not os.path.exists(testfolder):
    os.makedirs(testfolder)
    
print ("Your simulation will be stored in %s" % testfolder)


# In[2]:


import bifacial_radiance as br
import bifacialvf as bf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys, platform
import csv


# In[3]:


print("Working on a ", platform.system(), platform.release())
print("Python version ", sys.version)
print("Pandas version ", pd.__version__)
print("bifacial_radiance version ", br.__version__)
print("pyplot ", plt.matplotlib.__version__)
print("bifacialvf version ", bf.__version__)


# In[11]:


simulationname = 'A1'

# Location Albuquerque, New Mexico, USA
lat = 35.05
lon = -106.54

# Scene Parameters
azimuth=90
tilt=30

# MakeModule Parameters
moduletype='PVmod'
numpanels=1
module_x = 1.303 # m
module_y = 2.384 # m. slope we will measure
sensorsy=2
torquetube_diam = 0.15

zgap = 0.02 # m
xgap = 0.002 # m

# SceneDict Parameters
pitch = 9.536 # m
albedo = 0.2
hub_height = 1.5 # m  
nMods = 25 
nRows = 5

sceneDict = {'pitch':pitch,'albedo': albedo,'hub_height':hub_height,'azimuth':azimuth, 'nMods': nMods, 'nRows': nRows} 


# In[6]:


demo = br.RadianceObj(simulationname,path = testfolder)
demo.setGround(albedo)


# In[7]:


cumulativesky = False
trackerParams = {
    'limit_angle': 55,
    'backtrack': True,
    'gcr': 0.25,
    'azimuth': 180,  # axis angle, N-S = 180
    'cumulativesky': cumulativesky
}


# In[8]:


module=demo.makeModule(name=moduletype,x=module_x,y=module_y, xgap=xgap, zgap=zgap)


# In[12]:


module.addTorquetube(diameter=torquetube_diam, tubetype='Round', material='Metal_Grey', 
                     axisofrotation=True, visible=True, recompile=True)


# In[13]:


file = 'Phase2_meteo_hourly_psm3format.csv'
directory = os.path.expanduser('Documents/IEA-Bifacial-Tracking-Modeling')
weatherfile = os.path.join(directory, file)

metdata = demo.readWeatherFile(weatherfile, source='sam', starttime='2022-01-01_1000', endtime='2022-01-01_1200')


# In[ ]:


trackerdict = demo.set1axis(**trackerParams)


# In[ ]:


if cumulativesky:
    demo.genCumSky1axis()
else:
    demo.gendaylit1axis()


# In[ ]:


trackerdict = demo.makeScene1axis(module=module, sceneDict=sceneDict)
trackerdict = demo.makeOct1axis()


# In[ ]:


trakerdict = demo.analysis1axis(sensorsy=2)


# In[ ]:


trakerdict = demo.analysis1axis(sensorsy=2, modWanted = 1)


# In[ ]:


trakerdict = demo.analysis1axis(sensorsy=2, modWanted = 25)


# In[ ]:


trakerdict


# In[ ]:


demo


# In[ ]:


demo.calculateResults()


# In[ ]:


demo.CompiledResults
# Grear_mean and Gfront_mean values to be recorded in the excel


# In[ ]:





#!/usr/bin/env python
# coding: utf-8

# ## Sensor Position Sanity Check
# 
# Extreme case test: 90 degree.

# <a id='step1'></a>

# In[1]:


import bifacial_radiance
import numpy as np
import os # this operative system to do teh relative-path testfolder for this example.
import pprint    # We will be pretty-printing the trackerdictionary throughout to show its structure.


# In[2]:


testfolder = os.path.abspath(r'..\..\bifacial_radiance\TEMP')
albedo = "litesoil"      # this is one of the options on ground.rad
lat = 37.5   
lon = -77.6

# Scene variables
nMods = 1
nRows = 1
hub_height = 2.3 # meters
gcr = 0.35

moduletype = 'SimpleModule'
x=1
y=2
sensorsy = 4 # to make it fast

timeindex = 4020


# In[21]:


simulationName = 'Flat-135'    
demo = bifacial_radiance.RadianceObj(simulationName, path = testfolder)
demo.setGround(albedo) 
epwfile = demo.getEPW(lat = lat, lon = lon) 
metdata = demo.readWeatherFile(weatherFile = epwfile)
demo.gendaylit(metdata,timeindex)  
mymodule = demo.makeModule(name=moduletype, x=0.001, y=y, z = 0.05)
sceneDict = {'gcr': gcr,'hub_height':hub_height, 'tilt': 60, 'azimuth': 180, 'nMods':nMods, 'nRows': nRows}  
scene = demo.makeScene(moduletype,sceneDict) 
octfile = demo.makeOct(demo.getfilelist())  
analysis = bifacial_radiance.AnalysisObj(octfile, demo.basename)
frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy = sensorsy, frontsurfaceoffset=0.5)
results = analysis.analysis(octfile, demo.basename, frontscan, backscan) 
bifacial_radiance.load.read1Result('results\irr_Flat-135.csv')


# In[19]:


simulationName = 'Flat-135'    
demo = bifacial_radiance.RadianceObj(simulationName, path = testfolder)
demo.setGround(albedo) 
epwfile = demo.getEPW(lat = lat, lon = lon) 
metdata = demo.readWeatherFile(weatherFile = epwfile)
demo.gendaylit(metdata,timeindex)  
mymodule = demo.makeModule(name=moduletype, x=0.001, y=y, z = 0.05)
sceneDict = {'gcr': gcr,'hub_height':hub_height, 'tilt': 60, 'azimuth': 180, 'nMods':nMods, 'nRows': nRows}  
scene = demo.makeScene(moduletype,sceneDict) 
octfile = demo.makeOct(demo.getfilelist())  
analysis = bifacial_radiance.AnalysisObj(octfile, demo.basename)
frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy = sensorsy)
results = analysis.analysis(octfile, demo.basename, frontscan, backscan) 
bifacial_radiance.load.read1Result('results\irr_Flat-135.csv')


# In[ ]:





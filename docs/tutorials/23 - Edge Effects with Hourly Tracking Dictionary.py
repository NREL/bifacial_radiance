#!/usr/bin/env python
# coding: utf-8

# <a id='step1'></a>

# # 23 - Edge Effects with Hourly Tracking Dictionary
# 
# The tracker dictionary is the internal structure of bifacial_radiance to keep track of the multiple Angles or Hours that it's simulating, the rad files, scene, oct files and analysis. Before release v0.4.3, while you could run analysis various times to model different modules in the field and it would save your CSV irradiances, it only kep track of ONE analysis object (the one that was generated last). Given our new performance module calculation functionality, this was updated so that now it keeps track of every module/row analyzed. See example below.
# 
# Here we model a central module and an edge module on the center row of an array, to evaluate edge effects.

# In[1]:


import os
from pathlib import Path

testfolder = str(Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP' / 'Tutorial_23')
if not os.path.exists(testfolder):
    os.makedirs(testfolder)
        
print ("Your simulation will be stored in %s" % testfolder)


# In[2]:


import bifacial_radiance
import numpy as np
import pprint   
import pandas as pd


# <a id='step2'></a>

# In[5]:


import bifacial_radiance
import os 

simulationName = 'Tutorial 23'
moduletype = 'test-module'    
albedo = 0.2    
lat = 37.5   
lon = -77.6

#makeModule parameters
modx=1
mody=2
xgap = 0.01
ygap = 0.0
zgap = 0.15
numpanels = 1

# Scene variables
nMods = 20
nRows = 7
hub_height = 1.5 # meters
pitch = 6 # meters  
gcr = mody/pitch

# Traking parameters
cumulativesky = False
limit_angle = 45 # degrees 
angledelta = 0.01 # 
backtrack = True 


torquetube = True
# the Tracker rotates around the panels
tubeParams = {'diameter':0.15,
              'tubetype':'round',
              'material':'black',
              'axisofrotation':False}

startdate = '11_06_11'     
enddate = '11_06_12'
demo = bifacial_radiance.RadianceObj(simulationName, path=testfolder)  
demo.setGround(albedo) 
epwfile = demo.getEPW(lat,lon) 
metdata = demo.readWeatherFile(epwfile, starttime=startdate, endtime=enddate)  
mymodule = bifacial_radiance.ModuleObj(name=moduletype, x=modx, y=mody, xgap=xgap, ygap=ygap,   
                zgap=zgap, numpanels=numpanels, tubeParams=tubeParams)
sceneDict = {'pitch':pitch,'hub_height':hub_height, 'nMods': nMods, 'nRows': nRows}  
demo.set1axis(limit_angle = limit_angle, backtrack = backtrack, gcr = gcr, cumulativesky = cumulativesky)
demo.gendaylit1axis()
demo.makeScene1axis(module=mymodule,sceneDict=sceneDict) #makeScene creates a .rad file with 20 modules per row, 7 rows.
demo.makeOct1axis()


# In[7]:


demo.trackerdict.keys()


# In[13]:


demo.analysis1axis(modWanted=[1, 10])


# In[17]:


demo.calculateResults()


# In[16]:


demo.CompiledResults


# In[ ]:





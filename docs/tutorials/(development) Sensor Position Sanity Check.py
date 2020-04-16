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


# <a id='step3'></a>

# In[3]:


simulationName = 'Vertical-SouthFacing'    
demo = bifacial_radiance.RadianceObj(simulationName, path = testfolder)
demo.setGround(albedo) 
epwfile = demo.getEPW(lat = lat, lon = lon) 
metdata = demo.readWeatherFile(weatherFile = epwfile)
demo.gendaylit(metdata,timeindex)  
mymodule = demo.makeModule(name=moduletype, x=x, y=y)
sceneDict = {'gcr': gcr,'hub_height':hub_height, 'tilt': 90, 'azimuth': 180, 'nMods':nMods, 'nRows': nRows}  
scene = demo.makeScene(moduletype,sceneDict)
octfile = demo.makeOct(demo.getfilelist())  
analysis = bifacial_radiance.AnalysisObj(octfile, demo.basename)
frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy = sensorsy)
results = analysis.analysis(octfile, demo.basename, frontscan, backscan) 
bifacial_radiance.load.read1Result('results\irr_Vertical-SouthFacing.csv')


# In[4]:


pprint.pprint(frontscan)
pprint.pprint(backscan)


# In[5]:


frontscan['ystart'] = -0.5


# In[6]:


results = analysis.analysis(octfile, demo.basename+'_hack_ystart', frontscan, backscan) 
bifacial_radiance.load.read1Result('results\irr_Vertical-SouthFacing_hack_ystart.csv')


# In[7]:


pprint.pprint(frontscan)
pprint.pprint(backscan)


# In[8]:


frontscan['orient'] = '-0.000 1.000 -0.000'


# In[9]:


results = analysis.analysis(octfile, demo.basename+'_hack_ystart_orient', frontscan, backscan) 


# In[11]:


bifacial_radiance.load.read1Result('results\irr_Vertical-SouthFacing_hack_ystart_orient.csv')


# SUCCESS! Hitting the right Side now (front scan only)!
# 
# ## Vertical East Facing

# In[12]:


simulationName = 'Vertical-EastFacing'    
demo = bifacial_radiance.RadianceObj(simulationName, path = testfolder) 
demo.setGround(albedo) 
epwfile = demo.getEPW(lat = lat, lon = lon) 
metdata = demo.readWeatherFile(weatherFile = epwfile)
demo.gendaylit(metdata,timeindex)  
mymodule = demo.makeModule(name=moduletype, x=x, y=y)
sceneDict = {'gcr': gcr,'hub_height':hub_height, 'tilt': 90, 'azimuth': 90, 'nMods':nMods, 'nRows': nRows}  
scene = demo.makeScene(moduletype,sceneDict)
octfile = demo.makeOct(demo.getfilelist())  
analysis = bifacial_radiance.AnalysisObj(octfile, demo.basename)
frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy = sensorsy)
results = analysis.analysis(octfile, demo.basename, frontscan, backscan) 
bifacial_radiance.load.read1Result('results\irr_Vertical-EastFacing.csv')


# In[13]:


pprint.pprint(frontscan)
pprint.pprint(backscan)


# In[14]:


frontscan['xstart'] = 0.5


# In[15]:


results = analysis.analysis(octfile, demo.basename+'_hack_xstart', frontscan, backscan) 
bifacial_radiance.load.read1Result('results\irr_Vertical-EastFacing_hack_xstart.csv')


# In[16]:


pprint.pprint(frontscan)
pprint.pprint(backscan)


# In[17]:


frontscan['orient'] = '-1.000 0.000 -0.000'


# In[18]:


results = analysis.analysis(octfile, demo.basename+'_hack_xstart_orient', frontscan, backscan) 
bifacial_radiance.load.read1Result('results\irr_Vertical-EastFacing_hack_xstart_orient.csv')


# #  Success! :D 
# 
# # 75 ? 

# In[21]:


simulationName = 'Vertical-EastFacing-75'    
demo = bifacial_radiance.RadianceObj(simulationName, path = testfolder) 
demo.setGround(albedo) 
epwfile = demo.getEPW(lat = lat, lon = lon) 
metdata = demo.readWeatherFile(weatherFile = epwfile)
demo.gendaylit(metdata,timeindex)  
mymodule = demo.makeModule(name=moduletype, x=x, y=y)
sceneDict = {'gcr': gcr,'hub_height':hub_height, 'tilt': 75, 'azimuth': 90, 'nMods':nMods, 'nRows': nRows}  
scene = demo.makeScene(moduletype,sceneDict)
octfile = demo.makeOct(demo.getfilelist())  
analysis = bifacial_radiance.AnalysisObj(octfile, demo.basename)
frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy = sensorsy)
results = analysis.analysis(octfile, demo.basename, frontscan, backscan) 
bifacial_radiance.load.read1Result('results\irr_Vertical-EastFacing.csv')


# ## =(

# In[30]:


simulationName = 'Flat-135'    
demo = bifacial_radiance.RadianceObj(simulationName, path = testfolder)
demo.setGround(albedo) 
epwfile = demo.getEPW(lat = lat, lon = lon) 
metdata = demo.readWeatherFile(weatherFile = epwfile)
demo.gendaylit(metdata,timeindex)  
mymodule = demo.makeModule(name=moduletype, x=0.001, y=y)
sceneDict = {'gcr': gcr,'hub_height':hub_height, 'tilt': 45, 'azimuth': 135, 'nMods':nMods, 'nRows': nRows}  
scene = demo.makeScene(moduletype,sceneDict)
octfile = demo.makeOct(demo.getfilelist())  
analysis = bifacial_radiance.AnalysisObj(octfile, demo.basename)
frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy = sensorsy)
results = analysis.analysis(octfile, demo.basename, frontscan, backscan) 
bifacial_radiance.load.read1Result('results\irr_Flat-135.csv')


# In[31]:


pprint.pprint(frontscan)
pprint.pprint(backscan)


# In[37]:


pprint.pprint(backscan)


# In[38]:


frontscan['orient']='-0.500 0.500 -0.707'
backscan['orient'] = '0.500 -0.500 0.707'


# In[39]:


results = analysis.analysis(octfile, demo.basename+'_hack_orient', frontscan, backscan) 
bifacial_radiance.load.read1Result('results\irr_Flat-135_hack_orient.csv')


# In[ ]:





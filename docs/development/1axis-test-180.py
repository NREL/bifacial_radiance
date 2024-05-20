#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
from pathlib import Path

testfolder = 'Simulations/1axis'

if not os.path.exists(testfolder):
    os.makedirs(testfolder)
    
print ("Your simulation will be stored in %s" % testfolder)


# In[2]:


import bifacial_radiance as br
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# In[3]:


# This information helps with debugging and getting support :)
import sys, platform
print("Working on a ", platform.system(), platform.release())
print("Python version ", sys.version)
print("Pandas version ", pd.__version__)
print("bifacial_radiance version ", br.__version__)
print("pyplot ", plt.matplotlib.__version__)


# In[4]:


simulationname = '1axis-groundscan'

# Location
lat = 39.7555
lon = -105.2211

# Scene Parameters
azimuth_ang=90 # Facing south
tilt=30

# MakeModule Parameters
moduletype='PVmod'
numpanels=1
module_x = 2 # m
module_y = 1 # m. slope we will measure
sensorsy=2
sensorsground=5

# SceneDict Parameters
pitch = 6 # m
albedo = 0.2
clearance_height = 0.5 # m  
nMods = 4 
nRows = 3

sceneDict = {'tilt':10,'pitch':3,'clearance_height':0.2,'azimuth':180, 'nMods': 20, 'nRows': 7} 


# In[5]:


demo = br.RadianceObj(simulationname,path = testfolder)
demo.setGround(albedo)
epwfile = demo.getEPW(lat, lon)


# In[6]:


module=demo.makeModule(name=moduletype,x=module_x,y=module_y)


# In[7]:


metdata = demo.readWeatherFile(epwfile, coerce_year=2021, starttime='2021-06-01', endtime='2021-06-30_23')


# In[8]:


hub_height = 1.5
pitch = 5.7
sazm = 180 # axis angle, N-S = 180
fixed_tilt_angle = None
gcr = 2 / pitch
cumulativesky = True

trakerParams = {
    'limit_angle': 50,
    'angledelta': 30,
    'backtrack': True,
    'gcr': gcr,
    'cumulativesky': cumulativesky,
    'azimuth': sazm,  # axis angle, N-S = 180
    'fixed_tilt_angle': fixed_tilt_angle
}


# In[9]:


trackerdict = demo.set1axis(**trakerParams)


# In[10]:


if cumulativesky:
    demo.genCumSky1axis()
else:
    demo.gendaylit1axis()


# In[11]:


sceneDict = {
    'pitch': pitch,
    'hub_height': hub_height,
    'nMods': 5,
    'nRows': 2
}


# In[12]:


trakerdict = demo.makeScene1axis(module=moduletype, sceneDict=sceneDict)
trakerdict = demo.makeOct1axis()


# In[13]:


sensorsgroundvalues = np.array([3, 5, 10, 20, 30, 100, 150, 200, 250, 300, 400, 500])
angles = np.array([-0.0, -30.0, -60.0, 30.0, 60.0])


# In[14]:


trakerdict = demo.analysis1axis(sensorsy=4)


# In[15]:


resultsdict = {}

for i, sensorsground in enumerate(sensorsgroundvalues):
    print("Doing sensor", i)
    print(f"sensorsground: {sensorsground}")
    trakerdict = demo.analysis1axisground(customname='_sensorsground_' + str(sensorsground), 
                                          sensorsground=sensorsground, append=False)
    angleswm2dict = {}
    
    for i, angle in enumerate(angles):
        wm2 = []
        for i, x in enumerate(trakerdict[angle]['AnalysisObj'][0].x):
             if x >= 1 and x <= pitch - 1:
                wm2.append(trakerdict[angle]['AnalysisObj'][0].Wm2Ground[i])
        resultsdict[(sensorsground)] = np.mean(wm2)


# In[16]:


trakerdict


# In[17]:


resultsdict


# In[18]:


df1 = pd.DataFrame({
    'groundscan': sensorsgroundvalues,
    'average': resultsdict.values()
})

df1.plot(x='groundscan', y='average', marker='o', color='blue')
plt.xticks(np.arange(0, 501, 50))
plt.title('Cummulative irradiance at different groundscan for 1-axis')
plt.show()


# In[ ]:





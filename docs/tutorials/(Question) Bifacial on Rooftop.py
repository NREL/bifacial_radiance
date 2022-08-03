#!/usr/bin/env python
# coding: utf-8

# # Bifacial on Rooftop

# <a id='step1'></a>

# In[2]:


import os
from pathlib import Path

testfolder = str(Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP' / 'AgriPV_Oregon_A')
if not os.path.exists(testfolder):
    os.makedirs(testfolder)
    
print ("Your simulation will be stored in %s" % testfolder)


# In[3]:


from bifacial_radiance import *   
import numpy as np
import datetime


# In[83]:


lat = 32.2540
lon = -110.9742
tilt = 0 # degrees
sazm = 180 # degrees (south)
numpanels = 1
albedo = 0.15  #' white rooftoop'     

# Three sites differences:
ch = 0.2032  # m -- 8 in

y = 1.65
x = 1
pitch=0.0001


# In[84]:


demo = RadianceObj('Oregon', path=testfolder)  # Create a RadianceObj 'object'
demo.setGround(albedo) # input albedo number or material name like 'concrete'.  To see options, run this without any input.
epwfile = demo.getEPW(lat, lon) # NJ lat/lon 40.0583° N, 74.4057
metdata = demo.readWeatherFile(epwfile, coerce_year=2021) # read in the EPW weather data from above
demo.genCumSky()


# ## 1. Loop over the different heights

# In[85]:


moduletype='PV-module'
module = demo.makeModule(name=moduletype, x=x, y=y, numpanels=numpanels)
sceneDict = {'tilt':tilt, 'pitch':pitch, 'clearance_height':ch, 'azimuth':sazm, 'nMods':1, 'nRows':1}  
scene = demo.makeScene(module=moduletype, sceneDict=sceneDict) #makeScene creates a .rad file with 20 modules per row, 7 rows.
octfile = demo.makeOct()  # makeOct combines all of the ground, sky and object fil|es into a .oct file.

# Sensor calculation
analysis = AnalysisObj(octfile, demo.name)  # return an analysis object including the scan dimensions for back irradiance
frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=[1, 160], sensorsx = [1, 100])
analysis.analysis(octfile, 'UL', frontscan = frontscan, backscan = backscan)  # compare the back vs front irradiance  


# ## 2. Plot Bifacial Gain Results

# ## 3. Plot Heatmaps of the Ground Irradiance

# #### First, here is a complicated way to find the maximum of all arrays so all heatmaps are referenced to that value

# In[86]:


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib


# In[87]:


font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 22}
matplotlib.rc('font', **font)

sns.set(rc={'figure.figsize':(5,5)})


# In[88]:


filepvf= os.path.join(testfolder,'results',f'irr_UL_Row1_Module1_Front.csv')
filepvb= os.path.join(testfolder,'results',f'irr_UL_Row1_Module1_Back.csv')
resultsDF = load.read1Result(filepvf)
resultsDB = load.read1Result(filepvb)

#Saved: results\irr_UL_Row1_Module1_Front.csv
#Saved: results\irr_UL_Row1_Module1_Back.csv


# In[89]:


print(np.round(resultsDB['Wm2Back'].mean()*100/resultsDF['Wm2Front'].mean(),1))


# In[90]:


np.zeros([8,4])


# In[91]:


df = resultsDB.copy()
df['x'] = df['x']*1000
df['x'] = df['x'].astype(int)+490
df['y'] = df['y']*1000
df['y'] = df['y'].astype(int)+814


# In[92]:


import numpy as np
matrix = np.zeros((df.x.max()+1, df.y.max()+1))
matrix[df.x, df.y] = df.Wm2Back


# In[93]:


import seaborn as sns
sns.heatmap(matrix)


#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
from pathlib import Path

testfolder = str(Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP' / 'Vertical')
if not os.path.exists(testfolder):
    os.makedirs(testfolder)
    
print ("Your simulation will be stored in %s" % testfolder)


# In[2]:


from bifacial_radiance import *   
import numpy as np
import datetime


# In[3]:


lat = 44.57615187732146
lon = -123.23914850912513
tilt = 90 # degrees
sazm = 90 # degrees
numpanels = 1
albedo = 0.7  #'grass'     # ground albedo

# Three sites differences:
ch = 0.25
pitch = 5

y = 2
x = 1

demo = RadianceObj('Oregon', path=testfolder)  # Create a RadianceObj 'object'
demo.setGround(albedo) # input albedo number or material name like 'concrete'.  To see options, run this without any input.
epwfile = demo.getEPW(lat, lon) # NJ lat/lon 40.0583° N, 74.4057
startdt = datetime.datetime(2021,5,1,11)
#enddt = datetime.datetime(2021,9,30,23)
metdata = demo.readWeatherFile(epwfile, starttime=startdt, endtime=startdt, coerce_year=2021) # read in the EPW weather data from above
demo.genCumSky()
module = demo.makeModule(name='test-mod', x=x, y=y)
sceneDict = {'tilt':tilt, 'pitch':pitch, 'clearance_height':ch, 'azimuth':sazm, 'nMods':1, 'nRows':1}  
scene = demo.makeScene(module=module, sceneDict=sceneDict) #makeScene creates a .rad file with 20 modules per row, 7 rows.
octfile = demo.makeOct()  # makeOct combines all of the ground, sky and object fil|es into a .oct file.
analysis = AnalysisObj(octfile, demo.name)  # return an analysis object including the scan dimensions for back irradiance
frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=[1, 1])
analysis.analysis(octfile, name='Test', frontscan=frontscan, backscan=backscan)  # compare the back vs front irradiance  


# In[9]:


sazm=180
sceneDict = {'tilt':tilt, 'pitch':pitch, 'clearance_height':ch, 'azimuth':sazm, 'nMods':1, 'nRows':1}  
scene = demo.makeScene(module=module, sceneDict=sceneDict) #makeScene creates a .rad file with 20 modules per row, 7 rows.
octfile = demo.makeOct()  # makeOct combines all of the ground, sky and object fil|es into a .oct file.
analysis = AnalysisObj(octfile, demo.name)  # return an analysis object including the scan dimensions for back irradiance
frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=[1, 1])
analysis.analysis(octfile, name='Test_180', frontscan=frontscan, backscan=backscan)  # compare the back vs front irradiance  


# # Trackerdict

# In[30]:


sazm = 180


# In[31]:


demo.set1axis(limit_angle = 60, backtrack = False, gcr=0.3, cumulativesky = False,
             fixed_tilt_angle=90, azimuth=sazm)


# In[32]:


demo.gendaylit1axis()


# In[37]:


sceneDict = {'tilt':tilt, 'pitch':pitch, 'clearance_height':ch, 'azimuth':sazm, 'nMods':10, 'nRows':10}  


# In[38]:


demo.makeScene1axis(module=module,sceneDict=sceneDict) #makeScene creates a .rad file with 20 modules per row, 7 rows.


# In[39]:


demo.makeOct1axis()


# In[40]:


demo.analysis1axis(customname='Test-1axis-90')


# ## 1. Loop over the different heights

# In[ ]:


for ii in range(0,3):
    y= ys[ii]
    ch = clearance_heights[ii]
    pitch = pitchs[ii]
    
    moduletype='PV-module'
    sceneDict = {'tilt':tilt, 'pitch':pitch, 'clearance_height':ch, 'azimuth':sazm, 'nMods':20, 'nRows':7}  
    #starttime = '01_13_11';  endtime = '01_13_12'
    scene = demo.makeScene(module=moduletype, sceneDict=sceneDict) #makeScene creates a .rad file with 20 modules per row, 7 rows.
    octfile = demo.makeOct()  # makeOct combines all of the ground, sky and object fil|es into a .oct file.
    # Sensor calculation
    spacingbetweensamples = 0.05  # one sensor every 5 cm
    sensorsy = round(pitch/spacingbetweensamples) -1 # one sensor every 5 cm

    analysis = AnalysisObj(octfile, demo.name)  # return an analysis object including the scan dimensions for back irradiance
    frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=[1, 9])
    groundscan = frontscan.copy()
    groundscan['zstart'] = 0.05  # setting it 5 cm from the ground.
    groundscan['zinc'] = 0   # no tilt necessary. 
    groundscan['yinc'] = spacingbetweensamples   # increasing spacing so it covers all distance between rows
    groundscan['Ny'] = sensorsy   # increasing spacing so it covers all distance between rows

    analysis.analysis(octfile, 'Site_'+str(ii)+'_Module_', frontscan, backscan)  # compare the back vs front irradiance  
    analysis.analysis(octfile, 'Site_'+str(ii)+'_Ground_', frontscan, groundscan)  # compare the back vs front irradiance  


# In[ ]:





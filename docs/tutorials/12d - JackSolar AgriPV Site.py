#!/usr/bin/env python
# coding: utf-8

# ## The Ground Modeling Challenge for AgriPV Application

# ### Solution Steps ###
# - Setup of variables
# - Generating the scenes
# - Mapping the ground irradiance

# **Given that this is a 1-HSAT Tracker Routine, the workflow we follow is:**
# 
#     - set1axis(gets angles)
#     - makeScene1axis
#     - gendaylit1axis
#     - makeoct1axis
#     - analysis1axis

# ## 1. Load Bifacial Radiance and other essential packages

# In[1]:


import bifacial_radiance
import numpy as np
import os # this operative system to do the relative-path testfolder for this example.
import pprint    # We will be pretty-printing the trackerdictionary throughout to show its structure.
from pathlib import Path


# ## 2. Define all the system variables

# In[2]:


testfolder = str(Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP')

timestamp = 4020 # Noon, June 17th.
simulationName = 'AgriPV_JS'    # Optionally adding a simulation name when defning RadianceObj

#Location
lat = 40.1217  # Given for the project site at Colorado
lon = -105.1310  # Given for the project site at Colorado

# MakeModule Parameters
moduletype='PrismSolar'
numpanels = 1  # This site have 1 module in Y-direction
x = 1  
y = 2
#xgap = 0.15 # Leaving 15 centimeters between modules on x direction
#ygap = 0.10 # Leaving 10 centimeters between modules on y direction
zgap = 0 # no gap to torquetube.
sensorsy = 6  # this will give 6 sensors per module in y-direction
sensorsx = 3   # this will give 3 sensors per module in x-direction

torquetube = True
axisofrotationTorqueTube = True 
diameter = 0.15  # 15 cm diameter for the torquetube
tubetype = 'square'    # Put the right keyword upon reading the document
material = 'black'   # Torque tube of this material (0% reflectivity)

# Scene variables
nMods = 20
nRows = 7
hub_height = 1.8 # meters
pitch = 5.1816 # meters      # Pitch is the known parameter 
albedo = 0.2  #'Grass'     # ground albedo

cumulativesky = False
limit_angle = 60 # tracker rotation limit angle
angledelta = 0.01 # we will be doing hourly simulation, we want the angle to be as close to real tracking as possible.
backtrack = True 


# # Method 1: Gendaylit1axis, Hourly (Cumulativesky = False)

# In[3]:


demo = bifacial_radiance.RadianceObj(simulationName,path = testfolder)  # Create a RadianceObj 'object'
demo.setGround(albedo) 
epwfile = demo.getEPW(lat, lon) 
metdata = demo.readEPW(epwfile, coerce_year = 2021)

moduleDict = demo.makeModule(name=moduletype, x = x, y =y, numpanels = numpanels, torquetube=torquetube, diameter=diameter, tubetype=tubetype, material=material, 
                zgap=zgap, axisofrotationTorqueTube=axisofrotationTorqueTube)
gcr = moduleDict['sceney']/pitch


# In[16]:


startdate = '21_06_17_11'
enddate = '21_06_17_12' # '%y_%m_%d_%H'
#enddate = '06/18' 

trackerdict = demo.set1axis(metdata = metdata, limit_angle = limit_angle, backtrack = backtrack, 
                            gcr = gcr, cumulativesky = cumulativesky) 

trackerdict = demo.gendaylit1axis(startdate = startdate, enddate = enddate)

sceneDict = {'pitch': pitch,'hub_height':hub_height, 'nMods':nMods, 'nRows': nRows}  

scene = demo.makeScene1axis(moduletype=moduletype,sceneDict=sceneDict)

sensorsx = 2
spacingsensorsx = (moduleDict['scenex']+0.1)/(sensorsx+1)
startxsensors = (moduleDict['scenex']+0.1)/2-spacingsensorsx

sensorsy = 4
for key in trackerdict.keys():
    demo.makeOct1axis(singleindex=key)

    for i in range (0, sensorsx):  
        modscanfront = {'zstart': 0, 'xstart':0, 'orient': '0 0 -1', 'zinc':0, 'xinc':pitch/(sensorsy-1),
                       'ystart': startxsensors-spacingsensorsx*i}

        results = demo.analysis1axis(singleindex=key, customname='_'+str(i)+'_', modscanfront = modscanfront, sensorsy = sensorsy)


# # METHOD 2: FIXED TILT

# In[39]:


idx=4020
rad_obj = bifacial_radiance.RadianceObj(simulationName,path = testfolder)  # Create a RadianceObj 'object'
rad_obj.setGround(albedo) 
metdata = rad_obj.readEPW(epwfile, coerce_year = 2021)
solpos = rad_obj.metdata.solpos.iloc[idx]
zen = float(solpos.zenith)
azm = float(solpos.azimuth) - 180
dni = rad_obj.metdata.dni[idx]
dhi = rad_obj.metdata.dhi[idx]
rad_obj.gendaylit2manual(dni, dhi, 90 - zen, azm)
tilt = round(rad_obj.getSingleTimestampTrackerAngle(rad_obj.metdata, idx, gcr, limit_angle=65),1)


# In[68]:


foo=rad_obj.metdata.datetime[idx]
res_name = "irr_Jacksolar_"+str(foo.year)+"_"+str(foo.month)+"_"+str(foo.day)+"_"+str(foo.hour)+"_"+str(foo.minute)
res_name


# In[45]:


sceneDict = {'pitch': pitch, 'tilt': tilt, 'azimuth': 90, 'hub_height':hub_height, 'nMods':nMods, 'nRows': nRows}  


# In[46]:


scene = demo.makeScene(moduletype=moduletype,sceneDict=sceneDict)


# In[69]:


octfile = demo.makeOct(octname=res_name)  


# In[64]:


sensorsx = 2
sensorsy = 4
spacingsensorsx = (x+0.01+0.10)/(sensorsx+1)
startxsensors = (x+0.01+0.10)/2-spacingsensorsx
xinc = pitch/(sensorsy-1)

analysis = bifacial_radiance.AnalysisObj()

frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=sensorsy)
    


# In[65]:


frontscan


# In[66]:


for senx in range(0,sensorsx):
    frontscan['zstart'] = 0
    frontscan['xstart'] = 0
    frontscan['orient'] = '0 0 -1'
    frontscan['zinc'] = 0
    frontscan['xinc'] = xinc
    frontscan['ystart'] = startxsensors-spacingsensorsx*senx
    frontdict, backdict = analysis.analysis(octfile = octfile, name = 'xloc_'+str(senx), 
                                            frontscan=frontscan, backscan=backscan)


# In[ ]:





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

# In[ ]:


import bifacial_radiance
import numpy as np
import os # this operative system to do the relative-path testfolder for this example.
import pprint    # We will be pretty-printing the trackerdictionary throughout to show its structure.
from pathlib import Path


# ## 2. Define all the system variables

# In[ ]:


testfolder = str(Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP')


timestamp = 4020 # Noon, June 17th.
simulationName = 'AgriPV_JS'    # Optionally adding a simulation name when defning RadianceObj

# Surface    
#albedo = " green grass", which is not one of the default choices in the material list

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
nMods = 30
nRows = 7
hub_height = 1.8 # meters
pitch = 5.1816 # meters      # Pitch is the known parameter 
albedo = 0.2  #'Grass'     # ground albedo

#azimuth_ang=180 # Facing south 
#axis_azimuth should have a default value of 180

cumulativesky = False
limit_angle = 60 # tracker rotation limit angle
angledelta = 0.01 # we will be doing hourly simulation, we want the angle to be as close to real tracking as possible.
backtrack = True 


# ## 3. Create Radiance Object including Albedo and Weather

# In[ ]:


demo = bifacial_radiance.RadianceObj(simulationName,path = testfolder)  # Create a RadianceObj 'object'
demo.setGround(albedo) 
epwfile = demo.getEPW(lat, lon) 
metdata = demo.readEPW(epwfile, coerce_year = 2021)


# ## 4. Make Module

# In[ ]:


moduleDict = demo.makeModule(name=moduletype, x = x, y =y, numpanels = numpanels, torquetube=torquetube, diameter=diameter, tubetype=tubetype, material=material, 
                zgap=zgap, axisofrotationTorqueTube=axisofrotationTorqueTube)


# ## 5. Calculate GCR

# In[ ]:


# It's not really necessary for this irradiation simulation since we know the pitch
cw = 1  # Collector Width, CW = 1 as given
gcr = cw/pitch
print("GCR:",gcr)


# ## 6. Generate the Sky for the Tracking Angles

# In[ ]:


startdate = '06/17'     
enddate = '06/18' #In this case, we are looking to generate tracking scenarios for one day as opposed to a single hour

#trackerdict = demo.gendaylit1axis(startdate = startdate, enddate = enddate); doesn't work independently before using set1axis()

trackerdict = demo.set1axis(metdata = metdata, limit_angle = limit_angle, backtrack = backtrack, 
                            gcr = gcr, cumulativesky = cumulativesky) #in case we wanted trackerdict for the whole year


# In[ ]:


trackerdict = demo.gendaylit1axis(startdate = startdate, enddate = enddate)


# In[ ]:


#checking our trackdict

print ("\nTrimmed trackerdict by gendaylit1axis to start and enddate length: %s " % (len(trackerdict)))
print ("")
trackerkeys = sorted(trackerdict.keys())
print ("Option of hours are: ", trackerkeys)
print ("")
print ("Contents of trackerdict for sample hour:")
pprint.pprint(trackerdict[trackerkeys[7]])


# ## Make Scene1 Axis

# In[ ]:


# making the different scenes for the 1-axis tracking for the dates in trackerdict2.

sceneDict = {'pitch': pitch,'hub_height':hub_height, 'nMods':nMods, 'nRows': nRows}  


# In[ ]:


sceneDict


# ## Make the 1-axis Tracking Scene and Analyse Irradiance on Module

# In[ ]:


scene = demo.makeScene1axis(moduletype=moduletype,sceneDict=sceneDict)


# In[ ]:


# Wrong, because the scene is not defined yet

demo.makeOct1axis(singleindex='2021_06_17_12')


# In[ ]:


# define the modscanfront dictionary for simulating the ground surface scan instead of module scan
#xinc = pitch/(sensorsy-1)
modscanfront = {'zstart': 0, 'xstart':0, 'orient': '0 0 -1', 'zinc':0, 'xinc':pitch/(sensorsy-1)}


# In[ ]:


# do the analysis1axis

results = demo.analysis1axis(singleindex='2021_06_17_12', modscanfront = modscanfront, sensorsy = sensorsy)
print('\n\nHourly bifi gain: {:0.3}'.format(sum(demo.Wm2Back) / sum(demo.Wm2Front)))


# ## Now we shall simulate for all hours of the day 

# In[ ]:


#Code-looping for all hours of the day

for key in trackerdict.keys():
    demo.makeOct1axis(singleindex=key)
    results=demo.analysis1axis(singleindex=key, modscanfront = modscanfront, sensorsy = sensorsy)

print('Accumulated hourly bifi gain for the day: {:0.3}'.format(sum(demo.Wm2Back) / sum(demo.Wm2Front)))


# In[ ]:





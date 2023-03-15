#!/usr/bin/env python
# coding: utf-8

# # 19 - East & West Facing Sheds
# 
# This simulates a particular case where you have alternating rows facing east and west, in "E-W sheds". 
# 
# ![East West Sheds Example](../images_wiki/AdvancedJournals/EW_sheds.PNG)
# 
# 
# To simulate this, we will use the bases learned in Journal 7 of using multipe scene objects. One scene object will be all the "East facing modules", while the West facing modules will be the second scene object. We have to know some geometry to offset the modules, and that is calculated below:
# 
# ![East West Sheds Example](../images_wiki/AdvancedJournals/EW_sheds_Geometry.PNG)
# 

# In[1]:


import os
import numpy as np
import pandas as pd
from pathlib import Path
import bifacial_radiance


# In[2]:


bifacial_radiance.__version__


# In[3]:


testfolder = testfolder = str(Path().resolve().parent.parent / 'bifacial_radiance' / 'Tutorial_01')
if not os.path.exists(testfolder):
    os.makedirs(testfolder)

demo = bifacial_radiance.RadianceObj("tutorial_19", path = testfolder)  # Create a RadianceObj 'object'
demo.setGround(0.62)
epwfile = demo.getEPW(lat = 37.5, lon = -77.6)    
metdata = demo.readWeatherFile(epwfile, coerce_year=2001) 
timestamp = metdata.datetime.index(pd.to_datetime('2001-06-17 13:0:0 -5'))
demo.gendaylit(timestamp) 


# Define your shed characteristics. In this case it is a 4-up landscape setup:

# In[4]:


# For sanity check, we are creating the same module but with different names for each orientation.
numpanels=4 
ygap = 0.02 # m Spacing between modules on each shed.
y=1   # m. module size, one side
x=1.7 # m. module size, other side. for landscape, x > y
mymoduleEast = demo.makeModule(name='test-module_East',y=y,x=x, numpanels=numpanels, ygap=ygap)
mymoduleWest = demo.makeModule(name='test-module_West',y=y,x=x, numpanels=numpanels, ygap=ygap)


# Calculate the spacings so we can offset the West Facing modules properly:
# 
# ![East West Sheds Example](../images_wiki/AdvancedJournals/EW_sheds_Offset.PNG)
# 
# 

# In[5]:


tilt = 30
gap_between_EW_sheds = 1 # m
gap_between_shed_rows = 2 #m
CW = mymoduleEast.sceney
ground_underneat_shed = CW * np.cos(np.radians(tilt))
pitch = ground_underneat_shed*2 + gap_between_EW_sheds + gap_between_shed_rows
offset_westshed = -(ground_underneat_shed+gap_between_EW_sheds)


# Define the other characteristics of our array:

# In[6]:


clearance_height = 1.2 # m
nMods = 21
nRows = 7


# Create the Scene Objects and the Scene:

# In[7]:


sceneDict = {'tilt':tilt,'pitch':pitch,'clearance_height':clearance_height,'azimuth':90, 'nMods': nMods, 'nRows': nRows, 
             'appendRadfile':True} 
sceneObj1 = demo.makeScene(mymoduleEast, sceneDict)  

sceneDict2 = {'tilt':tilt,'pitch':pitch,'clearance_height':clearance_height,'azimuth':270, 'nMods': nMods, 'nRows': nRows, 
              'originx': offset_westshed, 'originy': 0, 
              'appendRadfile':True} 

sceneObj2 = demo.makeScene(mymoduleWest, sceneDict2)  


# Finally get all the files together by creating the Octfile:

# In[8]:


octfile = demo.makeOct(demo.getfilelist()) 


# ## View the Geometry
# 
# You can check the geometry on rvu with the following commands. You can run it in jupyter/Python if you comment the line, but the program will not continue processing until you close the rvu window. ( if running rvu directly on the console, navigate to the folder where you have the simulation, and don't use the exclamation point at the beginning)
# 
# Top view:

# In[9]:


#!rvu -vf views\front.vp -e .01 -pe 0.3 -vp 1 -45 40 -vd 0 0.7 -0.7 MultipleObj.oct


# another view, close up:

# In[10]:


# !rvu -vf views\front.vp -e .01 -pe 0.3 -vp -4 -29 3.5 -vd 0 1 0 MultipleObj.oct


# ## Analysis
# 
# We have to analyze the East and the West shed independently. 

# In[11]:


sensorsy=4  # 1 per module. consider increasing the number but be careful with sensors in the space between modules.
analysis = bifacial_radiance.AnalysisObj(octfile, demo.basename)  
frontscan, backscan = analysis.moduleAnalysis(sceneObj1, sensorsy=sensorsy)
frontdict, backdict = analysis.analysis(octfile, "EastFacingShed", frontscan, backscan)  # compare the back vs front irradiance  

frontscan, backscan = analysis.moduleAnalysis(sceneObj2, sensorsy=sensorsy )
frontdict2, backdict2 = analysis.analysis(octfile, "WestFacingShed", frontscan, backscan)  # compare the back vs front irradiance  


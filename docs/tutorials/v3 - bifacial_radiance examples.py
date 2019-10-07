#!/usr/bin/env python
# coding: utf-8

# # Simple Fixed-Tilt Example
# 
# ### Set a Folder 
# 
# First let's set the folder where the simulation will be saved. By default, this is the TEMP folder in the bifacial_radiance distribution.
# 
# The lines below find the location of the folder relative to this Jupyter Journal.
# 

# In[1]:


import os
testfolder = os.path.abspath(r'..\..\bifacial_radiance\TEMP')  

# You can alternatively point to an empty directory (it will open a load GUI Visual Interface)
# or specify any other directory in your computer. I.E.:
# testfolder = r'C:\Users\sayala\Documents\RadianceScenes\Demo'

print ("Your simulation will be stored in %s" % testfolder)


# In[2]:


try:
    from bifacial_radiance import *
except ImportError:
    raise RuntimeError('bifacial_radiance is required. download distribution')

import numpy as np


# ### Create a Radiance Object, Set the Albedo and Generate the Sky

# In[3]:


# Simple example system using Radiance.  We'll simulate a 1-up landscape system over a white rooftop
demo = RadianceObj('bifacial_example',testfolder)  # Create a RadianceObj 'object' named bifacial_example. no whitespace allowed

demo.setGround(0.62) # input albedo number or material name like 'concrete'.  
# To see options, run this without any input.

# Pull in meteorological data using pyEPW for any global lat/lon
epwfile = demo.getEPW(lat = 37.5, lon = -77.6) 

# Read in the weather data pulled in above. 
# If you want a different location, replace this filename with the new EPW file name in `epwfile`.    
metdata = demo.readEPW('EPWs\\USA_VA_Richmond.Intl.AP.724010_TMY.epw') 

# Solar resource definition.  Either choose a single time point with gendaylit, or use cumulativesky 
# for the entire year. 
fullYear = True
if fullYear:
    demo.genCumSky(demo.epwfile) # entire year.
else:
    demo.gendaylit(metdata,4020)  # Noon, June 17th (timepoint # 4020)


# ### DEFINE a Module type
# 
# You can create a custom PV module type. In this case we are defining a module named "Prism Solar Bi60", in landscape. The x value defines the size of the module along the row, so for landscape modules x > y. y = 0.984 x = 1.695. Bifaciality = 0.90
# 
# ###### Note:
# Modules are currently 100% opaque. For drawing each cell, makeModule needs more inputs with cellLevelModule = True. You can also specify a lot more variables in makeModule like multiple modules, torque tubes, spacing between modules, etc, so read the function definition.

# In[4]:



module_type = 'Prism Solar Bi60 landscape' 
demo.makeModule(name=module_type,x=1.695, y=0.984, bifi = 0.90)

# print available module types in data/module.json
print("\n\n AVAILABLE MODULES:")
availableModules = demo.printModules()


# ### MAKE the Scene:
# Create a scene uses the module created above and replicates it by the number of modules and number of rows specified in the scene Dictionary. The sceneDicitonary also specifies the azimuth, tilt, clearance_height (distance between the ground and lowest point of the module) and any other parameter. Azimuth gets measured from N = 0, so for South facing modules azimuth should equal 180.
# 
# makeScene creates a .rad file with the parameters specified in sceneDict. 
# 

# In[5]:


sceneDict = {'tilt':10,'pitch':3,'clearance_height':0.2,'azimuth':180, 'nMods': 20, 'nRows': 7} 

scene = demo.makeScene(module_type,sceneDict)


# ### COMBINE the Ground, Sky, and the Scene Objects
# makeOct combines all of the ground, sky and object files into a .oct file.
# 

# In[6]:


octfile = demo.makeOct(demo.getfilelist())  


# ### ANALYZE and get Results
# Once the octfile tying the scene, ground and sky has been created, we create an analysis object. We have to specify where the sensors will be located with moduleAnalysis. If no parameters are passed to moduleAnalysis, it will scan the center module of the center row.
# 
# The frontscan and backscan include a linescan along a chord of the module, both on the front and back. 
# 
# ![Simple example for south facing module](images_wiki/frontscan_backscan.png)
# Analysis saves the measured irradiances in the front and in the back on the results folder.  Prints out the ratio of the average of the rear and front irradiance values along a chord of the module.

# In[7]:


analysis = AnalysisObj(octfile, demo.basename)
frontscan, backscan = analysis.moduleAnalysis(scene)
analysis.analysis(octfile, demo.basename, frontscan, backscan)  
print('Annual bifacial ratio: %0.3f ' %( np.mean(analysis.Wm2Back) / np.mean(analysis.Wm2Front)) )


# ### View / Render the Scene
# 
# If you used gencumsky or gendaylit, you can view the scene by navigating on a command line to the folder and typing:
# 
# ##### objview materials\ground.rad objects\Prism_Solar_Bi60_landscape_0.2_3_10_20x7.rad     
# 
# This objview has 3 different light sources of its own, so the shading is not representative.
# 
# If you used gendaylit (only), you can view the scene correctly illuminated with the sky you generated after generating the oct file, with 
# 
# ##### rvu -vf views\front.vp -e .01 bifacial_example.oct
# 
# Or you can also use the code below from bifacial_radiance to generate an HDR rendered image of the scene:

# In[8]:


# Make a color render and falsecolor image of the scene.  
# Files are saved as .hdr (high definition render) files.  Try LuminanceHDR viewer (free) to view them
analysis.makeImage('side.vp')
analysis.makeFalseColor('side.vp')
# Note - if you want to have an interactive image viewer, use the `rvu` viewer - manual page here: http://radsite.lbl.gov/radiance/rvu.1.html


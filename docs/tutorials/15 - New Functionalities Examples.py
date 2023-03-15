#!/usr/bin/env python
# coding: utf-8

# # 15 - New Functionalities Examples
# 
# This journal includes short examples on how to use the new functionalities of version 0.4.0 of bifacial_radiance. The parts are:
# 
# 1. <a href='#functionality1'> Simulating Modules with Frames and Omegas </a>
# 2. <a href='#functionality2'> Improvements to irradiance sampling</a>
#   * Scanning full module (sensors on x)!
#   * Different points in the front and the back
# 3. <a href='#functionality3'> Full row scanning.</a>

# In[1]:


import bifacial_radiance

import os
from pathlib import Path

testfolder = str(Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP' / 'Tutorial_15')
if not os.path.exists(testfolder):
    os.makedirs(testfolder)
    
print ("Your simulation will be stored in %s" % testfolder)


# <a id='functionality1'></a>

# ## I. Simulating Frames and Omegas
# 
# The values for generating frames and omegas are described in the makeModule function, which is where they are introduced into the basic module unit. This diagram shows how they are measured. 

# 
# ![Folder Structure](../images_wiki/makeModule_ComplexGeometry.PNG)
# 

# In[2]:


module_type = 'test-module'

frameParams = {'frame_material' : 'Metal_Grey', 
               'frame_thickness' : 0.05,
               'nSides_frame' : 4,
               'frame_width' : 0.08}

frameParams = {'frame_material' : 'Metal_Grey', 
               'frame_thickness' : 0.05,
               'nSides_frame' : 4,
               'frame_width' : 0.08}

omegaParams = {'omega_material': 'litesoil',
                'x_omega1' : 0.4,
                'mod_overlap' : 0.25,
                'y_omega' : 1.5,
                'x_omega3' : 0.25,
                'omega_thickness' : 0.05,
                'inverted' : False}

tubeParams = { 'visible': True,
              'axisofrotation' : True,
              'diameter' : 0.3
             }


demo = bifacial_radiance.RadianceObj('tutorial_15', testfolder) 

mymodule = demo.makeModule(module_type,x=2, y=1, xgap = 0.02, ygap = 0.15, zgap = 0.3, 
                numpanels = 2, tubeParams=tubeParams,
                frameParams=frameParams, omegaParams=omegaParams)


# Alternatively, the paremeters can be passed from an Object Oriented Approach as follows:

# In[3]:


mymodule.addTorquetube(visible = True, axisofrotation = True, diameter = 0.3)

mymodule.addOmega(omega_material = 'litesoil', x_omega1 = 0.4, mod_overlap = 0.25,
                 y_omega = 1.5, x_omega3 = 0.25, omega_thickness = 0.05, inverted = False)

mymodule.addFrame(frame_material = 'Metal_Grey', frame_thickness = 0.05, nSides_frame = 4, frame_width = 0.08)
                


# Let's add the rest of the scene and go until OCT, so it can be viewed with rvu:

# In[4]:


demo.setGround(0.2)
epwfile = demo.getEPW(lat = 37.5, lon = -77.6)
metdata = demo.readWeatherFile(epwfile, coerce_year = 2021)
demo.gendaylit(4020)

sceneDict = {'tilt':0, 'pitch':3, 'clearance_height':3,'azimuth':90, 'nMods': 1, 'nRows': 1} 
scene = demo.makeScene(mymodule,sceneDict)
demo.makeOct()


# To view the module from different angles, you can use the following rvu commands in your terminal:
# 
#     rvu -vp -7 0 3 -vd 1 0 0 Sim1.oct
# 
# 
#     rvu -vp 0 -5 3 -vd 0 1 0 Sim1.oct

# In[5]:



## Comment any of the ! line below to run rvu from the Jupyter notebook instead of your terminal.
## Simulation will stop until you close the rvu window(s).

#!rvu -vp -7 0 3 -vd 1 0 0 Sim1.oct
#!rvu -vp 0 -5 3 -vd 0 1 0 Sim1.oct


# <a id='functionality2'></a>

# ## II. Improvements to irradiance sampling
# 

# The key ideas here are:
# 
# - `moduleAnalysis()` returns two structured dictionaries that have the coordinates necessary for analysis to know where to smaple. On the new version, different values can be given for sampling accross the collector slope (y), for both front and backs by using a single value or an array in ``sensorsy``. 
# 
# - Furthermore, now scanning on the module's <b> x-direction </b> is supported, by setting the variables ``sensorsx`` as an singel value or an array.
# 
# When the sensors differ between the front and the back, instead of saving one .csv with results, two .csv files are saved, one labeled "_Front.csv" and the other "_Back.csv".
# 
# To know more, read the functions documentation.
# 
# 
# We'll take advantage of Simulation 1 testfolder, Radiance Objects and sky, but let's make a simple module and scene and model it through from there.

# In[6]:


mymodule = demo.makeModule(name='test-module',x=2, y=1)
sceneDict = {'tilt':0, 'pitch':6, 'clearance_height':3,'azimuth':180, 'nMods': 1, 'nRows': 1} 


# In[7]:


scene = demo.makeScene(mymodule,sceneDict)
octfile = demo.makeOct()
analysis = bifacial_radiance.AnalysisObj()  # return an analysis object including the scan dimensions for back irradiance


# ### Same sensors front and back, two sensors accross x

# In[8]:


name='2222'
sensorsy_front = 2
sensorsy_back = 2
sensorsx_front = 2
sensorsx_back = 2

sensorsy = [sensorsy_front, sensorsy_back]
sensorsx = [sensorsx_front, sensorsx_back]

frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy = sensorsy, sensorsx=sensorsx)

frontDict, backDict = analysis.analysis(octfile = octfile, name = name, frontscan = frontscan, 
                                        backscan = backscan)

print('\n--> RESULTS for Front and Back are saved on the same file since the sensors match for front and back')
print('\n', bifacial_radiance.load.read1Result('results\irr_'+name+'.csv'))


# ### Different sensors front and back, two sensors accross x

# In[9]:


name='2412'

sensorsy_front = 2
sensorsy_back = 4

sensorsx_front = 1
sensorsx_back = 2

sensorsy = [sensorsy_front, sensorsy_back]
sensorsx = [sensorsx_front, sensorsx_back]

frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=sensorsy, sensorsx=sensorsx)

frontDict, backDict = analysis.analysis(octfile = octfile, name = name, frontscan = frontscan, 
                                        backscan = backscan)

print('\n--> RESULTS for Front and Back are saved on SEPARATE file since the sensors do not match for front and back')

print('\nFRONT\n', bifacial_radiance.load.read1Result('results\irr_'+name+'_Front.csv'))
print('\nBACK\n', bifacial_radiance.load.read1Result('results\irr_'+name+'_Back.csv'))


# <a id='functionality3'></a>

# ## III. Making Analysis Function for Row
# 
# 
# Let's explore how to analyze easily a row with the new function `analyzeRow`. As before, we are not repeating functions alreayd called above, just re-running the necessary ones to show the changes. 

# In[10]:


sceneDict = {'tilt':0, 'pitch':30, 'clearance_height':3,'azimuth':90, 'nMods': 3, 'nRows': 3} 
scene = demo.makeScene(mymodule,sceneDict)
octfile = demo.makeOct()


# The function requires to know the number of modules on the row

# In[11]:


sensorsy_back=1 
sensorsx_back=1 
sensorsy_front=1
sensorsx_front=1

sensorsy = [sensorsy_front, sensorsy_back]
sensorsx = [sensorsx_front, sensorsx_back]

rowscan = analysis.analyzeRow(name = name, scene = scene, sensorsy=sensorsy, sensorsx = sensorsx,
                              rowWanted = 1, octfile = octfile)


# ``rowscan`` is now a dataframe containing the values of each module in the row. Check the x, y and 

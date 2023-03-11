#!/usr/bin/env python
# coding: utf-8

# # 22 - Mirrors and Modules
# 
# 
# Doing an example tutorial for example brought up in Issue #372
# 
# ![Mirror and Module Combo](../images_wiki/AdvancedJournals/22_mirror_moduleCombo.PNG)
# 
# 

# In[1]:


import os
from pathlib import Path

testfolder = str(Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP' / 'Tutorial_22')
if not os.path.exists(testfolder):
    os.makedirs(testfolder)
        
print ("Your simulation will be stored in %s" % testfolder)


# In[2]:


import bifacial_radiance
import numpy as np
import pprint   
import pandas as pd


# <a id='step2'></a>

# In[3]:


demo = bifacial_radiance.RadianceObj('tutorial_22', path=testfolder)  # Adding a simulation name. This is optional.
demo.setGround(0.2) 
epwfile = demo.getEPW(lat=37.5, lon=-77.6) 
metdata = demo.readWeatherFile(weatherFile=epwfile, coerce_year=2021) 
timeindex = metdata.datetime.index(pd.to_datetime('2021-01-01 12:0:0 -5'))
demo.gendaylit(timeindex) # Choosing a december time when the sun is lower in the horizon


# ## 1. Create your module and evaluate irradiance without the mirror element

# In[4]:


tilt = 75
sceneDict1 = {'tilt':tilt,'pitch':5,'clearance_height':0.05,'azimuth':180, 
              'nMods': 1, 'nRows': 1, 'originx': 0, 'originy': 0, 'appendRadfile':True} 
mymodule1 = demo.makeModule(name='test-module',x=2,y=1, numpanels=1)
sceneObj1 = demo.makeScene(mymodule1, sceneDict1)  


# In[5]:


octfile = demo.makeOct(demo.getfilelist())  
analysis = bifacial_radiance.AnalysisObj(octfile, demo.basename)
frontscan, backscan = analysis.moduleAnalysis(sceneObj1, sensorsy=1)
results = analysis.analysis(octfile, demo.basename, frontscan, backscan)  


# In[6]:


withoutMirror = bifacial_radiance.load.read1Result('results\irr_tutorial_22.csv')
withoutMirror


# ## 2. Add Mirror
# 
# ### Approach 1: Pretend the mirror is another module.
# 
# We start by creating the mirror material in our ground.rad file, in case it is not there. For mirror or glass primitives (material classes), pecularity and roughness are not needed. 
# 
# You could alternatively do a plastic material, and increase the specularity and lower the roughness to get a very reflective surface.

# In[7]:


demo.addMaterial(material='testmirror', Rrefl=0.94, Grefl=0.96, Brefl=0.96, 
         materialtype = 'mirror') # specularity and roughness not needed for mirrors or glass. 


# In[8]:


mymodule2 = demo.makeModule(name='test-mirror',x=2,y=1, numpanels=1, modulematerial='testmirror')


# We calculate the displacement of the morrir as per the equations show in the image at the beginning of the tutorial 

# In[9]:


originy = -(0.5*mymodule2.sceney + 0.5*mymodule1.sceney*np.cos(np.radians(tilt)))


# In[10]:


sceneDict2 = {'tilt':0,'pitch':0.00001,'clearance_height':0.05,'azimuth':180, 
              'nMods': 1, 'nRows': 1, 'originx': 0, 'originy': originy, 'appendRadfile':True} 
sceneObj2 = demo.makeScene(mymodule2, sceneDict2)  


# In[11]:


octfile = demo.makeOct(demo.getfilelist())  


# Use rvu in the terminal or by commenting out the cell below to view the generated geometry, it should look like this:
#     
# ![Mirror and Module Combo](../images_wiki/AdvancedJournals/22_mirror_moduleCombo_rvu.PNG)
# 
# 

# In[12]:


## Comment the line below to run rvu from the Jupyter notebook instead of your terminal.
## Simulation will stop until you close the rvu window

# !rvu -vf views\front.vp -e .01 -vp 4 -0.6 1 -vd -0.9939 0.1104 0.0 tutorial_22.oct


# In[13]:


analysis = bifacial_radiance.AnalysisObj(octfile, demo.basename)
frontscan, backscan = analysis.moduleAnalysis(sceneObj1, sensorsy=1)
results = analysis.analysis(octfile, name=demo.basename+'_withMirror', frontscan=frontscan, backscan=backscan)  
withMirror = bifacial_radiance.load.read1Result('results\irr_tutorial_22_withMirror.csv')
withMirror


# Just as a sanity check, we could sample the mirror...

# In[14]:


frontscan, backscan = analysis.moduleAnalysis(sceneObj2, sensorsy=1)
results = analysis.analysis(octfile, name=demo.basename+'_Mirroritself', frontscan=frontscan, backscan=backscan)  
bifacial_radiance.load.read1Result('results\irr_tutorial_22_Mirroritself.csv')


# And we can calculate the increase in front irradiance from the mirror:

# In[15]:


print("Gain from mirror:", round((withMirror.Wm2Front[0] - withoutMirror.Wm2Front[0] )*100/withoutMirror.Wm2Front[0],1 ), "%" )


# ### Approach 2: 
# 
# Create mirrors as their own objects and Append to Scene, like on tutorial 5. Sample code below:

# In[16]:


# name='Mirror1'
# text='! genbox black cuteMirror 2 1 0.02 | xform -t -1 -0.5 0 -t 0 {} 0'.format(originy)
# customObject = demo.makeCustomObject(name,text)
# demo.appendtoScene(radfile=scene.radfiles, customObject=customObject, text="!xform -rz 0")
# sceneObj2 = demo.makeScene(mymodule2, sceneDict2)  


# and then you do your Scene, Oct, and Analysis as usual.

#!/usr/bin/env python
# coding: utf-8

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

# In[5]:


x= 30 # m
y= 30 # m
materialground = 'litesoil'
myground = demo.makeModule(name='sloped-ground',y=y,x=x)


# In[6]:


# For sanity check, we are creating the same module but with different names for each orientation.
numpanels=1
ygap = 0.02 # m Spacing between modules on each shed.
y=1   # m. module size, one side
x=2 # m. module size, other side. for landscape, x > y
mymoduleEast = demo.makeModule(name='Pvmodule',y=y,x=x, numpanels=numpanels, ygap=ygap)


# In[7]:


sceneDict = {'tilt':5.71,'pitch':0.000001,'clearance_height':0,'azimuth':90, 'nMods': 1, 'nRows': 1} 
sceneObj0 = demo.makeScene(mymoduleEast, sceneDict)  



# In[ ]:


sceneDict2 = {'tilt': 45,'pitch':0.0000001,'clearance_height':(15+5.96)*np.sin(np.radians(theta))+1.5,'azimuth':90, 'nMods': 25, 'nRows': 1, 
              'originx': (15.0+5.96)*np.cos(np.radians(theta)), 'originy': 0, 'appendRadfile':True} 
sceneObj2 = demo.makeScene(mymoduleWest, sceneDict3)
                                                          
sceneDict3 = {'tilt':45,'pitch':0.0000001,'clearance_height':15*sin(np.radians(theta)+1.5t,'azimuth':90, 'nMods': 25, 'nRows': 1, 
    'originx': 0, 'originy': 0, 'appendRadfile':True} 

sceneObj2 = demo.makeScene(mymoduleWest, sceneDict3)


# In[ ]:


octfile = demo.makeOct(demo.getfilelist()) 


# In[ ]:


#!rvu -vf views\front.vp -e .01 -pe 0.3 -vp 1 -45 40 -vd 0 0.7 -0.7 MultipleObj.oct


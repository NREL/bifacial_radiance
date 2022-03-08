#!/usr/bin/env python
# coding: utf-8

# In[1]:


import bifacial_radiance   
import numpy as np
import pandas as pd
from pathlib import Path
import os


# In[2]:


testfolder = str(Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP' / 'TestPosts')
if not os.path.exists(testfolder):
    os.makedirs(testfolder)              


# In[3]:


demo = bifacial_radiance.RadianceObj('test',path = testfolder)
demo.setGround(0.2)
#epwfile = demo.getEPW(40.0583,-74.4057) # NJ lat/lon 40.0583° N, 74.4057
epwfile = r'EPWs\USA_NJ_McGuire.AFB.724096_TMY3.epw'
metdata = demo.readWeatherFile(epwfile, coerce_year=2021) 
timestamp = metdata.datetime.index(pd.to_datetime('2021-06-17 13:0:0 -5'))
demo.gendaylit(timestamp)  # Use this to simulate only one hour at a time. 


# In[4]:


mymodule=demo.makeModule(name='test_module',x=1,y=2, xgap=0.2, zgap=0.2)
mymodule.addTorquetube(axisofrotation=True, visible=False)


# In[15]:


sceneDict = {'tilt':30,'pitch': 6,'hub_height':1.3,'azimuth':180, 
             'nMods': 13, 'nRows': 2}  

scene = demo.makeScene(module=mymodule, sceneDict=sceneDict) 


# In[16]:


demo.__dict__


# In[17]:


demo.addPosts()


# In[18]:


octfile = demo.makeOct(demo.getfilelist())


# In[19]:


get_ipython().system('rvu -vf views\\front.vp -e .01 -vp 0.1 -5.4 0.6 -vd 0.0 0.9901 0.1400 test.oct')


# In[ ]:





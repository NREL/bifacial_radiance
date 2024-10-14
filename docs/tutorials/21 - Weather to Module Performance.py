#!/usr/bin/env python
# coding: utf-8

# In[1]:


# This information helps with debugging and getting support :)
import sys, platform
import pandas as pd
import bifacial_radiance as br
print("Working on a ", platform.system(), platform.release())
print("Python version ", sys.version)
print("Pandas version ", pd.__version__)
print("bifacial_radiance version ", br.__version__)


# # 21 - Weather to Module Performance
# ## Modeling Performance, an End to End Simulation
# 
# This tutorial shows how to use the new function on bifacial_radiance calculatePerformanceModule performance, as well as how to find CEC Module parameters.
# 

# In[2]:


import os
from pathlib import Path

testfolder = str(Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP' / 'Tutorial_21')

if not os.path.exists(testfolder): os.mkdir(testfolder)

# Another option using relative address; for some operative systems you might need '/' instead of '\'
# testfolder = os.path.abspath(r'..\..\bifacial_radiance\TEMP')  

print ("Your simulation will be stored in %s" % testfolder)


# In[3]:


import bifacial_radiance
import numpy as np
import pandas as pd
import pvlib 

bifacial_radiance.__version__


# In[4]:


# Selecting only two times as examples
starttime = '01_13_11';  endtime = '01_13_12'
demo = bifacial_radiance.RadianceObj('tutorial_21', path = testfolder) # Create a RadianceObj 'object'
weatherfile = demo.getEPW(lat = 37.5, lon = -77.6)  # This location corresponds to Richmond, VA.
metdata = demo.readWeatherFile(weatherFile=weatherfile, starttime=starttime, endtime=endtime)
demo.setGround(0.2)
mymodule = demo.makeModule(name='test-module', x=1, y=2, bifi=0.9) 
sceneDict = {'tilt': 10, 'azimuth': 180, 'pitch': 5,'hub_height':1.5, 'nMods':3, 'nRows': 2}
trackerdict = demo.set1axis(metdata = metdata, cumulativesky = False)
trackerdict = demo.gendaylit1axis()
trackerdict = demo.makeScene1axis(moduletype = mymodule, sceneDict = sceneDict)
trackerdict = demo.makeOct1axis()
trackerdict = demo.analysis1axis(sensorsy=3)


# ## Geting a CEC Module

# In[5]:


url = 'https://raw.githubusercontent.com/NREL/SAM/patch/deploy/libraries/CEC%20Modules.csv'
db = pd.read_csv(url, index_col=0) # Reading this might take 1 min or so, the database is big.


# Find the module that you want. In this case we know it's a SunPower of model SPR-E19-310-COM. 
# 
# Make sure you select only 1 module from the database -- sometimes there are similar names.

# In[6]:


modfilter2 = db.index.str.startswith('SunPower') & db.index.str.endswith('SPR-E19-310-COM')
print(modfilter2)
CECMod = db[modfilter2]
print(len(CECMod), " modules selected. Name of 1st entry: ", CECMod.index[0])


# ## Calculating the Performance and Exporting the Results to a CSV

# In[7]:


print(trackerdict)
tracker_dict_sample = trackerdict['2021-01-13_1100']
eff_irr = tracker_dict_sample['Wm2Front'] + tracker_dict_sample['Wm2Back']
bifacial_radiance.performance.calculatePerformance(eff_irr[0],CECMod=CECMod)
#calculatePerformanceModule -> calculcateResults()


# In[8]:


demo.exportTrackerDict(savefile=os.path.join('results','Final_Results.csv'),reindex=False)
pd.read_csv(os.path.join('results','Final_Results.csv'))


# In[ ]:





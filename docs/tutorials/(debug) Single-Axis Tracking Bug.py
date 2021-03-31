#!/usr/bin/env python
# coding: utf-8

# ## Single-axis Hourly Debug
# #### BASED ON JOURNAL 3 - Medium Level Example - 1-Axis tracker by hour (gendaylit)
# 
# Example demonstrating the use of doing hourly smiulations with Radiance gendaylit for 1-axis tracking. This is a medium level example because it also explores a couple subtopics:
# 

# <a id='step1'></a>

# 
# ## 1. Load bifacial_radiance 
# 
# #### Pay attention: different importing method:
# 
# So far we've used "from bifacial_radiance import *" to import all the bifacial_radiance files into our working space in jupyter. For this journal we will do a "import bifacial_radiance" . This method of importing requires a different call for some functions as you'll see below. For example, instead of calling demo = RadianceObj(path = testfolder) as on Tutorial 2, in this case we will neeed to do demo = bifacial_radiance.RadianceObj(path = testfolder). 

# In[1]:


import bifacial_radiance
import numpy as np
import os # this operative system to do teh relative-path testfolder for this example.
import pprint    # We will be pretty-printing the trackerdictionary throughout to show its structure.
from pathlib import Path
import pandas as pd


# <a id='step2'></a>

# ## 2. Define all your system variables
# 
# Just like in the condensed version show at the end of Tutorial 2, for this tutorial we will be starting all of our system variables from the beginning of the jupyter journal, instead than throughout the different cells (for the most part)

# In[2]:


testfolder = r'C:\Users\sayala\Documents\Soltec\Troubleshooting\01Feb2020\Journal_3'

simulationName = 'Tutorial 3'    # For adding a simulation name when defning RadianceObj. This is optional.
moduletype = 'Custom Cell-Level Module'    # We will define the parameters for this below in Step 4.
albedo = "litesoil"      # this is one of the options on ground.rad
lat = 37.5   
lon = -77.6

# Scene variables
nMods = 20
nRows = 7
hub_height = 2.3 # meters
#pitch = 10 # meters      # We will be using pitch instead of GCR for this example.

# Traking parameters
cumulativesky = False
limit_angle = 45 # tracker rotation limit angle
angledelta = 0.01 # we will be doing hourly simulation, we want the angle to be as close to real tracking as possible.
backtrack = True 
gcr = 0.35


# <a id='step3'></a>

# ## 3. Create Radiance Object, Set Albedo and Weather
# 
# Same steps as previous two tutorials, so condensing it into one step. You hopefully have this down by now! :)
# 
# 
# <div class="alert alert-warning">
# Notice that we are doing bifacial_radiance.RadianceObj because we change the import method for this example!
# </div>

# In[3]:


demo = bifacial_radiance.RadianceObj(simulationName, path = str(testfolder))  # Adding a simulation name. This is optional.
demo.setGround(albedo) 
epwfile = demo.getEPW(lat = 32.2226, lon = -110.9747) 
metdata1 = demo.readWeatherFile(weatherFile = epwfile) 


# In[4]:


startdate = '01/01'     
enddate = '01/02'
sceneDict = {'gcr':gcr,'hub_height':hub_height, 'nMods': nMods, 'nRows': nRows}  
trackingdict= demo.set1axis(limit_angle = limit_angle, backtrack = backtrack, gcr = 0.35, cumulativesky = cumulativesky)
demo.gendaylit1axis(startdate=startdate, enddate=enddate)


# In[5]:


startdate = '01/01'     
enddate = '01/01'
sceneDict = {'gcr':gcr,'hub_height':hub_height, 'nMods': nMods, 'nRows': nRows}  
trackingdict= demo.set1axis(limit_angle = limit_angle, backtrack = backtrack, gcr = 0.35, cumulativesky = cumulativesky)
demo.gendaylit1axis(startdate=startdate, enddate=enddate)


# In[6]:


startdate = '02/02'     
enddate = '02/02'
sceneDict = {'gcr':gcr,'hub_height':hub_height, 'nMods': nMods, 'nRows': nRows}  
trackingdict= demo.set1axis(limit_angle = limit_angle, backtrack = backtrack, gcr = 0.35, cumulativesky = cumulativesky)
demo.gendaylit1axis(startdate=startdate, enddate=enddate)


# ### Testing Routine with TMY3

# In[21]:


tmyfile = r'C:\Users\sayala\Documents\GitHub\bifacialvf\bifacialvf\data\722740TYA.CSV'


# In[20]:


demo = bifacial_radiance.RadianceObj(simulationName, path = str(testfolder))  # Adding a simulation name. This is optional.
demo.setGround(albedo) 
metdata1 = demo.readWeatherFile(weatherFile = tmyfile) 


# In[22]:


startdate = '01/01'     
enddate = '01/02'
sceneDict = {'gcr':gcr,'hub_height':hub_height, 'nMods': nMods, 'nRows': nRows}  
trackingdict= demo.set1axis(limit_angle = limit_angle, backtrack = backtrack, gcr = 0.35, cumulativesky = cumulativesky)
demo.gendaylit1axis(startdate=startdate, enddate=enddate)


# In[23]:


startdate = '01/01'     
enddate = '01/01'
sceneDict = {'gcr':gcr,'hub_height':hub_height, 'nMods': nMods, 'nRows': nRows}  
trackingdict= demo.set1axis(limit_angle = limit_angle, backtrack = backtrack, gcr = 0.35, cumulativesky = cumulativesky)
demo.gendaylit1axis(startdate=startdate, enddate=enddate)


# In[24]:


startdate = '02/02'     
enddate = '02/02'
sceneDict = {'gcr':gcr,'hub_height':hub_height, 'nMods': nMods, 'nRows': nRows}  
trackingdict= demo.set1axis(limit_angle = limit_angle, backtrack = backtrack, gcr = 0.35, cumulativesky = cumulativesky)
demo.gendaylit1axis(startdate=startdate, enddate=enddate)


# # EXPLORE PVLIB EPW Issue

# In[7]:


import pvlib
import pandas as pd
import matplotlib.pyplot as plt


# In[8]:


(epwdata, metadata) = pvlib.iotools.epw.read_epw(epwfile, coerce_year=2002) #pvlib>0.6.1
(tmydata, metadata) = pvlib.iotools.tmy.read_tmy3(tmyfile, coerce_year=2002) #pvlib>0.6.1

fig, ax = plt.subplots()
ax.plot(tmydata.index[0:24], tmydata.DNI[0:24], label='TMY data read with pvlib')
ax.plot(epwdata.index[0:24], epwdata.dni[0:24], label='EPW read with pvlib')
ax.set_ylabel('DNI [W/m$^2$]')
ax.legend()
fig.autofmt_xdate()


# In[9]:


#### Using Suggested Fix


# In[10]:


epwdata_fix = epwdata.copy()
epwdata_fix .index = epwdata_fix .index+pd.Timedelta(hours=1) 

fig, ax = plt.subplots()
ax.plot(tmydata.index[0:24], tmydata.DNI[0:24], label='TMY data read with pvlib')
ax.plot(epwdata.index[0:24], epwdata.dni[0:24], label='EPW read with pvlib ')
ax.plot(epwdata_fix.index[0:24], epwdata_fix .dni[0:24], '*', label='EPW read with pvlib (with suggested shift)')
ax.set_ylabel('DNI [W/m$^2$]')
ax.legend()
fig.autofmt_xdate()


# In[11]:


### Comparing to what bifacial_radiance is reading


# In[12]:


demo = bifacial_radiance.RadianceObj(simulationName, path = str(testfolder))  # Adding a simulation name. This is optional.
demo.setGround(albedo) 
metdata1 = demo.readWeatherFile(weatherFile = epwfile) 
metdata2 = demo.readWeatherFile(weatherFile = tmyfile) 


# In[13]:


metdata1.dni[0:24]


# In[14]:


metdata2.dni[0:24]


# In[15]:


fig, ax = plt.subplots()
ax.plot(metdata1.datetime[0:24], metdata1.dni[0:24], label='EPW read with bifacial_radiance (with shift)')
ax.plot(metdata1.datetime[0:24], metdata2.dni[0:24], '*', label='TMY read with bifacial_radiance')
ax.legend()
fig.autofmt_xdate()


# ### Going into bifacial_radiance Matcher Code

# In[16]:


import pandas as pd
import re


# In[17]:


metdata1 = demo.readWeatherFile(weatherFile = epwfile) 
temp = pd.to_datetime(demo.metdata.datetime)
print(len(temp))
temp2 = temp.month*10000+temp.day*100+temp.hour
startdate = '01/01'  
match1 = re.split('_|/',startdate) 
matchval = int(match1[0])*10000+int(match1[1])*100
print(matchval)
startindex = temp2.to_list().index(matchval)
print(startindex)


# In[ ]:





# In[18]:


metdata1 = demo.readWeatherFile(weatherFile = tmyfile) 
temp = pd.to_datetime(demo.metdata.datetime)
temp2 = temp.month*10000+temp.day*100+temp.hour
print(len(temp))
startdate = '01/01'  
match1 = re.split('_|/',startdate) 
matchval = int(match1[0])*10000+int(match1[1])*100
print(matchval)
startindex = temp2.to_list().index(matchval)
print(startindex)


# In[19]:


enddate = '01/02'  
match1 = re.split('_|/',enddate) 
matchval = int(match1[0])*10000+int(match1[1])*100
print(matchval)
endindex = temp2.to_list().index(matchval)
print(endindex)


# In[ ]:





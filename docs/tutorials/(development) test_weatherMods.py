#!/usr/bin/env python
# coding: utf-8

# In[ ]:





# In[1]:


import bifacial_radiance as br
import datetime as dt
import pandas as pd
import numpy as np
import os
import pvlib


# In[2]:


simName = 'DLT_ME'
test = br.RadianceObj(simName,simName)


# ## A. Read Weather
# 
# - No start/stop restrictions
# - coerce year
# - label = None

# In[3]:


CSV = r'C:\users\mbrown2\Documents\GitHub\internStuff\weatherFiles\724666TYA.CSV'
TMY = r'C:\Users\mbrown2\Documents\GitHub\internStuff\weatherFiles\USA_VA_Sterling-Washington.Dulles.Intl.AP.724030_TMY3.epw'


# In[4]:


test.readWeatherFile(TMY)
for i in test.metdata.datetime[:5]: print(i)
print(f'{len(test.metdata.datetime)} MetData points')


# In[8]:


(tmydata, metadata) = pvlib.iotools.tmy.read_tmy3(filename=CSV)


# In[10]:


tmydata.index.year


# In[13]:


fish = np.array([1,2,3,4])
fishID = pd.Index(fish)
fishID


# ## TO DO:
# 
# In the generalized case, above call for readWeatherFile effectively reads just 1 day. This is bad. It should be 1 year

# In[4]:


test.setGround(0.084)


# ## B. Read Weather
# 
# - w/ start/stop restrictions
# - coerce year
# - label = 'center'

# In[5]:


test.readWeatherFile(CSV, starttime='21_02_01', endtime='21_02_28', coerce_year=2021)
for i in test.metdata.datetime[:5]: print(i)
print(f'{len(test.metdata.datetime)} MetData points')


# In[6]:


ALT = r'C:\Users\mbrown2\Documents\GitHub\internStuff\TEMP\Matt_Test.csv'


# ## C. Read Weather - Sub-Hourly
# 
# - no start/stop restrictions
# - delta = 15 min
# - label = None

# In[7]:


test.readWeatherFile(ALT)
for i in test.metdata.datetime[:5]: print(i)
print(f'{len(test.metdata.datetime)} MetData points')


# ## D. Read Weather - Sub-Hourly
# 
# - w/ start/stop restrictions

# In[8]:


test.readWeatherFile(ALT, starttime='20_03_01', endtime='20_03_31')
for i in test.metdata.datetime[:5]: print(i)
print(f'{len(test.metdata.datetime)} MetData points')


# In[9]:


delta1 = dt.timedelta(hours=1)
delta2 = dt.timedelta(minutes=15)
if delta1 > delta2: print("OK!")

dt1 = dt.datetime(2001,11,1,10)
dt2 = dt1 + delta1
dt3 = dt1 + delta2

if (dt2 - dt1) == delta1: print('OK 2')
if (dt3 - dt1) == delta2: print('OK 3')

longTime = 8760 * delta1
dt4 = dt1+longTime
print(dt4.year)


# In[10]:


yearTest = str(dt4.year)[-2:]
print(yearTest)


# ### Restricting Gencumsky to some hours/days
# 
# # NOT WORKING

# In[ ]:


startdt = datetime.datetime(2021,5,1,1)
enddt = datetime.datetime(2021,9,30,23)
simulationName = 'EMPTYFIELD'
rad_obj = bifacial_radiance.RadianceObj(simulationName, path=testfolder)  # Create a RadianceObj 'object'
rad_obj.setGround(albedo) 
metdata = rad_obj.readWeatherFile(epwfile, label='center', coerce_year=2021)
rad_obj.genCumSky(startdt=startdt, enddt=enddt)
#print(rad_obj.metdata.datetime[idx])
sceneDict = {'pitch': pitch, 'tilt': 0, 'azimuth': 90, 'hub_height':-0.2, 'nMods':1, 'nRows': 1}  
scene = rad_obj.makeScene(moduletype=moduletype,sceneDict=sceneDict)
octfile = rad_obj.makeOct()  
analysis = bifacial_radiance.AnalysisObj()
frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=1)
frontscan['zstart'] = 0.5
frontdict, backdict = analysis.analysis(octfile = octfile, name='FIELDTotal', frontscan=frontscan, backscan=backscan)
resname = os.path.join(testfolder, 'results')
resname = os.path.join(resname, 'irr_FIELDTotal.csv')
data = pd.read_csv(resname)
print("FIELD TOTAL Season:", data['Wm2Front'])


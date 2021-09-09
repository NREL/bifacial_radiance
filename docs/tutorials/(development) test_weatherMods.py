#!/usr/bin/env python
# coding: utf-8

# def readWeatherFile(self, weatherFile=None, starttime=None, 
#                         endtime=None, daydate=None, label = None, source=None,
#                         coerce_year=None):
#             starttime : str
#             Limited start time option in 'YY_MM_DD_HH' format
#         endtime : str
#             Limited end time option in 'YY_MM_DD_HH' format
#             daydate
# 
# def readEPW(self, epwfile=None, hpc=False, starttime=None, endtime=None, 
#                 daydate=None, label = 'right', coerce_year=None):
#                 # TODO: Is daydate working still?
# 
# def readTMY(self, tmyfile=None, starttime=None, endtime=None, daydate=None, 
#                 label = 'right', coerce_year=None):
#     
#         tmydata_trunc = self._saveTempTMY(tmydata,'tmy3_temp.csv', 
#                                           starttime=starttime, endtime=endtime, coerce_year=coerce_year)
#         
#         MetObj --> truncated data. 
#         
# gendaylit --> uses metdata internal or passed.
# 
# genCumSky --> uses internal csv from saveTempTMY, or passed epw.
#         
#         
# set1axis      (self, metdata=None, axis_azimuth=180, limit_angle=45,
#                  angledelta=5, backtrack=True, gcr=1.0 / 3, cumulativesky=True,
#                  fixed_tilt_angle=None):
# 
# gendaylit1axis(self, metdata=None, trackerdict=None, startdate=None,
#                        enddate=None, debug=False, hpc=False):   'YY_MM_DD_HH'
# 
# genCumSky1axis
# 
# analysis1axis (self, trackerdict=None, singleindex=None, accuracy='low',
#                customname=None, modWanted=None, rowWanted=None, sensorsy=9, hpc=False,
#                modscanfront = None, modscanback = None, relative=False, debug=False):

# In[1]:


import bifacial_radiance as br
import datetime as dt
import pandas as pd
import numpy as np
import os
import pvlib
from pathlib import Path


# In[2]:


testfolder = str(Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP' / 'WeatherTests')
if not os.path.exists(testfolder):
    os.makedirs(testfolder)
print(testfolder)


# # Weather File tests:
# * A. EPW
# * B. TMY3
# * C. TMY3 15 mins
# * D. TMY3 two years
# 

# In[3]:


TMY3file = '../../../tests/724666TYA.CSV'
EPWfile = 'USA_CO_Boulder.724699_TMY2.epw'
Customfile = 'Custom_WeatherFile_2years_15mins_BESTFieldData.csv'


# ## 1. TMY + readTMY3() + no restrictions + no coerce year
# 

# In[14]:


sim = 'testA'
demo = br.RadianceObj(sim, testfolder)
metdata = demo.readWeatherFile(TMY3file)

print("\nMETDATA")
print('start:', metdata.datetime[0])
print('end:', metdata.datetime[1])
print('idx 4020:', metdata.datetime[4020])
print('Length:', len(metdata.datetime))


# In[13]:


metdata.__dict__


# In[6]:


demo.setGround(0.2)
demo.gendaylit(4020)


# In[7]:


moduleDict=demo.makeModule(name='test',x=2,y=1)


# In[8]:


sceneDict = {'tilt':10,'pitch':0.001,'clearance_height':1,'azimuth':180, 'nMods': 1, 'nRows': 1} 
scene = demo.makeScene(moduletype='test',sceneDict=sceneDict, radname = sim)
octfile = demo.makeOct(octname = demo.basename)  
analysis = br.AnalysisObj(octfile=octfile, name=sim)
frontscan, backscan = analysis.moduleAnalysis(scene=scene, sensorsy_back=1)
analysis.analysis(octfile, name=sim, frontscan=frontscan, backscan=backscan)


# ## 2. TMY + readTMY3() + day restrictions + no coerce year
# 

# In[19]:


sim = 'testB'
demo = br.RadianceObj(sim, testfolder)
metdata = demo.readWeatherFile(TMY3file, starttime='01_02_01', endtime='01_02_28') # It internally coerces to 2001.

print("\nMETDATA")
print('start:', metdata.datetime[0])
print('index 1:', metdata.datetime[1])
print('end:', metdata.datetime[-1])
print('idx 20:', metdata.datetime[20])
print('Length:', len(metdata.datetime),'n')

demo.setGround(0.2)
demo.gendaylit(20)
scene = demo.makeScene(moduletype='test',sceneDict=sceneDict, radname = sim)
octfile = demo.makeOct(octname = demo.basename)  
analysis = br.AnalysisObj(octfile=octfile, name=sim)
frontscan, backscan = analysis.moduleAnalysis(scene=scene, sensorsy_back=1)
analysis.analysis(octfile, name=sim, frontscan=frontscan, backscan=backscan)


# # 3. TMY + readTMY3() + day restrictions + coerce year
# 

# In[20]:


sim = 'testB'
demo = br.RadianceObj(sim, testfolder)
metdata = demo.readWeatherFile(TMY3file, starttime='21_02_01', endtime='21_02_28', coerce_year=2021) # It internally coerces to 2001.

print("\nMETDATA")
print('start:', metdata.datetime[0])
print('index 1:', metdata.datetime[1])
print('end:', metdata.datetime[-1])
print('idx 20:', metdata.datetime[20])
print('Length:', len(metdata.datetime),'\n')

demo.setGround(0.2)
demo.gendaylit(20)
scene = demo.makeScene(moduletype='test',sceneDict=sceneDict, radname = sim)
octfile = demo.makeOct(octname = demo.basename)  
analysis = br.AnalysisObj(octfile=octfile, name=sim)
frontscan, backscan = analysis.moduleAnalysis(scene=scene, sensorsy_back=1)
analysis.analysis(octfile, name=sim, frontscan=frontscan, backscan=backscan)


# ## 3. TMY + readTMY3() + day restrictions + coerce year + GENCUMSKY

# # Gencumsky

# In[28]:


sim = 'testB'
demo = br.RadianceObj(sim, testfolder)
metdata = demo.readWeatherFile(TMY3file, coerce_year=2021) # It internally coerces to 2001.

print("\nMETDATA")
print('start:', metdata.datetime[0])
print('index 1:', metdata.datetime[1])
print('end:', metdata.datetime[-1])
print('idx 20:', metdata.datetime[20])
print('Length:', len(metdata.datetime),'\n')

demo.setGround(0.2)
demo.genCumSky()
scene = demo.makeScene(moduletype='test',sceneDict=sceneDict, radname = sim)
octfile = demo.makeOct(octname = demo.basename)  
analysis = br.AnalysisObj(octfile=octfile, name=sim)
frontscan, backscan = analysis.moduleAnalysis(scene=scene, sensorsy_back=1)
foo1 = analysis.analysis(octfile, name=sim, frontscan=frontscan, backscan=backscan)


# In[29]:


sim = 'testB'
demo = br.RadianceObj(sim, testfolder)
metdata = demo.readWeatherFile(TMY3file, starttime='21_02_01', endtime='21_02_28', coerce_year=2021) # It internally coerces to 2001.

print("\nMETDATA")
print('start:', metdata.datetime[0])
print('index 1:', metdata.datetime[1])
print('end:', metdata.datetime[-1])
print('idx 20:', metdata.datetime[20])
print('Length:', len(metdata.datetime),'\n')

demo.setGround(0.2)
demo.genCumSky()
scene = demo.makeScene(moduletype='test',sceneDict=sceneDict, radname = sim)
octfile = demo.makeOct(octname = demo.basename)  
analysis = br.AnalysisObj(octfile=octfile, name=sim)
frontscan, backscan = analysis.moduleAnalysis(scene=scene, sensorsy_back=1)
foo2 = analysis.analysis(octfile, name=sim, frontscan=frontscan, backscan=backscan)


# In[47]:


sim = 'testB'
demo = br.RadianceObj(sim, testfolder)
metdata = demo.readWeatherFile(TMY3file, starttime='21_02_01', endtime='21_02_28', coerce_year=2021) # It internally coerces to 2001.

print("\nMETDATA")
print('start:', metdata.datetime[0])
print('index 1:', metdata.datetime[1])
print('end:', metdata.datetime[-1])
print('idx 20:', metdata.datetime[20])
print('Length:', len(metdata.datetime),'\n')

demo.setGround(0.2)
startdt = datetime.datetime(2021,2,1,1)
enddt = datetime.datetime(2021,2,2,23)

demo.genCumSky(startdt=startdt, enddt=enddt)
scene = demo.makeScene(moduletype='test',sceneDict=sceneDict, radname = sim)
octfile = demo.makeOct(octname = demo.basename)  
analysis = br.AnalysisObj(octfile=octfile, name=sim)
frontscan, backscan = analysis.moduleAnalysis(scene=scene, sensorsy_back=1)
foo3 = analysis.analysis(octfile, name=sim, frontscan=frontscan, backscan=backscan)


# In[48]:


sim = 'testB'
demo = br.RadianceObj(sim, testfolder)
metdata = demo.readWeatherFile(TMY3file, coerce_year=2021) # It internally coerces to 2001.

print("\nMETDATA")
print('start:', metdata.datetime[0])
print('index 1:', metdata.datetime[1])
print('end:', metdata.datetime[-1])
print('idx 20:', metdata.datetime[20])
print('Length:', len(metdata.datetime),'\n')

demo.setGround(0.2)
startdt = datetime.datetime(2021,2,1,1)
enddt = datetime.datetime(2021,2,2,23)

demo.genCumSky(startdt=startdt, enddt=enddt)
scene = demo.makeScene(moduletype='test',sceneDict=sceneDict, radname = sim)
octfile = demo.makeOct(octname = demo.basename)  
analysis = br.AnalysisObj(octfile=octfile, name=sim)
frontscan, backscan = analysis.moduleAnalysis(scene=scene, sensorsy_back=1)
foo4 = analysis.analysis(octfile, name=sim, frontscan=frontscan, backscan=backscan)


# In[49]:


print("Full year", foo1[0]['Wm2'])
print("Read Weather File Limited", foo2[0]['Wm2'][0]/foo1[0]['Wm2'][0])             # This is a month
print("ReadWeatherFile and Gencumsky limited", foo3[0]['Wm2'][0]/foo1[0]['Wm2'][0]) # This is only 2 days 
print("Gencumsky limited", foo4[0]['Wm2'][0]/foo1[0]['Wm2'][0])                     # This should be only 2 days


# # CONCLUSION mGENCUMSKY DElimiter is not working. We were already thinking to deprecate, deprecate on this one?
# 

# # EPW File Input to Gencumsky does not work

# In[51]:


sim = 'testB'
demo = br.RadianceObj(sim, testfolder)
metdata = demo.readWeatherFile(TMY3file, coerce_year=2021) # It internally coerces to 2001.

print("\nMETDATA")
print('start:', metdata.datetime[0])
print('index 1:', metdata.datetime[1])
print('end:', metdata.datetime[-1])
print('idx 20:', metdata.datetime[20])
print('Length:', len(metdata.datetime),'\n')

demo.setGround(0.2)
demo.genCumSky(epwfile=EPWfile)
scene = demo.makeScene(moduletype='test',sceneDict=sceneDict, radname = sim)
octfile = demo.makeOct(octname = demo.basename)  
analysis = br.AnalysisObj(octfile=octfile, name=sim)
frontscan, backscan = analysis.moduleAnalysis(scene=scene, sensorsy_back=1)
foo5 = analysis.analysis(octfile, name=sim, frontscan=frontscan, backscan=backscan)


# In[ ]:


# 2 EPW


# In[ ]:





# In[ ]:





# In[46]:


import datetime


# In[26]:


sim = 'testB'
demo = br.RadianceObj(sim, testfolder)
metdata = demo.readWeatherFile(TMY3file, starttime='21_02_01', endtime='21_02_28', coerce_year=2021) # It internally coerces to 2001.

print("\nMETDATA")
print('start:', metdata.datetime[0])
print('index 1:', metdata.datetime[1])
print('end:', metdata.datetime[-1])
print('idx 20:', metdata.datetime[20])
print('Length:', len(metdata.datetime),'\n')

demo.setGround(0.2)
startdt = datetime.datetime(2021,2,1,1)
enddt = datetime.datetime(2021,2,2,23)

demo.genCumSky(startdt=startdt, enddt=enddt)
scene = demo.makeScene(moduletype='test',sceneDict=sceneDict, radname = sim)
octfile = demo.makeOct(octname = demo.basename)  
analysis = br.AnalysisObj(octfile=octfile, name=sim)
frontscan, backscan = analysis.moduleAnalysis(scene=scene, sensorsy_back=1)
analysis.analysis(octfile, name=sim, frontscan=frontscan, backscan=backscan)


# In[ ]:





# ## C. Read Weather - Sub-Hourly
# 
# - no start/stop restrictions
# - delta = 15 min
# - label = None

# In[ ]:


test.readWeatherFile(ALT)
for i in test.metdata.datetime[:5]: print(i)
print(f'{len(test.metdata.datetime)} MetData points')


# ## D. Read Weather - Sub-Hourly
# 
# - w/ start/stop restrictions

# In[ ]:


test.readWeatherFile(ALT, starttime='20_03_01', endtime='20_03_31')
for i in test.metdata.datetime[:5]: print(i)
print(f'{len(test.metdata.datetime)} MetData points')


# In[ ]:


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


# In[ ]:


yearTest = str(dt4.year)[-2:]
print(yearTest)


# In[ ]:





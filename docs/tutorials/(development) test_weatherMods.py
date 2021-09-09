#!/usr/bin/env python
# coding: utf-8

# # Testing Various Weather Files plus Sky generation options

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
EPWfile = '../../../tests/USA_CO_Boulder.724699_TMY2.epw'
TMY3file = '../../../tests/USA_CO_Boulder.724699_TMY2.epw'

Customfile = '../../../tests/Custom_WeatherFile_2years_15mins_BESTFieldData.csv'


# ## 1. TMY	unrestricted time	gendaylit

# In[ ]:





# In[4]:





# In[ ]:





# In[7]:


sim = 'testA'
demo = br.RadianceObj(sim, testfolder)
metdata = demo.readWeatherFile(TMY3file)

demo.setGround(0.2)
demo.gendaylit(4020)

moduleDict=demo.makeModule(name='test',x=2,y=1)

sceneDict = {'tilt':10,'pitch':0.001,'clearance_height':1,'azimuth':180, 'nMods': 1, 'nRows': 1} 
scene = demo.makeScene(moduletype='test',sceneDict=sceneDict, radname = sim)
octfile = demo.makeOct(octname = demo.basename)  
analysis = br.AnalysisObj(octfile=octfile, name=sim)
frontscan, backscan = analysis.moduleAnalysis(scene=scene, sensorsy_back=1)
analysis.analysis(octfile, name=sim, frontscan=frontscan, backscan=backscan)


# In[ ]:


print("\nMETDATA")
print('start:', metdata.datetime[0])
print('index 1:', metdata.datetime[1])
print('end:', metdata.datetime[-1])
print('idx 20:', metdata.datetime[20])
print('Length:', len(metdata.datetime),'n')


# ## 2	TMY	gendaylit	startime/endtime
# 

# In[8]:


sim = 'testB'
demo = br.RadianceObj(sim, testfolder)
metdata = demo.readWeatherFile(TMY3file, starttime='01_02_01_10', endtime='01_02_28_23', coerce_year=2001) 



demo.setGround(0.2)
demo.gendaylit(20)
scene = demo.makeScene(moduletype='test',sceneDict=sceneDict, radname = sim)
octfile = demo.makeOct(octname = demo.basename)  
analysis = br.AnalysisObj(octfile=octfile, name=sim)
frontscan, backscan = analysis.moduleAnalysis(scene=scene, sensorsy_back=1)
analysis.analysis(octfile, name=sim, frontscan=frontscan, backscan=backscan)


# In[ ]:





# ## 3	TMY	gendaylit	daydate
# 

# In[9]:


sim = 'test03'
demo = br.RadianceObj(sim, testfolder)
metdata = demo.readWeatherFile(TMY3file, daydate='21_11_06', coerce_year=2021)

demo.setGround(0.2)
demo.gendaylit(5)
scene = demo.makeScene(moduletype='test',sceneDict=sceneDict, radname = sim)
octfile = demo.makeOct(octname = demo.basename)  
analysis = br.AnalysisObj(octfile=octfile, name=sim)
frontscan, backscan = analysis.moduleAnalysis(scene=scene, sensorsy_back=1)
analysis.analysis(octfile, name=sim, frontscan=frontscan, backscan=backscan)


# ## 4. TMY	gencumsky	unrestricted time
# 

# In[10]:


sim = 'testB'
demo = br.RadianceObj(sim, testfolder)
metdata = demo.readWeatherFile(TMY3file, coerce_year=2021) # It internally coerces to 2001.

demo.setGround(0.2)
demo.genCumSky()
scene = demo.makeScene(moduletype='test',sceneDict=sceneDict, radname = sim)
octfile = demo.makeOct(octname = demo.basename)  
analysis = br.AnalysisObj(octfile=octfile, name=sim)
frontscan, backscan = analysis.moduleAnalysis(scene=scene, sensorsy_back=1)
foo4 = analysis.analysis(octfile, name=sim, frontscan=frontscan, backscan=backscan)


# ## 5. TMY	gencumsky	startime/endtime

# In[11]:


sim = 'testB'
demo = br.RadianceObj(sim, testfolder)
metdata = demo.readWeatherFile(TMY3file, starttime='21_02_01', endtime='21_02_28', coerce_year=2021) # It internally coerces to 2001.

demo.setGround(0.2)
demo.genCumSky()
scene = demo.makeScene(moduletype='test',sceneDict=sceneDict, radname = sim)
octfile = demo.makeOct(octname = demo.basename)  
analysis = br.AnalysisObj(octfile=octfile, name=sim)
frontscan, backscan = analysis.moduleAnalysis(scene=scene, sensorsy_back=1)
foo5 = analysis.analysis(octfile, name=sim, frontscan=frontscan, backscan=backscan)


# # 6	TMY	gencumsky	daydate
# 

# In[12]:


sim = 'testB'
demo = br.RadianceObj(sim, testfolder)
metdata = demo.readWeatherFile(TMY3file, daydate='21_02_03', coerce_year=2021) # It internally coerces to 2001.

demo.setGround(0.2)
demo.genCumSky()
scene = demo.makeScene(moduletype='test',sceneDict=sceneDict, radname = sim)
octfile = demo.makeOct(octname = demo.basename)  
analysis = br.AnalysisObj(octfile=octfile, name=sim)
frontscan, backscan = analysis.moduleAnalysis(scene=scene, sensorsy_back=1)
foo6 = analysis.analysis(octfile, name=sim, frontscan=frontscan, backscan=backscan)


# In[13]:


print("Full year", foo4[0]['Wm2'])
print( foo5[0]['Wm2'][0]/foo4[0]['Wm2'][0]) # 1 month       # 5	TMY	gencumsky	startime/endtime
print( foo6[0]['Wm2'][0]/foo4[0]['Wm2'][0]) # 1 day        # 6	TMY	gencumsky	daydate


# # EPW File Input to Gencumsky does not work

# In[ ]:


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





# In[ ]:


import datetime


# In[ ]:


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





#!/usr/bin/env python
# coding: utf-8

# # Variety of Routines
# 
# This journals explores the different ways 
# 
# <b> 1. Fixed tilt routine for fixed tilt systems </b>
# * makeScene
# * gendaylit   or gencumsky
# * makeoct
# * analysis
# 
# 
# <b> 2. Tracker Routine for 1-HSAT </b>
# * set1axis          (gets angles)
# * makeScene1axis            
# * gendaylit1axis   or gencumsky1axis
# * makeoct1axis
# * analysis1axis
# 
# 
# <b> 3. Fixtilt tilt routine for a 1-HSAT, 1 single timestamp</b>
# * gettrackerangle
# * makeScene
# * gendaylit or gencumsky
# * makeoct
# * analysis

# # Fixed tilt routine for fixed tilt systems

# #### A. Gendaylit: Probably looping over IDX

# In[1]:


import bifacial_radiance
import os
from pathlib import Path

testfolder = Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP' / 'Tutorial_01'
if not os.path.exists(testfolder):
    os.makedirs(testfolder)


# In[2]:


#Main Variables needed throughout
albedo = 0.6
sim_general_name = 'bifacial_example'
lat = 37.5
lon = -77.6
epwfile = r'C:\Users\sayala\Documents\RadianceScenes\HPC_Test\USA_VA_Richmond.Intl.AP.724010_TMY.epw'
moduletype = 'Prism Solar Bi60 landscape'

tilt = 10
pitch = 3
clearance_height = 0.2
azimuth = 90
nMods = 20
nRows = 7


# In[3]:


idx = 5
sim_name = sim_general_name+'_'+str(idx)
demo = bifacial_radiance.RadianceObj(sim_name,str(testfolder))  
demo.setGround(albedo)
metdata = demo.readWeatherFile(epwfile) 
mymodule = demo.makeModule('test-module', x=1, y=2)
demo.gendaylit(idx)
sceneDict = {'tilt':tilt,'pitch':pitch,'clearance_height':clearance_height,'azimuth':azimuth, 'nMods': 4, 'nRows': 3} 
scene = demo.makeScene(module=mymodule,sceneDict=sceneDict, radname = sim_name)
octfile = demo.makeOct(octname = demo.basename)  
analysis = bifacial_radiance.AnalysisObj(octfile=octfile, name=sim_name)
frontscan, backscan = analysis.moduleAnalysis(scene=scene)


# In[4]:


# 1 Module
#frontscan, backscan = analysis.moduleAnalysis(scene=scene, sensorsy=[3,2])
#analysis.analysis(octfile, name=sim_name, frontscan=frontscan, backscan=backscan)


# In[5]:


# Full Field
results = analysis.analyzeField(octfile, scene, sensorsy=[3,2], sensorsx=[1,4])


# In[11]:


import pandas as pd
import numpy as np


# In[12]:


url = 'https://raw.githubusercontent.com/NREL/SAM/patch/deploy/libraries/CEC%20Modules.csv'
db = pd.read_csv(url, index_col=0) # Reading this might take 1 min or so, the database is big.
modfilter2 = db.index.str.startswith('Pr') & db.index.str.endswith('BHC72-400')
CECMod = db[modfilter2]
print(len(CECMod), " modules selected. Name of 1st entry: ", CECMod.index[0])


# In[13]:


results.reset_index(inplace=True, drop=True)


# In[14]:


ress= bifacial_radiance.performance.arrayResults(CECMod=CECMod, results=results)


# In[15]:


ress


# # IF READ

# In[ ]:


csvfile = os.path.join(testfolder, 'results', 'CompiledResults', 'compiledField_FieldAnalysis.csv')


# In[ ]:


ress= bifacial_radiance.performance.arrayResults(CECMod=CECMod, csvfile=csvfile)


# In[ ]:


ress


# In[ ]:


#data = pd.read_csv(os.path.join(testfolder, 'results', 'CompiledResults', 'compiledField_FieldAnalysis.csv'))
#data['Wm2Front'].str.strip('[]').str.split(',', expand=True).astype(float)


# # IF from Results

# In[ ]:


import pandas as pd
import numpy as np


# In[ ]:


br = results.copy()


# In[ ]:


Wm2Front = pd.DataFrame.from_dict(dict(zip(br.index,br['Wm2Front']))).T


# In[ ]:


Wm2Back = pd.DataFrame.from_dict(dict(zip(br.index,br['Wm2Back']))).T


# In[ ]:


mattype = pd.DataFrame.from_dict(dict(zip(br.index,br['mattype']))).T


# In[ ]:


rearMat = pd.DataFrame.from_dict(dict(zip(br.index,br['rearMat']))).T


# In[ ]:


matchers = ['sky','pole','tube','bar','ground', '3267', '1540']

maskfront = np.column_stack([mattype[col].str.contains('|'.join(matchers), na=False) for col in mattype])
Wm2Front[maskfront] = np.nan

maskback = np.column_stack([rearMat[col].str.contains('|'.join(matchers), na=False) for col in rearMat])
Wm2Back[maskback] = np.nan

# Filling Nans...        
filledFront = Wm2Front.interpolate().mean(axis=1)
filledBack = Wm2Back.interpolate()
POA=filledBack.apply(lambda x: x + filledFront)


# Statistics Calculatoins
dfst=pd.DataFrame()
#dfst['MAD/G_Total'] = bifacial_radiance.mismatch.mad_fn(POA.T)  # 'MAD/G_Total
dfst['Poa_total'] = POA.mean(axis=1)
#dfst['MAD/G_Total**2'] = dfst['MAD/G_Total']**2
#dfst['stdev'] = POA.std(axis=1)/ dfst['poat']

dfst['Pout'] = bifacial_radiance.performance.calculatePerformance(dfst['Poa_total'], CECMod)
dfst['Mismatch'] = bifacial_radiance.mismatch.mismatch_fit3(POA.T)
dfst['Pout_red'] = dfst['Pout']*(1-dfst['Mismatch']/100)


# In[ ]:


dfst


# In[ ]:





# # Line by Line ORiginal

# In[ ]:


matchers = ['sky','pole','tube','bar','ground', '3267', '1540']


# In[ ]:


maskfront = np.column_stack([mattype[col].str.contains('|'.join(matchers), na=False) for col in mattype])
Wm2Front[maskfront] = np.nan

maskback = np.column_stack([rearMat[col].str.contains('|'.join(matchers), na=False) for col in rearMat])
Wm2Back[maskback] = np.nan


# In[ ]:


filledFront = Wm2Front.interpolate().mean(axis=1)
filledBack = Wm2Back.interpolate()
POA=filledBack.apply(lambda x: x + filledFront)


# In[ ]:


POA


# In[ ]:


# Statistics Calculatoins
dfst=pd.DataFrame()
dfst['MAD/G_Total'] = bifacial_radiance.mismatch.mad_fn(POA.T)  # 'MAD/G_Total
dfst['poat'] = POA.mean(axis=1)
dfst['MAD/G_Total**2'] = dfst['MAD/G_Total']**2
dfst['stdev'] = POA.std(axis=1)/ dfst['poat']


# In[ ]:


dfst['Pout'] = bifacial_radiance.performance.calculatePerformance(dfst.poat, CECMod)


# In[ ]:


dfst['mismatch'] = bifacial_radiance.mismatch.mismatch_fit3(POA.T)


# In[ ]:


dfst['Pout_red']=dfst['Pout']*(1-dfst['mismatch']/100)


# In[ ]:


dfst


# In[ ]:


ress


# In[ ]:





# In[ ]:


dfst


# In[ ]:


analysis.analyzeRow(octfile, scene, rowWanted=1)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# #### B. Gencumsky: Probably looping over something in the Geometry

# In[ ]:


tilt = 30


# In[ ]:


#Main Variables needed throughout
albedo = 0.6
sim_general_name = 'bifacial_example'
lat = 37.5
lon = -77.6
epwfile = r'C:\Users\sayala\Documents\RadianceScenes\HPC_Test\USA_VA_Richmond.Intl.AP.724010_TMY.epw'
testfolder = r'C:\Users\sayala\Documents\RadianceScenes\HPC_Test\Routine1' 
moduletype = 'Prism Solar Bi60 landscape'

tilt = 10
pitch = 3
clearance_height = 0.2
azimuth = 90
nMods = 20
nRows = 7
hpc = True


# In[ ]:


import bifacial_radiance

sim_name = sim_general_name+'_'+str(tilt)
demo = bifacial_radiance.RadianceObj(sim_name,str(testfolder))  
demo.setGround(albedo)
metdata = demo.readWeatherFile(epwfile) 
demo.genCumSky(savefile = sim_name)
sceneDict = {'tilt':tilt,'pitch':pitch,'clearance_height':clearance_height,'azimuth':azimuth, 'nMods': nMods, 'nRows': nRows} 
scene = demo.makeScene(moduletype=moduletype,sceneDict=sceneDict, hpc=hpc, radname = sim_name)
octfile = demo.makeOct(octname = demo.basename , hpc=hoc)  
analysis = bifacial_radiance.AnalysisObj(octfile=octfile, name=sim_name)
frontscan, backscan = analysis.moduleAnalysis(scene=scene)
analysis.analysis(octfile, name=sim_name, frontscan=frontscan, backscan=backscan)


# #### C. Option: Gencumsky segmented ....

# In[ ]:


# ADD LATER


# <a id='step2'></a>

# ## 2. Tracker Routine for 1-HSAT

# #### Gendaylit1axis, looping over hours

# In[ ]:


#Main Variables needed throughout
albedo = 0.6
sim_general_name = 'bifacial_example'
lat = 37.5
lon = -77.6
epwfile = r'C:\Users\sayala\Documents\RadianceScenes\HPC_Test\USA_VA_Richmond.Intl.AP.724010_TMY.epw'
testfolder = r'C:\Users\sayala\Documents\RadianceScenes\HPC_Test\Routine1' 
moduletype = 'Prism Solar Bi60 landscape'

hub_height = 0.2
nMods = 20
nRows = 7
hpc = True

limit_angle = 60
backtrack = True
gcr = 0.35
angledelta = 0.01

starttime = '21_11_06_10'# 'YY_MM_DD_HH'
endtime = starttime
cumulativesky = False


# In[ ]:


import bifacial_radiance

sim_name = sim_general_name + starttime
demo = bifacial_radiance.RadianceObj(sim_name, path=testfolder)  
demo.setGround(albedo) 
metdata = demo.readWeatherFile(epwfile, coerce_year=2021, daydate='05_01')  
sceneDict = {'gcr':gcr,'hub_height':hub_height, 'nMods': nMods, 'nRows': nRows}  
trackerdict = demo.set1axis(limit_angle = limit_angle, backtrack = backtrack, gcr = gcr, cumulativesky = cumulativesky)


# In[ ]:


metdata = demo.readWeatherFile(epwfile, coerce_year=2021, daydate='21_05_22')  
sceneDict = {'gcr':gcr,'hub_height':hub_height, 'nMods': nMods, 'nRows': nRows}  
trackerdict = demo.set1axis(limit_angle = limit_angle, backtrack = backtrack, gcr = gcr, cumulativesky = cumulativesky)


# In[ ]:


foodict = {k: v for k, v in trackerdict.items() if k.startswith('21_'+day_date)}


# In[ ]:


foodict


# In[ ]:


foodict


# In[ ]:


enddate


# In[ ]:


import datetime as dt 
startindex = list(metdata.datetime).index(dt.datetime.strptime(startdate,'%y_%m_%d_%H'))
startindex


# In[ ]:


enddate


# In[ ]:


startindex = list(metdata.datetime).index(dt.datetime.strptime(startdate,'%y_%m_%d_%H'))
startindex


# In[ ]:





# In[ ]:


startdate = list(foodict.keys())[0][:-3]
enddate = list(foodict.keys())[-1][:-3]
trackerdict = demo.gendaylit1axis(trackerdict = foodict, startdate = startdate, enddate = enddate, hpc=True)
trackerdict


# In[ ]:


trackerdict = demo.makeScene1axis(moduletype=moduletype,sceneDict=sceneDict, cumulativesky=cumulativesky, hpc=hpc) #makeScene creates a .rad file with 20 modules per row, 7 rows.
trackerdict = demo.makeOct1axis(customname = sim_name, hpc=hpc)
demo.analysis1axis(customname = sim_name, hpc=hpc)


# #### GencumSky1axis, looping over tracker_angles

# In[ ]:


#Main Variables needed throughout
albedo = 0.6
sim_general_name = 'bifacial_example'
lat = 37.5
lon = -77.6
epwfile = r'C:\Users\sayala\Documents\RadianceScenes\HPC_Test\USA_VA_Richmond.Intl.AP.724010_TMY.epw'
testfolder = r'C:\Users\sayala\Documents\RadianceScenes\HPC_Test\Routine1' 
moduletype = 'Prism Solar Bi60 landscape'

hub_height = 0.2
nMods = 20
nRows = 7
hpc = True

limit_angle = 60
backtrack = True
gcr = 0.35
angledelta = 0.01

starttime = '2021_11_06_10'# 'YY_MM_DD_HH'
endtime = starttime
cumulativesky = True


# In[ ]:


theta = str(20)


# In[ ]:


import bifacial_radiance

sim_name = sim_general_name + theta
demo = bifacial_radiance.RadianceObj(simulationName, path=testfolder)  
demo.setGround(albedo) 
metdata = demo.readWeatherFile(epwfile, starttime=starttime, endttime=endttime, coerce_year=2021)  
sceneDict = {'gcr':gcr,'hub_height':hub_height, 'nMods': nMods, 'nRows': nRows}  
trackerdict =demo.set1axis(limit_angle = limit_angle, backtrack = backtrack, gcr = gcr, cumulativesky = cumulativesky)
trackerdict = demo.genCumSky1axis()
trackerdict = demo.makeScene1axis(trackerdict = trackerdict[tetha], moduletype=moduletype,sceneDict=sceneDict, cumulativesky=cumulativesky, hpc=hpc) #makeScene creates a .rad file with 20 modules per row, 7 rows.
trackerdict = demo.makeOct1axis(customname = sim_name, hpc=hpc)
demo.analysis1axis(customname = sim_name, hpc=hpc)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





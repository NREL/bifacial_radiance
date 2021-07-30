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

# In[ ]:


idx = 4020


# In[2]:


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

sim_name = sim_general_name+'_'+str(idx)
demo = bifacial_radiance.RadianceObj(sim_name,str(testfolder))  
demo.setGround(albedo)
metdata = demo.readWeatherFile(epwfile) 
demo.gendaylit(idx)
sceneDict = {'tilt':tilt,'pitch':pitch,'clearance_height':clearance_height,'azimuth':azimuth, 'nMods': nMods, 'nRows': nRows} 
scene = demo.makeScene(moduletype=moduletype,sceneDict=sceneDict, hpc=hpc, radname = sim_name)
octfile = demo.makeOct(octname = demo.basename , hpc=hpc)  
analysis = bifacial_radiance.AnalysisObj(octfile=octfile, name=sim_name)
frontscan, backscan = analysis.moduleAnalysis(scene=scene)
analysis.analysis(octfile, name=sim_name, frontscan=frontscan, backscan=backscan)


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

# In[5]:


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


# In[86]:


import bifacial_radiance

sim_name = sim_general_name + starttime
demo = bifacial_radiance.RadianceObj(sim_name, path=testfolder)  
demo.setGround(albedo) 
metdata = demo.readWeatherFile(epwfile, coerce_year=2021, daydate='05_01')  
sceneDict = {'gcr':gcr,'hub_height':hub_height, 'nMods': nMods, 'nRows': nRows}  
trackerdict = demo.set1axis(limit_angle = limit_angle, backtrack = backtrack, gcr = gcr, cumulativesky = cumulativesky)


# In[80]:


metdata = demo.readWeatherFile(epwfile, coerce_year=2021, daydate='21_05_22')  
sceneDict = {'gcr':gcr,'hub_height':hub_height, 'nMods': nMods, 'nRows': nRows}  
trackerdict = demo.set1axis(limit_angle = limit_angle, backtrack = backtrack, gcr = gcr, cumulativesky = cumulativesky)


# In[41]:


foodict = {k: v for k, v in trackerdict.items() if k.startswith('21_'+day_date)}


# In[47]:


foodict


# In[43]:


foodict


# In[53]:


enddate


# In[55]:


import datetime as dt 
startindex = list(metdata.datetime).index(dt.datetime.strptime(startdate,'%y_%m_%d_%H'))
startindex


# In[72]:


enddate


# In[78]:


startindex = list(metdata.datetime).index(dt.datetime.strptime(startdate,'%y_%m_%d_%H'))
startindex


# In[ ]:





# In[75]:


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


# In[7]:


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





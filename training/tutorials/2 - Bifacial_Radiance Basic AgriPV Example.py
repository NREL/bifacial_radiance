#!/usr/bin/env python
# coding: utf-8

# # 2 - bifacial_radiance Basic AgriPV Example
# 
# 
# This journal shows how to model an AgriPV site, calculating the irradiance not only on the modules but also the irradiance received by the ground to evaluate available solar ersource for plants. 
# 
# We assume that `bifacia_radiance` and `radiance` are properly installed.
# 
# These journal outlines 4 useful uses of bifacial_radiance and some tricks: 
# 
# * Creating the modules in the AgriPV site
# * Adding extra geometry for the pillars/posts supporting the AgriPV site
# * Hacking the sensors to sample the ground irradiance and create irradiance map
# * Adding object to simulate variations in ground albedo from different crops between rows.
# 
# 
# #### Steps:
# 
# 1. <a href='#step1'> Generate the geometry </a>
# 2. <a href='#step2'> Analyse the Ground Irradiance </a>
# 3. <a href='#step3'> Analyse and Map the Ground Irradiance </a>
# 4. <a href='#step4'> Adding different Albedo Section </a>
#     
# #### Preview of what we will create: 
#     
# ![Another view](images/AgriPV_2.PNG)
# ![AgriPV Image We will create](images/AgriPV_1.PNG)
# And this is how it will look like:
# 
# ![AgriPV modeled step 4](images/AgriPV_step4.PNG)
# 
# 

# ## 0. Setup 

# In[ ]:


get_ipython().run_cell_magic('bash', '', 'wget https://github.com/LBNL-ETA/Radiance/releases/download/012cb178/Radiance_012cb178_Linux.zip -O radiance.zip\nunzip radiance.zip\ntar -xvf radiance-5.3.012cb17835-Linux.tar.gz;\n')


# In[ ]:


get_ipython().system('pip install git+https://github.com/NREL/bifacial_radiance.git@development')


# In[ ]:


#!cp -r radiance-5.3.012cb17835-Linux/usr/local/radiance/bin/* /usr/local/bin
#!cp -r radiance-5.3.012cb17835-Linux/usr/local/radiance/lib/* /usr/local/lib
#!rm -r radiance*


# In[ ]:


import os
os.environ['PATH'] += ":radiance-5.3.012cb17835-Linux/usr/local/radiance/bin"
os.environ['LIBRARYPATH'] += ":radiance-5.3.012cb17835-Linux/usr/local/radiance/lib"
os.environ['RAYPATH'] = ":radiance-5.3.012cb17835-Linux/usr/local/radiance/lib"


# ## 1. Create bifacial_radiance object

# In[ ]:


import bifacial_radiance as br
import numpy as np
import pandas as pd


# In[ ]:


# This information helps with debugging and getting support :)
import sys, platform
print("Working on a ", platform.system(), platform.release())
print("Python version ", sys.version)
print("Pandas version ", pd.__version__)
print("bifacial_radiance version ", br.__version__)


# In[ ]:


import os
from pathlib import Path

testfolder = 'TEMP'

if not os.path.exists(testfolder):
    os.makedirs(testfolder)
    
print ("Your simulation will be stored in %s" % testfolder)


# In[ ]:


simulationname = 'tutorial_1'

# Location:
lat = 25.2854 # ° N, 
lon = 51.5310 # ° E

# Scene Parameters:
azimuth_ang=90 # Facing south
tilt = 30 # tilt.
numpanels = 3

# MakeModule Parameters
moduletype='test-module'
numpanels = 3  # AgriPV site has 3 modules along the y direction
module_x = 2 # m
module_y = 1 # m. slope we will measure x>y landscape.
ygap = 0.03 # m
xgap = 1.5 # m

# SceneDict Parameters
pitch = 7 # m
albedo = 0.2  # 'grass'     # ground albedo
clearance_height = 2.5 # m  
nMods = 5 # six modules per row.
nRows = 3  # 3 row


# In[ ]:


demo = br.RadianceObj(simulationname,path = testfolder)  
demo.setGround(albedo) 
epwfile = demo.getEPW(lat, lon) # NJ lat/lon 40.0583° N, 74.4057


# In[ ]:


module=demo.makeModule(name=moduletype,x=module_x,y=module_y)


# In[ ]:


#Valid options: mm_dd, mm_dd_HH, mm_dd_HHMM, YYYY-mm-dd_HHMM
metdata = demo.readWeatherFile(epwfile, coerce_year=2023, starttime='2023-12-04', endtime='2023-12-04')


# In[ ]:


demo.gendaylit(timeindex=7)  


# In[ ]:


sceneDict = {'tilt':tilt,'pitch': pitch,'clearance_height':clearance_height,'azimuth':azimuth_ang, 
             'nMods': nMods, 'nRows': nRows}  
scene = demo.makeScene(module=moduletype, sceneDict=sceneDict) 


# In[ ]:


octfile = demo.makeOct()


# In[ ]:


analysis = br.AnalysisObj(octfile, demo.name)  
frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=sensorsy)


# In[ ]:


analysis.analysis(octfile, simulationname+"_modulescan", frontscan, backscan)  # compare the back vs front irradiance  


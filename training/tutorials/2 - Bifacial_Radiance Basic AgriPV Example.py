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

# In[1]:


import bifacial_radiance as br
import numpy as np
import pandas as pd


# In[2]:


# This information helps with debugging and getting support :)
import sys, platform
print("Working on a ", platform.system(), platform.release())
print("Python version ", sys.version)
print("Pandas version ", pd.__version__)
print("bifacial_radiance version ", br.__version__)


# In[3]:


import os
from pathlib import Path

testfolder = 'TEMP'

if not os.path.exists(testfolder):
    os.makedirs(testfolder)
    
print ("Your simulation will be stored in %s" % testfolder)


# In[5]:


demo = br.RadianceObj('AgriPV_example',path = testfolder)  


# ### Download and read the weather data

# In[6]:


#Valid options: mm_dd, mm_dd_HH, mm_dd_HHMM, YYYY-mm-dd_HHMM
epwfile = demo.getEPW(25.2854, 51.5310) # Doha!
metdata = demo.readWeatherFile(epwfile, coerce_year=2023, starttime='2023-12-04', endtime='2023-12-04')


# ### Set the albedom

# In[7]:


demo.setGround() # You can pass a value for  fixed value, or empty it will grab the albedo column from the weatherdata 


# ### Make the module

# In[8]:


# MakeModule Parameters
modulename='3-up-collector'
numpanels = 3  # AgriPV site has 3 modules along the y direction
module_x = 2 # m
module_y = 1 # m. slope we will measure x>y landscape.
ygap = 0.03 # m
xgap = 1.5 # m
zgap = 0.1 # m

# TorqueTube Parameters
tubetype='square' # Other options: 'square' , 'hex'
material = 'Metal_Grey' # Other options: 'black'
diameter = 0.1 # m
axisofrotationTorqueTube = False
zgap = 0.05 # m
visible = True 

#Add torquetube 
tubeParams = {'tubetype':tubetype,
              'diameter':diameter,
              'material':material,
              'axisofrotation':False,
              'visible':True}

module=demo.makeModule(name=modulename,x=module_x,y=module_y,numpanels=numpanels, 
                       xgap=xgap, ygap=ygap, zgap=zgap, tubeParams=tubeParams)


# ### Make the Sky

# In[9]:


metdata.datetime


# In[10]:


timeindex = metdata.datetime.index(pd.to_datetime('2023-12-04 13:00:0 +4'))  # Make this timezone aware, use -5 for EST.
demo.gendaylit(timeindex)  


# ### Make the Scene

# In[11]:


# Scene Parameters:
azimuth_ang=90 # Facing south
tilt = 20 # tilt.
pitch = 7 # m
albedo = 0.2  # 'grass'     # ground albedo
clearance_height = 2.5 # m  
nMods = 5 # six modules per row.
nRows = 3  # 3 row

sceneDict = {'tilt':tilt,'pitch': pitch,'clearance_height':clearance_height,'azimuth':azimuth_ang, 
             'nMods': nMods, 'nRows': nRows}  

scene = demo.makeScene(module=modulename, sceneDict=sceneDict) 


# ### Put it all together

# In[12]:


octfile = demo.makeOct()


# If desired, you can view the Oct file at this point:
# 
# ***rvu -vf views\front.vp -e .01 tutorial_1.oct***

# In[13]:


## Comment the ! line below to run rvu from the Jupyter notebook instead of your terminal.
## Simulation will stop until you close the rvu window

# !rvu -vf views\front.vp -e .01 tutorial_1.oct


# And adjust the view parameters, you should see this image.
# 
# ![AgriPV modeled step 1](images/AgriPV_step1.PNG)
# 

# ### Analyze the Panel

# In[14]:


analysis = br.AnalysisObj(octfile, demo.name)  
frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=3, modWanted=1, rowWanted=2) 


# In[21]:


moduleresultsfront, moduleresultsback = analysis.analysis(octfile, "_modulescan", frontscan, backscan)  # compare the back vs front irradiance


# ### Analyze the Ground 

# In[28]:


sensorsground = 5
frontscan, backscan, groundscan = analysis.moduleAnalysis(scene, sensorsy=3, sensorsground = 2) 


# In[30]:


groundresults, moduleresultsback = analysis.analysis(octfile, "_groundscan", groundscan, backscan)  # compare the back vs front irradiance  


# ![AgriPV modeled step 4](images/spacing_between_modules.PNG)

# In[ ]:





#!/usr/bin/env python
# coding: utf-8

# # 16 - AgriPV - 3-up and 4-up collector optimization
# 
# 
# This journal helps the exploration of varying collector widths and xgaps in the ground underneath as well as on the rear irradiance for bifacial AgriPV. The optimization varies the numpanels combinations with xgaps for having 3-up and 4-up collectors with varying space along the row (xgap). The actual raytracing is not performed in the jupyter journal but rather on the HPC, but the geometry is the same as presented here.
# 
# The steps on this journal:
# 1. <a href='#step1'> Making Collectors for each number panel and xgap case </a>
# 2. <a href='#step2'> Builds the Scene so it can be viewed with rvu </a>
# 
# 
# An area of 40m x 20 m area is sampled on the HPC, and is highlighted in the visualizations below with an appended terrain of 'litesoil'. The image below shows the two extremes of the variables optimized and the raytrace results, including the worst-case shading experienced under the array ( 100 - min_irradiance *100 / GHI).
# 
# 
# 
# ![AgriPV Collector Width and Xgap Optimization](../images_wiki/AdvancedJournals/AgriPV_CWandXgap_Optimization.PNG)
# 

# In[1]:


import os
from pathlib import Path

testfolder = Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP' /  'Tutorial_16'
if not os.path.exists(testfolder):
    os.makedirs(testfolder)

print ("Your simulation will be stored in %s" % testfolder)


# In[2]:


import bifacial_radiance
import numpy as np

rad_obj = bifacial_radiance.RadianceObj('tutorial_16', str(testfolder)) 


# <a id='step1'></a>

# ## 1. Making Collectors for each number panel and xgap case

# In[3]:


x = 2
y = 1
ygap = 0.1524 # m = 6 in
zgap = 0.002 # m, veyr little gap to torquetube.

tubeParams = {'diameter':0.15,
              'tubetype':'square',
              'material':'Metal_Grey',
              'axisofrotation':True,
               'visible': True}

ft2m = 0.3048
xgaps = [3, 4, 6, 9, 12, 15, 18, 21]
numpanelss = [3, 4]


# Loops
for ii in range(0, len(numpanelss)):
    numpanels = numpanelss[ii]
    for jj in range(0, len(xgaps)):
        xgap = xgaps[jj]*ft2m

        moduletype = 'test-module_'+str(numpanels)+'up_'+str(round(xgap,1))+'xgap'
        rad_obj.makeModule(moduletype, 
                    x=x, y=y, 
                    xgap=xgap, zgap=zgap, ygap = ygap, numpanels=numpanels, 
                    tubeParams=tubeParams)


# <a id='step2'></a>

# ## 2. Build the Scene so it can be viewed with rvu

# In[4]:


xgaps = np.round(np.array([3, 4, 6, 9, 12, 15, 18, 21]) * ft2m,1)
numpanelss = [3, 4]
sensorsxs = np.array(list(range(0, 201)))   

# Select CASE:
xgap = np.round(xgaps[-1],1)
numpanels = 4

# All the rest

ft2m = 0.3048
hub_height = 8.0 * ft2m
y = 1
pitch = 0.001 # If I recall, it doesn't like when pitch is 0 even if it's a single row, but any value works here. 
ygap = 0.15
tilt = 18

sim_name = ('Coffee_'+str(numpanels)+'up_'+
            str(round(xgap,1))+'_xgap')

albedo = 0.35 # Grass value from Torres Molina, "Measuring UHI in Puerto Rico" 18th LACCEI 
            # International Multi-Conference for Engineering, Education, and Technology

azimuth = 180
if numpanels == 3:
    nMods = 9
if numpanels == 4:
    nMods = 7
nRows = 1

moduletype = 'test-module_'+str(numpanels)+'up_'+str(round(xgap,1))+'xgap'

rad_obj.setGround(albedo)
lat = 18.202142
lon = -66.759187
metfile = rad_obj.getEPW(lat,lon)
rad_obj.readWeatherFile(metfile)

sceneDict = {'tilt':tilt,'pitch':pitch,'hub_height':hub_height,'azimuth':azimuth, 'nMods': nMods, 'nRows': nRows} 
scene = rad_obj.makeScene(module=moduletype,sceneDict=sceneDict,  radname = sim_name)

rad_obj.gendaylit(4020)


octfile = rad_obj.makeOct(filelist = rad_obj.getfilelist(), octname = rad_obj.basename)  

name='SampleArea'
text='! genbox litesoil cuteBox 40 20 0.01 | xform -t -20 -10 0.01'
customObject =rad_obj.makeCustomObject(name,text)
rad_obj.appendtoScene(scene.radfiles, customObject, '!xform -rz 0')

octfile = rad_obj.makeOct(rad_obj.getfilelist())  


# 
# ### To View the generated Scene, you can navigate to the testfolder on a terminal and use:
# 
# <b>front view:</b>
# > rvu -vf views\front.vp -e .0265652 -vp 2 -21 2.5 -vd 0 1 0 makemod.oct
# 
# <b> top view: </b>
# > rvu -vf views\front.vp -e .0265652 -vp 5 0 70 -vd 0 0.0001 -1 makemod.oct
#     
# <b> Or run it directly from Jupyter by removing the comment from the following cell: </b>
# 

# In[5]:



## Comment the ! line below to run rvu from the Jupyter notebook instead of your terminal.
## Simulation will stop until you close the rvu window

#!rvu -vf views\front.vp -e .0265652 -vp 2 -21 2.5 -vd 0 1 0 makemod.oct
#!rvu -vf views\front.vp -e .0265652 -vp 5 0 70 -vd 0 0.0001 -1 makemod.oct


#!/usr/bin/env python
# coding: utf-8

# # Vertical Shading 

# ## 1. Yearly Irradiance and Shading

# ![image.png](attachment:image.png)

# In[1]:


import os
from pathlib import Path

testfolder = str(Path().resolve().parent / 'TEMP' /  'August')

if not os.path.exists(testfolder):
    os.makedirs(testfolder)
    
print ("Your simulation will be stored in %s" % testfolder)


# In[2]:


import bifacial_radiance as br
import numpy as np
import pandas as pd


# In[3]:


# This information helps with debugging and getting support :)
import sys, platform
print("Working on a ", platform.system(), platform.release())
print("Python version ", sys.version)
print("Pandas version ", pd.__version__)
print("bifacial_radiance version ", br.__version__)


# In[4]:


testopstelling = br.RadianceObj('x',str(testfolder))

testopstelling.setGround()
albedo = 0.35
testopstelling.setGround(albedo)


# Make Module:

# In[5]:


#2-up landscape
simpleModule = True

moduletype = 'test-module'

num_panels = 2
x = 2
y = 1

x_gap = 0.20
y_gap = 0.10
z_gap = 0

num_cells_x = 12
num_cells_y = 24
x_cell = 0.17283
y_cell = 0.08692
x_cell_gap = 0.002
y_cell_gap = 0.002

cellLevelModuleParams = {'numcellsx': num_cells_y, 'numcellsy': num_cells_x,
                         'xcell': y_cell, 'ycell': x_cell, 'xcellgap': y_cell_gap, 'ycellgap': x_cell_gap}


if simpleModule:
    module = testopstelling.makeModule(name=moduletype, x=x, y=y, numpanels=num_panels,
                                   xgap=x_gap, ygap=y_gap)
else:
    module = testopstelling.makeModule(name=moduletype, x=x, y=y, numpanels=num_panels,
                                   xgap=x_gap, ygap=y_gap, cellModule=cellLevelModuleParams)



# In[6]:


#epwfile = r'C:/Users/Gebruiker/Downloads/tmy_51.036_2.658_2005_2020 (1).epw'
epwfile = testopstelling.getEPW(lat=33,lon=-110)
metdata = testopstelling.readWeatherFile(epwfile)


# Scene parameters

# In[8]:


pitch = 9  # m
hub_height = 1.75  # m  2.8m to top; -1 m for module, -0.5 xgap
nMods = 6  # six modules per row.
nRows = 3  # 3 row
azimuth_ang = 270  # Facing west
tilt = 90  # tilt.

sceneDict = {'tilt': tilt, 'pitch': pitch, 'hub_height': hub_height, 'azimuth': azimuth_ang, 'nMods': nMods,
             'nRows': nRows}


# In[9]:


testopstelling.genCumSky() # entire year.


# In[10]:


scene = testopstelling.makeScene(module=moduletype, sceneDict=sceneDict)


# In[11]:


octfile = testopstelling.makeOct(testopstelling.getfilelist()) 


# In[12]:


analysis = br.AnalysisObj(octfile, testopstelling.basename)


# ### Without Frame evaluation

# In[13]:


frontscan, backscan = analysis.moduleAnalysis(scene, modWanted = 4, rowWanted =2,  sensorsx=12, sensorsy=12)
results = analysis.analysis(octfile, testopstelling.basename+'baseline', frontscan, backscan)


# ## WITH frame

# In[15]:


torquetubelength = 14.036
postheight = 0.03
postwidth = 0.06

#horizontale palen
post_x = -2.25 #verschuift palen van links naar rechts, hoe negatiever hoe meer naar links
z_step = 1.09 #verhoogt de palen
y_step = 9 #bepaald de afstand tussen de verschillende rijen

y = 9.1

for i in range(3):
    post_z = 2.84
    for j in range(3):
        name = 'Post{}{}'.format(i, j)
        text = '! genbox Metal_Aluminum_Anodized torquetube_row2 {} {} {} | xform -t {} -0.2 0.15 | xform -t {} {} {} ' \
               '| ' \
               'xform -rz 90'.format(
            torquetubelength, postheight, postwidth, (-torquetubelength + module.sceney) / 2.0, post_x, y, post_z)
        customObject = testopstelling.makeCustomObject(name, text)
        testopstelling.appendtoScene(radfile=scene.radfiles, customObject=customObject)
        post_z -= z_step

    y -= y_step
pileheight = 3.05
pilewidth = 0.17
piledepth = 0.08


# In[16]:


#nulpunt paal
x_value = 0
y_value = 0
name_string = 'pileZERO'
text = ('! genbox Metal_Grey pile{}row{} ' + '{} {} {} '.format(0.1, 0.1, 10)
        + '| xform -t {} {} {}'.format(x_value, y_value, 0))
customObject = testopstelling.makeCustomObject(name_string, text)
testopstelling.appendtoScene(scene.radfiles, customObject)

#verticale palen
x_offset = - 0.1
y_step = 2.15

x_value = -9.1
for i in range(3):
    y_value = -8.23
    for j in range(7):
        name_string = 'pile{}{}'.format(i, j)
        text = ('! genbox Metal_Grey pile{}row{} '.format(i, j) + '{} {} {} '.format(pilewidth, piledepth, pileheight)
                + '| xform -t {} {} {}'.format(x_value, y_value, 0))
        customObject = testopstelling.makeCustomObject(name_string, text)
        testopstelling.appendtoScene(scene.radfiles, customObject)
        y_value += 2.331

    x_value += 9


# #### Append grass material

# In[ ]:


# Try to run only once or it keeps adding it to the file every run
#testopstelling.addMaterial('grass', Rrefl=.0, Grefl=.170, Brefl=.0)


# In[17]:


name='gras_ondergrond'
carpositionx=-2
carpositiony=-1
text='! genbox grass CenterPatch 18 25 0.1 | xform -t -10 -13 0'.format(carpositionx, carpositiony)
customObject = testopstelling.makeCustomObject(name,text)
testopstelling.appendtoScene(scene.radfiles, customObject)


# #### Sanity check

# In[18]:


#testopstelling.scene.showScene()


# Another way to view, but you NEED to have a single hour sun, and an updated octfile

# In[ ]:


#testopstelling.gendaylit1axis(4000)


# In[ ]:


#testopstelling.makeOct()


# In[ ]:


#!rvu -vf views\front.vp -e .01 -pe 0.02 -vp -2 -12 14.5 x.oct


# In[19]:


octfile = testopstelling.makeOct(testopstelling.getfilelist()) 


# In[21]:


frontscan, backscan = analysis.moduleAnalysis(scene, modWanted = 4, rowWanted =2,  sensorsx=12, sensorsy=12)
analysis.analysis(octfile, testopstelling.basename, frontscan, backscan)


# ## 2. Hourly Irradiance (1-axis method)

# Rerunning weatherfile to do only 1 day 

# In[27]:


metdata = testopstelling.readWeatherFile(epwfile, coerce_year=2021, starttime='2021-06-01', endtime='2021-06-01')


# In[22]:


# -- establish tracking angles
fixed_tilt_angle = 90 # Vertical
cumulativesky = False # Want to do hourly simulations

trackerParams = {
             'cumulativesky':cumulativesky,
             'azimuth': azimuth_ang,
             'fixed_tilt_angle': fixed_tilt_angle
             }


# In[28]:


trackerdict = testopstelling.set1axis(**trackerParams)


# In[29]:


trackerdict = testopstelling.makeScene1axis(module=moduletype,sceneDict=sceneDict)


# In[32]:


trackerdict = testopstelling.gendaylit1axis()


# In[33]:


trackerdict = testopstelling.makeOct1axis()


# ### Hourly baseline without racking

# In[ ]:


trackerdict = demo.analysis1axis(customname = 'Baseline', sensorsy=2, sensorsx=2)


# # @Chris: How to append the objects here like in the fixed tilt routine above. Thanks.

# In[ ]:


# ADD GEOMETRY HERE


# In[ ]:


#redo Oct with the new geometry
trackerdict = testopstelling.makeOct1axis()


# In[ ]:


trackerdict = demo.analysis1axis(sensorsy=2, sensorsx=2)


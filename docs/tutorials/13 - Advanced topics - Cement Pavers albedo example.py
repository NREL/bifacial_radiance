#!/usr/bin/env python
# coding: utf-8

# # 13 - Advanced topics - Cement Pavers albedo example
# 
# This journal creates a paver underneath the single-axis trackers, and evaluates the improvement for noon, June 17th with and without the pavers for a location in Davis, CA.
# 
# ![Paver](../images_wiki/AdvancedJournals/Pavers.PNG)
# 
# Measurements:
# ![Paver](../images_wiki/AdvancedJournals/Pavers_Geometry.PNG)

# In[1]:


import os
from pathlib import Path

testfolder = str(Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP' / 'NewMat')

# Another option using relative address; for some operative systems you might need '/' instead of '\'
# testfolder = os.path.abspath(r'..\..\bifacial_radiance\TEMP')  

try:
    os.stat(testfolder)
except:
    os.mkdir(testfolder)
    
print ("Your simulation will be stored in %s" % testfolder)


# In[2]:


from bifacial_radiance import *   
import numpy as np


# In[3]:


timestamp = 4020 # Noon, June 17th. 
simulationname = 'PVEL_Davis'

#Location:
lat = 38.5449 # Davis, CA
lon = -121.7405 # Davis, CA
# MakeModule Parameters
moduletype='60cellmod'
numpanels = 1  # AgriPV site has 3 modules along the y direction (N-S since we are facing it to the south) .
x = 0.95  
y = 1.838
xgap = 0.02# Leaving 2 centimeters between modules on x direction
ygap = 0.0 # 1 - up 
zgap = 0.06 # gap between modules and torquetube.

# Other default values:

# TorqueTube Parameters
axisofrotationTorqueTube=True
torqueTube = False
cellLevelModule = True

numcellsx = 6
numcellsy = 10
xcell = 0.156
ycell = 0.158
xcellgap = 0.015
ycellgap = 0.015

sensorsy = numcellsy   # one sensor per cell

cellLevelModuleParams = {'numcellsx': numcellsx, 'numcellsy':numcellsy, 
                         'xcell': xcell, 'ycell': ycell, 'xcellgap': xcellgap, 'ycellgap': ycellgap}

# SceneDict Parameters
gcr = 0.33 # m
albedo = 0.2  #'grass'     # ground albedo
hub_height = 1.237 # m  
nMods = 20 # six modules per row.
nRows = 3  # 3 row

azimuth_ang = 90 # Facing east 


demo = RadianceObj(simulationname,path = testfolder)  # Create a RadianceObj 'object'
demo.setGround(albedo) # input albedo number or material name like 'concrete'.  To see options, run this without any input.
epwfile = demo.getEPW(lat, lon) # NJ lat/lon 40.0583° N, 74.4057
metdata = demo.readEPW(epwfile) # read in the EPW weather data from above
moduleDict=demo.makeModule(name=moduletype,x=x,y=y,numpanels = numpanels, xgap=xgap, ygap=ygap, cellLevelModuleParams = cellLevelModuleParams)


# In[4]:


description = 'Sherman Williams "Chantilly White" acrylic paint'
materialpav = 'sw_chantillywhite'
Rrefl = 0.5
Grefl = 0.5 
Brefl = 0.5
demo.addMaterial(material=materialpav, Rrefl=Rrefl, Grefl=Grefl, Brefl=Brefl, comment=description)


# In[5]:


demo.gendaylit(timestamp)
tilt = demo.getSingleTimestampTrackerAngle(metdata, timeindex=timestamp, gcr=gcr, 
                                   axis_azimuth=180, axis_tilt=0, 
                                   limit_angle=60, backtrack=True)
# create a scene with all the variables
sceneDict = {'tilt':tilt,'gcr': gcr,'hub_height':hub_height,'azimuth':azimuth_ang, 'module_type':moduletype, 'nMods': nMods, 'nRows': nRows}  
scene = demo.makeScene(moduletype=moduletype, sceneDict=sceneDict) #makeScene creates a .rad file with 20 modules per row, 7 rows.
octfile = demo.makeOct(demo.getfilelist())  # makeOct combines all of the ground, sky and object fil|es into a .oct file.


# ### Simulation without Pavers

# In[6]:


analysis = AnalysisObj(octfile, demo.name)  # return an analysis object including the scan dimensions for back irradiance
frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=sensorsy)
analysis.analysis(octfile, simulationname+"_noPavers", frontscan, backscan)  # compare the back vs front irradiance  
print("Simulation without Pavers Finished")


# ### Simulation With Pavers

# In[7]:


torquetubelength = moduleDict['scenex']*(nMods) 
pitch = demo.moduleDict['sceney']/gcr
startpitch = -pitch * (nRows-1)/2
p_w = 0.947 # m
p_h = 0.092 # m
p_w2 = 0.187 # m
p_h2 = 0.184 # m
offset_w1y = -(p_w/2)+(p_w2/2)
offset_w2y = (p_w/2)-(p_w2/2)

for i in range (0, nRows):    
    name='PAVER'+str(i)
    text='! genbox {} paver{} {} {} {} | xform -t {} {} 0 | xform -t {} 0 0'.format(materialpav, i, 
                                    p_w, torquetubelength, p_h, 
                                    -p_w/2, (-torquetubelength+moduleDict['sceney'])/2.0,
                                    startpitch+pitch*i)
    text += '\r\n! genbox {} paverS1{} {} {} {} | xform -t {} {} 0 | xform -t {} 0 0'.format(materialpav, i,
                                    p_w2, torquetubelength, p_h2, 
                                    -p_w2/2+offset_w1y, (-torquetubelength+moduleDict['sceney'])/2.0,
                                    startpitch+pitch*i)
    text += '\r\n! genbox {} paverS2{} {} {} {} | xform -t {} {} 0 | xform -t {} 0 0'.format(materialpav, i,
                                    p_w2, torquetubelength, p_h2, 
                                    -p_w2/2+offset_w2y, (-torquetubelength+moduleDict['sceney'])/2.0,
                                    startpitch+pitch*i)

    customObject = demo.makeCustomObject(name,text)
    demo.appendtoScene(radfile=scene.radfiles, customObject=customObject, text="!xform -rz 0")


# In[8]:


demo.makeOct()


# ### rvu -vf views\front.vp -e .01 -pe 0.01 -vp -5 -14 1 -vd 0 0.9946 -0.1040 PVEL_Davis.oct

# In[9]:


analysis = AnalysisObj(octfile, demo.name)  # return an analysis object including the scan dimensions for back irradiance
frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=sensorsy)
analysis.analysis(octfile, simulationname+"_WITHPavers", frontscan, backscan)  # compare the back vs front irradiance  
print("Simulation WITH Pavers Finished")


# In[10]:


df_0 = load.read1Result(os.path.join(testfolder, 'results', 'irr_PVEL_Davis_noPavers.csv'))
df_w = load.read1Result(os.path.join(testfolder, 'results', 'irr_PVEL_Davis_WITHPavers.csv'))                        


# In[11]:


df_0


# In[12]:


df_w


# ## Improvement in Rear Irradiance

# In[18]:


round((df_w['Wm2Back'].mean()-df_0['Wm2Back'].mean())*100/df_0['Wm2Back'].mean(),1)


# In[ ]:





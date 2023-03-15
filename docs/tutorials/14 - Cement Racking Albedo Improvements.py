#!/usr/bin/env python
# coding: utf-8

# # 14 - Cement Racking Albedo Improvements
# 
# This journal creates a paver underneath the single-axis trackers, and evaluates the improvement for one day -- June 17th with and without the pavers for a location in Davis, CA.
# 
# ![Paver](../images_wiki/AdvancedJournals/Pavers.PNG)
# 

# Measurements:
# ![Paver](../images_wiki/AdvancedJournals/Pavers_Geometry.PNG)

# In[1]:


import os
from pathlib import Path
import pandas as pd

testfolder = str(Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP' / 'Tutorial_14')
if not os.path.exists(testfolder):
    os.makedirs(testfolder)
    
print ("Your simulation will be stored in %s" % testfolder)


# In[2]:


from bifacial_radiance import *   
import numpy as np


# In[3]:


simulationname = 'tutorial_14'

#Location:
lat = 38.5449 # Davis, CA
lon = -121.7405 # Davis, CA
# MakeModule Parameters
moduletype='test-module'
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
demo.setGround(albedo) #
epwfile = demo.getEPW(lat, lon) 
metdata = demo.readWeatherFile(epwfile, coerce_year=2021) # read in the EPW weather data from above
mymodule=demo.makeModule(name=moduletype,x=x,y=y,numpanels = numpanels, xgap=xgap, ygap=ygap)
mymodule.addCellModule(numcellsx=numcellsx, numcellsy=numcellsy,
                       xcell=xcell, ycell=ycell, xcellgap=xcellgap, ycellgap=ycellgap)


# In[4]:


description = 'Sherman Williams "Chantilly White" acrylic paint'
materialpav = 'sw_chantillywhite'
Rrefl = 0.5
Grefl = 0.5 
Brefl = 0.5
demo.addMaterial(material=materialpav, Rrefl=Rrefl, Grefl=Grefl, Brefl=Brefl, comment=description)


# ## Simulation without Pavers

# In[5]:


timeindex = metdata.datetime.index(pd.to_datetime('2021-06-17 12:0:0 -8'))  # Davis, CA is TZ -8
demo.gendaylit(timeindex)  
    
tilt = demo.getSingleTimestampTrackerAngle(timeindex=timeindex, gcr=gcr, 
                                   azimuth=180, axis_tilt=0, 
                                   limit_angle=60, backtrack=True)
# create a scene with all the variables
sceneDict = {'tilt':tilt,'gcr': gcr,'hub_height':hub_height,'azimuth':azimuth_ang, 'module_type':moduletype, 'nMods': nMods, 'nRows': nRows}  
scene = demo.makeScene(module=mymodule, sceneDict=sceneDict) #makeScene creates a .rad file with 20 modules per row, 7 rows.
octfile = demo.makeOct(demo.getfilelist())  # makeOct combines all of the ground, sky and object fil|es into a .oct file.


# In[6]:


analysis = AnalysisObj(octfile, demo.name)  # return an analysis object including the scan dimensions for back irradiance
frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=sensorsy)
analysis.analysis(octfile, simulationname+"_noPavers", frontscan, backscan)  # compare the back vs front irradiance  
print("Simulation without Pavers Finished")


# ## Looping on the day

# In[7]:


j=0
starttimeindex = metdata.datetime.index(pd.to_datetime('2021-06-17 7:0:0 -8'))
endtimeindex = metdata.datetime.index(pd.to_datetime('2021-06-17 19:0:0 -8'))
for timess in range (starttimeindex, endtimeindex):
    j+=1
    demo.gendaylit(timess)
    tilt = demo.getSingleTimestampTrackerAngle(metdata=metdata, timeindex=timess, gcr=gcr, 
                                       azimuth=180, axis_tilt=0, 
                                       limit_angle=60, backtrack=True)
    # create a scene with all the variables
    sceneDict = {'tilt':tilt,'gcr': gcr,'hub_height':hub_height,'azimuth':azimuth_ang, 'module_type':moduletype, 'nMods': nMods, 'nRows': nRows}  
    scene = demo.makeScene(module=mymodule, sceneDict=sceneDict) #makeScene creates a .rad file with 20 modules per row, 7 rows.
    octfile = demo.makeOct(demo.getfilelist())  # makeOct combines all of the ground, sky and object fil|es into a .oct file
    frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=sensorsy)
    analysis.analysis(octfile, simulationname+"_noPavers_"+str(j), frontscan, backscan)  # compare the back vs front irradiance  
    


# ## Simulation With Pavers

# In[8]:


demo.gendaylit(timeindex)
tilt = demo.getSingleTimestampTrackerAngle(metdata=metdata, timeindex=timeindex, gcr=gcr, 
                                   azimuth=180, axis_tilt=0, 
                                   limit_angle=60, backtrack=True)
# create a scene with all the variables
sceneDict = {'tilt':tilt,'gcr': gcr,'hub_height':hub_height,'azimuth':azimuth_ang, 'module_type':moduletype, 'nMods': nMods, 'nRows': nRows}  
scene = demo.makeScene(module=mymodule, sceneDict=sceneDict) #makeScene creates a .rad file with 20 modules per row, 7 rows.


# In[9]:


torquetubelength = demo.module.scenex*(nMods) 
pitch = demo.module.sceney/gcr
startpitch = -pitch * (nRows-1)/2
p_w = 0.947 # m
p_h = 0.092 # m
p_w2 = 0.187 # m
p_h2 = 0.184 # m
offset_w1y = -(p_w/2)+(p_w2/2)
offset_w2y = (p_w/2)-(p_w2/2)

customObjects = []
for i in range (0, nRows):    
    name='PAVER'+str(i)
    text='! genbox {} paver{} {} {} {} | xform -t {} {} 0 | xform -t {} 0 0'.format(materialpav, i, 
                                    p_w, torquetubelength, p_h, 
                                    -p_w/2, (-torquetubelength+demo.module.sceney)/2.0,
                                    startpitch+pitch*i)
    text += '\r\n! genbox {} paverS1{} {} {} {} | xform -t {} {} 0 | xform -t {} 0 0'.format(materialpav, i,
                                    p_w2, torquetubelength, p_h2, 
                                    -p_w2/2+offset_w1y, (-torquetubelength+demo.module.sceney)/2.0,
                                    startpitch+pitch*i)
    text += '\r\n! genbox {} paverS2{} {} {} {} | xform -t {} {} 0 | xform -t {} 0 0'.format(materialpav, i,
                                    p_w2, torquetubelength, p_h2, 
                                    -p_w2/2+offset_w2y, (-torquetubelength+demo.module.sceney)/2.0,
                                    startpitch+pitch*i)

    customObject = demo.makeCustomObject(name,text)
    customObjects.append(customObject)
    demo.appendtoScene(radfile=scene.radfiles, customObject=customObject, text="!xform -rz 0")


# In[10]:


demo.makeOct()


# You can view the geometry generated in the terminal with:
# 
# **rvu -vf views\front.vp -e .01 -pe 0.01 -vp -5 -14 1 -vd 0 0.9946 -0.1040 tutorial_14.oct**

# In[11]:



## Comment the ! line below to run rvu from the Jupyter notebook instead of your terminal.
## Simulation will stop until you close the rvu window

#!rvu -vf views\front.vp -e .01 -pe 0.01 -vp -5 -14 1 -vd 0 0.9946 -0.1040 tutorial_14.oct


# In[12]:


analysis = AnalysisObj(octfile, demo.name)  # return an analysis object including the scan dimensions for back irradiance
frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=sensorsy)
analysis.analysis(octfile, simulationname+"_WITHPavers", frontscan, backscan)  # compare the back vs front irradiance  
print("Simulation WITH Pavers Finished")


# ## LOOP WITH PAVERS

# In[13]:


j=0
for timess in range (starttimeindex, endtimeindex):
    j+=1
    demo.gendaylit(timess)
    tilt = demo.getSingleTimestampTrackerAngle(metdata=metdata, timeindex=timess, gcr=gcr, 
                                       azimuth=180, axis_tilt=0, 
                                       limit_angle=60, backtrack=True)
    # create a scene with all the variables
    sceneDict = {'tilt':tilt,'gcr': gcr,'hub_height':hub_height,'azimuth':azimuth_ang, 'module_type':moduletype, 'nMods': nMods, 'nRows': nRows}  
    scene = demo.makeScene(mymodule, sceneDict=sceneDict) #makeScene creates a .rad file with 20 modules per row, 7 rows.
    # Appending Pavers here
    demo.appendtoScene(radfile=scene.radfiles, customObject=customObjects[0], text="!xform -rz 0")
    demo.appendtoScene(radfile=scene.radfiles, customObject=customObjects[1], text="!xform -rz 0")
    demo.appendtoScene(radfile=scene.radfiles, customObject=customObjects[2], text="!xform -rz 0")
    octfile = demo.makeOct(demo.getfilelist())  # makeOct combines all of the ground, sky and object fil|es into a .oct file
    frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=sensorsy)
    analysis.analysis(octfile, simulationname+"_WITHPavers_"+str(j), frontscan, backscan)  # compare the back vs front irradiance  
    


# # RESULTS ANALYSIS NOON

# In[14]:


df_0 = load.read1Result(os.path.join(testfolder, 'results', 'irr_tutorial_14_noPavers.csv'))
df_w = load.read1Result(os.path.join(testfolder, 'results', 'irr_tutorial_14_WITHPavers.csv'))                        


# In[15]:


df_0


# In[16]:


df_w


# ## Improvement in Rear Irradiance

# In[17]:


round((df_w['Wm2Back'].mean()-df_0['Wm2Back'].mean())*100/df_0['Wm2Back'].mean(),1)


# # RESULT ANALYSIS DAY

# In[18]:


df_0 = load.read1Result(os.path.join(testfolder, 'results', 'irr_tutorial_14_noPavers_1.csv'))
df_w = load.read1Result(os.path.join(testfolder, 'results', 'irr_tutorial_14_WITHPavers_1.csv'))


# In[19]:


df_w


# In[20]:


df_0


# In[21]:


round((df_w['Wm2Back'].mean()-df_0['Wm2Back'].mean())*100/df_0['Wm2Back'].mean(),1)


# In[22]:


average_back_d0=[]
average_back_dw=[]
average_front = []
hourly_rearirradiance_comparison = []

timessimulated = endtimeindex-starttimeindex

for i in range (1, timessimulated+1):
    df_0 = load.read1Result(os.path.join(testfolder, 'results', 'irr_tutorial_14_noPavers_'+str(i)+'.csv'))
    df_w = load.read1Result(os.path.join(testfolder, 'results', 'irr_tutorial_14_WITHPavers_'+str(i)+'.csv'))
    print(round((df_w['Wm2Back'].mean()-df_0['Wm2Back'].mean())*100/df_0['Wm2Back'].mean(),1))
    hourly_rearirradiance_comparison.append(round((df_w['Wm2Back'].mean()-df_0['Wm2Back'].mean())*100/df_0['Wm2Back'].mean(),1))
    average_back_d0.append(df_0['Wm2Back'].mean())
    average_back_dw.append(df_w['Wm2Back'].mean())
    average_front.append(df_0['Wm2Front'].mean())
    


# In[23]:


print("Increase in rear irradiance: ", round((sum(average_back_dw)-sum(average_back_d0))*100/sum(average_back_d0),1))


# In[24]:


print("BG no Pavers: ", round(sum(average_back_d0)*100/sum(average_front),1))
print("BG with Pavers: ", round(sum(average_back_dw)*100/sum(average_front),1))


# In[27]:


import matplotlib.pyplot as plt

#metdata.datetime[starttime].hour # 7
#metdata.datetime[endtimeindex].hour # 17
xax= [7, 8, 9, 10, 11, 12,13,14,15,16,17,18]  # Lazy way to get the x axis...


# In[28]:


plt.plot(xax,hourly_rearirradiance_comparison)
plt.ylabel('$\Delta$ in G$_{rear}$ [%] \n(G$_{rear-with}$ - G$_{rear-without}$ / G$_{rear-without}$)')
plt.xlabel('Hour')


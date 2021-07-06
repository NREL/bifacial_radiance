#!/usr/bin/env python
# coding: utf-8

# ## 12d - JackSolar AgriPV Site

# May September (idx 2881 : 6552)
# 
# Configuration A:
# <li>Under 6 ft panels : 1.8288m
# <li>Hub height: 6 ft   : 1.8288m  
# 
#     
# Configuration B:
# <li>8 ft panels : 2.4384m
# <li>Hub height 8 ft : 2.4384m
# 
# Module x = 3 ft
#     
# Row-to-row spacing: 17 ft --> 5.1816
# 
# torquetube: square, diam 15 cm, zgap = 0
# modules on portrait
# albedo = green grass
#  
# COMPARE TO:
# Open air (no panels)
# 

# In[52]:


gcr = 8/17
gcr


# ** Two Methods: **
#     - Hourly with Fixed tilt, getTrackerAngle to update tilt of tracker
#     - Hourly with gendaylit1axis
#     - Cumulatively with gencumsky1axis
# 

# ## 1. Load Bifacial Radiance and other essential packages

# In[1]:


import bifacial_radiance
import numpy as np
import os # this operative system to do the relative-path testfolder for this example.
import pprint    # We will be pretty-printing the trackerdictionary throughout to show its structure.
from pathlib import Path


# ## 2. Define all the system variables

# In[2]:


testfolder = str(Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP')

timestamp = 4020 # Noon, June 17th.
simulationName = 'AgriPV_JS'    # Optionally adding a simulation name when defning RadianceObj

#Location
lat = 40.1217  # Given for the project site at Colorado
lon = -105.1310  # Given for the project site at Colorado

# MakeModule Parameters
moduletype='PrismSolar'
numpanels = 1  # This site have 1 module in Y-direction
x = 1  
y = 2
#xgap = 0.15 # Leaving 15 centimeters between modules on x direction
#ygap = 0.10 # Leaving 10 centimeters between modules on y direction
zgap = 0 # no gap to torquetube.
sensorsy = 6  # this will give 6 sensors per module in y-direction
sensorsx = 3   # this will give 3 sensors per module in x-direction

torquetube = True
axisofrotationTorqueTube = True 
diameter = 0.15  # 15 cm diameter for the torquetube
tubetype = 'square'    # Put the right keyword upon reading the document
material = 'black'   # Torque tube of this material (0% reflectivity)

# Scene variables
nMods = 20
nRows = 7
hub_height = 1.8 # meters
pitch = 5.1816 # meters      # Pitch is the known parameter 
albedo = 0.2  #'Grass'     # ground albedo
gcr = y/pitch


cumulativesky = False
limit_angle = 60 # tracker rotation limit angle
angledelta = 0.01 # we will be doing hourly simulation, we want the angle to be as close to real tracking as possible.
backtrack = True 


# In[10]:


test_folder_fmt


# In[32]:


indices = np.array(list(range(2881, 6552)))
len(indices)/36


# In[11]:


idx


# In[9]:


test_folder_fmt.format(f'{idx:04}')


# In[19]:


resfmt = 'irr_1axis_Hour_{}.pkl'.format(f'{i:04}')
resfmt


# In[17]:


i=44
resfmt = 'irr_1axis_Hour_{}.pkl'
compfile = resfmt.format(f'{i:04}')
compfile


# In[8]:


test_folder_fmt = 'Hour_{}'
epwfile = r'C:\Users\sayala\Documents\GitHub\bifacial_radiance\bifacial_radiance\TEMP\EPWs\USA_CO_Boulder-Broomfield-Jefferson.County.AP.724699_TMY3.epw'

for idx in range(270, 283):
#for idx in range(272, 273):

    test_folderinner = os.path.join(testfolder, test_folder_fmt.format(f'{idx:04}'))
    if not os.path.exists(test_folderinner):
        os.makedirs(test_folderinner)

    rad_obj = bifacial_radiance.RadianceObj(simulationName,path = test_folderinner)  # Create a RadianceObj 'object'
    rad_obj.setGround(albedo) 
    metdata = rad_obj.readWeatherFile(epwfile, label='center', coerce_year=2021)
    solpos = rad_obj.metdata.solpos.iloc[idx]
    zen = float(solpos.zenith)
    azm = float(solpos.azimuth) - 180
    dni = rad_obj.metdata.dni[idx]
    dhi = rad_obj.metdata.dhi[idx]
    rad_obj.gendaylit(idx)
  # rad_obj.gendaylit2manual(dni, dhi, 90 - zen, azm)
    #print(rad_obj.metdata.datetime[idx])
    tilt = round(rad_obj.getSingleTimestampTrackerAngle(rad_obj.metdata, idx, gcr, limit_angle=65),1)
    sceneDict = {'pitch': pitch, 'tilt': tilt, 'azimuth': 90, 'hub_height':hub_height, 'nMods':nMods, 'nRows': nRows}  
    scene = rad_obj.makeScene(moduletype=moduletype,sceneDict=sceneDict)
    octfile = rad_obj.makeOct()  


# In[7]:


test_folderinner


# In[ ]:


rad_obj.gendaylit(idx)
octfile = rad_obj.makeOct()  


# In[ ]:





# 
# rvu -vf views\front.vp -e .0265652 -vp 2 -21 2.5 -vd 0 1 0 AgriPV_JS.oct
# 
# 
# cd C:\Users\sayala\Documents\GitHub\bifacial_radiance\bifacial_radiance\TEMP

# In[20]:


# Ground Irradiance on panels


# In[25]:


import datetime


# In[27]:


startdt = datetime.datetime(2021,5,1,1)
enddt = datetime.datetime(2021,9,30,23)
simulationName = 'EMPTYFIELD'
rad_obj = bifacial_radiance.RadianceObj(simulationName,path = test_folderinner)  # Create a RadianceObj 'object'
rad_obj.setGround(albedo) 
metdata = rad_obj.readWeatherFile(epwfile, label='center', coerce_year=2021)
rad_obj.genCumSky(startdt=startdt, enddt=enddt)
#print(rad_obj.metdata.datetime[idx])
sceneDict = {'pitch': pitch, 'tilt': 0, 'azimuth': 90, 'hub_height':-0.2, 'nMods':1, 'nRows': 1}  
scene = rad_obj.makeScene(moduletype=moduletype,sceneDict=sceneDict)
octfile = rad_obj.makeOct()  
analysis = bifacial_radiance.AnalysisObj()
frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=1)
frontscan['zstart'] = 0.5
frontdict, backdict = analysis.analysis(octfile = octfile, name='FIELDTotal', frontscan=frontscan, backscan=backscan)


# In[36]:


import pandas as pd


# In[54]:


resname = os.path.join(test_folderinner, 'results')
resname = os.path.join(resname, 'irr_FIELDTotal.csv')
data = pd.read_csv(resname)


# In[55]:


data['Wm2Front']


# In[46]:


A = []
B = []
A.append(4)
A.append(4)
A.append(14)
B.append(4)
B.append(3)
B.append(15)

data=pd.DataFrame([A,B]).T
data.columns=['name','age']


# In[49]:


ASDF = True


# # Method 1: Gendaylit1axis, Hourly (Cumulativesky = False)

# In[ ]:


demo = bifacial_radiance.RadianceObj(simulationName,path = testfolder)  # Create a RadianceObj 'object'
demo.setGround(albedo) 
epwfile = demo.getEPW(lat, lon) 
metdata = demo.readEPW(epwfile, coerce_year = 2021)
moduleDict = demo.makeModule(name=moduletype, x = x, y =y, numpanels = numpanels, torquetube=torquetube, diameter=diameter, tubetype=tubetype, material=material, 
                zgap=zgap, axisofrotationTorqueTube=axisofrotationTorqueTube)


# In[ ]:


startdate = '21_06_17_11'
enddate = '21_06_17_12' # '%y_%m_%d_%H'
#enddate = '06/18' 

trackerdict = demo.set1axis(metdata = metdata, limit_angle = limit_angle, backtrack = backtrack, 
                            gcr = gcr, cumulativesky = cumulativesky) 

trackerdict = demo.gendaylit1axis(startdate = startdate, enddate = enddate)

sceneDict = {'pitch': pitch,'hub_height':hub_height, 'nMods':nMods, 'nRows': nRows}  

scene = demo.makeScene1axis(moduletype=moduletype,sceneDict=sceneDict)


# In[ ]:


import matplotlib.pyplot as plt


# In[ ]:


plt.plot(demo.metdata.dni[270:282])


# In[ ]:


len(demo.metdata.dhi)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:


startdate = '21_06_17_11'
enddate = '21_06_17_12' # '%y_%m_%d_%H'
#enddate = '06/18' 

trackerdict = demo.set1axis(metdata = metdata, limit_angle = limit_angle, backtrack = backtrack, 
                            gcr = gcr, cumulativesky = cumulativesky) 

trackerdict = demo.gendaylit1axis(startdate = startdate, enddate = enddate)

sceneDict = {'pitch': pitch,'hub_height':hub_height, 'nMods':nMods, 'nRows': nRows}  

scene = demo.makeScene1axis(moduletype=moduletype,sceneDict=sceneDict)

sensorsx = 2
spacingsensorsx = (moduleDict['scenex']+0.1)/(sensorsx+1)
startxsensors = (moduleDict['scenex']+0.1)/2-spacingsensorsx

sensorsy = 4
for key in trackerdict.keys():
    demo.makeOct1axis(singleindex=key)

    for i in range (0, sensorsx):  
        modscanfront = {'zstart': 0, 'xstart':0, 'orient': '0 0 -1', 'zinc':0, 'xinc':pitch/(sensorsy-1),
                       'ystart': startxsensors-spacingsensorsx*i}

        results = demo.analysis1axis(singleindex=key, customname='_'+str(i)+'_', modscanfront = modscanfront, sensorsy = sensorsy)


# # METHOD 2: FIXED TILT

# In[ ]:


plt.plot(demo.metdata.datetime[270:282], demo.metdata.dni[270:282])


# In[ ]:


for idx in range(270, 283):
    testfolder = 
    rad_obj = bifacial_radiance.RadianceObj(simulationName,path = testfolder)  # Create a RadianceObj 'object'
    rad_obj.setGround(albedo) 
    metdata = rad_obj.readEPW(epwfile, 'center', coerce_year=2021)
    solpos = rad_obj.metdata.solpos.iloc[idx]
    zen = float(solpos.zenith)
    azm = float(solpos.azimuth) - 180
    dni = rad_obj.metdata.dni[idx]
    dhi = rad_obj.metdata.dhi[idx]
    rad_obj.gendaylit2manual(dni, dhi, 90 - zen, azm)
    print(rad_obj.metdata.datetime[idx])
    tilt = round(rad_obj.getSingleTimestampTrackerAngle(rad_obj.metdata, idx, gcr, limit_angle=65),1)
    print(tilt)


# In[ ]:


foo=rad_obj.metdata.datetime[idx]
res_name = "irr_Jacksolar_"+str(foo.year)+"_"+str(foo.month)+"_"+str(foo.day)+"_"+str(foo.hour)+"_"+str(foo.minute)
res_name


# In[ ]:


sceneDict = {'pitch': pitch, 'tilt': tilt, 'azimuth': 90, 'hub_height':hub_height, 'nMods':nMods, 'nRows': nRows}  


# In[ ]:


scene = demo.makeScene(moduletype=moduletype,sceneDict=sceneDict)


# In[ ]:


octfile = demo.makeOct(octname=res_name)  


# In[ ]:


sensorsx = 2
sensorsy = 4
spacingsensorsx = (x+0.01+0.10)/(sensorsx+1)
startxsensors = (x+0.01+0.10)/2-spacingsensorsx
xinc = pitch/(sensorsy-1)

analysis = bifacial_radiance.AnalysisObj()

frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=sensorsy)
    


# In[ ]:


frontscan


# In[ ]:





# In[ ]:


for senx in range(0,sensorsx):
    frontscan['zstart'] = 0
    frontscan['xstart'] = 0
    frontscan['orient'] = '0 0 -1'
    frontscan['zinc'] = 0
    frontscan['xinc'] = xinc
    frontscan['ystart'] = startxsensors-spacingsensorsx*senx
    frontdict, backdict = analysis.analysis(octfile = octfile, name = 'xloc_'+str(senx), 
                                            frontscan=frontscan, backscan=backscan)


# In[ ]:


# TESTING SOMETHING


# In[ ]:


demo = bifacial_radiance.RadianceObj(simulationName,path = testfolder)  # Create a RadianceObj 'object'
demo.setGround(albedo) 
epwfile = demo.getEPW(lat, lon) 


# In[ ]:


startdate = '21_06_17_11'
enddate = '21_06_17_12'

metdata = demo.readWeatherFile(epwfile, starttime=startdate, endtime=enddate, coerce_year = 2021)
metdata.solpos


# In[ ]:


startdate = '21_06_17_11'
enddate = '21_06_17_11'

metdata = demo.readWeatherFile(epwfile, starttime=startdate, endtime=enddate, coerce_year = 2021)
metdata.solpos


# In[ ]:


metdata


# In[ ]:


trackerdict = demo.set1axis(cumulativesky=False)


# In[ ]:


trackerdict


# In[ ]:


time = metdata.datetime[0]
time


# In[ ]:


filename = time.strftime('%y_%m_%d_%H_%M')
filename


# In[ ]:


metdata.ghi[0]
metdata.tracker_theta[0]


# In[ ]:


skyfile = demo.gendaylit(metdata=metdata,timeindex=0)
skyfile


# In[ ]:


trackerdict.keys()


# In[ ]:


trackerdict[filename]


# In[ ]:


trackerdict = demo.gendaylit1axis()


# In[ ]:


sceneDict = {'pitch': pitch, 'tilt': 30, 'azimuth': 90, 'hub_height':hub_height, 'nMods':nMods, 'nRows': nRows}  


# In[ ]:


trackerdict = demo.makeScene1axis(trackerdict=trackerdict, moduletype=moduletype, sceneDict=sceneDict)


# In[ ]:


startdate = '21_06_17_11'
enddate = '21_06_17_12'


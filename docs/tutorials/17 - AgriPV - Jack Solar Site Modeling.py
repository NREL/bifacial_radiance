#!/usr/bin/env python
# coding: utf-8

# ## 17 - AgriPV - Jack Solar Site Modeling

# Modeling Jack Solar AgriPV site in Longmonth CO, for crop season May September. The site has two configurations:
# 
# 
# <b> Configuration A: </b>
# * Under 6 ft panels : 1.8288m
# * Hub height: 6 ft   : 1.8288m 
# 
#     
# Configuration B:
# * 8 ft panels : 2.4384m
# * Hub height 8 ft : 2.4384m
# 
# Other general parameters:
# * Module Size: 3ft x 6ft (portrait mode)
# * Row-to-row spacing: 17 ft --> 5.1816
# * Torquetube: square, diam 15 cm, zgap = 0
# * Albedo = green grass
#  
# 
# ### Steps in this Journal:
# <ol>
#     <li> <a href='#step1'> Load Bifacial Radiance and other essential packages</a> </li>
#     <li> <a href='#step2'> Define all the system variables </a> </li>
#     <li> <a href='#step3'> Build Scene for a pretty Image </a> </li>
# </ol>
# 
# #### More details
# There are three methods to perform the following analyzis: 
#     <ul><li>A. Hourly with Fixed tilt, getTrackerAngle to update tilt of tracker </li>
#         <li>B. Hourly with gendaylit1axis using the tracking dictionary </li>
#         <li>C. Cumulatively with gencumsky1axis </li>
#     </ul>
# 
#     
# The analysis itself is performed with the HPC with method A, and results are compared to GHI (equations below). The code below shows how to build the geometry and view it for accuracy, as well as evaluate monthly GHI, as well as how to model it with `gencumsky1axis` which is more suited for non-hpc environments. 
# 
# 
# 
# ![AgriPV Jack Solar Study](../images_wiki/AdvancedJournals/AgriPV_JackSolar.PNG)
# 

# <a id='step1'></a>

# ## 1. Load Bifacial Radiance and other essential packages

# In[2]:


import bifacial_radiance
import numpy as np
import os # this operative system to do the relative-path testfolder for this example.
import pprint    # We will be pretty-printing the trackerdictionary throughout to show its structure.
from pathlib import Path
import pandas as pd


# <a id='step2'></a>

# ## 2. Define all the system variables

# In[3]:


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


test_folder_fmt = 'Hour_{}' 
epwfile = r'C:\Users\sayala\Documents\GitHub\bifacial_radiance\bifacial_radiance\TEMP\EPWs\USA_CO_Boulder-Broomfield-Jefferson.County.AP.724699_TMY3.epw'


# <a id='step3'></a>

# # 3. Build Scene for a pretty Image

# In[ ]:


#for idx in range(270, 283):
for idx in range(272, 273):

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


# #### The scene generated can be viewed by navigating on the terminal to the testfolder and typing
# 
# > rvu -vf views\front.vp -e .0265652 -vp 2 -21 2.5 -vd 0 1 0 AgriPV_JS.oct
# 
# 
# 

# <a id='step4'></a>

# # GHI Calculations 
# 
# Note: Crop season in weather file is index 2881 to 6552

# ### From Weather File

# In[ ]:


# BOULDER
# Simple method where I know the index where the month starts and collect the monthly values this way.

starts = [2881, 3626, 4346, 5090, 5835]
ends = [3621, 4341, 5085, 5829, 6550]

ghi_Boulder = []
for ii in range(0, len(starts)):
    start = starts[ii]
    end = ends[ii]
    ghi_Boulder.append(metdata.ghi[start:end].sum())
print(" GHI Boulder Monthly May to September Wh/m2:", ghi_Boulder)


# ### With raytrace

# In[18]:


# Not working on development branch up to 09/Sept/21. Maybe will get updated later.
'''
import datetime
startdt = datetime.datetime(2021,5,1,1)
enddt = datetime.datetime(2021,5,31,23)
simulationName = 'EMPTYFIELD'
rad_obj = bifacial_radiance.RadianceObj(simulationName, path=testfolder)  # Create a RadianceObj 'object'
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
resname = os.path.join(testfolder, 'results')
resname = os.path.join(resname, 'irr_FIELDTotal.csv')
data = pd.read_csv(resname)
print("FIELD TOTAL Season:", data['Wm2Front'])
'''


# In[ ]:





# In[ ]:





# In[ ]:





# # CHECK - from previous '12c journal'

# In[ ]:


for jj in range (0, 1): #len(hub_heights)):
    hub_height = hub_heights[jj]
    simulationname = 'height_'+ str(int(hub_height*100))+'cm'

    #Location:
    # MakeModule Parameters
    moduletype='PrismSolar'
    numpanels = 1 
    x = 0.95  
    y = 1.95
    xgap = 0.01# Leaving 1 centimeters between modules on x direction
    ygap = 0.0 # Leaving 10 centimeters between modules on y direction
    zgap = 0.05 # cm gap between torquetube
    sensorsy = 12*numpanels  # t`his will give 6 sensors per module, 1 per cell

    # Other default values:

    # TorqueTube Parameters
    axisofrotationTorqueTube=True
    torqueTube = True
    cellLevelModule = False

    # SceneDict Parameters
    pitch = 5.1816 # m
    torquetube_height = hub_height - 0.1 # m
    nMods = 30 # six modules per row.
    nRows = 7  # 3 row

    azimuth_ang=90 # Facing south
    tilt =35 # tilt. 

    # Now let's run the example
#    demo = RadianceObj(simulationname,path = testfolder)  # Create a RadianceObj 'object'
    demo.setGround(albedo) # input albedo number or material name like 'concrete'.  To see options, run this without any input.

    #demo.gendaylit(4020)  # Use this to simulate only one hour at a time. 
    # Making module with all the variables
    moduleDict=demo.makeModule(name=moduletype,x=x,y=y,numpanels = numpanels, 
                               xgap=xgap, ygap=ygap, 
                               torquetube=False, diameter=0.12, tubetype='Square')
    
    # create a scene with all the variables
    sceneDict = {'tilt':tilt,'pitch': 15,'hub_height':hub_height,'azimuth':azimuth_ang, 'module_type':moduletype, 'nMods': nMods, 'nRows': nRows}  
    scene = demo.makeScene(moduletype=moduletype, sceneDict=sceneDict) #makeScene creates a .rad file with 20 modules per row, 7 rows.
    octfile = demo.makeOct(demo.getfilelist())  # makeOct combines all of the ground, sky and object fil|es into a .oct file.

    starttime = '05_01_01' 
    endtime = '10_01_01'


    metdata = demo.readEPW(epwfile, starttime = starttime, endtime = endtime) # read in the EPW weather data from above
    
    demo.genCumSky()

    octfile = demo.makeOct()  # makeOct combines all of the ground, sky and object files into a .oct file.

    analysis = AnalysisObj(octfile, demo.name)  # return an analysis object including the scan dimensions for back irradiance
    sensorsy = 10
    sensorsx = 5
    startgroundsample=-moduleDict['scenex']
    spacingbetweensamples = moduleDict['scenex']/(sensorsx-1)

    for i in range (0, sensorsx):  
        frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=sensorsy)
        groundscan = frontscan
        groundscan['zstart'] = 0.05  # setting it 5 cm from the ground.
        groundscan['zinc'] = 0   # no tilt necessary. 
        groundscan['yinc'] = pitch/(sensorsy-1)   # increasing spacing so it covers all distance between rows
        groundscan['xstart'] = startgroundsample + i*spacingbetweensamples   # increasing spacing so it covers 
                                                                          # all distance between rows
        analysis.analysis(octfile, simulationname+'_'+str(i), groundscan, backscan)  # compare the back vs front irradiance  

    metdata = demo.readEPW(epwfile) # read in the EPW weather data from above
    demo.genCumSky(savefile = 'PV')#startdt=startdt, enddt=enddt)

    octfile = demo.makeOct()  # makeOct combines all of the ground, sky and object files into a .oct file.

    analysis = AnalysisObj(octfile, demo.name)  # return an analysis object including the scan dimensions for back irradiance
    sensorsy = 20
    sensorsx = 12
    startPVsample=-moduleDict['x']
    spacingbetweenPVsamples = moduleDict['x']/(sensorsx-1)



#!/usr/bin/env python
# coding: utf-8

# ## 1-Axis tracker example
# 
# Example demonstrating Radiance gencumulativesky for 1-axis tracking.
# 
# #### Types of 1-axis tracking simulations:
# 
# <b> CumulativeSky: True</b> gencumsky has been modified to divide the yearly-cumulative sky into various skies, each one representing the cumulative irradiance for the hours at which the tracker is at a certain angle. For faster running, for a tracker that moves between 60 and -60 degrees limit angle, if only positions every 5 degrees are considered (60, 55, 50 ... -55, -60), then only 25 skies (and 25 simulations) will be run for the whole year.
# 
# This procedure was presented in. Reffer to this journal for more information:
# 
#     S. Ayala Pelaez, C. Deline, P. Greenberg, J. S. Stein, and R. K. Kostuk, “Model and Validation of Single-Axis Tracking with Bifacial PV - Preprint,” Golden Co Natl. Renew. Energy Lab. NREL/CP-5K00-72039., no. October, 2018. https://www.nrel.gov/docs/fy19osti/72039.pdf
# 
# <b>CumulativeSky: False </b>. This uses Gendaylit function, which performs the simulation hour by hour. A good computer and a ton of patience are needed for doing the ~4000 daylight-hours of the year, or else a high-performance-computing for handling full year simulations. The procedure can be broken into shorter steps for one day or a single timestamp simulation which is exemplified below.
# 
# The first part is common to both procedures. We show a couple tricks of loading files / or weather files here too.
# 
# 
# 

# In[2]:


import os
testfolder = os.path.abspath(r'..\bifacial_radiance\TEMP')  

# You can alternatively point to an empty directory (it will open a load GUI Visual Interface)
# or specify any other directory in your computer. I.E.:
# testfolder = r'C:\Users\sayala\Documents\RadianceScenes\Demo'

print ("Your simulation will be stored in %s" % testfolder)


# In[3]:


#tracker geometry options:
module_height = 1.7  # module portrait dimension in meters
gcr = 0.33   # ground cover ratio,  = module_height / pitch
albedo = 0.3     # ground albedo
hub_height = 2   # tracker height at 0 tilt in meters (hub height)
limit_angle = 45 # tracker rotation limit angle


# In[4]:


try:
    from bifacial_radiance import RadianceObj, AnalysisObj
except ImportError:
    raise RuntimeError('bifacial_radiance is required. download distribution')
    # Simple example system using Radiance.
import numpy as np

# Easy graphical director picker:  
# this is only required if you want a graphical directory picker.  
# Note:  easygui sometimes opens in the background forcing you to hunt for the window!  
#import easygui 
#testfolder = easygui.diropenbox(msg = 'Select or create an empty directory for the Radiance tree',title='Browse for empty Radiance directory')

demo = RadianceObj(path = testfolder)  # Create a RadianceObj 'object'
demo.setGround(albedo) # input albedo number or material name like 'concrete'.  To see options, run this without any input.


# #### Look at a couple of ways to get meteorological data

# In[8]:


EPWmode = True
if EPWmode is True:
    epwfile = demo.getEPW(37.5,-77.6) #Pull EPW data for any global lat/lon. In this case, Richmond, VA
    metdata = demo.readEPW(epwfile) # read in the weather data
    #metdata = demo.readEPW('EPWs\\USA_VA_Richmond.Intl.AP.724010_TMY.epw') # read in the weather data directly
else:
    metdata = demo.readTMY() # load TMY3 data from another source, like solar prospector. A version is saved as \EPWs\tmy3_temp.csv

# Alternatively, you can use readWeatherFile, which doesn't care if the file is an EPW or a CSV.
metdata = demo.readWeatherFile(epwfile)


# ## CumulativeSky Workflow

# In[9]:


# We have 2 workflows: cumulativesky and hourly.  Start with cumulativesky

# create metdata files for each condition. It will create a met-data file for each angle the tracker will find itself in.
# set1axis has as input variable cumulativesky, which is set to True as default.
trackerdict = demo.set1axis(metdata, limit_angle = limit_angle, backtrack = True, gcr = gcr)

# Create the skies for each sub-metdata file created by set1axis.
trackerdict = demo.genCumSky1axis(trackerdict)


# In[11]:


# Create a new moduletype: Prism Solar Bi60. width = .984m height = 1.695m. Bifaciality = 0.90
demo.makeModule(name='Prism Solar Bi60',x=0.984,y=module_height)
# note that beginning in v0.2.3 you can add torque tubes and multiple module arrays. e.g:
demo.makeModule(name='2upTracker',x=0.984,y=module_height, torquetube = True, tubetype = 'round', 
    diameter = 0.1, xgap=0.02, ygap = 0.05, zgap = 0.05, numpanels = 2, axisofrotationTorqueTube=True)
# and now in v0.2.4 you can even add cell-level options if you want non-opaque, cell-defined modules.
# To do this, pass a dictionary with the Cell Level Module PArameters:
cellLevelModuleParams = {'numcellsx': 6, 'numcellsy':10, 'xcell': 0.156, 'ycell':0.156, 'xcellgap':0.02, 'ycellgap':0.02}

demo.makeModule(name='cellLevelModule', bifi=1, torquetube=True, diameter=0.1, tubetype='Oct', material='Metal_Grey', 
                xgap=0.02, ygap=0.05, zgap=0.05, numpanels=2, 
                cellLevelModuleParams=cellLevelModuleParams, 
                axisofrotationTorqueTube=False)


# In[12]:


# For more options on makemodule, see the help description of the function.  

print("")
demo.printModules()# print available module types


# In[13]:


# Now let's create a scene using panels in portrait, 2m hub height, 0.33 GCR. 
# NOTE: clearance needs to be calculated at each step. hub height is constant.
# 'orientation':'portrait' deprecated in v0.2.4 Also, sceneDict now defines nMods and nRows for the scene.
sceneDict = {'pitch':module_height / gcr,'hub_height':hub_height, 'nMods': 20, 'nRows': 7}  
module_type = 'Prism Solar Bi60' # We are using the first simple module we defined.
# makeScene creates a .rad file with 20 modules per row, 7 rows repeating the module_type Prism Solar Bi60.
trackerdict = demo.makeScene1axis(trackerdict,module_type,sceneDict) 

# makeOct1axis joins the sky.rad file, ground.rad file, and the geometry.rad files created in makeScene.
trackerdict = demo.makeOct1axis(trackerdict)

# Note: with v0.2.4 the analysis1axis has additional parameters to allow custom scans.  parameters: 
#    sensorsy = int() (9 = default)
#    modwanted = int() (middle module default)
#    rowwanted   =  int() (middle row default)
# Now we need to run analysis and combine the results into an annual total.  
# This can be done by doing a frontscan and backscan for the modwanted and rowwanted specified.
# the frontscan and backscan include a linescan along a chord of the module, both on the front and back.  
trackerdict = demo.analysis1axis(trackerdict, modWanted=9, rowWanted = 2)

# Return the minimum of the irradiance ratio, and the average of the irradiance ratio along a chord of the module.
print('Annual RADIANCE bifacial ratio for 1-axis tracking: %0.3f' %(sum(demo.Wm2Back)/sum(demo.Wm2Front)) )


# ### Note: same workflow can use stored self inputs rather than repeatedly keep passing trackerdict. 
# In super short version:

# In[8]:


try:
    from bifacial_radiance import *
except ImportError:
    raise RuntimeError('bifacial_radiance is required. download distribution')

demo = RadianceObj(path = testfolder) 
demo.setGround(0.2)
epwfile = demo.getEPW(37.5,-77.6) 
metdata = demo.readEPW(epwfile)
demo.set1axis()
demo.genCumSky1axis()
module_type = '2upTracker' # Since we already created this module type, we don't need to makeModule, we just need to call it when we make the Scene.
sceneDict = {'pitch':module_height / gcr,'height':hub_height, 'nMods': 20, 'nRows': 7}  # orientation deprecated on v.0.2.4.
demo.makeScene1axis(moduletype=module_type,sceneDict = sceneDict)
demo.makeOct1axis()
demo.analysis1axis()
print('Annual bifacial ratio for 1-axis tracking: %0.3f' %(np.mean(demo.Wm2Back)/np.mean(demo.Wm2Front)) )


# # GENDAYLIT Workflow.  -- hourly tracker option

# In[ ]:


## New v0.2.3 software includes the option for hourly tracked simulation workflow using gendaylit. 

# The first part is the same:
demo2 = RadianceObj('Gendaylit_TrackingHourly',testfolder)  
demo2.setGround(0.2) 
epwfile = demo2.getEPW(37.5,-77.6) #pull TMY data for any global lat/lon
metdata = demo2.readEPW(epwfile) # read in the weather data   

# This is the same for gencumsky and gendaylit: create a new moduletype, and specify a sceneDict. 
module_type = 'Prism Solar Bi60'
demo2.makeModule(name=module_type,x=0.984,y=1.695,bifi = 0.90)  # set module type to be used and passed into makeScene1axis
# Create the scenedictionary for the 1-axis tracking
sceneDict = {'pitch':1.695 / 0.33,'height':2.35, 'nMods': 20, 'nRows': 7}  


# In[ ]:


# NEW hourly gendaylit workflow. Note that trackerdict is returned with hourly time points as keys instead of tracker angles.
trackerdict2 = demo2.set1axis(cumulativesky = False)  # this cumulativesky = False key is crucial to set up the hourly workflow

# This is for exemplifying the changes undergone in the trackerdict by each step. Just printing information.
print ("Full trackerdict for all the year created by set1axis: %s " % (len(trackerdict2))) # trackerdict contains all hours in the year as keys. For example: trackerdict2['12_16_08']
print ("Contents of trackerdict for sample hour after creating on set1axis, \n trackerdict2['12_16_08']: \n %s \n" % ( trackerdict2['12_16_08']))

# Create the skyfiles needed for 1-axis tracking. 
# If you don't specify a startdate and enddate, all the year will be created, which will take more time. 
# For this example we are doing the first half of January.
# Specifying the startdate and enddate also trims down the trackerdict from the whole year to just the entries between that start and enddate.
trackerdict2 = demo2.gendaylit1axis(startdate='01/01', enddate='01/15')  # optional parameters 'startdate', 'enddate' inputs = string 'MM/DD' or 'MM_DD' 

# This is for exemplifying the changes undergone in the trackerdict by each step. Just printing information.
print ("\nTrimmed trackerdict by gendaylit1axis to start and enddate: %s " % (len(trackerdict2)))
print ("Contents of trackerdict for sample hour after running gendaylit1axis \n trackerdict2['01_01_11']: %s " % ( trackerdict2['01_01_11']))


# In[ ]:


# making the different scenes for the 1-axis tracking for the dates in trackerdict2.
trackerdict2 = demo2.makeScene1axis(trackerdict2, module_type,sceneDict, cumulativesky = False) #makeScene creates a .rad file with 20 modules per row, 7 rows.

# This is for exemplifying the changes undergone in the trackerdict by each step. Just printing information.
print ("\n Contents of trackerdict for sample hour after makeScene1axis: \n trackerdict2['01_01_11']: \n %s " % ( trackerdict2['01_01_11']))


# #### Run one single index (super fast example):

# In[ ]:


# Now this is the part that takes a long time, and will probably require parallel computing for doing more time points or the full year. 
# For this example we just run one hourly point:

demo2.makeOct1axis(trackerdict2,singleindex='01_01_11')

# This is for exemplifying the changes undergone in the trackerdict by each step. Just printing information.
print ("\n Contents of trackerdict for sample hour after makeOct1axis: \n trackerdict2['01_01_11']: \n %s \n" % ( trackerdict2['01_01_11']))

demo2.analysis1axis(trackerdict2,singleindex='01_01_11')

# This is for exemplifying the changes undergone in the trackerdict by each step. Just printing information.
print ("\n Contents of trackerdict for sample hour after makeOct1axis: \n trackerdict2['01_01_11']: \n %s \n" % ( trackerdict2['01_01_11']))

# Printing the results.
print('\n\n1-axis tracking hourly bifi gain: {:0.3}'.format(sum(demo2.Wm2Back) / sum(demo2.Wm2Front)))


# #### Run a range of indexes: (not as fast as a single index, not as slow as all!)
# 

# In[ ]:


for time in ['01_01_11','01_01_12']:  # just two timepoints
    demo2.makeOct1axis(trackerdict2,singleindex=time)
    demo2.analysis1axis(trackerdict2,singleindex=time)

print('1-axis tracking hourly bifi gain: {:0.3}'.format(sum(demo2.Wm2Back) / sum(demo2.Wm2Front)))


# #### Run the full trackingdictionary...
# (this might considerably more time, depending on the number of entries on the trackerdictionary! You've been warned) 
# 

# In[ ]:


demo2.makeOct1axis(trackerdict2,singleindex=time)
demo2.analysis1axis(trackerdict2,singleindex=time)
print('1-axis tracking hourly bifi gain: {:0.3}'.format(sum(demo2.Wm2Back) / sum(demo2.Wm2Front)))


# ### Gendaylit for the WHOLE Year
# And because you asked: this is the summarized version to run with gendaylit the WHOLE year. 
# #### This will take ~4 days on a really good computer. IF you're sure this is what you want, uncomment and run below :)

# In[ ]:


'''
demo2 = RadianceObj('Gendaylit_AllYear_Tracking',testfolder)  
demo2.setGround(0.2) 
epwfile = demo2.getEPW(37.5,-77.6) #pull TMY data for any global lat/lon
metdata = demo2.readEPW(epwfile) # read in the weather data   
module_type = 'Prism Solar Bi60'
sceneDict = {'pitch':1.695 / 0.33,'height':2.35, 'nMods': 20, 'nRows': 7}  
trackerdict2 = demo2.set1axis(cumulativesky = False)  # this cumulativesky = False key is crucial to set up the hourly workflow
trackerdict2 = demo2.gendaylit1axis()  # optional parameters 'startdate', 'enddate' inputs = string 'MM/DD' or 'MM_DD' 
trackerdict2 = demo2.makeScene1axis(trackerdict2, module_type,sceneDict, cumulativesky = False) #makeScene creates a .rad file with 20 modules per row, 7 rows.
demo2.makeOct1axis(trackerdict2)
demo2.analysis1axis(trackerdict2)
'''


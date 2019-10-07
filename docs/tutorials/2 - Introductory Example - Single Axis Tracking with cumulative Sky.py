#!/usr/bin/env python
# coding: utf-8

# ## 2 - Introductory Example - 1-Axis tracker with cumulative sky
# 
# Method <b> Gencumsky </b> has been modified to divide the yearly-cumulative sky into various skies, each one representing the cumulative irradiance for the hours at which the tracker is at a certain angle. For faster running, for a tracker that moves between 45 and -45 degrees limit angle, if only positions every 5 degrees are considered (45, 40, 35 .... -4-, -45), then only 18 skies (and 18 simulations) will be run for the whole year.
# 
# ![Example of the hemisphere cumulative sky](../images_wiki/Journal2Pics/tracking_cumulativesky.png)
# 
# 
# This procedure was presented in:
# 
#     S. Ayala Pelaez, C. Deline, P. Greenberg, J. S. Stein, and R. K. Kostuk, “Model and Validation of Single-Axis Tracking with Bifacial PV - Preprint,” Golden Co Natl. Renew. Energy Lab. NREL/CP-5K00-72039., no. October, 2018. https://www.nrel.gov/docs/fy19osti/72039.pdf
# 
# 
# Steps:
# <ol>
#     <li> <a href='#step1'> Create a folder for your simulation, and Load bifacial_radiance </a></li> 
#     <li> <a href='#step2'> Create a Radiance Object </a></li> 
#     <li> <a href='#step3'> Set the Albedo </a></li> 
#     <li> <a href='#step4'> Download Weather Files </a></li> 
#     <li> <a href='#step5'> Generate the Sky </a></li> 
#     <li> <a href='#step6'> Define a Module type </a></li> 
#     <li> <a href='#step7'> Create the scene </a></li> 
#     <li> <a href='#step8'> Combine Ground, Sky and Scene Objects </a></li> 
#     <li> <a href='#step9'> Analyze and get results </a></li> 
#     <li> <a href='#step10'> Visualize scene options </a></li>   
# </ol>
# 

# <a id='step1'></a>

# 
# ## 1. Create a folder for your simulation, and load bifacial_radiance 
# 
# First let's set the folder where the simulation will be saved. By default, this is the TEMP folder in the bifacial_radiance distribution.
# 
# The lines below find the location of the folder relative to this Jupyter Journa. You can alternatively point to an empty directory (it will open a load GUI Visual Interface) or specify any other directory in your computer, for example:
# 
# #### testfolder = r'C:\Users\sayala\Documents\RadianceScenes\Demo'
# 
# 

# In[6]:


import os
testfolder = os.path.abspath(r'..\..\bifacial_radiance\TEMP')  

print ("Your simulation will be stored in %s" % testfolder)


# This will load bifacial_radiance and other libraries from python that will be useful for this Jupyter Journal:

# In[5]:


try:
    from bifacial_radiance import RadianceObj, AnalysisObj
except ImportError:
    raise RuntimeError('bifacial_radiance is required. download distribution')
import numpy as np


# <a id='step2'></a>

# ## 2. Create a Radiance Object

# In[7]:


# Create a RadianceObj 'object' named bifacial_example. no whitespace allowed
demo = RadianceObj('bifacial_tracking_example',testfolder)  


# This will create all the folder structure of the bifacial_radiance Scene in the designated testfolder in your computer, and it should look like this:
# 
# 
# ![Folder Structure](../images_wiki/Journal1Pics/folderStructure.png)

# <a id='step3'></a>

# ## 3. Set the Albedo

# To see more options of ground materials available (located on ground.rad), run this function without any input. 

# In[9]:


# Input albedo number or material name like 'concrete'.  
demo.setGround()  # This prints available materials.


# If a number between 0 and 1 is passed, it assumes it's an albedo value. For this example, we want a natural-ground albedo value, so we'll use 0.25

# In[10]:


albedo = 0.25
demo.setGround(albedo)


# <a id='step4'></a>

# ## 4. Download and Load Weather Files
# 
# There are various options provided in bifacial_radiance to load weatherfiles. getEPW is useful because you just set the latitude and longitude of the location and it donwloads the meteorologicla data for any location. 

# In[11]:


# Pull in meteorological data using pyEPW for any global lat/lon
epwfile = demo.getEPW(lat = 37.5, lon = -77.6)  # This location corresponds to Richmond, VA.


# The downloaded EPW will be in the EPWs folder.
# 
# To load the data, use readWeatherFile. This reads EPWs, TMY meterological data, or even your own data as long as it follows TMY data format (With any time resoultion).

# In[12]:


# Read in the weather data pulled in above. 
metdata = demo.readWeatherFile(epwfile) 


# ## TRACKING Workflow

# Until now, all the steps looked the same from the Introductory Example for Fixed Tilt. The following section follows similar steps, but the functions are specific for working with single axis tracking.
# 
# ## 5. Set Tracking Angles
# 
# This function will read the weather file, and based on the sun position it will calculate the angle the tracker should be at for each hour. It will create metdata files for each of the tracker angles considered.

# In[16]:


limit_angle = 45 # tracker rotation limit angle
backtrack = True
gcr = 0.33
cumulativesky = True # This is important for this example!
trackerdict = demo.set1axis(metdata, limit_angle = limit_angle, backtrack = backtrack, gcr = gcr, cumulativesky=cumulativesky)


# Setting backtrack to True is important in this step, so the trackers correct for self-shading when following the sun at high zenith angles. 

# <a id='step6'></a>

# ## 6. Generate the Sky
# 
# This will create the skies for each sub-metdata file created by set1axis.
# 

# In[19]:


trackerdict = demo.genCumSky1axis(trackerdict)


# This is how one of the cumulative sky .cal files associated with each .rad file generated look like: 
# 
# ![Example of the gencumsky1axis](../images_wiki/Journal2Pics/gencumsky1axis_example_file_structure_and_contents.png)
# 
# 
# Each of the values corresponds to the cumulative rradiance of one of those patches, for when the tracker is at that specific angle through the year.

# <a id='step7'></a>

# ## 7. Define the Module type
# 
# Let's make a more interesting module in this example. Let's do 2-up configuration in portrait, with the modules rotating around a 10 centimeter round torque tube. Let's add a gap between the two modules in 2-UP of 10 centimeters, as well as gap between the torque tube and the modules of 5 centimeters. Along the row, the modules are separated only 2 centimeters for this example. The torquetube is painted Metal_Grey in this example (it's one of the materials available in Ground.rad, and it is 40% reflective).
# 

# In[21]:


x = 0.984  # meters
y = 1.7    # meters
module_type = 'Custom Tracker Module'
torquetube = True
tubetype = 'round'
diameter = 0.1 # diameter of the torque tube
numpanels = 2
axisofrotationTorqueTube = True
zgap = 0.05
ygap = 0.10
xgap = 0.02
material = 'Metal_Grey'

demo.makeModule(name=module_type,x=x,y=y, torquetube = torquetube, tubetype = tubetype, material = material,
    diameter = diameter, xgap=xgap, ygap =ygap, zgap = zgap, numpanels = numpanels, axisofrotationTorqueTube=axisofrotationTorqueTube)


# 

# ## 7. Make the Scene
# 
# The sceneDicitonary specifies the information of the scene. For tracking, different input parameters are expected in the dictionary, such as number of rows, number of modules per row, row azimuth, hube_height (distance between the axis of rotation of the modules and the ground). 
# 
# Azimuth gets measured from N = 0, so for South facing modules azimuth should equal 180 degrees
# 

# In[25]:


hub_height = 2.
sceneDict = {'gcr': gcr,'hub_height':hub_height, 'nMods': 20, 'nRows': 7}  


# To make the scene we have to create a Scene Object through the method makeScene1axis. This method will create a .rad file in the objects folder, with the parameters specified in sceneDict and the module created above.

# In[26]:


trackerdict = demo.makeScene1axis(trackerdict,module_type,sceneDict) 


# In[ ]:




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


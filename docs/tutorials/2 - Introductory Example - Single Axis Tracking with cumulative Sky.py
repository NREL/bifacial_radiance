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
# Ayala Pelaez S, Deline C, Greenberg P, Stein JS, Kostuk RK. Model and validation of single-axis tracking with bifacial PV. IEEE J Photovoltaics. 2019;9(3):715–21. https://ieeexplore.ieee.org/document/8644027 and https://www.nrel.gov/docs/fy19osti/72039.pdf (pre-print, conference version)
# 
# 
# ### Steps:
# <ol>
#     <li> <a href='#step1'> Create a folder for your simulation, and load bifacial_radiance </a></li> 
#     <li> <a href='#step2'> Create a Radiance Object </a></li> 
#     <li> <a href='#step3'> Set the Albedo </a></li> 
#     <li> <a href='#step4'> Download Weather Files </a></li>    
#     <ul> (VERY SIMILAR TO FIXED TILT EXAMPLE UNTIL HERE) </ul> 
#     <li> <a href='#step5'> Set Tracking Angles </a></li> 
#     <li> <a href='#step6'> Generate the Sky </a></li> 
#     <li> <a href='#step7'> Define a Module type </a></li> 
#     <li> <a href='#step8'> Create the scene </a></li> 
#     <li> <a href='#step9'> Combine Ground, Sky and Scene Objects </a></li> 
#     <li> <a href='#step10'> Analyze and get results </a></li> 
#     <li> <a href='#step11'> Clean Results </a></li>   
#    
# </ol>
# 
# And finally:  <ul> <a href='#condensed'> Condensed instructions </a></ul>   

# <a id='step1'></a>

# 
# ## 1. Create a folder for your simulation, and load bifacial_radiance 
# 
# First let's set the folder where the simulation will be saved. By default, this is the TEMP folder in the bifacial_radiance distribution.
# 
# The lines below find the location of the folder relative to this Jupyter Journa. You can alternatively point to an empty directory (it will open a load GUI Visual Interface) or specify any other directory in your computer, for example:
# 
# #### testfolder = r'C:\Users\sayala\Documents\RadianceScenes\Tutorials\Journal2'
# 
# 

# In[1]:


import os
testfolder = os.path.abspath(r'..\..\bifacial_radiance\TEMP')  

print ("Your simulation will be stored in %s" % testfolder)


# This will load bifacial_radiance and other libraries from python that will be useful for this Jupyter Journal:

# In[2]:


from bifacial_radiance import *
import numpy as np


# <a id='step2'></a>

# ## 2. Create a Radiance Object

# In[3]:


# Create a RadianceObj 'object' named bifacial_example. no whitespace allowed
demo = RadianceObj('bifacial_tracking_example', path = testfolder)  


# This will create all the folder structure of the bifacial_radiance Scene in the designated testfolder in your computer, and it should look like this:
# 
# 
# ![Folder Structure](../images_wiki/Journal1Pics/folderStructure.png)

# <a id='step3'></a>

# ## 3. Set the Albedo

# To see more options of ground materials available (located on ground.rad), run this function without any input. 

# In[4]:


# Input albedo number or material name like 'concrete'.  
demo.setGround()  # This prints available materials.


# If a number between 0 and 1 is passed, it assumes it's an albedo value. For this example, we want a natural-ground albedo value, so we'll use 0.25

# In[5]:


albedo = 0.25
demo.setGround(albedo)


# <a id='step4'></a>

# ## 4. Download and Load Weather Files
# 
# There are various options provided in bifacial_radiance to load weatherfiles. getEPW is useful because you just set the latitude and longitude of the location and it donwloads the meteorologicla data for any location. 

# In[6]:


# Pull in meteorological data using pyEPW for any global lat/lon
epwfile = demo.getEPW(lat = 37.5, lon = -77.6)  # This location corresponds to Richmond, VA.


# The downloaded EPW will be in the EPWs folder.
# 
# To load the data, use readWeatherFile. This reads EPWs, TMY meterological data, or even your own data as long as it follows TMY data format (With any time resoultion).

# In[7]:


# Read in the weather data pulled in above. 
metdata = demo.readWeatherFile(weatherFile = epwfile) 


# ## TRACKING Workflow

# <a id='step5'></a>

# Until now, all the steps looked the same from Tutorial 1. The following section follows similar steps, but the functions are specific for working with single axis tracking.
# 
# ## 5. Set Tracking Angles
# 
# This function will read the weather file, and based on the sun position it will calculate the angle the tracker should be at for each hour. It will create metdata files for each of the tracker angles considered.

# In[8]:


limit_angle = 5 # tracker rotation limit angle. Setting it ridiculously small so this runs faster.
angledelta = 5 # sampling between the limit angles. 
backtrack = True
gcr = 0.33
cumulativesky = True # This is important for this example!
trackerdict = demo.set1axis(metdata = metdata, limit_angle = limit_angle, backtrack = backtrack, 
                            gcr = gcr, cumulativesky = cumulativesky)


# Setting backtrack to True is important in this step, so the trackers correct for self-shading when following the sun at high zenith angles. 

# <a id='step6'></a>

# ## 6. Generate the Sky
# 
# This will create the skies for each sub-metdata file created by set1axis.
# 

# In[9]:


trackerdict = demo.genCumSky1axis(trackerdict = trackerdict)


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

# In[10]:


x = 0.984  # meters
y = 1.7    # meters
moduletype = 'Custom Tracker Module'
torquetube = True
tubetype = 'round'
diameter = 0.1 # diameter of the torque tube
numpanels = 2
axisofrotationTorqueTube = True
zgap = 0.05
ygap = 0.10
xgap = 0.02
material = 'Metal_Grey'

demo.makeModule(name = moduletype, x = x, y = y, 
                torquetube = torquetube, tubetype = tubetype, material = material,
                diameter = diameter, xgap = xgap, ygap = ygap, zgap = zgap, 
                numpanels = numpanels, axisofrotationTorqueTube = axisofrotationTorqueTube)


# <a id='step8'></a>

# ## 8. Make the Scene
# 
# The scene Dictionary specifies the information of the scene. For tracking, different input parameters are expected in the dictionary, such as number of rows, number of modules per row, row azimuth, hub_height (distance between the axis of rotation of the modules and the ground). 

# In[11]:


hub_height = 2.3
sceneDict = {'gcr': gcr,'hub_height':hub_height, 'nMods': 20, 'nRows': 7}  


# To make the scene we have to create a Scene Object through the method makeScene1axis. This method will create a .rad file in the objects folder, with the parameters specified in sceneDict and the module created above.

# In[12]:


trackerdict = demo.makeScene1axis(trackerdict = trackerdict, moduletype = moduletype, sceneDict = sceneDict) 


# <a id='step9'></a>

# ## 9. Combine Ground, Sky and Scene Objects
# 
# makeOct1axis joins the sky.rad file, ground.rad file, and the geometry.rad files created in makeScene.

# In[13]:


trackerdict = demo.makeOct1axis(trackerdict = trackerdict)


# <a id='step10'></a>

# ## 10. Analyze and get results
# 
# We can choose to analyze any module in the Scene we have created. The default, if no modWanted or rowWanted is passed, is to sample the center module of the center row. 
# 
# For this example we will sample row 2, module 9.

# In[14]:


modWanted = 9
rowWanted = 2
customname = '_Row_2_Module_09' # This is useful if we want to do various analysis.
trackerdict = demo.analysis1axis(trackerdict, modWanted=9, rowWanted = 2, customname=customname)


# Let's look at the results with more detail. The analysis1axis routine created individual result .csv files for each angle, as well as one cumulative result .csv where the irradiance is added by sensor.
# 

# In[15]:


results = load.read1Result('cumulative_results__Row_2_Module_09.csv')
results


# There are various things to notice:
# 
# I. The materials column has a specific format that will tell you if you are sampling the correct module:
# 
#                                 a{ModWanted}.{rowWanted}.a{numPanel}.{moduletype}.material_key
# 
# * Since for this journal numPanels = 2, numPanel can either be 0 or 1, for the East-most and West-most module in the collector width.
# * numPanel, ModWanted and RowWanted are indexed starting at 0 in the results.
# * material_key is from the surface generated inside radiance. Usually it is 6457 for top surface of hte module and .2310 for the bottom one. 
# 
# II. Sensors sample always in the same direction. For this N-S aligned tracker, that is East-most to West. For this 2-up portrait tracker which is 3.5 meters, 20x7 rows and we are sampling module 9 on row 2, the East to West sampling goes from 22.6 m to 19.81 m = 2.79m. It is not exatly 3.5 because the sensors are spaced evenly through the collector width (CW): 
# 
# 
# ![Sensors spaced along collector width](../images_wiki/Journal2Pics/spaced_sensors.png)
# 
# III. When there is a ygap in the collector width (2-UP or more configuration), some of the sensors might end up sampling the torque tube, or the sky. You can ses that in the materials columns. This also happens if the number of sensors is quite high, the edges of the module might be sampled instead of the sensors. For this reason, before calculating bifacial gain these results must be cleaned. For more advanced simulations, make sure you clean each result csv file individually.  We provide some options on load.py but some are very use-specific, so you might have to develop your own cleaning tool (or let us know on issues!)
# 
# <div class="alert alert-warning">
# Important: If you have torquetubes and y-gap values, make sure you clean your results.
# </div>
# 

# <a id='step11'></a>

# ## 11. Clean Results
# 
# We have two options for cleaning results. The simples on is <b>load.cleanResults</b>, but there is also a deepClean for specific purposes.
# 
# cleanResults will find materials that should not have values and set them to NaN.

# In[16]:


results_clean = load.cleanResult(results)
results_clean


# These are the total irradiance values over all the hours of the year that the module at each sampling point will receive. Dividing the back irradiance average by the front irradiance average will give us the bifacial gain for the year:
# 
# ![Bifacial Gain in Irradiance Formula](../images_wiki/Journal1Pics/BGG_Formula.png)
# 
# Assuming that our module from Prism Solar has a bifaciality factor (rear to front performance) of 90%, our <u> bifacial gain </u> is of:

# In[17]:


bifacialityfactor = 0.9
print('Annual bifacial ratio: %0.3f ' %( np.nanmean(results_clean.Wm2Back) * bifacialityfactor / np.nanmean(results_clean.Wm2Front)) )


# <a id='condensed'></a>

# ## CONDENSED VERSION
# Everything we've done so far in super short condensed version:

# In[18]:


albedo = 0.25
lat = 37.5
lon = -77.6
nMods = 20
nRows = 7
hub_height = 2.3
gcr = 0.33
moduletype = 'Custom Tracker Module'  # this must already exist since we are not calling makeModule in this CONDENSED example.
testfolder = r'C:\Users\sayala\Documents\RadianceScenes\Tutorials\Journal2'
limit_angle = 60
angeldelta = 5
backtrack = True
gcr = gcr
modWanted = 9
rowWanted = 2
cumulativesky = True

import bifacial_radiance
demo = RadianceObj(path = testfolder) 
demo.setGround(albedo)
epwfile = demo.getEPW(lat,lon) 
metdata = demo.readEPW(epwfile)
demo.set1axis(limit_angle = limit_angle, backtrack = backtrack, gcr = gcr, cumulativesky = cumulativesky)
demo.genCumSky1axis()
sceneDict = {'gcr': gcr,'height':hub_height, 'nMods': nMods, 'nRows': nRows}  # orientation deprecated on v.0.2.4.
demo.makeScene1axis(moduletype=moduletype,sceneDict = sceneDict)
demo.makeOct1axis()
demo.analysis1axis(modWanted = modWanted, rowWanted = rowWanted)


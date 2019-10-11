#!/usr/bin/env python
# coding: utf-8

# ## 3 - Medium Level Example - 1-Axis tracker by hour (gendaylit)
# 
# Example demonstrating the use of doing hourly smiulations with Radiance gendaylit for 1-axis tracking. This is a medium level example because it also explores a couple subtopics:
# 
# #### Subtopics:
# <ul>
#     <li> The structure of the tracker dictionary "trackerDict". </li>
#     <li> How to calculate GCR </li>
#     <li> How to make a cell-level module </li>
#     <li> Various methods to use the trackerdictionary for analysis. </li>
# </ul>
#  
# #### Doing full year simulations with gendaylit: 
# 
# Performs the simulation hour by hour requires either a good computer or some patience, since there are ~4000 daylight-hours in the year. With a 32GB RAM, Windows 10 i7-8700 CPU @ 3.2GHz with 6 cores this takes 1 day. The code also allows for multiple cores or HPC use -- there is documentation/examples inside the software at the moment, but that is an advanced topic. The procedure can be broken into shorter steps for one day or a single timestamp simulation which is exemplified below.
# 
# ### Steps:
# <ol>
#     <li> <a href='#step1'> Create a folder for your simulation, and load bifacial_radiance </a></li> 
#     <li> <a href='#step2'> Define all your system variables </a></li> 
#     <li> <a href='#step3'> Create Radiance Object, Set Albedo and Weather </a></li> 
#     <li> <a href='#step4'> Make Module: Cell Level Module Example </a></li>    
#     <li> <a href='#step5'> Calculate GCR</a></li> 
#     <li> <a href='#step6'> Set Tracking Angles </a></li> 
#     <li> <a href='#step7'> Generate the Sky </a></li> 
#     <li> <a href='#step8'> Make Scene 1axis </a></li> 
#     <li> <ol type="A"><li><a href='#step9a'> Make Oct and AnalyzE 1 HOUR </a></li> 
#     <li> <a href='#step9b'> Make Oct and Analye Range of Hours </a></li> 
#         <li> <a href='#step9c'>  Make Oct and Analyze All Tracking Dictionary </a></li> </ol>
# </ol>
# 
# And finally:  <ul> <a href='#condensed'> Condensed Version: All Tracking Dictionary </a></ul>   

# <a id='step1'></a>

# 
# ## 1. Create a folder for your simulation, and load bifacial_radiance 
# 
# First let's set the folder where the simulation will be saved. By default, this is the TEMP folder in the bifacial_radiance distribution.
# 
# The lines below find the location of the folder relative to this Jupyter Journal. You can alternatively point to an empty directory (it will open a load GUI Visual Interface) or specify any other directory in your computer, for example:
# 
# #### testfolder = r'C:\Users\sayala\Documents\RadianceScenes\Tutorials\Journal3'
# 

# In[1]:


import os
testfolder = os.path.abspath(r'..\..\bifacial_radiance\TEMP')  

print ("Your simulation will be stored in %s" % testfolder)


# #### Pay attention: different importing method:
# 
# So far we've used "from bifacial_radiance import *" to import all the bifacial_radiance files into our working space in jupyter. For this journal we will do a "import bifacial_radiance" . This method of importing requires a different call for some functions as you'll see below. For example, instead of calling demo = RadianceObj(path = testfolder) as on Tutorial 2, in this case we will neeed to do demo = bifacial_radiance.RadianceObj(path = testfolder). 

# In[2]:


import bifacial_radiance
import numpy as np
import pprint    # We will be pretty-printing the trackerdictionary throughout to show its structure.


# <a id='step2'></a>

# ## 2. Define all your system variables
# 
# Just like in the condensed version show at the end of Tutorial 2, for this tutorial we will be starting all of our system variables from the beginning of the jupyter journal, instead than throughout the different cells (for the most part)

# In[3]:


simulationName = 'Tutorial 3'    # For adding a simulation name when defning RadianceObj. This is optional.
moduletype = 'Custom Cell-Level Module'    # We will define the parameters for this below in Step 4.
testfolder = r'C:\Users\sayala\Documents\RadianceScenes\Tutorials\Journal2'
albedo = "litesoil"      # this is one of the options on ground.rad
lat = 37.5   
lon = -77.6

# Scene variables
nMods = 20
nRows = 7
hub_height = 2.3 # meters
pitch = 10 # meters      # We will be using pitch instead of GCR for this example.

# Traking parameters
cumulativesky = False
limit_angle = 45 # tracker rotation limit angle
angledelta = 0.01 # we will be doing hourly simulation, we want the angle to be as close to real tracking as possible.
backtrack = True 

#makeModule parameters
# x and y will be defined later on Step 4 for this tutorial!!
xgap = 0.01
ygap = 0.10
zgap = 0.05
numpanels = 2
torquetube = True
axisofrotationTorqueTube = False
diameter = 0.1
tubetype = 'Oct'    # This will make an octagonal torque tube.
material = 'black'   # Torque tube of this material (0% reflectivity)


# <a id='step3'></a>

# ## 3. Create Radiance Object, Set Albedo and Weather
# 
# Same steps as previous two tutorials, so condensing it into one step. You hopefully have this down by now! :)
# 
# 
# <div class="alert alert-warning">
# Notice that we are doing bifacial_radiance.RadianceObj because we change the import method for this example!
# </div>

# In[4]:


demo = bifacial_radiance.RadianceObj(simulationName, path = testfolder)  # Adding a simulation name. This is optional.
demo.setGround(albedo) 
epwfile = demo.getEPW(lat = lat, lon = lon) 
metdata = demo.readWeatherFile(weatherFile = epwfile) 


# <a id='step4'></a>

# ## 4. Make Module: Cell Level Module Example
# 
# Instead of doing a opaque, flat single-surface module, in this tutorial we will create a module made up by cells. We can define variuos parameters to make a cell-level module, such as cell size and spacing between cells. To do this, we will pass a dicitonary with the needed parameters to makeModule, as shown below.
# 
# <div class="alert alert-warning">
# Since we are passing a cell-level dictionary, the values for module's x and y of the module will be calculated by the software -- no need to pass them (and if you do, they'll just get ignored)
#     </div>

# In[5]:


numcellsx = 6
numcellsy = 12
xcell = 0.156
ycell = 0.156
xcellgap = 0.02
ycellgap = 0.02

cellLevelModuleParams = {'numcellsx': numcellsx, 'numcellsy':numcellsy, 
                         'xcell': xcell, 'ycell': ycell, 'xcellgap': xcellgap, 'ycellgap': ycellgap}

mymodule = demo.makeModule(name=moduletype, torquetube=torquetube, diameter=diameter, tubetype=tubetype, material=material, 
                xgap=xgap, ygap=ygap, zgap=zgap, numpanels=numpanels, 
                cellLevelModuleParams=cellLevelModuleParams, 
                axisofrotationTorqueTube=axisofrotationTorqueTube)


# <a id='step5'></a>

# ## 5. Calculate GCR
# 
# In this example we passed the parameter "pitch". Pitch is the spacing between rows (for example, between hub-posts) in a field.
# To calculate Ground Coverage Ratio (GCR), we must relate the pitch to the collector-width by:
#     
# ![GCR = CW / pitch](../images_wiki/Journal3Pics/Equation_GCR.png)
# 
# The collector width for our system must consider the number of panels and the y-gap:
#     
# ![CW](../images_wiki/Journal3Pics/Equation_CW.png)
#     
# Collector Width gets saved in your module parameters (and later on your scene and trackerdict) as "sceney". You can calculate your collector width with the equation, or you can use this method to know your GCR:

# In[6]:


# For more options on makemodule, see the help description of the function.  
CW = mymodule['sceney']
gcr = CW / pitch
print ("The GCR is :", gcr)


# <a id='step6'></a>

# ## 6. Set Tracking Angles
# 
# This function will read the weather file, and based on the sun position it will calculate the angle the tracker should be at for each hour. It will create metdata files for each of the tracker angles considered.
# 
# For doing hourly simulations, remember to set **cumulativesky = False** here!

# In[7]:


trackerdict = demo.set1axis(metdata = metdata, limit_angle = limit_angle, backtrack = backtrack, 
                            gcr = gcr, cumulativesky = cumulativesky)


# In[8]:


print ("Full trackerdict for all the year created by set1axis: %s " % (len(demo.trackerdict))) 


# set1axis initializes the trackerdictionary Trackerdict. Trackerdict contains all hours in the year as keys. For example: trackerdict['12_16_08']. It is a return variable on many of the 1axis functions, but it is also stored inside of your Radiance Obj (i.e. demo.trackerdict). In this journal we are storing it as a variable to mute the option (otherwise it prints the returned trackerdict contents every time)
# 

# In[9]:


pprint.pprint(trackerdict['12_16_08'])


# In[10]:


pprint.pprint(demo.trackerdict['12_16_08'])


# All of the following functions add up elements to trackerdictionary to keep track (ba-dum tupzz) of the Scene and simulation parameters. In advanced journals we will explore the inner structure of trackerdict. For now, just now it exists :)

# <a id='step7'></a>

# ## 7. Generate the Sky
# 
# 
# We will create skies for each hour we want to model with the function gendaylit1axis. 
# 
# **If you don't specify a startdate and enddate, all the year will be created, which will take more time.**
# 
# For this example we are doing just two days in January. Format has to be a 'MM_DD' or 'MM/DD'

# In[11]:


startdate = '01/13'     
enddate = '01/14'
trackerdict = demo.gendaylit1axis(startdate=startdate, enddate=enddate) 


# Since we passed startdate and enddate to gendaylit, it will prune our trackerdict to only the desired days.
# Let's explore our trackerdict:

# In[12]:


print ("\nTrimmed trackerdict by gendaylit1axis to start and enddate length: %s " % (len(trackerdict)))
print ("")
trackerkeys = sorted(trackerdict.keys())
print ("Option of hours are: ", trackerkeys)
print ("")
print ("Contents of trackerdict for sample hour:")
pprint.pprint(trackerdict[trackerkeys[0]])


# <a id='step8'></a>

# ## 8. Make Scene 1axis
# 
# We can use gcr or pitch fo our scene dictionary.

# In[13]:


# making the different scenes for the 1-axis tracking for the dates in trackerdict2.

sceneDict = {'pitch': pitch,'hub_height':hub_height, 'nMods':nMods, 'nRows': nRows}  

trackerdict = demo.makeScene1axis(trackerdict = trackerdict, moduletype = moduletype, sceneDict = sceneDict) 


# The scene parameteres are now stored in the trackerdict. To view them and to access them:
#     

# In[14]:


pprint.pprint(trackerdict[trackerkeys[0]])


# In[15]:


pprint.pprint(demo.trackerdict[trackerkeys[5]]['scene'].__dict__)


# <a id='step9a'></a>

# ## 9. Make Oct and Analyze 
# 
# ### A. Make Oct and Analyze 1Hour
# 
# There are various options now to analyze the trackerdict hours we have defined. We will start by doing just one hour, because it's the fastest. Make sure to select an hour that exists in your trackerdict!
# 
# Options of hours:

# In[16]:


pprint.pprint(trackerkeys)


# In[17]:


demo.makeOct1axis(singleindex='01_13_08')
results = demo.analysis1axis(singleindex='01_13_08')
print('\n\nHourly bifi gain: {:0.3}'.format(sum(demo.Wm2Back) / sum(demo.Wm2Front)))


# The trackerdict now contains information about the octfile, as well as the Analysis Object results

# In[18]:


print ("\n Contents of trackerdict for sample hour after analysis1axis: ")
pprint.pprint(trackerdict[trackerkeys[0]])


# In[19]:


pprint.pprint(trackerdict[trackerkeys[0]]['AnalysisObj'].__dict__)


# <a id='step9b'></a>

# ### B. Make Oct and Analye Range of Hours

# You could do a range of indexes following a similar procedure:

# In[20]:


for time in ['01_13_09','01_13_13']:  
    demo.makeOct1axis(singleindex=time)
    results=demo.analysis1axis(singleindex=time)

print('Accumulated hourly bifi gain: {:0.3}'.format(sum(demo.Wm2Back) / sum(demo.Wm2Front)))


# Note that the bifacial gain printed above is for the accumulated irradiance between the hours modeled so far. 
# That is, demo.Wm2Back and demo.Wm2Front are for January 13, 8AM to 1 AM. Compare demo.Wm2back below with what we had before:

# In[21]:


demo.Wm2Back


# To print the specific bifacial gain for a specific hour, you can use the following:

# In[22]:


sum(trackerdict['01_13_13']['AnalysisObj'].Wm2Back) / sum(trackerdict['01_13_13']['AnalysisObj'].Wm2Front)


# <a id='step9c'></a>

# ### C. Make Oct and Analyze All Tracking Dictionary
# 
# This might considerably more time, depending on the number of entries on the trackerdictionary. If no **startdt** and **enddt** where specified on STEP **gendaylit1axis, this will run ALL of the hours in the year (~4000 hours).**
# 

# In[ ]:


demo.makeOct1axis()
results = demo.analysis1axis()
print('Accumulated hourly bifi gain for all the trackerdict: {:0.3}'.format(sum(demo.Wm2Back) / sum(demo.Wm2Front)))


# <div class="alert alert-warning">
# Remember you should clean your results first! This will have torquetube and sky results if performed this way so don't trust this simplistic bifacial_gain examples.
# </div>

# <a id='condensed'></a>

# ### Condensed Version: All Tracking Dictionary
# 
# This is the summarized version to run gendaylit for one entries in the trackigndictionary.

# In[ ]:


simulationName = 'Tutorial 3'
moduletype = 'Custom Cell-Level Module'    # We will define the parameters for this below in Step 4.
testfolder = r'C:\Users\sayala\Documents\RadianceScenes\Tutorials\Journal2'
albedo = "litesoil"      # this is one of the options on ground.rad
lat = 37.5   
lon = -77.6

# Scene variables
nMods = 20
nRows = 7
hub_height = 2.3 # meters
pitch = 10 # meters      # We will be using pitch instead of GCR for this example.

# Traking parameters
cumulativesky = False
limit_angle = 45 # tracker rotation limit angle
angledelta = 0.01 # we will be doing hourly simulation, we want the angle to be as close to real tracking as possible.
backtrack = True 

#makeModule parameters
# x and y will be defined later on Step 4 for this tutorial!!
xgap = 0.01
ygap = 0.10
zgap = 0.05
numpanels = 2
torquetube = True
axisofrotationTorqueTube = False
diameter = 0.1
tubetype = 'Oct'    # This will make an octagonal torque tube.
material = 'black'   # Torque tube of this material (0% reflectivity)

startdate = '11/06'     
enddate = '11/06'
demo = bifacial_radiance.RadianceObj(simulationName, path=testfolder)  
demo.setGround(albedo) 
epwfile = demo.getEPW(lat,lon) 
metdata = demo.readWeatherFile(epwfile)  
sceneDict = {'pitch':pitch,'hub_height':hub_height, 'nMods': nMods, 'nRows': nRows}  
demo.set1axis(limit_angle = limit_angle, backtrack = backtrack, gcr = gcr, cumulativesky = cumulativesky)
demo.gendaylit1axis(startdate=startdate, enddate=enddate)
demo.makeScene1axis(moduletype=moduletype,sceneDict=sceneDict) #makeScene creates a .rad file with 20 modules per row, 7 rows.
demo.makeOct1axis()
demo.analysis1axis()


#!/usr/bin/env python
# coding: utf-8

# # 1 - Introductory Example: Fixed-Tilt simple setup
# 
# This jupyter journal will walk us through the creation of the most basic fixed-tilt simulation possible with bifacial_radiance.
# We will simulate a 1-up landscape system over a white rooftop.
# 
# Steps include:
# 
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
# 

# In[1]:


import os
testfolder = os.path.abspath(r'..\..\bifacial_radiance\TEMP\Demo1')  

print ("Your simulation will be stored in %s" % testfolder)


# Load bifacial_radiance

# In[2]:


from bifacial_radiance import *

import numpy as np


# <a id='step2'></a>

# ## 2. Create a Radiance Object

# In[3]:


demo = RadianceObj('bifacial_example',testfolder)  


# This will create all the folder structure of the bifacial_radiance Scene in the designated testfolder in your computer, and it should look like this:
# 
# 
# <img src="..\images_wiki\Journal1Pics\folderStructure.png">

# <a id='step3'></a>

# ## 3. Set the Albedo

# If a number between 0 and 1 is passed, it assumes it's an albedo value. For this example, we want a high-reflectivity rooftop albedo surface, so we will set the albedo to 0.62

# In[4]:


albedo = 0.62
demo.setGround(albedo)


# To see more options of ground materials available (located on ground.rad), run this function without any input. 

# ## 4. Download and Load Weather Files
# 
# There are various options provided in bifacial_radiance to load weatherfiles. getEPW is useful because you just set the latitude and longitude of the location and it donwloads the meteorologicla data for any location. 

# In[5]:


epwfile = demo.getEPW(lat = 37.5, lon = -77.6) 


# The downloaded EPW will be in the EPWs folder.
# 
# To load the data, use readWeatherFile. This reads EPWs, TMY meterological data, or even your own data as long as it follows TMY data format (With any time resoultion).

# In[6]:


# Read in the weather data pulled in above. 
metdata = demo.readWeatherFile(epwfile) 


# <a id='step5'></a>

# ## 5. Generate the Sky.
# 
# Sky definitions can either be for a single time point with gendaylit function,
# or using gencumulativesky to generate a cumulativesky for the entire year.
# 

# In[7]:


fullYear = True
if fullYear:
    demo.genCumSky(demo.epwfile) # entire year.
else:
    demo.gendaylit(metdata,4020)  # Noon, June 17th (timepoint # 4020)


# The method gencumSky calculates the hourly radiance of the sky hemisphere by dividing it into 145 patches. Then it adds those hourly values to generate one single <b> cumulative sky</b>. Here is a visualization of this patched hemisphere for Richmond, VA, US. Can you deduce from the radiance values of each patch which way is North?
# 
# <img src="../images_wiki/Journal1Pics/cumulativesky.png">

# 
# <img src="../images_wiki/Journal1Pics/cumulativesky.png">
# 
# Answer: Since Richmond is in the Northern Hemisphere, the modules face the south, which is where most of the radiation from the sun is coming. The north in this picture is the darker blue areas.

# <a id='step6'></a>

# ## 6. DEFINE a Module type
# 
# You can create a custom PV module type. In this case we are defining a module named "Prism Solar Bi60", in landscape. The x value defines the size of the module along the row, so for landscape modules x > y. This module measures y = 0.984 x = 1.695. 
# 
# 
# <div class="alert alert-success">
# You can specify a lot more variables in makeModule like cell-level modules, multiple modules along the Collector Width (CW), torque tubes, spacing between modules, etc. 
#     
# Reffer to the <a href="https://bifacial-radiance.readthedocs.io/en/latest/generated/bifacial_radiance.RadianceObj.makeModule.html#bifacial_radiance.RadianceObj.makeModule"> Module Documentation </a> and read the following jupyter journals to explore all your options.
# </div>
# 

# In[8]:


module_type = 'Prism Solar Bi60 landscape' 
demo.makeModule(name=module_type,x=1.695, y=0.984)


# In case you want to use a pre-defined module or a module you've created previously, they are stored in a JSON format in data/module.json, and the options available can be called with printModules:

# In[9]:


availableModules = demo.printModules()


# <a id='step7'></a>

# ## 7. Make the Scene
# 
#  The sceneDicitonary specifies the information of the scene, such as number of rows, number of modules per row, azimuth, tilt, clearance_height (distance between the ground and lowest point of the module), pitch or gcr, and any other parameter. 
#  
# <img src="../images_wiki/Webinar/scenegoal.png">
# 
# 
# Reminder: Azimuth gets measured from N = 0, so for South facing modules azimuth should equal 180 degrees

# In[10]:


sceneDict = {'tilt':10,'pitch':3,'clearance_height':0.2,'azimuth':180, 'nMods': 3, 'nRows': 3} 


# To make the scene we have to create a Scene Object through the method makeScene. This method will create a .rad file in the objects folder, with the parameters specified in sceneDict and the module created above.

# In[11]:


scene = demo.makeScene(module_type,sceneDict)


# <a id='step8'></a>

# ## 8. COMBINE the Ground, Sky, and the Scene Objects
# 
# Radiance requires an "Oct" file that combines the ground, sky and the scene object into it. 
# The method makeOct does this for us.

# In[12]:


octfile = demo.makeOct(demo.getfilelist())  


# In[13]:


demo.getfilelist()


# This is how the octfile looks like (** broke the first line so it would fit in the view, it's usually super long)
# 
# <img src="../images_wiki/Webinar/octfileexample.png">

# <a id='step9'></a>

# ## 9. ANALYZE and get Results
# 
# Once the octfile tying the scene, ground and sky has been created, we create an Analysis Object. We first have to create an Analysis object, and then we have to specify where the sensors will be located with moduleAnalysis. 
# 
# <img src="../images_wiki/Webinar/analysisgoal.png">
# 
# Let's query the cente rmodule (default)
# 
# 

# First let's create the Analysis Object

# In[14]:


analysis = AnalysisObj(octfile, demo.basename)


# Then let's specify the sensor location. If no parameters are passed to moduleAnalysis, it will scan the center module of the center row:

# In[15]:


frontscan, backscan = analysis.moduleAnalysis(scene)


# The frontscan and backscan include a linescan along a chord of the module, both on the front and back. 
# 
# <img src="../images_wiki/Journal1Pics/frontscan_backscan.png">
# Analysis saves the measured irradiances in the front and in the back on the results folder. 

# In[16]:


results = analysis.analysis(octfile, demo.basename, frontscan, backscan)  


# The results are also automatically saved in the results folder. Some of our input/output functions can be used to read the results and work with them, for example:

# In[17]:


load.read1Result('results\irr_bifacial_example.csv')


# As can be seen in the results for the *Wm2Front* and *WM2Back*, the irradiance values are quite high. This is because a cumulative sky simulation was performed on <b> step 5 </b>, so this is the total irradiance over all the hours of the year that the module at each sampling point will receive. Dividing the back irradiance average by the front irradiance average will give us the bifacial gain for the year:
# 
# <img src="../images_wiki/Journal1Pics/BGG_Formula.png">
# 
# Assuming that our module from Prism Solar has a bifaciality factor (rear to front performance) of 90%, our <u> bifacial gain </u> is of:

# In[18]:


bifacialityfactor = 0.9
print('Annual bifacial ratio: %0.2f ' %( np.mean(analysis.Wm2Back) * bifacialityfactor / np.mean(analysis.Wm2Front)) )


# ### ANALYZE and get Results for another module
# 
# You can select what module you want to sample.
# 
# <img src="../images_wiki/Webinar/analysisgoal2.png">
# 

# In[19]:


modWanted=1
rowWanted=1
sensorsy=4
resultsfilename = demo.basename+"_Mod1Row1"

frontscan, backscan = analysis.moduleAnalysis(scene, modWanted = modWanted, rowWanted=rowWanted, sensorsy=sensorsy)
results = analysis.analysis(octfile, resultsfilename, frontscan, backscan)  


# In[20]:


load.read1Result('results\irr_bifacial_example_Mod1Row1.csv')


# <a id='step10'></a>

# ## 10. View / Render the Scene
# 
# 
# If you used gencumsky or gendaylit, you can view the <b> Scene </b> by navigating on a command line to the folder and typing:
# 
# ***objview materials\ground.rad objects\Prism_Solar_Bi60_landscape_0.2_3_10_20x7_origin0,0.rad***   
# 
# This <b> objview </b> has 3 different light sources of its own, so the shading is not representative.
# 
# ONLY If you used <b> gendaylit </b>, you can view the scene correctly illuminated with the sky you generated after generating the oct file, with 
# 
# ***rvu -vf views\front.vp -e .01 bifacial_example.oct***
# 
# The <b> rvu </b> manual can be found here: manual page here: http://radsite.lbl.gov/radiance/rvu.1.html
# 

# 
# Or you can also use the code below from bifacial_radiance to generate an *.HDR* rendered image of the scene. You can choose from front view or side view in the views folder:

# In[21]:


# Make a color render and falsecolor image of the scene.
analysis.makeImage('side.vp')
analysis.makeFalseColor('side.vp')


# This is how the False Color image stored in images folder should look like:
# 
# <img src="../images_wiki/Journal1Pics/openhdr_FalseColorExample.png">

# Files are saved as .hdr (high definition render) files.  Try LuminanceHDR viewer (free) to view them, or https://viewer.openhdr.org/ 
# 
# 

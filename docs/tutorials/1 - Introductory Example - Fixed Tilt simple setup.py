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
# First let's set the folder where the simulation will be saved. By default, this is the TEMP folder in the bifacial_radiance distribution.
# 
# The lines below find the location of the folder relative to this Jupyter Journa. You can alternatively point to an empty directory (it will open a load GUI Visual Interface) or specify any other directory in your computer, for example:
# 
# #### testfolder = r'C:\Users\sayala\Documents\RadianceScenes\Tutorials\Journal1'
# 
# 

# In[1]:


import os
testfolder = os.path.abspath(r'..\..\bifacial_radiance\TEMP')  

print ("Your simulation will be stored in %s" % testfolder)


# This will load bifacial_radiance and other libraries from python that will be useful for this Jupyter Journal:

# In[2]:


try:
    from bifacial_radiance import *
except ImportError:
    raise RuntimeError('bifacial_radiance is required. download distribution')

import numpy as np


# <a id='step2'></a>

# ## 2. Create a Radiance Object

# In[3]:


# Create a RadianceObj 'object' named bifacial_example. no whitespace allowed
demo = RadianceObj('bifacial_example',testfolder)  


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


# If a number between 0 and 1 is passed, it assumes it's an albedo value. For this example, we want a high-reflectivity rooftop albedo surface, so we will set the albedo to 0.62

# In[5]:


albedo = 0.62
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
metdata = demo.readWeatherFile(epwfile) 


# <a id='step5'></a>

# ## 5. Generate the Sky.
# 
# Sky definitions can either be for a single time point with gendaylit function,
# or using gencumulativesky to generate a cumulativesky for the entire year.
# 

# In[8]:


fullYear = True
if fullYear:
    demo.genCumSky(demo.epwfile) # entire year.
else:
    demo.gendaylit(metdata,4020)  # Noon, June 17th (timepoint # 4020)


# The method gencumSky calculates the hourly radiance of the sky hemisphere by dividing it into 145 patches. Then it adds those hourly values to generate one single <b> cumulative sky</b>. Here is a visualization of this patched hemisphere for Richmond, VA, US. Can you deduce from the radiance values of each patch which way is North?
# 
# ![Example of the hemisphere cumulative sky](../images_wiki/Journal1Pics/cumulativesky.png)
# 
# Answer: Since Richmond is in the Northern Hemisphere, the modules face the south, which is where most of the radiation from the sun is coming. The north in this picture is the darker blue areas.

# <a id='step6'></a>

# ## 6. DEFINE a Module type
# 
# You can create a custom PV module type. In this case we are defining a module named "Prism Solar Bi60", in landscape. The x value defines the size of the module along the row, so for landscape modules x > y. This module measures y = 0.984 x = 1.695. 
# 
# 
# <div class="alert alert-success">
# Modules in this example are 100% opaque. For drawing each cell, makeModule needs more inputs with cellLevelModule = True. You can also specify a lot more variables in makeModule like multiple modules, torque tubes, spacing between modules, etc. Reffer to the <a href="https://bifacial-radiance.readthedocs.io/en/latest/generated/bifacial_radiance.RadianceObj.makeModule.html#bifacial_radiance.RadianceObj.makeModule"> Module Documentation </a> and read the following jupyter journals to explore all your options.
# </div>
# 

# In[9]:


module_type = 'Prism Solar Bi60 landscape' 
demo.makeModule(name=module_type,x=1.695, y=0.984)


# In case you want to use a pre-defined module or a module you've created previously, they are stored in a JSON format in data/module.json, and the options available can be called with printModules:

# In[10]:


availableModules = demo.printModules()


# <a id='step7'></a>

# ## 7. Make the Scene
# 
#  The sceneDicitonary specifies the information of the scene, such as number of rows, number of modules per row, azimuth, tilt, clearance_height (distance between the ground and lowest point of the module) and any other parameter. 
#  
#  Azimuth gets measured from N = 0, so for South facing modules azimuth should equal 180 degrees
# 

# In[11]:


sceneDict = {'tilt':10,'pitch':3,'clearance_height':0.2,'azimuth':180, 'nMods': 20, 'nRows': 7} 


# To make the scene we have to create a Scene Object through the method makeScene. This method will create a .rad file in the objects folder, with the parameters specified in sceneDict and the module created above.

# In[12]:


scene = demo.makeScene(module_type,sceneDict)


# <a id='step8'></a>

# ## 8. COMBINE the Ground, Sky, and the Scene Objects
# 
# Radiance requires an "Oct" file that combines the ground, sky and the scene object into it. 
# The method makeOct does this for us.

# In[13]:


octfile = demo.makeOct(demo.getfilelist())  


# To see what files got merged into the octfile, you can use the helper method getfilelist. This is useful for advanced simulations too, specially when you want to have different Scene objects in the same simulation, or if you want to add other custom elements to your scene (like a building, for example)

# In[14]:


demo.getfilelist()


# <a id='step9'></a>

# ## 9. ANALYZE and get Results
# 
# Once the octfile tying the scene, ground and sky has been created, we create an Analysis Object. We first have to create an Analysis object, and then we have to specify where the sensors will be located with moduleAnalysis. 
# 

# First let's create the Analysis Object

# In[15]:


analysis = AnalysisObj(octfile, demo.basename)


# Then let's specify the sensor location. If no parameters are passed to moduleAnalysis, it will scan the center module of the center row:

# In[16]:



frontscan, backscan = analysis.moduleAnalysis(scene)


# The frontscan and backscan include a linescan along a chord of the module, both on the front and back. 
# 
# ![Simple example for south facing module](../images_wiki/Journal1Pics/frontscan_backscan.png)
# Analysis saves the measured irradiances in the front and in the back on the results folder.  Prints out the ratio of the average of the rear and front irradiance values along a chord of the module.

# In[21]:


results = analysis.analysis(octfile, demo.basename, frontscan, backscan)  


# The results are also automatically saved in the results folder. Some of our input/output functions can be used to read the results and work with them, for example:

# In[24]:


load.read1Result('results\irr_bifacial_example.csv')


# As can be seen in the results for the *Wm2Front* and *WM2Back*, the irradiance values are quite high. This is because a cumulative sky simulation was performed on <b> step 5 </b>, so this is the total irradiance over all the hours of the year that the module at each sampling point will receive. Dividing the back irradiance average by the front irradiance average will give us the bifacial gain for the year:
# 
# ![Bifacial Gain in Irradiance Formula](../images_wiki/Journal1Pics/BGG_Formula.png)
# 
# Assuming that our module from Prism Solar has a bifaciality factor (rear to front performance) of 90%, our <u> bifacial gain </u> is of:

# In[19]:


bifacialityfactor = 0.9
print('Annual bifacial ratio: %0.2f ' %( np.mean(analysis.Wm2Back) * bifacialityfactor / np.mean(analysis.Wm2Front)) )


# <a id='step10'></a>

# ## 10. View / Render the Scene
# 
# If you used gencumsky or gendaylit, you can view the <b> Scene </b> by navigating on a command line to the folder and typing:
# 
# ##### objview materials\ground.rad objects\Prism_Solar_Bi60_landscape_0.2_3_10_20x7_origin0,0.rad     
# 
# This <b> objview </b> has 3 different light sources of its own, so the shading is not representative.
# 
# ONLY If you used <b> gendaylit </b>, you can view the scene correctly illuminated with the sky you generated after generating the oct file, with 
# 
# ##### rvu -vf views\front.vp -e .01 bifacial_example.oct
# 
# The <b> rvu </b> manual can be found here: manual page here: http://radsite.lbl.gov/radiance/rvu.1.html
# 
# Or you can also use the code below from bifacial_radiance to generate an HDR rendered image of the scene. You can choose from front view or side view in the views folder:

# In[20]:


# Make a color render and falsecolor image of the scene.
analysis.makeImage('side.vp')
analysis.makeFalseColor('side.vp')


# This is how the False Color image stored in images folder should look like:
# 
# ![OpenHDR image example of False color](../images_wiki/Journal1Pics/openhdr_FalseColorExample.png)

# Files are saved as .hdr (high definition render) files.  Try LuminanceHDR viewer (free) to view them, or https://viewer.openhdr.org/ 
# 
# 

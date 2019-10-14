#!/usr/bin/env python
# coding: utf-8

# # 6 - Advanced topics: Understanding trackerdict structure
# 
# Tutorial 3 gives a good, detailed introduction to the trackerdict structure step by step.
# Here is a condensed summary of functions you can use to explore the tracker dictionary.
# 
# 
# ### Steps:
# 
# <ol>
#     <li> <a href='#step1'> Create a short Simulation + tracker dictionary beginning to end for 1 day </a></li>
#     <li> <a href='#step2'> Explore the tracker dictionary </a></li>
#     <li> <a href='#step3'> Explore Save Options </a></li>
# </ol>

# <a id='step 1'></a>

# ### 1. Create a short Simulation + tracker dictionary beginning to end for 1 day

# In[ ]:


import bifacial_radiance

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

# Simulation range days
startdate = '11/06'     
enddate = '11/06'

# Cell Parameters
numcellsx = 6
numcellsy = 12
xcell = 0.156
ycell = 0.156
xcellgap = 0.02
ycellgap = 0.02

demo = bifacial_radiance.RadianceObj(simulationName, path=testfolder)  
demo.setGround(albedo) 
epwfile = demo.getEPW(lat,lon) 
metdata = demo.readWeatherFile(epwfile)  
cellLevelModuleParams = {'numcellsx': numcellsx, 'numcellsy':numcellsy, 
                         'xcell': xcell, 'ycell': ycell, 'xcellgap': xcellgap, 'ycellgap': ycellgap}
mymodule = demo.makeModule(name=moduletype, torquetube=torquetube, diameter=diameter, tubetype=tubetype, material=material, 
                xgap=xgap, ygap=ygap, zgap=zgap, numpanels=numpanels, 
                cellLevelModuleParams=cellLevelModuleParams, 
                axisofrotationTorqueTube=axisofrotationTorqueTube)
sceneDict = {'pitch':pitch,'hub_height':hub_height, 'nMods': nMods, 'nRows': nRows}  
demo.set1axis(limit_angle = limit_angle, backtrack = backtrack, gcr = mymodule['sceney'] / pitch, cumulativesky = cumulativesky)
demo.gendaylit1axis(startdate=startdate, enddate=enddate)
demo.makeScene1axis(moduletype=moduletype,sceneDict=sceneDict) #makeScene creates a .rad file with 20 modules per row, 7 rows.
demo.makeOct1axis()
demo.analysis1axis()


# <a id='step2'></a>

# ### 2. Explore the tracker dictionary
# 
# You can use any of the below options to explore the tracking dictionary. Copy it into an empty cell to see their contents.

# In[ ]:


demo.__dict__   # Shows all keys 

trackerkeys = sorted(trackerdict.keys()) # get the trackerdict keys to see a specific hour.

demo.trackerdict[trackerkeys[0]] # This prints all trackerdict content
demo.trackerdict[trackerkeys[0]]['scene']  # This just prints that scene is a Scene object
demo.trackerdict[trackerkeys[0]]['scene'].__dict__ # This shows the Scene Object contents
demo.trackerdict[trackerkeys[0]]['scene'].scenex  # Addressing one of the variables in the Scene object
demo.trackerdict[trackerkeys[0]]['scene'].sceneDict # Printing the scene dictionary saved in the Scene Object
demo.trackerdict[trackerkeys[0]]['scene'].sceneDict['tilt'] # Addressing one of the variables in the scene dictionary
demo.trackerdict[trackerkeys[0]]['scene'].scene.__dict__ # Swhoing the scene dictionary inside the Scene Object values 

# Looking at the AnalysisObj results indivudally
demo.trackerdict[trackerkeys[0]]['AnalysisObj']  # This just prints that AnalysisObj is an Analysis object
demo.trackerdict[trackerkeys[0]]['AnalysisObj'].__dict__ # This shows the Analysis Object contents
demo.trackerdict[trackerkeys[0]]['AnalysisObj'].mattype # Addressing one of the variables in the Analysis Object

# Looking at the Analysis results Accumulated for the day:
demo.Wm2Back  # this value is the addition of every individual irradiance result for each hour simulated.

#  THREE WAYS OF CALLING THE SAME THING:
# (this might be cleaned up/streamlined in following releases.
demo.trackerdict[trackerkeys[0]]['scene'].scenex
demo.trackerdict[trackerkeys[0]]['scene'].moduleDict['scenex']
demo.trackerdict[trackerkeys[0]]['scene'].scene.scenex


# <a id='step3'></a>

# ### 3. Explore Save Options
# 
# The following lines offer ways to save your trackerdict or your demo object.

# In[ ]:


demo.exportTrackerDict(trackerdict = demo.trackerdict, savefile = 'results\\test_reindexTrue.csv', reindex = False)
demo.save(savefile = 'results\\demopickle.pickle')


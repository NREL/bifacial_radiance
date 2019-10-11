#!/usr/bin/env python
# coding: utf-8

# # 7 - Advanced topics - Multiple SceneObjects Example
# 
# This journal shows how to:
# 
# <ul>
#     <li> Create multiple scene objects in the same scene. </li>
#     <li> Analyze multiple scene objects in the same scene </li>
#     <li> Add a marker to find the origin (0,0) on a scene (for sanity-checks/visualization). </li>
# 
# A scene Object is defined as an array of modules, with whatever parameters you want to give it. In this case, we are modeling one array of 2 rows of 5 modules in landscape, and one array of 1 row of 5 modules in 2-UP, portrait configuration, as the image below:
# 
# ![multiple Scene Objects Example](..\images_wiki\Journal_example_multiple_objects.PNG)
# 

# In[2]:


import os
testfolder = os.path.abspath(r'..\bifacial_radiance\TEMP')  

print ("Your simulation will be stored in %s" % testfolder)
    
from bifacial_radiance import RadianceObj, AnalysisObj    


# In[3]:


# Generating Standard FIXED SETUP
demo = RadianceObj("MultipleObj", path = testfolder)  # Create a RadianceObj 'object'
demo.setGround(0.62)
epwfile = demo.getEPW(lat = 37.5, lon = -77.6)    
metdata = demo.readEPW('EPWs\\USA_VA_Richmond.Intl.AP.724010_TMY.epw') 
#metdata = demo.readEPW('EPWs\\USA_VA_Richmond.Intl.AP.724010_TMY.epw') # read in the weather data directly
fullYear = True
#demo.genCumSky(demo.epwfile) # entire year.
demo.gendaylit(metdata,4020)  # Noon, June 17th 
module_type = 'Prism Solar Bi60 landscape' 
demo.makeModule(name=module_type,y=1,x=1.7,bifi = 0.90)
sceneDict = {'tilt':10,'pitch':1.5,'clearance_height':0.2,'azimuth':180, 'nMods': 5, 'nRows': 2, 'appendRadfile':True} 
sceneObj1 = demo.makeScene(module_type,sceneDict)  


# In[4]:


# Checking values after Scene
print ("SceneObj1 modulefile: %s" % sceneObj1.modulefile)
print ("SceneObj1 SceneFile: %s" %sceneObj1.radfiles)
print ("SceneObj1 GCR: %s" % round(sceneObj1.gcr,2))
print ("FileLists: \n %s" % demo.getfilelist())


# Creating a different Scene. Same Module, different values.
# Notice we are passing a originx and originy to displace the center of this new sceneObj to that location.
# 

# In[5]:


sceneDict2 = {'tilt':30,'pitch':5,'clearance_height':1,'azimuth':180, 'nMods': 5, 'nRows': 1, 'originx': 0, 'originy': 3.5, 'appendRadfile':True} 
module_type2='Module2'
demo.makeModule(name=module_type2,x=1,y=1.6, numpanels=2, ygap=0.15)
sceneObj2 = demo.makeScene(module_type2,sceneDict2)  


# In[6]:


# Checking values for both scenes after creating new SceneObj
print ("SceneObj1 modulefile: %s" % sceneObj1.modulefile)
print ("SceneObj1 SceneFile: %s" %sceneObj1.radfiles)
print ("SceneObj1 GCR: %s" % round(sceneObj1.gcr,2))

print ("\nSceneObj2 modulefile: %s" % sceneObj2.modulefile)
print ("SceneObj2 SceneFile: %s" %sceneObj2.radfiles)
print ("SceneObj2 GCR: %s" % round(sceneObj2.gcr,2))

#getfilelist should have info for the rad file created by BOTH scene objects.
print ("NEW FileLists: \n %s" % demo.getfilelist())


# ### Add a Marker at the Origin (coordinates 0,0) for help with visualization
# I usually use this to create "markers" for the geometry to orient myself when doing sanity-checks (for example, marke where 0,0 is, or where 5,0 coordinate is). That is what I am doing here, for the image I'm attaching.

# In[7]:


# NOTE: offsetting translation by 0.1 so the center of the marker is at the desired coordinate.
name='Post1'
text='! genbox black originMarker 0.2 0.2 1 | xform -t -0.1 -0.1 0'
customObject = demo.makeCustomObject(name,text)
demo.appendtoScene(sceneObj1.radfiles, customObject, '!xform -rz 0')


# ### Combine all scene Objects into one OCT file 
# Run makeOCT to make the scene with both scene objects AND the marker in it, the ground and the skies.

# In[8]:


octfile = demo.makeOct(demo.getfilelist()) 


# At this point you should be able to go into a command window (cmd.exe) and check the geometry. Example:
# 
# ##### rvu -vf views\front.vp -e .01 -pe 0.3 -vp 1 -7.5 12 MultipleObj.oct
# 
# And then proceed happily with your analysis. 
# 
# ### Analysis for Each sceneObject:
# sceneDict is saved for each scene. When calling the Analysis, you should reference the scene object you want.
# 

# In[9]:


sceneObj1.sceneDict


# In[10]:


sceneObj2.sceneDict


# In[11]:


analysis = AnalysisObj(octfile, demo.basename)  
frontscan, backscan = analysis.moduleAnalysis(sceneObj1)
frontdict, backdict = analysis.analysis(octfile, "FirstObj", frontscan, backscan)  # compare the back vs front irradiance  
print('Annual bifacial ratio First Set of Panels: %0.3f ' %( np.mean(analysis.Wm2Back) / np.mean(analysis.Wm2Front)) )


# In[12]:


# Sanity check for first object. Since we didn't pass any desired module, it should grab the center module of the center row (rounding down)
# for 2 rows, that is row 1, module 5 ~ indexed at 0, a4.0.a0.PVmodule.....""
print (frontdict['x'])
print ("")
print (frontdict['y'])
print ("")
print (frontdict['mattype'])


# In[13]:


analysis = AnalysisObj(octfile, demo.basename)  
# Remember we can specify which module/row we want. We only have one row in this Object though.
modWanted = 3
rowWanted = 1
sensorsy=4
frontscan, backscan = analysis.moduleAnalysis(sceneObj2, modWanted = modWanted, rowWanted = rowWanted, sensorsy=sensorsy)
frontdict2, backdict2 = analysis.analysis(octfile, "SecondObj", frontscan, backscan)  # compare the back vs front irradiance  
print('Annual bifacial ratio Second Set of Panels: %0.3f ' %( np.mean(analysis.Wm2Back) / np.mean(analysis.Wm2Front)) )


# Sanity check for first object. Since we didn't pass any desired module, it should grab the center module of the center row (rounding down). For 1 rows, that is row 0, module 3 ~ indexed at 0, a2.0.a0.PVmodule... and a2.0.a1.PVmodule since it is a 2-UP system.
# 

# In[14]:


print (frontdict2['x'])
print ("")
print (frontdict2['y'])
print ("")
print (frontdict2['mattype'])


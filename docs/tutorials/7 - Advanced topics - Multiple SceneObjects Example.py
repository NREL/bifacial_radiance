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
# 
# ### Steps:
# 
# <ol>
#     <li> <a href='#step1'> Generating the setups</a></li>
#     <ol type='A'>
#         <li> <a href='#step1a'> Generating the firt scene object</a></li>
#         <li> <a href='#step1b'> Generating the second scene object.</a></li>
#     </ol>
#     <li> <a href='#step2'> Add a Marker at the Origin (coordinates 0,0) for help with visualization </a></li>   
#     <li> <a href='#step3'> Combine all scene Objects into one OCT file  & Visualize </a></li>
#     <li> <a href='#step4'> Analysis for Each sceneObject </a></li>
# </ol>

# <a id='step1'></a>

# ### 1. Generating the Setups

# In[3]:


import os
import numpy as np
testfolder = os.path.abspath(r'..\..\bifacial_radiance\TEMP')  

print ("Your simulation will be stored in %s" % testfolder)
    
from bifacial_radiance import RadianceObj, AnalysisObj    


# <a id='step1a'></a>

# ### A. Generating the firt scene object
# 
# This is a standard fixed-tilt setup for one hour. Gencumsky could be used too for the whole year.
# 
# The key here is that we are setting in sceneDict the variable **appendRadfile** to true.

# In[4]:


demo = RadianceObj("MultipleObj", path = testfolder)  # Create a RadianceObj 'object'
demo.setGround(0.62)
epwfile = demo.getEPW(lat = 37.5, lon = -77.6)    
metdata = demo.readWeatherFile('EPWs\\USA_VA_Richmond.Intl.AP.724010_TMY.epw') 
fullYear = True
demo.gendaylit(metdata,4020)  # Noon, June 17th  . # Gencumsky could be used too.
module_type = 'Prism Solar Bi60 landscape' 
demo.makeModule(name=module_type,y=1,x=1.7)
sceneDict = {'tilt':10,'pitch':1.5,'clearance_height':0.2,'azimuth':180, 'nMods': 5, 'nRows': 2, 'appendRadfile':True} 
sceneObj1 = demo.makeScene(module_type,sceneDict)  


# Checking values after Scene for the scene Object created

# In[5]:


print ("SceneObj1 modulefile: %s" % sceneObj1.modulefile)
print ("SceneObj1 SceneFile: %s" %sceneObj1.radfiles)
print ("SceneObj1 GCR: %s" % round(sceneObj1.gcr,2))
print ("FileLists: \n %s" % demo.getfilelist())


# <a id='step1b'></a>

# ### B. Generating the second scene object.
# 
# Creating a different Scene. Same Module, different values.
# Notice we are passing a different **originx** and **originy** to displace the center of this new sceneObj to that location.
# 

# In[6]:


sceneDict2 = {'tilt':30,'pitch':5,'clearance_height':1,'azimuth':180, 
              'nMods': 5, 'nRows': 1, 'originx': 0, 'originy': 3.5, 'appendRadfile':True} 
module_type2='Longi'
demo.makeModule(name=module_type2,x=1,y=1.6, numpanels=2, ygap=0.15)
sceneObj2 = demo.makeScene(module_type2,sceneDict2)  


# In[7]:


# Checking values for both scenes after creating new SceneObj
print ("SceneObj1 modulefile: %s" % sceneObj1.modulefile)
print ("SceneObj1 SceneFile: %s" %sceneObj1.radfiles)
print ("SceneObj1 GCR: %s" % round(sceneObj1.gcr,2))

print ("\nSceneObj2 modulefile: %s" % sceneObj2.modulefile)
print ("SceneObj2 SceneFile: %s" %sceneObj2.radfiles)
print ("SceneObj2 GCR: %s" % round(sceneObj2.gcr,2))

#getfilelist should have info for the rad file created by BOTH scene objects.
print ("NEW FileLists: \n %s" % demo.getfilelist())


# <a id='step2'></a>

# ### 2. Add a Marker at the Origin (coordinates 0,0) for help with visualization
# 
# Creating a "markers" for the geometry is useful to orient one-self when doing sanity-checks (for example, marke where 0,0 is, or where 5,0 coordinate is).
# 
# <div class="alert alert-warning">
# Note that if you analyze the module that intersects with the marker, some of the sensors will be wrong. To perform valid analysis, do so without markers, as they are 'real' objects on your scene. 
# </div>
# 

# In[8]:


# NOTE: offsetting translation by 0.1 so the center of the marker (with sides of 0.2) is at the desired coordinate.
name='Post1'
text='! genbox black originMarker 0.2 0.2 1 | xform -t -0.1 -0.1 0'
customObject = demo.makeCustomObject(name,text)
demo.appendtoScene(sceneObj1.radfiles, customObject, '!xform -rz 0')


# <a id='step3'></a>

# ### 3. Combine all scene Objects into one OCT file & Visualize
# Marking this as its own steps because this is the step that joins our Scene Objects 1, 2 and the appended Post.
# Run makeOCT to make the scene with both scene objects AND the marker in it, the ground and the skies.

# In[9]:


octfile = demo.makeOct(demo.getfilelist()) 


# At this point you should be able to go into a command window (cmd.exe) and check the geometry. Example:
# 
# ##### rvu -vf views\front.vp -e .01 -pe 0.3 -vp 1 -7.5 12 MultipleObj.oct
# 
# It should look something like this:
# 
# ![multiple Scene Objects Example](..\images_wiki\Journal_example_multiple_objects.PNG)
# 

# <a id='step4'></a>

# ### 4. Analysis for Each sceneObject
# 
# a **sceneDict** is saved for each scene. When calling the Analysis, you should reference the scene object you want.

# In[10]:


sceneObj1.sceneDict


# In[11]:


sceneObj2.sceneDict


# In[13]:


analysis = AnalysisObj(octfile, demo.basename)  
frontscan, backscan = analysis.moduleAnalysis(sceneObj1)
frontdict, backdict = analysis.analysis(octfile, "FirstObj", frontscan, backscan)  # compare the back vs front irradiance  
print('Annual bifacial ratio First Set of Panels: %0.3f ' %( np.mean(analysis.Wm2Back) / np.mean(analysis.Wm2Front)) )


# Let's do a Sanity check for first object:
# Since we didn't pass any desired module, it should grab the center module of the center row (rounding down). For 2 rows and 5 modules, that is row 1, module 3 ~ indexed at 0, a2.0.a0.PVmodule.....""

# In[14]:


print (frontdict['x'])
print ("")
print (frontdict['y'])
print ("")
print (frontdict['mattype'])


# Let's analyze a module in sceneobject 2 now. Remember we can specify which module/row we want. We only have one row in this Object though.
# 

# In[19]:


analysis = AnalysisObj(octfile, demo.basename)  
modWanted = 4
rowWanted = 1
sensorsy=4
frontscan, backscan = analysis.moduleAnalysis(sceneObj2, modWanted = modWanted, rowWanted = rowWanted, sensorsy=sensorsy)
frontdict2, backdict2 = analysis.analysis(octfile, "SecondObj", frontscan, backscan)  # compare the back vs front irradiance  
print('Annual bifacial ratio Second Set of Panels: %0.3f ' %( np.mean(analysis.Wm2Back) / np.mean(analysis.Wm2Front)) )


# Sanity check for first object. Since we didn't pass any desired module, it should grab the center module of the center row (rounding down). For 1 rows, that is row 0, module 4 ~ indexed at 0, a3.0.a0.Longi... and a3.0.a1.Longi since it is a 2-UP system.
# 

# In[23]:


print ("x coordinate points:" , frontdict2['x'])
print ("")
print ("y coordinate points:", frontdict2['y'])
print ("")
print ("Elements intersected at each point: ", frontdict2['mattype'])


# Visualizing the coordinates and module analyzed with an image:
#     
# ![multiple Scene Objects Example](..\images_wiki\AdvancedJournals\MultipleSceneObject_AnalysingSceneObj2_Row1_Module4.PNG)
# 

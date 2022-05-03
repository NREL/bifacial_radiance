#!/usr/bin/env python
# coding: utf-8

# -	The details of the C-beam and angles structure (how to implement)
# -	Any limitations you see in implementing this structure within the analysis.
# -	If we had the .cad models it possible to implement this directly? Is this process quicker?
# -	Any advise you may have?
# 
# 
# Two main options: obj2rad to import the STP > Obj > Rad & Mat file object. Difficulties: materials and multiple mesh creation; heavy to process if the surfaces are not recognized easily and divided into million teseracts, and you don't have the analysis function working as easily so have to come up with your own SENSOR SAMPLING positions (frontscan and backscan) dictionary. Not too terrible though if you do a similar system side by side with an originx and originy offset and then modify your backscan['xstart'] parameter.
# 
# Option 2: Simulate the geometry without and with Beams. We have some I beams in tutorial 20; you need to modify the offset so the shape is a C and not an I. 
# 
# 

# In[1]:


import os
from pathlib import Path
import bifacial_radiance
import numpy as np
import pandas as pd

testfolder = Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP' / 'Tutorial_24'
print ("Your simulation will be stored in %s" % testfolder)

if not os.path.exists(testfolder):
    os.makedirs(testfolder)
    
bifacial_radiance.__version__


# 
# ## Option one: obj2rad:* 
# 

# In[ ]:


demo = bifacial_radiance.RadianceObj('tutorial_1',str(testfolder))  
albedo = 0.62
demo.setGround(albedo)
epwfile = demo.getEPW(lat = 37.5, lon = -77.6)  
metdata = demo.readWeatherFile(epwfile, coerce_year=2001) 
timeindex = metdata.datetime.index(pd.to_datetime('2001-06-17 12:0:0 -7'))
demo.gendaylit(timeindex)  
#demo.genCumSky() # entire year.

# Adding a dummy module. Place this outside of area of interest after making sure it's being built.
mymod= demo.makeModule('test-module', x=0.5, y=0.5, z=5)
sceneDict = {'tilt':10,'pitch':3,'clearance_height':0.2,'azimuth':180, 'nMods': 1, 'nRows': 1, 'originx':-3, 'originy':-3} 
scene = demo.makeScene(mymod,sceneDict)


# ### Convert and Append the Radfile to the OctFile

# STEPS FROM: https://discourse.radiance-online.org/t/import-to-radiance/3594
# 
# (a) Convert to *.obj* file by other tools,
#        
# (b) Then use *obj2rad* to convert the *obj* file to .*rad* file;
# 
# (c) Define materials in another .mat file (material names could be found
# in the objfile.data by using command: obj2rad -n objfile > objfile.data)

# In[ ]:


cadfile=r'C:\Users\sayala\Documents\CustomerSupport\DNV_Seranya\3Deg-N_S.stp'


# In[ ]:


get_ipython().system('obj2rad C:\\Users\\sayala\\Documents\\CustomerSupport\\DNV_Seranya\\3Deg-N_S.obj > 3Deg-N_S.rad')


# In[ ]:


get_ipython().system('obj2rad -n C:\\Users\\sayala\\Documents\\CustomerSupport\\DNV_Seranya\\3Deg-N_S.obj > objfile.data')


# In[ ]:


radfileNew = '3Deg-N_S.rad'
materialfileNew = 'objfile.data'


# In[ ]:


demo.appendtoScene(scene.radfiles, radfileNew, '!xform -rz 0')


# In[ ]:


filesss = demo.getfilelist().copy()
filesss


# In[ ]:


filesss.append(materialfileNew)


# In[ ]:


filesss


# In[ ]:


demo.makeOct(filesss)


# In[ ]:


get_ipython().system('rvu -vf views\\front.vp -e .01 tutorial_1.oct')


# #### Truncated octtree. Probably materials fault. 
# Try:
# <ol>
#    <li> Creating obj directly from the autocad or software, instead of converting it from the STP. </li>
#     <li> Identifying the materials in the file, and appending them to the materials\ground.rad file manually, instead of appending a .data file with the material names. </li>
# </ol>

# # Option 2: Create Geometry
# Based on Tutorial 20: Example Simulation with I Beams, but calculate the shift to convert the I to the C shape.

# In[2]:


demo = bifacial_radiance.RadianceObj('CBeam',str(testfolder))  
albedo = 0.62
demo.setGround(albedo)
epwfile = demo.getEPW(lat = 37.5, lon = -77.6)  
metdata = demo.readWeatherFile(epwfile, coerce_year=2001) 
timeindex = metdata.datetime.index(pd.to_datetime('2001-06-17 12:0:0 -7'))
demo.gendaylit(timeindex)  # Noon, June 17th (timepoint # 4020)
#demo.gencumsky()


# In[3]:


moduletype='Sharp_NU-U235F2'
x=2
y=1
xgap = 0.134
zgap = 0
ygap = 0.273
numpanels=4

Collector = demo.makeModule(name=moduletype,x=x, y=y, numpanels=numpanels, 
                                   xgap=xgap, ygap = ygap, zgap=zgap)


# In[4]:


sceneDict = {'tilt':20, 'pitch':0.0001, 'clearance_height':0.9,
                         'azimuth':180, 'nMods':11, 'nRows':1}

sceneObj = demo.makeScene(Collector, sceneDict=sceneDict)


# In[6]:


octfile = demo.makeOct()
analysis = bifacial_radiance.AnalysisObj(octfile, demo.basename)
frontscan, backscan = analysis.moduleAnalysis(sceneObj, sensorsy=10)  # Change to a higher number for real calculation
results = analysis.analysis(octfile, demo.basename+'_NoBEAMS', frontscan, backscan)  


# In[7]:


get_ipython().system('rvu -vf views\\front.vp -e .01 -vp -18.5 -5.5 2.4 -vd 0.9147 0.3705 -0.1613 CBeam.oct')


# (Close the rvu pop up window to continue).
# <br>
# This finishes the analysis WITHOUT the beams. Now let's add the beams

# ### Adding the I-Beams
# 
# HEre is where the magic happens. We will calculate the row length (number of modules times the collector x value plus the xgaps between), and we will also calculate the spacing between the beams accross the collector width so that the beas are placed at the start of the collector and then between each module, just like in the image (5 modules = 6 Beams then)

# In[8]:


beam_count = 5
beam_mat = 'Metal_Grey'
beam_len = sceneDict['nMods']*Collector.x + (sceneDict['nMods']-1)*Collector.xgap
beam_len = round(beam_len,0)
beam_ydist = np.linspace(Collector.sceney/2,0-Collector.sceney/2,6)

# by photograph approximation
beam_cap = {'len':beam_len, 'height':0.02, 'width':0.12}
beam_ctr = {'len':beam_len, 'height':0.30, 'width':0.02}

print(f'Beam Length: {beam_len} meters')
print(f'Vertical Distribution: {beam_ydist}')


# We will use makeCustomObject like in previous journal examples and appendtoScene the IBeams.
# 
# Note that the IBeams geometry is being generated:
# <ol>
#     <li> Generate the geometry (genbox)</li>
#     <li> Translate the beam so that the center of the world (0,0,0) is positioned at the beam's center</li>
#     <li> Tilt by the angle of the array,</li>
#     <li> Then move to the correct clearance height and position accross the collector width calculated above.</li>
#     </ol>

# In[9]:


rows = sceneDict['nRows']
offsetMultiplier = np.linspace(-(rows//2),(rows//2),rows)
for row in range(0,sceneDict['nRows']):
    offset = offsetMultiplier[row]*sceneDict['pitch']
    customObjects = []
    for pos in beam_ydist:
        count = list(beam_ydist).index(pos)
        name = f'BEAM_r{row}_c{count}'
        ydisp = pos * np.cos(sceneDict['tilt']*np.pi/180.0) + offset
        zdisp = np.sin(sceneDict['tilt']*np.pi/180.0) * (pos-beam_ydist[-1]) + sceneDict['clearance_height'] - .05
        text = '! genbox {} beamTop{} {} {} {} | xform -t {} {} 0 | xform -rx {} | xform -t 0 {} {}'.format(
                                                beam_mat, count,
                                                beam_cap['len'], beam_cap['width'], beam_cap['height'],
                                                -beam_cap['len']/2+.8, -beam_cap['width']/2,
                                                sceneDict['tilt'],
                                                ydisp, zdisp)

        text+= '\r\n! genbox {} beamBot{} {} {} {} | xform -t {} {} 0 | xform -rx {} | xform -t 0 {} {}'.format(
                                                beam_mat, count,
                                                beam_cap['len'], beam_cap['width'], beam_cap['height'],
                                                -beam_cap['len']/2+.8, -beam_cap['width']/2,
                                                sceneDict['tilt'],
                                                ydisp + beam_ctr['height']*np.cos(np.pi/2 - np.pi*sceneDict['tilt']/180.0), zdisp - beam_ctr['height'])

        text+= '\r\n! genbox {} beamCtr{} {} {} {} | xform -t {} {} {} | xform -rx {} | xform -t 0 {} {}'.format(
                                                beam_mat, count,
                                                beam_ctr['len'], beam_ctr['width'], beam_ctr['height'],
                                                -beam_ctr['len']/2+.8, -beam_ctr['width']/2, beam_cap['height'],
                                                sceneDict['tilt'],
                                                ydisp + beam_ctr['height']*np.cos(np.pi/2 - np.pi*sceneDict['tilt']/180.0), zdisp - beam_ctr['height'])
        customObj = demo.makeCustomObject(name,text)
        customObjects.append(customObj)
        demo.appendtoScene(radfile=sceneObj.radfiles, customObject=customObj, text="!xform -rz 0")


# In[10]:


octfile = demo.makeOct()


# In[11]:


get_ipython().system('rvu -vf views\\front.vp -e .01 -vp -18.5 -5.5 2.4 -vd 0.9147 0.3705 -0.1613 CBeam.oct')


# ### Close the rvu window that poped up to continue

# In[13]:


octfile = demo.makeOct()  # make OCT again so that it captures are this new appended object Beams created.
analysis = bifacial_radiance.AnalysisObj(octfile, demo.basename)
frontscan, backscan = analysis.moduleAnalysis(sceneObj, sensorsy=10)  # Change to a higher number for real calculation
results = analysis.analysis(octfile, demo.basename+'_WITHBeams', frontscan, backscan)  


# In[17]:


NoBEAMS = bifacial_radiance.load.read1Result('results\irr_CBeam_NoBEAMS_Row1_Module6.csv')
BEAMS = bifacial_radiance.load.read1Result('results\irr_CBeam_WITHBEAMS_Row1_Module6.csv')


# In[32]:


print("Example of Results file for NoBeams Case")
NoBEAMS


# ## Remember to clean the results and do the below calculation with ONLY rearMat values that end with suffix '.2310' 

# <img src="../images_wiki/AdvancedJournals/Equation_ShadingFactor.PNG">

# In[30]:


ShadingFactor = (1 - BEAMS['Wm2Back'].sum() / NoBEAMS['Wm2Back'].sum())*100
print("Shading Factor ", round(ShadingFactor,2), "%")


# alternatively if you end up cleaning different points in the collector, you can use the mean. For this case since it's the same number of points in both cases it has no issues. 

# In[24]:


SHADING_FACTOR = (NoBEAMS['Wm2Back'].mean()-BEAMS['Wm2Back'].mean())*100/NoBEAMS['Wm2Back'].mean()
print("Shading Factor ", round(SHADING_FACTOR,2), "%")


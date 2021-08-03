#!/usr/bin/env python
# coding: utf-8

# In[1]:


# -*- coding: utf-8 -*-
"""
Created on Tue Jul  6 13:30:49 2021

rvu -vp -7 0 3 -vd 1 0 0 Sim1.oct
rvu -vp 0 -5 3 -vd 0 1 0 Sim1.oct

@author: sarefeen
"""


# In[2]:


import bifacial_radiance
import pytest

import os
from pathlib import Path

testfolder = str(Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP' / 'makeModTests')

if not os.path.exists(testfolder):
    os.makedirs(testfolder)
    
print ("Your simulation will be stored in %s" % testfolder)


# In[3]:


demo = bifacial_radiance.RadianceObj('FrameOmegaTest', testfolder)


# In[4]:


#generating sky

x = 2
y = 1
xgap = 0.02
ygap = 0.15
zgap = 0.10
numpanels = 1
offsetfromaxis = True
Ny = numpanels  

module_type = 'TEST'
frameParams = {'frame_material' : 'Metal_Grey', 
               'frame_thickness' : 0.003,
               'frame_z' : 0.03,
               'nSides_frame' : 4,
               'frame_width' : 0.05}


omegaParams = {'omega_material': 'litesoil',
                'x_omega1' : 0.10,
                'mod_overlap' : 0.5,
                'y_omega' : 1.5,
                'x_omega3' : 0.05,
                'omega_thickness' : 0.01,
                'inverted' : False}

nMods = 1
nRows = 1
sceneDict = {'tilt':0, 'pitch':3, 'clearance_height':3,'azimuth':90, 'nMods': nMods, 'nRows': nRows} 


# In[5]:


demo.setGround(0.2)
epwfile = demo.getEPW(lat = 37.5, lon = -77.6)
metdata = demo.readWeatherFile(epwfile, coerce_year = 2021)
demo.gendaylit(4020)


# In[6]:


loopaxisofRotation = [True, True, True, True, True, True, True, True]
loopTorquetube = [True, True, True, True, False, False, False, False ]
loopOmega = [omegaParams, omegaParams, None, None, omegaParams, omegaParams, None, None]
loopFrame = [frameParams, None, frameParams, None, frameParams,  None, frameParams, None]
expectedModuleZ = [3.179, 3.149, 3.179, 3.149, 3.129, 3.099, 3.129, 3.099]


# In[7]:


assertionResults = []
for ii in range (0, len(loopOmega)):
    omegaParams = loopOmega[ii]
    frameParams = loopFrame[ii]
    axisofrotationTorqueTube = loopaxisofRotation[ii]
    torquetube = loopTorquetube[ii]
    
    diam = 0.1
    if torquetube is False:
        diam = 0.0
        
    demo.makeModule(name=module_type,x=x, y=y, torquetube = torquetube, 
                    diameter = diam, xgap = xgap, ygap = ygap, zgap = zgap, 
                    numpanels = Ny, frameParams=frameParams, omegaParams=omegaParams,
                    axisofrotationTorqueTube=axisofrotationTorqueTube)
    
    scene = demo.makeScene(module_type,sceneDict)
    octfile = demo.makeOct()
    analysis = bifacial_radiance.AnalysisObj()  # return an analysis object including the scan dimensions for back irradiance
    frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=1) # Gives us the dictionaries with coordinates
    assertionResults.append(backscan['zstart'])
    # assert backscan['zstart'] == expectedModuleZ[ii]
    
#assert assertionResults == expectedModuleZ


# In[8]:


assertionResults == expectedModuleZ


# In[10]:


for i in range(len(assertionResults)):
    if assertionResults[i] != expectedModuleZ[i]:
        print('Omega =',loopOmega[i] is not None, end = ', ')
        print('Frame =',loopFrame[i] is not None, end = ', ')
        print('Axis of Rotation =',loopaxisofRotation[i], end = ', ')
        print('Torquetube =',loopTorquetube[i], end = ', ')
        print('Off by =',assertionResults[i] - expectedModuleZ[i], end = '\n')
    


# In[ ]:





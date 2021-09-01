#!/usr/bin/env python
# coding: utf-8

# # 15 - Simulating Frames and Omegas

# 
# ![Folder Structure](../images_wiki/makeModule_ComplexGeometry.PNG)
# 

# In[1]:


import bifacial_radiance

import os
from pathlib import Path

testfolder = str(Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP' / 'makeModTests')

if not os.path.exists(testfolder):
    os.makedirs(testfolder)
    
print ("Your simulation will be stored in %s" % testfolder)


# In[2]:


x = 2
y = 1
xgap = 0.02
ygap = 0.15
zgap = 0.3
numpanels = 2
offsetfromaxis = True

module_type = 'TEST'
frameParams = {'frame_material' : 'Metal_Grey', 
               'frame_thickness' : 0.05,
               'nSides_frame' : 4,
               'frame_width' : 0.08}


omegaParams = {'omega_material': 'litesoil',
                'x_omega1' : 0.4,
                'mod_overlap' : 0.25,
                'y_omega' : 1.5,
                'x_omega3' : 0.25,
                'omega_thickness' : 0.05,
                'inverted' : False}

demo = bifacial_radiance.RadianceObj('Sim1', testfolder) 

axisofrotationTorqueTube = False

mymod = demo.makeModule(module_type,x=x, y=y, xgap = xgap, ygap = ygap, zgap = zgap, 
                torquetube = True, diameter = 0.3, axisofrotationTorqueTube=axisofrotationTorqueTube,
                numpanels = numpanels, 
                frameParams=frameParams, omegaParams=omegaParams)


# In[3]:


demo.setGround(0.2)
epwfile = demo.getEPW(lat = 37.5, lon = -77.6)
metdata = demo.readWeatherFile(epwfile, coerce_year = 2021)
demo.gendaylit(4020)

nMods = 1
nRows = 1
sceneDict = {'tilt':0, 'pitch':3, 'clearance_height':3,'azimuth':90, 'nMods': nMods, 'nRows': nRows} 
scene = demo.makeScene(module_type,sceneDict)
demo.makeOct()


# To view the module from different angles, you can use the following rvu commands. See tutorial 1 for more on how to do rvu.
# 
#     rvu -vp -7 0 3 -vd 1 0 0 Sim1.oct
# 
#     rvu -vp 0 -5 3 -vd 0 1 0 Sim1.oct

# In[ ]:





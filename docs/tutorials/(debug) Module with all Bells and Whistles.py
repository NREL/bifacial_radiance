#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
from pathlib import Path

testfolder = Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP'


import pandas as pd
import bifacial_radiance


demo = bifacial_radiance.RadianceObj('demo',str(testfolder))  

demo.setGround(0.3)  # This prints available materials.
#epwfile = demo.getEPW(lat = 37.5, lon = -77.6)  # This location corresponds to Richmond, VA.
epwfile = r'C:\Users\sayala\Documents\GitHub\bifacial_radiance\tests\724666TYA.CSV'
metdata = demo.readWeatherFile(epwfile, coerce_year=2001) 
timeindex = metdata.datetime.index(pd.to_datetime('2001-06-17 12:0:0 -7'))
demo.gendaylit(timeindex)  # Noon, June 17th (timepoint # 4020)


module_type='half_cell'
x=1
y=2
xgap = 0.1
ygap = 0.2
numpanels =1

cellLevelModuleParams = {'numcellsx': 1,
'numcellsy' : 4,
'xcell' : 0.1,      
'ycell' : 0.1,      
'xcellgap' : 0.05,  
'ycellgap' : 0.05,   
'centerJB' : 0.2}


frameParams={'frame_material' : 'Metal_Grey',
                'frame_thickness' : 0.002,  
                'frame_z' : 0.024,
                'frame_width' : 0.02,
                'nSides_frame' : 4}
    
    
omegaParams = { 'omega_material': 'Metal_Grey',
               'x_omega1' : 0.05,
               'mod_overlap' : 0.02,
               'y_omega' : 1,
               'omega_thickness' : 0.005,
               'x_omega3' : 0.03,
                'inverted' : True}
omegaParams = None

material = 'Metal_Grey'
diameter = 0.05
tubetype = 'Round'
axisofrotationTorqueTube = False
torquetube = True
tubeParams = {'diameter': diameter, 
              'tubetype': tubetype, 
              'material': material}

TEST = demo.makeModule(name='TEST', x=x, y=y, bifi=1, torquetube=torquetube, xgap=xgap, ygap=ygap, 
                numpanels=numpanels, axisofrotationTorqueTube=axisofrotationTorqueTube, 
                cellModule=cellLevelModuleParams, glass=True, tubeParams=tubeParams,
                 omegaParams=omegaParams, frameParams=frameParams)

sceneDict = {'tilt':0,'pitch':3,'hub_height':2.0,'azimuth':90, 'nMods': 1, 'nRows': 1} 

scene = demo.makeScene(TEST,sceneDict)

octfile = demo.makeOct(demo.getfilelist())  

get_ipython().system('rvu -vf views\\front.vp -e .01 -vp -0.1 0 3.5 -vd 0.0 0.0101 -0.9999 demo.oct')
#!rvu -vf views\front.vp -e .01 -vp -0.4 0 5 -vd 0.0 0.0101 -0.9999 demo.oct


# In[2]:


print(a)


# In[ ]:





# In[ ]:





# In[ ]:


import os
from pathlib import Path

testfolder = Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP'


# In[ ]:


import pandas as pd


# In[ ]:


import bifacial_radiance


# In[ ]:


demo = bifacial_radiance.RadianceObj('demo',str(testfolder))  


# In[ ]:


demo.setGround(0.3)  # This prints available materials.
#epwfile = demo.getEPW(lat = 37.5, lon = -77.6)  # This location corresponds to Richmond, VA.
epwfile = r'C:\Users\sayala\Documents\GitHub\bifacial_radiance\tests\724666TYA.CSV'
metdata = demo.readWeatherFile(epwfile, coerce_year=2001) 
timeindex = metdata.datetime.index(pd.to_datetime('2001-06-17 12:0:0 -7'))
demo.gendaylit(timeindex)  # Noon, June 17th (timepoint # 4020)


# # Issue 1: makeModule x value not being updated for cell level module

# In[ ]:





# In[ ]:


get_ipython().system('rvu -vf views\\front.vp -e .01 -vp -1.2 0.9 2.9 -vd -0.3991 -0.3823 -0.8334 demo.oct')


# In[ ]:





# In[ ]:





# In[ ]:


module_type='half_cell'
x=2.3
y=1
xgap = 0.1
ygap = 0.2
numpanels =3

frameParams={'frame_material' : 'Metal_Grey',
                'frame_thickness' : 0.002,  
                'frame_z' : 0.024,
                'frame_width' : 0.02,
                'nSides_frame' : 4}
    
    
omegaParams = { 'omega_material': 'Metal_Grey',
               'x_omega1' : 0.05,
               'mod_overlap' : 0.02,
               'y_omega' : 1,
               'omega_thickness' : 0.005,
               'x_omega3' : 0.03,
                'inverted' : True}

material = 'Metal_Grey'
diameter = 0.05
tubetype = 'Round'
axisofrotationTorqueTube = True
torquetube = True
tubeParams = {'diameter': diameter, 
              'tubetype': tubetype, 
              'material': material}

TEST = demo.makeModule(name='TEST', x=x, y=y, bifi=1, torquetube=torquetube, xgap=xgap, ygap=ygap, 
                numpanels=numpanels, axisofrotationTorqueTube=axisofrotationTorqueTube, 
                #cellModule=cellLevelModuleParams, 
                 glass=True, tubeParams=tubeParams,
                 omegaParams=omegaParams, frameParams=frameParams 
                 )

sceneDict = {'tilt':0,'pitch':3,'hub_height':2.0,'azimuth':180, 'nMods': 1, 'nRows': 1} 
scene = demo.makeScene(TEST,sceneDict)

octfile = demo.makeOct(demo.getfilelist())  


# In[ ]:


get_ipython().system('rvu -vf views\\front.vp -e .01 -vp -2 -1 1.5 -vd 0.9159 0.2789 0.2886 demo.oct')


# In[ ]:


get_ipython().system('rvu -vf views\\front.vp -e .01 -vp -2.5 -1 2 -vd 0.9850 0.1407 -0.0995 demo.oct')


# ## ISSUE 2:           x > y makemodule and nframes = 2

# In[ ]:


module_type='half_cell'
x=2.3
y=1
xgap = 0.1
ygap = 0.2
numpanels =3

frameParams={'frame_material' : 'Metal_Grey',
                'frame_thickness' : 0.002,  
                'frame_z' : 0.024,
                'frame_width' : 0.02,
                'nSides_frame' : 2}
    
    
omegaParams = { 'omega_material': 'Metal_Grey',
               'x_omega1' : 0.05,
               'mod_overlap' : 0.02,
               'y_omega' : 1,
               'omega_thickness' : 0.005,
               'x_omega3' : 0.03,
                'inverted' : True}

material = 'Metal_Grey'
diameter = 0.05
tubetype = 'Round'
axisofrotationTorqueTube = False
torquetube = True
tubeParams = {'diameter': diameter, 
              'tubetype': tubetype, 
              'material': material}

TEST = demo.makeModule(name='TEST', x=x, y=y, bifi=1, torquetube=torquetube, xgap=xgap, ygap=ygap, 
                numpanels=numpanels, axisofrotationTorqueTube=axisofrotationTorqueTube, 
                #cellModule=cellLevelModuleParams, 
                 glass=False, tubeParams=tubeParams,
                 omegaParams=omegaParams, frameParams=frameParams)

sceneDict = {'tilt':25,'pitch':3,'hub_height':2.0,'azimuth':180, 'nMods': 1, 'nRows': 1} 
scene = demo.makeScene(TEST,sceneDict)

octfile = demo.makeOct(demo.getfilelist())  


# In[ ]:


get_ipython().system('rvu -vf views\\front.vp -e .01 demo.oct')


# In[ ]:


get_ipython().system('rvu -vf views\\front.vp -e .01 -vp -3.5 -1 2 -vd 0.9850 0.1407 -0.0995 demo.oct')


# ## ISSUE 3:         Glass offset and Cell thickness

# In[ ]:





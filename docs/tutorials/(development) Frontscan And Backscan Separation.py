#!/usr/bin/env python
# coding: utf-8

# ## Separating Frontscan and Backscan for different number of Sensors

# The key ideas here are:
# 
# - Functions like moduleAnalysis() returns two identically structured dictionaries that contain the keys like xstart, ystart, zstart, xinc, yinc, zinc, Nx, Ny, Nz, orientation. For the function arguments like sensorsy or sensorsx, there is an assumption that those will be equal for both the front and back surface.
# 
# - We need to develop a separate function, pretty much functionally parallel with moduleAnalysis() to bring out the frontscan and backscan separately.....may be two distinct functions with distinct arguments for frontscan() and backscan()
# 
# - The new functions will have variables passed on as arguments which can be different for front and back

# In[1]:


import bifacial_radiance
import numpy as np
import os
from pathlib import Path

testfolder = str(Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP')


# In[2]:


demo = bifacial_radiance.RadianceObj('ScanSeparate', testfolder) 


# In[3]:


x = 2
y = 1
xgap = 0.02
ygap = 0.15
zgap = 0.10
numpanels = 1
offsetfromaxis = True
axisofrotationTorqueTube = True
frameParams = None
omegaParams = None
diam = 0.1


# In[4]:


module_type = 'TEST'
nMods = 3
nRows = 2
sceneDict = {'tilt':30, 'pitch':6, 'clearance_height':3,'azimuth':90, 'nMods': nMods, 'nRows': nRows} 


# In[5]:


demo.setGround(0.2)
epwfile = demo.getEPW(lat = 37.5, lon = -77.6)
metdata = demo.readWeatherFile(epwfile, coerce_year = 2021)
demo.gendaylit(4020)


# In[6]:


demo.makeModule(name=module_type,x=x, y=y, torquetube = True, 
                    diameter = diam, xgap = xgap, ygap = ygap, zgap = zgap, 
                    numpanels = numpanels, omegaParams=None,
                    axisofrotationTorqueTube=axisofrotationTorqueTube)


# In[7]:


scene = demo.makeScene(module_type,sceneDict)
octfile = demo.makeOct()
analysis = bifacial_radiance.AnalysisObj()  # return an analysis object including the scan dimensions for back irradiance


# In[8]:


name = 'ModuleScanTest'
rowWanted = 1
modWanted = 2


# In[9]:



sensors_diff = True


# # Test 0 - Same sensors Front and back, xsensors=y

# In[10]:


name='test0'

sensorsy_front = 2
sensorsy_back = 2

sensorsx_front = 1
sensorsx_back = 1

frontscan, backscan, start_shift, flag_s = analysis.moduleAnalysis(scene, modWanted=None, rowWanted=None,
                       sensorsy_back=sensorsy_back, sensorsx_back=sensorsx_back, frontsurfaceoffset=0.001, 
                        backsurfaceoffset=0.001, 
                       modscanfront=None, modscanback=None, debug=False, 
                       sensorsy_front=sensorsy_front, sensorsx_front=sensorsx_front)

print('Start shift:', start_shift, 'flag:', flag_s)
print('frontscan', frontscan)
print('backscan', backscan, '\n')

frontDict, backDict = analysis.analysis(octfile = octfile, name = name, frontscan = frontscan, 
                                        backscan = backscan, start_shift = start_shift, flag_s = flag_s)
print('\nBOTH\n', bifacial_radiance.load.read1Result('results\irr_'+name+'.csv'))


# # Test 1: more sensors on back than front, xsensors=1

# In[11]:


name='test1'

sensorsy = 2
sensorsy_back = 4

sensorsx = 1
sensorsx_back = 1


frontscan, backscan, start_shift, flag_s = analysis.moduleAnalysis(scene, modWanted=None, rowWanted=None,
                       sensorsy_back=sensorsy_back, sensorsx_back=sensorsx_back, frontsurfaceoffset=0.001, 
                        backsurfaceoffset=0.001, 
                       modscanfront=None, modscanback=None, debug=False, 
                       sensorsy_front=sensorsy_front, sensorsx_front=sensorsx_front)

print('Start shift:', start_shift, 'flag:', flag_s)
print('frontscan', frontscan)
print('backscan', backscan, '\n')

frontDict, backDict = analysis.analysis(octfile = octfile, name = name, frontscan = frontscan, 
                                        backscan = backscan, start_shift = start_shift, flag_s = flag_s)
print('\nFRONT\n', bifacial_radiance.load.read1Result('results\irr_'+name+'_Front.csv'))
print('BACK\n', bifacial_radiance.load.read1Result('results\irr_'+name+'_Back.csv'))


# # Test 2 - Same sensors front and back, xsensors = 2

# In[12]:


name='test2'

sensorsy = 2
sensorsy_back = 2

sensorsx = 2
sensorsx_back = 2


frontscan, backscan, start_shift, flag_s = analysis.moduleAnalysis(scene, modWanted=None, rowWanted=None,
                       sensorsy_back=sensorsy_back, sensorsx_back=sensorsx_back, frontsurfaceoffset=0.001, 
                        backsurfaceoffset=0.001, 
                       modscanfront=None, modscanback=None, debug=False, 
                       sensorsy_front=sensorsy_front, sensorsx_front=sensorsx_front)

print('Start shift:', start_shift, 'flag:', flag_s)
print('frontscan', frontscan)
print('backscan', backscan, '\n')

frontDict, backDict = analysis.analysis(octfile = octfile, name = name, frontscan = frontscan, 
                                        backscan = backscan, start_shift = start_shift, flag_s = flag_s)
print('\nBOTH\n', bifacial_radiance.load.read1Result('results\irr_'+name+'.csv'))


# # Test 3 - Different sensors front and back, xsensors = 2

# In[ ]:


name='test3'

sensorsy = 2
sensorsy_back = 4

sensorsx = 2
sensorsx_back = 2

frontscan, backscan, start_shift, flag_s = analysis.moduleAnalysis(scene, modWanted=None, rowWanted=None,
                       sensorsy_back=sensorsy_back, sensorsx_back=sensorsx_back, frontsurfaceoffset=0.001, 
                        backsurfaceoffset=0.001, 
                       modscanfront=None, modscanback=None, debug=False, 
                       sensorsy_front=sensorsy_front, sensorsx_front=sensorsx_front)

print('Start shift:', start_shift, 'flag:', flag_s)
print('frontscan', frontscan)
print('backscan', backscan, '\n')

frontDict, backDict = analysis.analysis(octfile = octfile, name = name, frontscan = frontscan, 
                                        backscan = backscan, start_shift = start_shift, flag_s = flag_s)
print('\nFRONT\n', bifacial_radiance.load.read1Result('results\irr_'+name+'_Front.csv'))
print('BACK\n', bifacial_radiance.load.read1Result('results\irr_'+name+'_Back.csv'))


# # Test 4 - Different sensors front and back, different xsensors

# In[ ]:


name='test4'

sensorsy = 2
sensorsy_back = 4

sensorsx = 2
sensorsx_back = 4

frontscan, backscan, start_shift, flag_s = analysis.moduleAnalysis(scene, modWanted=None, rowWanted=None,
                       sensorsy=sensorsy, sensorsx=sensorsx, frontsurfaceoffset=0.001, backsurfaceoffset=0.001, 
                       modscanfront=None, modscanback=None, debug=False, sensors_diff = sensors_diff, 
                       sensorsy_back=sensorsy_back, sensorsx_back=sensorsx_back)

print('Start shift:', start_shift, 'flag:', flag_s)
print('frontscan', frontscan)
print('backscan', backscan, '\n')

frontDict, backDict = analysis.analysis(octfile = octfile, name = name, frontscan = frontscan, 
                                        backscan = backscan, start_shift = start_shift, flag_s = flag_s)
print('\nFRONT\n', bifacial_radiance.load.read1Result('results\irr_'+name+'_Front.csv'))
print('BACK\n', bifacial_radiance.load.read1Result('results\irr_'+name+'_Back.csv'))


# In[ ]:





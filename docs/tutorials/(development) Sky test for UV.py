#!/usr/bin/env python
# coding: utf-8

# # Test for UV Sky 
# 
# Not sure if a low low value of DNI/DHI will get captured in a gendaylit.
# Then try gencumsky
# Then try multiplying x 100 and dividing? 

# <a id='step1'></a>

# In[1]:


import os
from pathlib import Path

testfolder = Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP'

try:
    from bifacial_radiance import *
except ImportError:
    raise RuntimeError('bifacial_radiance is required. download distribution')

import numpy as np


# In[56]:


# Create a RadianceObj 'object' named bifacial_example. no whitespace allowed
demo = RadianceObj('bifacial_example',str(testfolder))  
demo.setGround(0.00001)
epwfile = demo.getEPW(lat = 37.5, lon = -77.6)  # This location corresponds to Richmond, VA.
metdata = demo.readWeatherFile(epwfile) 
demo.makeModule(name='Prism Solar Bi60 landscape',x=1.695, y=0.984)
sceneDict = {'tilt':10,'pitch':3,'clearance_height':0.2,'azimuth':180, 'nMods': 20, 'nRows': 7} 
scene = demo.makeScene(module_type,sceneDict)

dniall = [500, 50, 5, 0.5, 0.05, 0.005, 0.00005]

for i in range (0, len(dniall)):
    dni = dniall[i]
    dhi = dni/5
    demo.gendaylit2manual(dni = dni, dhi = dhi, sunalt = 67.167217, sunaz = 153.735606)
    octfile = demo.makeOct(demo.getfilelist())  
    analysis = AnalysisObj(octfile, demo.basename)
    frontscan, backscan = analysis.moduleAnalysis(scene)
    results = analysis.analysis(octfile, demo.basename+'_albedo_0.00001_'+str(dni), frontscan, backscan)  
    
    
dni = 500
dhi = dni/5
demo.gendaylit2manual(dni = dni, dhi = dhi, sunalt = 67.167217, sunaz = 153.735606)
octfile = demo.makeOct(demo.getfilelist())  
analysis = AnalysisObj(octfile, demo.basename)
frontscan, backscan = analysis.moduleAnalysis(scene)
results = analysis.analysis(octfile, demo.basename+'_albedo_0.00001_1_'+str(dni), frontscan, backscan)  
results = analysis.analysis(octfile, demo.basename+'_albedo_0.00001_2'+str(dni), frontscan, backscan)  
results = analysis.analysis(octfile, demo.basename+'_albedo_0.00001_3'+str(dni), frontscan, backscan)  


dni = 0.00005
dhi = dni/5
demo.gendaylit2manual(dni = dni, dhi = dhi, sunalt = 67.167217, sunaz = 153.735606)
octfile = demo.makeOct(demo.getfilelist())  
analysis = AnalysisObj(octfile, demo.basename)
frontscan, backscan = analysis.moduleAnalysis(scene)
results = analysis.analysis(octfile, demo.basename+'_albedo_0.00001_1_'+str(dni), frontscan, backscan)  
results = analysis.analysis(octfile, demo.basename+'_albedo_0.00001_2_'+str(dni), frontscan, backscan)  
results = analysis.analysis(octfile, demo.basename+'_albedo_0.00001_3_'+str(dni), frontscan, backscan)  


# In[57]:


demo.setGround(0.62)
demo.makeModule(name='Prism Solar Bi60 landscape',x=1.695, y=0.984)
sceneDict = {'tilt':10,'pitch':3,'clearance_height':0.2,'azimuth':180, 'nMods': 20, 'nRows': 7} 
scene = demo.makeScene(module_type,sceneDict)


dniall = [500, 50, 5, 0.5, 0.05, 0.005, 0.00005]

for i in range (0, len(dniall)):
    dni = dniall[i]
    dhi = dni/5
    demo.gendaylit2manual(dni = dni, dhi = dhi, sunalt = 67.167217, sunaz = 153.735606)
    octfile = demo.makeOct(demo.getfilelist())  
    analysis = AnalysisObj(octfile, demo.basename)
    frontscan, backscan = analysis.moduleAnalysis(scene)
    results = analysis.analysis(octfile, demo.basename+'_'+str(dni), frontscan, backscan)  
    
    
dni = 500
dhi = dni/5
demo.gendaylit2manual(dni = dni, dhi = dhi, sunalt = 67.167217, sunaz = 153.735606)
octfile = demo.makeOct(demo.getfilelist())  
analysis = AnalysisObj(octfile, demo.basename)
frontscan, backscan = analysis.moduleAnalysis(scene)
results = analysis.analysis(octfile, demo.basename+'_1_'+str(dni), frontscan, backscan)  
results = analysis.analysis(octfile, demo.basename+'_2_'+str(dni), frontscan, backscan)  
results = analysis.analysis(octfile, demo.basename+'_3_'+str(dni), frontscan, backscan)  


dni = 0.00005
dhi = dni/5
demo.gendaylit2manual(dni = dni, dhi = dhi, sunalt = 67.167217, sunaz = 153.735606)
octfile = demo.makeOct(demo.getfilelist())  
analysis = AnalysisObj(octfile, demo.basename)
frontscan, backscan = analysis.moduleAnalysis(scene)
results = analysis.analysis(octfile, demo.basename+'_1_'+str(dni), frontscan, backscan)  
results = analysis.analysis(octfile, demo.basename+'_2_'+str(dni), frontscan, backscan)  
results = analysis.analysis(octfile, demo.basename+'_3_'+str(dni), frontscan, backscan)  


# In[ ]:


load.read1Result('results\irr_bifacial_example.csv')


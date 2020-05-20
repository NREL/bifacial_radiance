#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
from pathlib import Path

testfolder = Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP'

# Another option using relative address; for some operative systems you might need '/' instead of '\'
# testfolder = os.path.abspath(r'..\..\bifacial_radiance\TEMP')  
print ("Your simulation will be stored in %s" % testfolder)


# In[2]:


from bifacial_radiance import *
demo = RadianceObj('bifacial_example',str(testfolder))  
demo.setGround(0.30)  # This prints available materials.
epwfile = demo.getEPW(lat = 37.5, lon = -77.6)  # This location corresponds to Richmond, VA.
metdata = demo.readWeatherFile(epwfile) 
demo.gendaylit(8)  # Noon, June 17th (timepoint # 4020)\


# In[16]:





# In[12]:


module_type = 'Bi60' 

numcellsx = 6
numcellsy = 12
xcell = 0.156
ycell = 0.156
xcellgap = 0.02
ycellgap = 0.02

torquetube = True
diameter = 0.15
tubetype = 'round'
material = 'Metal_Grey'
xgap = 0.1
ygap = 0
zgap = 0.05
numpanels = 1
axisofrotationTorqueTube = False
glass = True

cellLevelModuleParams = {'numcellsx': numcellsx, 'numcellsy':numcellsy, 
                         'xcell': xcell, 'ycell': ycell, 'xcellgap': xcellgap, 'ycellgap': ycellgap}

mymodule = demo.makeModule(name=module_type, torquetube=torquetube, diameter=diameter, tubetype=tubetype, material=material, 
                xgap=xgap, ygap=ygap, zgap=zgap, numpanels=numpanels, 
                cellLevelModuleParams=cellLevelModuleParams, 
                axisofrotationTorqueTube=axisofrotationTorqueTube, glass=glass, z=0.0002)

sceneDict = {'tilt':25,'pitch':5.5,'hub_height':1.0,'azimuth':90, 'nMods': 20, 'nRows': 1, originx=0, originy=0} 
scene = demo.makeScene(module_type,sceneDict)
octfile = demo.makeOct(demo.getfilelist())  


# In[15]:


sceneDict = {'tilt':25,'pitch':5.5,'hub_height':1.0,'azimuth':90, 'nMods': 20, 'nRows': 10, 'originx':0, 'originy':0} 
scene = demo.makeScene(module_type,sceneDict)
octfile = demo.makeOct(demo.getfilelist())  

Advanced Rendering:

My workflow for going from oct file to png is:
rvu -> rpict -> pcond -> pfilt -> ra_tiff -> convert
In detail:
1.	Use rvu to view the oct file
rvu 1axis_07_01_08.oct
use aim and origin to move around, zoom in/out, etc
save a view file with view render.vf
2.	Run rpict to render the image to hdr. This is the time consuming step. It takes between 1 and 3 hours depending on how complex the geometry is.
rpict -x 4800 -y 4800 -i -ps 1 -dp 530 -ar 964 -ds 0.016 -dj 1 -dt 0.03 -dc 0.9 -dr 5 -st 0.12 -ab 5 -aa 0.11 -ad 5800 -as 5800 -av 25 25 25 -lr 14 -lw 0.0002 -vf render.vf bifacial_example.oct > render.hdr
3.	Run pcond to mimic human visual response:
pcond -h render.hdr > render.pcond.hdr
4.	Resize and adjust exposure with pfilt
pfilt -e +0.2 -x /4 -y /4 render.pcond.hdr > render.pcond.pfilt.hdr
5.	Convert hdr to tif
ra_tiff render.pcond.pfilt.hdr render.tif
6.	Convert tif to png with imagemagick convert utility
convert render.tif render.png
7.	Annotate the image with convert
convert render.png -fill black -gravity South -annotate +0+5 'Created with NREL bifacial_radiance https://github.com/NREL/bifacial_radiance' render_annotated.png

# In[8]:


analysis = AnalysisObj(octfile, demo.basename)


# In[9]:


frontscan, backscan = analysis.moduleAnalysis(scene)
results = analysis.analysis(octfile, demo.basename, frontscan, backscan)  
load.read1Result('results\irr_bifacial_example.csv')


# In[10]:


frontscan, backscan = analysis.moduleAnalysis(scene, frontsurfaceoffset=0.02, backsurfaceoffset = 0.02)
results = analysis.analysis(octfile, demo.basename, frontscan, backscan)  
load.read1Result('results\irr_bifacial_example.csv')


# In[ ]:





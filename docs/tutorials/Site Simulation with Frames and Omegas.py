#!/usr/bin/env python
# coding: utf-8

# This journal investigates the effects of a simulation with and without frames using gendaylit1axis

# In[1]:


import bifacial_radiance
import os
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# In[2]:


bifacial_radiance.__version__


# #### Control variables

# In[3]:


smallsim = True
shamsul = False


# In[ ]:





# In[4]:


testfolder = str(Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP' / 'FrameTest')

if not os.path.exists(testfolder):
    os.makedirs(testfolder)
    
print ("Your simulation will be stored in %s" % testfolder)


# In[5]:


if shamsul:
    TMYtoread = r'C:\Users\sarefeen\Documents\RadianceScenes\Temp\SRRL_WeatherFile_TMY3_60_2020.csv'
else:
    TMYtoread = r'C:\Users\sayala\Documents\GitHub\RTCanalysis\TEMP\SRRL_WeatherFile_TMY3_60_2020_FIXED.csv'


# In[6]:


#### Reading the weatherfile
'''
weatherfile = pd.read_csv(TMYtoread, header = 1)
weatherfile.head()
wf2 = weatherfile[weatherfile['DNI (W/m^2)'] == weatherfile['DNI (W/m^2)'].max()]
wf3 = weatherfile[weatherfile['Date (MM/DD/YYYY)']== '4/29/2020']
y = wf3['DNI (W/m^2)']
x = wf3['Time (HH:MM)']
plt.plot(x,y)
plt.xticks(rotation = 45)
weatherfile.groupby('Date (MM/DD/YYYY)')['DNI (W/m^2)'].sum().max()
''';


# ### Make Modules

# In[7]:


simulationname = 'OmegaTestField'
moduletype_framed='Framed_Panel'
moduletype_simple='NotFramed_Panel'

numpanels = 1  
x = 1  
y = 2
lat=39.742 # NREL SSRL location
lon=-105.179 # NREL SSRL location
elev=1829
timezone=-7
axis_tilt=0
axis_azimuth=180
limit_angle=60
backtrack=True 
gcr=0.35
angledelta=0.01
numpanels=1
torquetube=True
diameter = 0.130175        # 5 1/8 in
torqueTubeMaterial='Metal_Grey'
tubetype='Round'

# for torquetube, the simulation 
axisofrotationTorqueTube = False  # This is particular to the NREL site.
hub_height = 1.35    
xgap = 0.01    # 1 cm
zgap = 0.05    # 1 inch of arm, + 1 3/16 of panel width on average ~ 0.055 m
pitch=5.7      # distance between rows

sensorsy = 3 # Increase sampling for edge 


# In[8]:


# TorqueTube Parameters
axisofrotationTorqueTube=False
torqueTube = True
cellLevelModule = False


# In[9]:


albedo = 0.2  #'grass'     # ground albedo


#this change is for smalling the simulation
if smallsim:
    nMods = 1 
    nRows = 1 
    sensorsy = 9
else:
    nMods = 20 
    nRows = 10 
    sensorsy = 9
cumulativesky = False


# In[10]:


demo = bifacial_radiance.RadianceObj(simulationname, path = testfolder)  # Create a RadianceObj 'object'


# In[11]:


frameParams = {'frame_material' : 'Metal_Grey', 
               'frame_thickness' : 0.003,
               'frame_z' : 0.03,
               'nSides_frame' : 4,
               'frame_width' : 0.05}


omegaParams = {'omega_material': 'litesoil',
                'x_omega1' : 0.08,
                'mod_overlap' : 0.03,
                'y_omega' : 0.75,
                'x_omega3' : 0.02,
                'omega_thickness' : 0.01,
                'inverted' : False}
moduleDict=demo.makeModule(name=moduletype_simple,x=x,y=y,numpanels = numpanels, xgap=xgap, zgap=zgap,
                            torquetube=torquetube, diameter=diameter, tubetype=tubetype, material=torqueTubeMaterial,
                            axisofrotationTorqueTube=axisofrotationTorqueTube, omegaParams = None, frameParams = None)

moduleDict=demo.makeModule(name=moduletype_framed,x=x,y=y,numpanels = numpanels, xgap=xgap, zgap=zgap,
                            torquetube=torquetube, diameter=diameter, tubetype=tubetype, material=torqueTubeMaterial,
                            axisofrotationTorqueTube=axisofrotationTorqueTube, omegaParams = omegaParams, frameParams = frameParams)


# ## A. SIMPLE Module run

# In[12]:


# Restricting run to one hour for speed, 'MM_DD_HH'
metdata = demo.readWeatherFile(TMYtoread)
demo.setGround() 
sceneDict = {'pitch': pitch,'hub_height':hub_height, 'nMods':nMods, 'nRows': nRows, 'sceney':y}  
trackerdict = demo.set1axis(metdata = metdata, limit_angle = limit_angle, backtrack = backtrack, 
                            gcr = gcr, cumulativesky = cumulativesky)
startdate = '20_01_01_12'      
enddate = '20_01_01_12'
trackerdict = demo.gendaylit1axis(startdate = startdate, enddate = enddate) 
trackerdict = demo.makeScene1axis(moduletype = moduletype_simple, sceneDict = sceneDict) 
trackerdict = demo.makeOct1axis()
result = demo.analysis1axis(customname='test_A')

print("\n TRACKER TILT:", demo.trackerdict['20_01_01_12_00']['surf_tilt']) # Sanity checkt of surface tilt


# ## B. With Frame Test

# In[13]:


# Restricting run to one hour for speed, 'MM_DD_HH'
metdata = demo.readWeatherFile(TMYtoread)
demo.setGround() 
sceneDict = {'pitch': pitch,'hub_height':hub_height, 'nMods':nMods, 'nRows': nRows, 'sceney':y}  
trackerdict = demo.set1axis(metdata = metdata, limit_angle = limit_angle, backtrack = backtrack, 
                            gcr = gcr, cumulativesky = cumulativesky)
startdate = '20_01_01_12'      
enddate = '20_01_01_12'
trackerdict = demo.gendaylit1axis(startdate = startdate, enddate = enddate) 
trackerdict = demo.makeScene1axis(moduletype = moduletype_framed, sceneDict = sceneDict) 
trackerdict = demo.makeOct1axis()
print(demo.trackerdict['20_01_01_12_00']['surf_tilt'])
result = demo.analysis1axis(customname='test_B', sensorsy=sensorsy)


# ## Compare Results

# In[14]:


bifacial_radiance.load.read1Result('results\irr_1axis_20_01_01_12_00test.csv')


# In[15]:


bifacial_radiance.load.read1Result('results\irr_1axis_20_01_01_12_00test_B.csv')


# # C. Modify Scanning position, Not Framed

# In[17]:


# Restricting run to one hour for speed, 'MM_DD_HH'
metdata = demo.readWeatherFile(TMYtoread)
demo.setGround() 
sceneDict = {'pitch': pitch,'hub_height':hub_height, 'nMods':nMods, 'nRows': nRows, 'sceney':y}  
trackerdict = demo.set1axis(metdata = metdata, limit_angle = limit_angle, backtrack = backtrack, 
                            gcr = gcr, cumulativesky = cumulativesky)
singleindex = '20_01_01_12'      
singleindex = '20_01_01_12'
trackerdict = demo.gendaylit1axis(startdate = singleindex, enddate = singleindex) 
trackerdict = demo.makeScene1axis(moduletype = moduletype_simple, sceneDict = sceneDict) 
trackerdict = demo.makeOct1axis()
print(demo.trackerdict['20_01_01_12_00']['surf_tilt'])

scanpoints = int(0.05/0.005)     # sample 5 cm from the edge, with a resolution of 0.005 mm 
frame_thickness = 0.01
modscanBack = {}
for ii in range(1, 3):
    modscanBack['ystart']  = x/2.0 - (frame_thickness + 0.001) - 0.005*ii # (adding frame thicknes plus 1 mm so it does not overlay exactly) 
    result = demo.analysis1axis(singleindex=singleindex+'_00', modscanfront=modscanBack, modscanback=modscanBack, relative = False, customname='_test_C_pos_'+str(ii), debug=True)
#    result = demo.analysis1axis(modscanfront=modscanBack, modscanback=modscanBack, relative = False, customname='_test_C_pos_'+str(ii))

    


# In[18]:


bifacial_radiance.load.read1Result('results\irr_1axis_20_01_01_12_00_test_C_pos_1.csv')


# In[19]:


bifacial_radiance.load.read1Result('results\irr_1axis_20_01_01_12_00_test_C_pos_2.csv')


# ## D. Modifying Scanning Position with Frames

# In[20]:


# Restricting run to one hour for speed, 'MM_DD_HH'
metdata = demo.readWeatherFile(TMYtoread)
demo.setGround() 
sceneDict = {'pitch': pitch,'hub_height':hub_height, 'nMods':nMods, 'nRows': nRows, 'sceney':y}  
trackerdict = demo.set1axis(metdata = metdata, limit_angle = limit_angle, backtrack = backtrack, 
                            gcr = gcr, cumulativesky = cumulativesky)
singleindex = '20_01_01_12'      
trackerdict = demo.gendaylit1axis(startdate = singleindex, enddate = singleindex) 
trackerdict = demo.makeScene1axis(moduletype = moduletype_framed, sceneDict = sceneDict) 
trackerdict = demo.makeOct1axis()
print(demo.trackerdict['20_01_01_12_00']['surf_tilt'])

scanpoints = int(0.05/0.005)     # sample 5 cm from the edge, with a resolution of 0.005 mm 
frame_thickness = 0.01
modscanBack = {}
for ii in range(0, 2):
    modscanBack['ystart']  = x/2.0 - (frame_thickness + 0.001) - 0.005*ii # (adding frame thicknes plus 1 mm so it does not overlay exactly) 
    result = demo.analysis1axis(modscanfront=modscanBack, modscanback=modscanBack, relative = False, customname='_test_D_pos_'+str(ii))

    


# In[21]:


bifacial_radiance.load.read1Result('results\irr_1axis_20_01_01_12_00_test_D_pos_0.csv')


# In[22]:


bifacial_radiance.load.read1Result('results\irr_1axis_20_01_01_12_00_test_C_pos_1.csv')


# In[ ]:





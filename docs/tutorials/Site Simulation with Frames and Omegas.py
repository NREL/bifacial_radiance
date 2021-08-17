#!/usr/bin/env python
# coding: utf-8

# In[148]:


import bifacial_radiance


# In[149]:


simulationname = 'OmegaTestField'


# In[150]:


testfolder = r'C:\Users\sarefeen\Documents\RadianceScenes\Temp'


# In[151]:


TMYtoread = r'C:\Users\sarefeen\Documents\RadianceScenes\Temp\SRRL_WeatherFile_TMY3_60_2020.csv'


# In[152]:


TMYtoread


# In[153]:


import pandas as pd
weatherfile = pd.read_csv(TMYtoread, header = 1)


# In[154]:


weatherfile.head()


# In[22]:


wf2 = weatherfile[weatherfile['DNI (W/m^2)'] == weatherfile['DNI (W/m^2)'].max()]


# In[144]:


wf3 = weatherfile[weatherfile['Date (MM/DD/YYYY)']== '4/29/2020']


# In[145]:


y = wf3['DNI (W/m^2)']
x = wf3['Time (HH:MM)']


# In[147]:


import matplotlib.pyplot as plt
plt.plot(x,y)
plt.xticks(rotation = 45)


# In[71]:


wf2


# In[29]:


weatherfile.groupby('Date (MM/DD/YYYY)')['DNI (W/m^2)'].sum().max()


# In[155]:


moduletype='Framed_Panel'
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
axisofrotationTorqueTube = False
hub_height = 1.35    # This is what we've been using but I measured 0.927 to torquetube...
xgap = 0.01    # 1 cm
zgap = 0.05    # 1 inch of arm, + 1 3/16 of panel width on average ~ 0.055 m
pitch=5.7      # distance between rows

# this is something I shall need to change to have better simulation resolution at the edge
sensorsy = 9


# In[156]:


# TorqueTube Parameters
axisofrotationTorqueTube=False
torqueTube = True
cellLevelModule = False


# In[157]:


albedo = 0.2  #'grass'     # ground albedo
# nMods = 20 
# nRows = 10 

#this change is for smalling the simulation

nMods = 1 
nRows = 1 

cumulativesky = False


# In[158]:


demo = bifacial_radiance.RadianceObj(simulationname, path = testfolder)  # Create a RadianceObj 'object'


# In[169]:


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
moduleDict=demo.makeModule(name=moduletype,x=x,y=y,numpanels = numpanels, xgap=xgap, zgap=zgap,
                            torquetube=torquetube, diameter=diameter, tubetype=tubetype, material=torqueTubeMaterial,
                            axisofrotationTorqueTube=axisofrotationTorqueTube, omegaParams = None, frameParams = None)


# In[170]:


metdata = demo.readWeatherFile(TMYtoread)
demo.setGround() 
sceneDict = {'pitch': pitch,'hub_height':hub_height, 'nMods':nMods, 'nRows': nRows, 'sceney':y}  
trackerdict = demo.set1axis(metdata = metdata, limit_angle = limit_angle, backtrack = backtrack, 
                            gcr = gcr, cumulativesky = cumulativesky)


# In[171]:


# Restricting run to one day for speed, 'MM_DD_HH'
startdate = '20_01_01_12'      
enddate = '20_01_01_12'
trackerdict = demo.gendaylit1axis(startdate = startdate, enddate = enddate) 
trackerdict = demo.makeScene1axis(moduletype = moduletype, sceneDict = sceneDict) 
trackerdict = demo.makeOct1axis()

# find the frontscan and backscan with the desired ystart value and then input them for function analysis1axis
#results = demo.analysis1axis(modWanted=16, rowWanted=3, sensorsy=sensorsy)


# In[173]:


demo.__dict__


# In[174]:


demo.trackerdict['20_01_01_12_00']['surf_tilt']


# In[172]:


scanpoints = int(0.05/0.005)     # sample 5 cm from the edge, with a resolution of 0.005 mm 
frame_thickness = 0.01
modscanBack = {}
for ii in range(0, 2):
    modscanBack['ystart']  = x/2.0 - (frame_thickness + 0.001) - 0.005*ii # (adding frame thicknes plus 1 mm so it does not overlay exactly) 
    result = demo.analysis1axis(modscanfront=modscanBack, modscanback=modscanBack, relative = False, customname='_WITHOUT_'+'pos_'+str(ii))


'''
irr_1axis_08_05_09_pos_0
irr_1axis_08_05_10_pos_0
irr_1axis_08_05_11_pos_0

irr_1axis_08_05_09_pos_1
irr_1axis_08_05_10_pos_1
irr_1axis_08_05_11_pos_1
irr_1axis_08_05_09_pos_2
irr_1axis_08_05_10_pos_2
irr_1axis_08_05_11_pos_2
'''


# In[ ]:





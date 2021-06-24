#!/usr/bin/env python
# coding: utf-8

# # 12c - Jack's Solar Garden
# 
# This is a tracking site
# 
# Two hub heights: 6ft and 8 ft
# rtr = 17 ft
# panels: 2 x 1 m
# 
# 

# <a id='step1'></a>

# In[11]:





# In[10]:


import os
from pathlib import Path

testfolder = str(Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP' / 'AgriPVStudy')

# Another option using relative address; for some operative systems you might need '/' instead of '\'
# testfolder = os.path.abspath(r'..\..\bifacial_radiance\TEMP')  

try:
    os.stat(testfolder)
except:
    os.mkdir(testfolder)
    
print ("Your simulation will be stored in %s" % testfolder)


# In[12]:


from bifacial_radiance import *   
import numpy as np
import datetime


# In[13]:





# In[15]:


hub_heights = [1.8, 2.4]
albedo = 0.12  #'grass'     # ground albedo
crops = ['tomato', 'kale']

# Redundant. Overwritihng the Radiance Obj for each loop below to have a unique name.
demo = RadianceObj('JackSolar', path=testfolder)  # Create a RadianceObj 'object'
demo.setGround(albedo) # input albedo number or material name like 'concrete'.  To see options, run this without any input.
lat = 40.12172917261154  # Jacks Solar Garden
lon = -105.13098877923312
epwfile = demo.getEPW(lat, lon)


# In[20]:





# In[18]:





# In[23]:


for jj in range (0, 1): #len(hub_heights)):
    hub_height = hub_heights[jj]
    simulationname = 'height_'+ str(int(hub_height*100))+'cm'

    #Location:
    # MakeModule Parameters
    moduletype='PrismSolar'
    numpanels = 1 
    x = 0.95  
    y = 1.95
    xgap = 0.01# Leaving 1 centimeters between modules on x direction
    ygap = 0.0 # Leaving 10 centimeters between modules on y direction
    zgap = 0.05 # cm gap between torquetube
    sensorsy = 12*numpanels  # t`his will give 6 sensors per module, 1 per cell

    # Other default values:

    # TorqueTube Parameters
    axisofrotationTorqueTube=True
    torqueTube = True
    cellLevelModule = False

    # SceneDict Parameters
    pitch = 5.1816 # m
    torquetube_height = hub_height - 0.1 # m
    nMods = 30 # six modules per row.
    nRows = 7  # 3 row

    azimuth_ang=90 # Facing south
    tilt =35 # tilt. 

    # Now let's run the example
#    demo = RadianceObj(simulationname,path = testfolder)  # Create a RadianceObj 'object'
    demo.setGround(albedo) # input albedo number or material name like 'concrete'.  To see options, run this without any input.

    #demo.gendaylit(4020)  # Use this to simulate only one hour at a time. 
    # Making module with all the variables
    moduleDict=demo.makeModule(name=moduletype,x=x,y=y,numpanels = numpanels, 
                               xgap=xgap, ygap=ygap, 
                               torquetube=False, diameter=0.12, tubetype='Square')
    
    # create a scene with all the variables
    sceneDict = {'tilt':tilt,'pitch': 15,'hub_height':hub_height,'azimuth':azimuth_ang, 'module_type':moduletype, 'nMods': nMods, 'nRows': nRows}  
    scene = demo.makeScene(moduletype=moduletype, sceneDict=sceneDict) #makeScene creates a .rad file with 20 modules per row, 7 rows.
    octfile = demo.makeOct(demo.getfilelist())  # makeOct combines all of the ground, sky and object fil|es into a .oct file.

    starttime = '05_01_01' 
    endtime = '10_01_01'


    metdata = demo.readEPW(epwfile, starttime = starttime, endtime = endtime) # read in the EPW weather data from above
    
    demo.genCumSky()

    octfile = demo.makeOct()  # makeOct combines all of the ground, sky and object files into a .oct file.

    analysis = AnalysisObj(octfile, demo.name)  # return an analysis object including the scan dimensions for back irradiance
    sensorsy = 10
    sensorsx = 5
    startgroundsample=-moduleDict['scenex']
    spacingbetweensamples = moduleDict['scenex']/(sensorsx-1)

    for i in range (0, sensorsx):  
        frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=sensorsy)
        groundscan = frontscan
        groundscan['zstart'] = 0.05  # setting it 5 cm from the ground.
        groundscan['zinc'] = 0   # no tilt necessary. 
        groundscan['yinc'] = pitch/(sensorsy-1)   # increasing spacing so it covers all distance between rows
        groundscan['xstart'] = startgroundsample + i*spacingbetweensamples   # increasing spacing so it covers 
                                                                          # all distance between rows
        analysis.analysis(octfile, simulationname+'_'+str(i), groundscan, backscan)  # compare the back vs front irradiance  

    metdata = demo.readEPW(epwfile) # read in the EPW weather data from above
    demo.genCumSky(savefile = 'PV')#startdt=startdt, enddt=enddt)

    octfile = demo.makeOct()  # makeOct combines all of the ground, sky and object files into a .oct file.

    analysis = AnalysisObj(octfile, demo.name)  # return an analysis object including the scan dimensions for back irradiance
    sensorsy = 20
    sensorsx = 12
    startPVsample=-moduleDict['x']
    spacingbetweenPVsamples = moduleDict['x']/(sensorsx-1)



# In[ ]:





# In[ ]:


cleanResult


# ## PLOT RESULTS

# In[58]:


import pandas as pd
import seaborn as sns


# In[44]:


import matplotlib.pyplot as plt
import matplotlib


# In[45]:


font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 22}
matplotlib.rc('font', **font)


# In[39]:


hub_heights = [4.3, 3.5, 2.5, 1.5]
results_BGG=[]
for i in range(0, len(hub_heights)):
    hub_height = str(int(hub_heights[i]*100))
    filepv= r'C:\Users\Silvana\Documents\GitHub\bifacial_radiance\bifacial_radiance\TEMP\AgriPVStudy\results\irr_height_{}cm_PV_6.csv'.format(hub_height)
    resultsDF = load.read1Result(filepv)
    resultsDF = load.cleanResult(resultsDF).dropna()
    results_BGG.append(resultsDF['Wm2Back'].sum()*100/resultsDF['Wm2Front'].sum())


# In[52]:


plt.figure(figsize=(14,10))
plt.plot(hub_heights, results_BGG, '.-')
plt.ylabel('Bifacial Gain in Irradiance (BG$_G$) [%]')
plt.xlabel('Hub height [m]')


# In[59]:


sns.set(rc={'figure.figsize':(11.7,8.27)})


# In[56]:





# In[ ]:


hub_heights = [4.3, 3.5, 2.5, 1.5]
#'irr_height_150cm_PV_10'
    


# In[73]:


maxmax = 0
for hh in range (0, len(hub_heights)):
    for cc in range (0, len(crops)):
        filestarter = "irr_height_"+ str(int(hub_heights[hh]*100))+'cm_'+crops[cc]

        filelist = sorted(os.listdir(os.path.join(testfolder, 'results')))
        prefixed = [filename for filename in filelist if filename.startswith(filestarter)]
        arrayWm2Front = []
        arrayWm2Back = []
        arrayMatFront = []
        arrayMatBack = []
        filenamed = []
        faillist = []

        print('{} files in the directory'.format(filelist.__len__()))
        print('{} groundscan files in the directory'.format(prefixed.__len__()))
        i = 0  # counter to track # files loaded.

        for i in range (0, len(prefixed)-1):
            ind = prefixed[i].split('_')
            #print(" Working on ", filelist[i], locs[ii], Scenario[jj])
            try:
                resultsDF = load.read1Result(os.path.join(testfolder, 'results', prefixed[i]))
                arrayWm2Front.append(list(resultsDF['Wm2Front']))
                arrayWm2Back.append(list(resultsDF['Wm2Back']))
                arrayMatFront.append(list(resultsDF['mattype']))
                arrayMatBack.append(list(resultsDF['rearMat']))
                filenamed.append(prefixed[i])
            except:
                print(" FAILED ", i, prefixed[i])
                faillist.append(prefixed[i])

        resultsdf = pd.DataFrame(list(zip(arrayWm2Front, arrayWm2Back, 
                                          arrayMatFront, arrayMatBack)),
                                 columns = ['br_Wm2Front', 'br_Wm2Back', 
                                            'br_MatFront', 'br_MatBack'])
        resultsdf['filename'] = filenamed
        
        df3 = pd.DataFrame(resultsdf['br_Wm2Front'].to_list())
        reversed_df = df3.T.iloc[::-1]
        
        if df3.max().max() > maxmax:
            maxmax = df3.max().max()


print(" MAX Found," maxmax)


# In[77]:


for hh in range (0, len(hub_heights)):
    for cc in range (0, len(crops)):
        filestarter = "irr_height_"+ str(int(hub_heights[hh]*100))+'cm_'+crops[cc]

        filelist = sorted(os.listdir(os.path.join(testfolder, 'results')))
        prefixed = [filename for filename in filelist if filename.startswith(filestarter)]
        arrayWm2Front = []
        arrayWm2Back = []
        arrayMatFront = []
        arrayMatBack = []
        filenamed = []
        faillist = []

        i = 0  # counter to track # files loaded.

        for i in range (0, len(prefixed)-1):
            ind = prefixed[i].split('_')
            #print(" Working on ", filelist[i], locs[ii], Scenario[jj])
            try:
                resultsDF = load.read1Result(os.path.join(testfolder, 'results', prefixed[i]))
                arrayWm2Front.append(list(resultsDF['Wm2Front']))
                arrayWm2Back.append(list(resultsDF['Wm2Back']))
                arrayMatFront.append(list(resultsDF['mattype']))
                arrayMatBack.append(list(resultsDF['rearMat']))
                filenamed.append(prefixed[i])
            except:
                print(" FAILED ", i, prefixed[i])
                faillist.append(prefixed[i])

        resultsdf = pd.DataFrame(list(zip(arrayWm2Front, arrayWm2Back, 
                                          arrayMatFront, arrayMatBack)),
                                 columns = ['br_Wm2Front', 'br_Wm2Back', 
                                            'br_MatFront', 'br_MatBack'])
        resultsdf['filename'] = filenamed
        
        df3 = pd.DataFrame(resultsdf['br_Wm2Front'].to_list())
        reversed_df = df3.T.iloc[::-1]
            
        plt.figure()
        ax = sns.heatmap(reversed_df/maxmax, vmin=0, vmax=1)
        ax.set_yticks([])
        ax.set_xticks([])
        ax.set_ylabel('')  
        ax.set_xlabel('')
        mytitle = crops[cc]+' '+str(hub_heights[hh])
        ax.set_title(mytitle)
        
        print(mytitle, df3.max().max(), df3.min().min())

print("")


# In[ ]:





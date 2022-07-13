#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
from pathlib import Path
from bifacial_radiance import *
import numpy as np

testfolder = Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP' / 'Tutorial_02'
if not os.path.exists(testfolder):
    os.makedirs(testfolder)  
print ("Your simulation will be stored in %s" % testfolder)


# In[2]:


demo = RadianceObj('tutorial_2', path = str(testfolder))  
demo.setGround(0.25)
#epwfile = demo.getEPW(lat = 37.5, lon = -77.6)  # This location corresponds to Richmond, VA.
epwfile = r'EPWs\USA_VA_Richmond.724010_TMY2.epw'
metdata = demo.readWeatherFile(weatherFile = epwfile) 

limit_angle = 5 # tracker rotation limit angle. Setting it ridiculously small so this runs faster.
angledelta = 5 # sampling between the limit angles. 
backtrack = True
gcr = 0.33
cumulativesky = True # This is important for this example!
trackerdict = demo.set1axis(metdata = metdata, limit_angle = limit_angle, backtrack = backtrack, 
                            gcr = gcr, cumulativesky = cumulativesky)
trackerdict = demo.genCumSky1axis()
module = demo.makeModule(name='test-module', x=1, y=2)
sceneDict = {'gcr': gcr,'hub_height':2.3, 'nMods': 5, 'nRows': 2}  
trackerdict = demo.makeScene1axis(trackerdict = trackerdict, module = module, sceneDict = sceneDict) 
trackerdict = demo.makeOct1axis(trackerdict = trackerdict)
trackerdict = demo.analysis1axis(trackerdict, modWanted=[1,4], rowWanted = 2, customname='_MyCustomName')


# In[3]:


trackerdict= demo.calculateResults()


# In[4]:


demo.CompiledResults


# In[ ]:


import pandas as pd

keys = list(trackerdict.keys())

temp_air = []
wind_speed = []
Wm2Front = []
Wm2Back = []
rearMat = []
frontMat = []
rowWanted = []
modWanted = []
keys_all = []

for key in keys:
    for row_mod in trackerdict[key]['Results']: # loop over multiple row & module in trackerDict['Results']
        keys_all.append(key)               
        Wm2Front.append(row_mod['AnalysisObj'].Wm2Front)
        Wm2Back.append(row_mod['AnalysisObj'].Wm2Back)
        frontMat.append(row_mod['AnalysisObj'].mattype)
        rearMat.append(row_mod['AnalysisObj'].rearMat)
        rowWanted.append(row_mod['AnalysisObj'].rowWanted)
        modWanted.append(row_mod['AnalysisObj'].modWanted)     
        if demo.cumulativesky is False:
            temp_air.append(trackerdict[key]['temp_air'])
            wind_speed.append(trackerdict[key]['wind_speed'])

# trackerdict[key]['effective_irradiance'] = eff_irrad

data= pd.DataFrame(zip(keys_all, rowWanted, modWanted, 
                       Wm2Front, Wm2Back, frontMat, rearMat), 
                                 columns=('timestamp', 'row','module',
                                          'Wm2Front', 'Wm2Back', 'mattype',
                                          'rearMat'))


# In[ ]:


data


# In[ ]:


demo


# In[ ]:


1.609801e+06+336657.59390000004


# # results = performance.calculateResultsGencumsky1axis(results=data)
# 

# In[ ]:


csvfile = None
dfst=pd.DataFrame()
results = data.copy()

if csvfile is not None:
    data = pd.read_csv(csvfile)
    Wm2Front = data['Wm2Front'].str.strip('[]').str.split(',', expand=True).astype(float)
    Wm2Back = data['Wm2Back'].str.strip('[]').str.split(',', expand=True).astype(float)
    mattype = data['mattype'].str.strip('[]').str.split(',', expand=True)
    rearMat = data['rearMat'].str.strip('[]').str.split(',', expand=True)

    if 'timestamp' in data:
        dfst['timestamp'] = data['timestamp']
    if 'ModNumber' in data:
        dfst['ModNumber'] = data['ModNumber']
    if 'Row' in data:
        dfst['rowNum'] = data['Row']
else:
    if results is not None:
        Wm2Front = pd.DataFrame.from_dict(dict(zip(results.index,results['Wm2Front']))).T
        Wm2Back = pd.DataFrame.from_dict(dict(zip(results.index,results['Wm2Back']))).T
        mattype = pd.DataFrame.from_dict(dict(zip(results.index,results['mattype']))).T
        rearMat = pd.DataFrame.from_dict(dict(zip(results.index,results['rearMat']))).T

        if 'timestamp' in results:
            dfst['timestamp'] = results['timestamp']
        if 'ModNumber' in results:
            dfst['ModNumber'] = results['ModNumber']
        if 'Row' in results:
            dfst['rowNum'] = results['Row']

    else:
        print("Data or file not passed. Ending calculateResults")


# In[ ]:


filledFront,filledBack = performance._cleanDataFrameResults(mattype, rearMat, Wm2Front, Wm2Back, fillcleanedSensors=True)


# In[ ]:


filledFront


# In[ ]:


demo.CompiledResults


# In[ ]:


filledBack


# In[ ]:


dfst


# In[ ]:


dfst['Wm2Back'].iloc[0]


# In[ ]:


dfst['POA_eff'].iloc[0]


# In[ ]:


bifacialityfactor=1


# In[ ]:


filledBack[mask].apply(lambda x: x*bifacialityfactor + filledFront[mask]).sum(axis=0)


# In[ ]:


cumFront=[]
cumBack=[]
cumRow=[]
cumMod=[]
Grear_mean=[]
#    Gfront_mean=[]
POA_eff=[]   

for rownum in results['row'].unique():
    for modnum in results['module'].unique():
        mask = (results['row']==rownum) & (results['module']==modnum)
        cumBack.append(list(filledBack[mask].sum(axis=0)))
        cumFront.append(filledFront[mask].sum(axis=0))
        cumRow.append(rownum)
        cumMod.append(modnum)

        # Maybe this would be faster by first doing the DF with the above,
        # exploding the column and calculating. 
        POA_eff.append(list((filledBack[mask].apply(lambda x: x*bifacialityfactor + filledFront[mask])).sum(axis=0)))
        Grear_mean.append(filledBack[mask].sum(axis=0).mean())
#           Gfront_mean.append(filledFront[mask].sum(axis=0).mean())

dfst= pd.DataFrame(zip(cumRow, cumMod, cumFront, 
                       cumBack, Grear_mean,POA_eff),
                                 columns=('row','module',
                                          'Gfront_mean', 'Wm2Back',
                                          'Grear_mean',
                                          'POA_eff'))

dfst['BGG'] = dfst['Grear_mean']*100*bifacialityfactor/dfst['Gfront_mean']

# Reordering columns    
cols = ['row', 'module', 'BGG', 'Gfront_mean', 'Grear_mean', 'POA_eff', 'Wm2Back']
dfst = dfst[cols]


# In[ ]:


filledFront


# In[ ]:


filledBack


# In[ ]:


dfst.iloc[0]['POA_eff']


# In[ ]:





# In[ ]:


data


# In[ ]:


filledBack


# In[ ]:


bifacialityfactor=1


# In[ ]:


filledBack[mask].sum(axis=0).mean()


# In[ ]:


cumFront=[]
cumBack=[]
cumRow=[]
cumMod=[]
Grear_mean=[]
Gfront_mean=[]
POA_eff=[]
BGG = []


for rownum in results['row'].unique():
    for modnum in results['module'].unique():
        mask = (results['row']==rownum) & (results['module']==modnum)
        cumBack.append(filledBack[mask].sum(axis=0))
        cumFront.append(filledFront[mask].sum(axis=0))
        cumRow.append(rownum)
        cumMod.append(modnum)

        # Maybe this would be faster by first doing the DF with the above,
        # exploding the column and calculating. 
        POA_eff.append((filledBack[mask].apply(lambda x: x*bifacialityfactor + filledFront[mask])).mean(axis=1))
        Grear_mean.append(filledBack[mask].sum(axis=0).mean())
        Gfront_mean.append(filledFront[mask].sum(axis=0).mean())


# In[ ]:





# In[ ]:


dfst['BGG'] = dfst['Grear_mean']*100/dfst['Gfront_mean']
dfst


# In[ ]:


list(dfst['POA_eff'].iloc[0])


# In[ ]:


cumFront=[]
cumBack=[]
cumRow=[]
cumMod=[]
Grear_mean=[]
Gfront_mean=[]
POA_eff=[]
BGG = []


for rownum in results['row'].unique():
    for modnum in results['module'].unique():
        mask = (results['row']==rownum) & (results['module']==modnum)
        cumBack.append(list(filledBack[mask].sum(axis=0)))
        cumFront.append(filledFront[mask].sum(axis=0))
        cumRow.append(rownum)
        cumMod.append(modnum)

        # Maybe this would be faster by first doing the DF with the above,
        # exploding the column and calculating. 
        POA_eff.append(list((filledBack[mask].apply(lambda x: x*bifacialityfactor + filledFront[mask])).mean(axis=0)))
        Grear_mean.append(filledBack[mask].sum(axis=0).mean())
        Gfront_mean.append(filledFront[mask].sum(axis=0).mean())


# In[ ]:


dfst= pd.DataFrame(zip(cumRow, cumMod, cumFront, 
                       cumBack, Gfront_mean,Grear_mean,POA_eff),
                                 columns=('row','module',
                                          'Wm2Front', 'Wm2Back',
                                          'Gfront_mean', 'Grear_mean',
                                          'POA_eff'))
dfst


# In[ ]:


dfst['BGG'] = dfst['Grear_mean']*100/dfst['Gfront_mean']


# In[ ]:


dfst


# In[ ]:


dfst.POA_eff.iloc[0]


# In[ ]:


data['module'].unique()


# In[ ]:


trackerdict = demo.trackerdict

temp_air = []
wind_speed = []
Wm2Front = []
Wm2Back = []
rearMat = []
frontMat = []
rowWanted = []
modWanted = []
keys_all = []

for key in keys:
        for row_mod in trackerdict[key]['Results']: # loop over multiple row & module in trackerDict['Results']
            keys_all.append(key)               
            Wm2Front.append(row_mod['AnalysisObj'].Wm2Front)
            Wm2Back.append(row_mod['AnalysisObj'].Wm2Back)
            frontMat.append(row_mod['AnalysisObj'].mattype)
            rearMat.append(row_mod['AnalysisObj'].rearMat)
            rowWanted.append(row_mod['AnalysisObj'].rowWanted)
            modWanted.append(row_mod['AnalysisObj'].modWanted)     
            if demo.cumulativesky is False:
                temp_air.append(trackerdict[key]['temp_air'])
                wind_speed.append(trackerdict[key]['wind_speed'])


# In[ ]:


import pandas as pd


# In[ ]:



data= pd.DataFrame(zip(keys_all, Wm2Front, Wm2Back, frontMat, rearMat,  
                                     wind_speed, temp_air, rowWanted, modWanted), 
                                 columns=('timestamp', 'Wm2Front', 
                                          'Wm2Back', 'mattype',
                                          'rearMat','rowWanted','modWanted'))

if demo.cumulativesky is False:
    data['temp_air'] = temp_air
    data['wind_speed'] = wind_speed


# In[ ]:


data= pd.DataFrame(zip(keys_all, Wm2Front, Wm2Back, frontMat, rearMat,  
                                     rowWanted, modWanted), 
                                 columns=('timestamp', 'Wm2Front', 
                                          'Wm2Back', 'mattype',
                                          'rearMat','rowWanted','modWanted'))


# In[ ]:


data


# In[ ]:


keys=list(trackerdict.keys())
print(keys)


# In[ ]:


trackerdict[keys[0]]['Results']


# In[ ]:


trackerdict[-5.0].keys()


# In[ ]:


demo.cumulativesky


# In[ ]:


demo.calculateResults()


# In[ ]:


results = load.read1Result('cumulative_results__Row_2_Module_09.csv')
results


# In[ ]:


results_clean = load.cleanResult(results)
results_clean


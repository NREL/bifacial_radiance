#!/usr/bin/env python
# coding: utf-8

# In[1]:


import bifacial_radiance
import os
import pandas as pd


# In[19]:


inifile = r'C:\Users\sayala\Documents\GitHub\bifacial_radiance\tests\ini_highAzimuth.ini'
weatherfile = r'C:\Users\sayala\Documents\GitHub\bifacial_radiance\tests\724666TYA.csv'
testfolder = r'C:\Users\sayala\Documents\GitHub\bifacial_radiance\bifacial_radiance\TEMP\Modelchain'


# In[14]:


(Params)= bifacial_radiance.load.readconfigurationinputfile(inifile=inifile)


# In[15]:


Params[0]


# In[16]:


Params[2]


# In[24]:


Params[0]['testfolder'] = testfolder
Params[0]['weatherFile'] = weatherfile
Params[2].update({'starttime': '06_17_13', 'endtime':'06_17_14'}); 


# In[25]:


demo2, analysis = bifacial_radiance.modelchain.runModelChain(*Params ) 


# In[37]:


demo2.trackerdict


# In[39]:


#CEC Module
url = 'https://raw.githubusercontent.com/NREL/SAM/patch/deploy/libraries/CEC%20Modules.csv'
db = pd.read_csv(url, index_col=0) # Reading this might take 1 min or so, the database is big.
modfilter2 = db.index.str.startswith('Pr') & db.index.str.endswith('BHC72-400')
CECMod = db[modfilter2]
print(len(CECMod), " modules selected. Name of 1st entry: ", CECMod.index[0])


# In[47]:


trackerdict = demo2.calculatePerformanceModule(CECMod)


# In[46]:


demo2.exportTrackerDict(savefile=os.path.join('results','Final_Results.csv'),reindex=False)
pd.read_csv(os.path.join('results','Final_Results.csv'))


# In[ ]:


#assert np.round(np.mean(analysis.backRatio),2) == 0.20  # bifi ratio was == 0.22 in v0.2.2
assert np.mean(analysis.Wm2Front) == pytest.approx(898, rel = 0.005)  # was 912 in v0.2.3
assert np.mean(analysis.Wm2Back) == pytest.approx(189, rel = 0.02)  # was 182 in v0.2.2


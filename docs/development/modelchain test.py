#!/usr/bin/env python
# coding: utf-8

# In[1]:


import bifacial_radiance
import os
import pandas as pd


# In[2]:


inifile = r'C:\Users\sayala\Documents\GitHub\bifacial_radiance\tests\ini_highAzimuth.ini'
#inifile = r'C:\Users\sayala\Documents\GitHub\bifacial_radiance\tests\ini_gencumsky.ini'
#inifile = r'C:\Users\sayala\Documents\GitHub\bifacial_radiance\tests\ini_1axis.ini'

weatherfile = r'C:\Users\sayala\Documents\GitHub\bifacial_radiance\tests\724666TYA.csv'
testfolder = r'C:\Users\sayala\Documents\GitHub\bifacial_radiance\bifacial_radiance\TEMP\Modelchain'


# In[3]:


(Params)= bifacial_radiance.load.readconfigurationinputfile(inifile=inifile)


# In[4]:


Params


# In[5]:


Params[0]['testfolder'] = testfolder
Params[0]['weatherFile'] = weatherfile
Params[2].update({'starttime': '06_17_13', 'endtime':'06_17_14'}); 


# In[6]:


Params[6]['modWanted'] = [1, 3]


# In[7]:


demo2, analysis = bifacial_radiance.modelchain.runModelChain(*Params ) 


# In[ ]:


analysis -- Wm2Back adn Wm2Front


# In[13]:


demo2.__dict__


# In[ ]:


demo2


# In[ ]:


demo2


# In[ ]:


demo2.results


# In[ ]:


trackerdict = demo2.trackerdict
keys = list(demo2.trackerdict.keys())


# In[ ]:


frontirrad = trackerdict[keys[0]]['AnalysisObj'].Wm2Front


# In[ ]:


type(frontirrad)


# In[ ]:


#CEC Module
url = 'https://raw.githubusercontent.com/NREL/SAM/patch/deploy/libraries/CEC%20Modules.csv'
db = pd.read_csv(url, index_col=0) # Reading this might take 1 min or so, the database is big.
modfilter2 = db.index.str.startswith('Pr') & db.index.str.endswith('BHC72-400')
CECMod = db[modfilter2]
print(len(CECMod), " modules selected. Name of 1st entry: ", CECMod.index[0])


# In[ ]:


type(CECMod)


# In[ ]:


CECModParamsDict = Params[-1]


# In[ ]:


CECModParamsDict


# In[ ]:


pd.DataFrame(CECModParamsDict, index=[0])


# In[ ]:


import numpy as np


# In[ ]:


demo2.trackerdict[keys[0]]['AnalysisObj'].Wm2Front[1] = np.nan
demo2.trackerdict[keys[0]]['AnalysisObj'].Wm2Front[2] = np.nan
demo2.trackerdict[keys[0]]['AnalysisObj'].Wm2Front[3] = np.nan
demo2.trackerdict[keys[0]]['AnalysisObj'].Wm2Front[4] = np.nan
demo2.trackerdict[keys[0]]['AnalysisObj'].Wm2Front[5] = np.nan
demo2.trackerdict[keys[0]]['AnalysisObj'].Wm2Front[6] = np.nan
demo2.trackerdict[keys[0]]['AnalysisObj'].Wm2Front[7] = np.nan


# In[ ]:


type(CECMod)


# In[ ]:


CECMod)


# In[ ]:


trackerdict = demo2.calculateResults(CECMod = CECMod)


# In[ ]:


CECMod.Adjust


# In[ ]:


print("Error: Mising/wrong parameters for CECMod, setting dictionary to None.",
      "MAke sure to include alpha_sc, a_ref, I_L_ref, I_o_ref, ",
      "R_sh_ref, R_s, and Adjust"
      "Performance calculations, if performed, will use default module")


# In[ ]:


demo2.exportTrackerDict(savefile=os.path.join('results','Final_Results.csv'),reindex=False)


# In[ ]:


pd.read_csv(os.path.join('results','Final_Results.csv'))


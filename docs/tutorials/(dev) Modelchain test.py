#!/usr/bin/env python
# coding: utf-8

# In[1]:


import bifacial_radiance
import os
import pandas as pd


# In[2]:


#inifile = r'C:\Users\sayala\Documents\GitHub\bifacial_radiance\tests\simulationView.ini'
#inifile = r'C:\Users\sayala\Documents\GitHub\bifacial_radiance\tests\ini_highAzimuth.ini'
inifile = r'C:\Users\sayala\Documents\GitHub\bifacial_radiance\tests\simulation3.ini'
#inifile = r'C:\Users\sayala\Documents\GitHub\bifacial_radiance\tests\simulation_T01.ini'
#inifile = r'C:\Users\sayala\Documents\GitHub\bifacial_radiance\tests\simulation_D9.ini' # timestamp without year test
#inifile = r'C:\Users\sayala\Documents\GitHub\bifacial_radiance\tests\simulation_D2.ini' # Sub-hourly data PErformance Aggregation test


# In[3]:


(Params)= bifacial_radiance.load.readconfigurationinputfile(inifile=inifile)


# In[4]:


demo2, analysis = bifacial_radiance.modelchain.runModelChain(*Params) 


# In[7]:


get_ipython().system('rvu -vf views\\side.vp -e .01 1axis_2021-06-17_1300.oct')


# In[ ]:


get_ipython().system('rvu -vf views\\side.vp -e .01 1axis_2021-05-01_0900.oct')


# In[ ]:


data = demo2.CompiledResults


# In[ ]:


customtext 


# In[ ]:


df =data[data['module']==1].copy()


# In[ ]:


df.set_index(df['timestamp'])


# In[ ]:


df['timestamp'] = pd.to_datetime(df['timestamp'], format="%Y-%m-%d_%H%M")
df = df.set_index('timestamp')


# In[ ]:


type(df.index)


# In[ ]:


df


# In[ ]:


(df.index[1]-df.index[0]).total_seconds() / 60


# In[ ]:


(df.index[1]-df.index[0]).dt.days


# In[ ]:


if (df.index[1]-df.index[0]).total_seconds() / 60 == 15.0:
    print("yes")


# In[ ]:


import pandas as pd


# In[ ]:


df = pd.DataFrame()


# In[ ]:


if df.empty is True:
    print("Yes")


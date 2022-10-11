#!/usr/bin/env python
# coding: utf-8

# In[5]:


import bifacial_radiance
import os
import pandas as pd


# In[9]:


#inifile = r'C:\Users\sayala\Documents\GitHub\bifacial_radiance\tests\simulationView.ini'
#inifile = r'C:\Users\sayala\Documents\GitHub\bifacial_radiance\tests\ini_highAzimuth.ini'
#inifile = r'C:\Users\sayala\Documents\GitHub\bifacial_radiance\tests\simulation3.ini'
inifile = r'C:\Users\sayala\Documents\GitHub\bifacial_radiance\tests\simulation_T01.ini'


# In[10]:


(Params)= bifacial_radiance.load.readconfigurationinputfile(inifile=inifile)


# In[8]:


demo2, analysis = bifacial_radiance.modelchain.runModelChain(*Params ) 


# In[ ]:


get_ipython().system('rvu -vf views\\side.vp -e .01 1axis_2021-06-17_1300.oct')


# In[ ]:


demo2.CompiledResults


# In[ ]:


demo2.trackerdict


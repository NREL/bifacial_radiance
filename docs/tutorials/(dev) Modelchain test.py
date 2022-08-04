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


# In[3]:


(Params)= bifacial_radiance.load.readconfigurationinputfile(inifile=inifile)


# In[4]:


demo2, analysis = bifacial_radiance.modelchain.runModelChain(*Params ) 


# In[5]:


get_ipython().system('rvu -vf views\\side.vp -e .01 1axis_2021-06-17_1300.oct')


# In[6]:


demo2.CompiledResults


# In[7]:


demo2.trackerdict


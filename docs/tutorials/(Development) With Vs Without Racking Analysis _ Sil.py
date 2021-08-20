#!/usr/bin/env python
# coding: utf-8

# In[2]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import math
import os


# ## We have simulation results for 40 ysensors for each of the 196 positions approx. 5 cm apart from each other to cover the 2m y-length of the panel (real-world x). At first, we observe the 'with racking' scenario. 

# In[3]:


testfolder = r'C:\Users\sayala\Documents\INTERNS\SHAMSUL'


# In[5]:


data_with = pd.read_csv(os.path.join(testfolder,'COMPILED_Results_WITH_19AUG_complete.csv'), index_col = 0)
data_without = pd.read_csv(os.path.join(testfolder,'COMPILED_Results_WITHOUT_19AUG_complete.csv'), index_col = 0)


# In[8]:


# Just a function to flip the columns (required for x and associated readings to be put as from east to west)
def df_correct(df):
    return df[df.columns[::-1]]


# ### WITH

# In[18]:


Wm2Front_with = data_with["Wm2Front"].str.strip('[]').str.split(',', expand=True).astype(float)
Wm2Back_with = data_with["Wm2Back"].str.strip('[]').str.split(',', expand=True).astype(float)
Wm2Front_with_w2e = df_correct(Wm2Front_with)
data_backirr_with = df_correct(Wm2Back_with)


# In[ ]:





# In[16]:


# Clean this up
r'''
x = data_with["x"].str.strip('[]').str.split(',', expand=True).astype(float)
y = data_with["y"].str.strip('[]').str.split(',', expand=True).astype(float)
x_w2e = df_correct(x)
data_backirr_with = Wm2Back_with_w2e
y_vals = y.iloc[:,0]
data_backirr_with.set_index(y_vals)
data_backirr_with.columns = x_w2e.iloc[0,:]
data_backirr_with.set_index(y_vals, inplace = True)
''';


# ### WITHOUT

# In[19]:


Wm2Front_without = data_without["Wm2Front"].str.strip('[]').str.split(',', expand=True).astype(float)
Wm2Back_without = data_without["Wm2Back"].str.strip('[]').str.split(',', expand=True).astype(float)
Wm2Front_without_w2e = df_correct(Wm2Front_without)
data_backirr_without = df_correct(Wm2Back_without)


# In[ ]:


#data_backirr_without = data_backirr_with
#data_backirr_without.iloc[:,:] = Wm2Back_without_w2e


# In[20]:


plt.rcParams.update({'font.size': 22})
plt.rcParams['figure.figsize'] = (12, 8)


# In[23]:


minboth = min(np.min(data_backirr_with).min(), np.min(data_backirr_without).min())
maxboth = max(np.max(data_backirr_with).max(), np.max(data_backirr_without).max())


# In[26]:


data_backirr_without.iloc[100].mean()


# In[24]:


with sns.axes_style("white"):
    fig = plt.imshow(data_backirr_with, cmap='hot', vmin=minboth, 
                     vmax=maxboth, interpolation='none', aspect = 0.1)
    plt.colorbar(label='G$_{rear}$')
    #plt.title('Yearly Bifacial, in matrix form')
    fig.axes.get_yaxis().set_visible(False)
    fig.axes.get_xaxis().set_visible(False)
    
plt.figure()

with sns.axes_style("white"):
    fig = plt.imshow(data_backirr_without, cmap='hot', vmin=minboth, 
                     vmax=maxboth, interpolation='none', aspect = 0.1)
    plt.colorbar(label='G$_{rear}$')
    #plt.title('Yearly Bifacial, in matrix form')
    fig.axes.get_yaxis().set_visible(False)
    fig.axes.get_xaxis().set_visible(False)


# In[ ]:





# This is just the preliminary analysis for a morning hour (11am) of a clear-sky day (29th April, 2021). Way to go!!!

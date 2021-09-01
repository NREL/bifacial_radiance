#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import math
import os


# ## We have simulation results for 40 ysensors for each of the 196 positions approx. 5 cm apart from each other to cover the 2m y-length of the panel (real-world x). At first, we observe the 'with racking' scenario. 

# In[2]:


data_with = pd.read_csv('COMPILED_Results_WITH_19AUG_complete.csv', index_col = 0)


# In[4]:


data_with.shape


# In[6]:


data_with.columns


# In[7]:


data_with.head(10)


# The strings are to split as appropriate datatype

# In[8]:


Wm2Front_with = data_with["Wm2Front"].str.strip('[]').str.split(',', expand=True).astype(float)
Wm2Back_with = data_with["Wm2Back"].str.strip('[]').str.split(',', expand=True).astype(float)


# In[9]:


# Just a function to flip the columns (required for x and associated readings to be put as from east to west)
def df_correct(df):
    return df[df.columns[::-1]]


# In[19]:


Wm2Front_with_w2e = df_correct(Wm2Front_with)
Wm2Back_with_w2e = df_correct(Wm2Back_with)


# In[11]:


x = data_with["x"].str.strip('[]').str.split(',', expand=True).astype(float)
y = data_with["y"].str.strip('[]').str.split(',', expand=True).astype(float)


# In[15]:


print(x.shape)
x.head()


# It is observed that the x positions move from east to west before flipping.

# In[16]:


y.head()


# In[17]:


y.tail()


# It is observed that the y readings are identical for the same position as expected. The positions move from north to south before flipping.

# In[22]:


x_w2e = df_correct(x)


# In[20]:


data_backirr_with = Wm2Back_with_w2e


# In[23]:


y_vals = y.iloc[:,0]


# In[24]:


y_vals


# In[25]:


data_backirr_with.set_index(y_vals)


# In[27]:


data_backirr_with.columns = x_w2e.iloc[0,:]


# In[31]:


data_backirr_with.set_index(y_vals, inplace = True)


# In[32]:


data_backirr_with.head()


# In[ ]:


plt.rcParams.update({'font.size': 22})
plt.rcParams['figure.figsize'] = (12, 8)


# In[33]:


with sns.axes_style("white"):
    fig = plt.imshow(data_backirr_with, cmap='hot', vmin=np.min(data_backirr_with).min(), vmax=np.max(data_backirr_with).max(), interpolation='none', aspect = 0.1)
    plt.colorbar(label='G$_{rear}$')
    #plt.title('Yearly Bifacial, in matrix form')
    fig.axes.get_yaxis().set_visible(False)
    fig.axes.get_xaxis().set_visible(False)


# Time to analyze the 'without' scenario

# In[34]:


data_without = pd.read_csv('COMPILED_Results_WITHOUT_19AUG_complete.csv', index_col = 0)


# In[35]:


data_without.shape


# In[36]:


data_without.head()


# The strings are to split as appropriate datatype

# In[37]:


Wm2Front_without = data_without["Wm2Front"].str.strip('[]').str.split(',', expand=True).astype(float)
Wm2Back_without = data_without["Wm2Back"].str.strip('[]').str.split(',', expand=True).astype(float)


# In[39]:


Wm2Front_without_w2e = df_correct(Wm2Front_without)
Wm2Back_without_w2e = df_correct(Wm2Back_without)


# In[43]:


data_backirr_without = data_backirr_with


# In[44]:


data_backirr_without.iloc[:,:] = Wm2Back_without_w2e


# In[45]:


data_backirr_without.head()


# In[46]:


with sns.axes_style("white"):
    fig = plt.imshow(data_backirr_without, cmap='hot', vmin=np.min(data_backirr_without).min(), 
                     vmax=np.max(data_backirr_without).max(), interpolation='none', aspect = 0.1)
    plt.colorbar(label='G$_{rear}$')
    #plt.title('Yearly Bifacial, in matrix form')
    fig.axes.get_yaxis().set_visible(False)
    fig.axes.get_xaxis().set_visible(False)


# This is just the preliminary analysis for a morning hour (11am) of a clear-sky day (29th April, 2021). Way to go!!!

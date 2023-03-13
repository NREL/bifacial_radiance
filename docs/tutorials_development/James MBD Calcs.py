#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd


# In[2]:


rad_file = r'C:\Users\sayala\Desktop\JAMES\Rad.csv'
vf_file = r'C:\Users\sayala\Desktop\JAMES\VF.csv'


# In[3]:


df1 = pd.read_csv(rad_file)
df2 = pd.read_csv(vf_file)


# In[4]:


df1 = df1.rename(columns={'1': '1.0', '2': '2.0'})


# In[5]:


df1 = df1.add_prefix('rad_')
#df2 = df2.add_prefix('vf_')


# In[6]:


from bifacial_radiance.performance import MBD, RMSE, MBD_abs, RMSE_abs


# In[7]:


from scipy.interpolate import interp1d

ch = ['0.25', '0.5', '0.75', '1.0', '1.5', '2.0']

for c in ch:
    print
    f2 = interp1d(df2['y'],df2[c],bounds_error=False)
    df1['vf_'+c] = f2(df1.rad_y)


# In[8]:


res = df1.dropna()


# In[9]:


res


# In[10]:


ch = ['0.25', '0.5', '0.75', '1.0', '1.5', '2.0']

#MBD, RMSE, MBD_abs, RMSE_abs

print('MBD,  RMSE,  MBD_abs, RMSE_abs')
for cs in ch:
    print(round(MBD(res['rad_'+cs], res['vf_'+cs]),1) ,
          round(RMSE(res['rad_'+cs], res['vf_'+cs]),1) , 
          round(MBD_abs(res['rad_'+cs], res['vf_'+cs]),1) ,
          round(RMSE_abs(res['rad_'+cs], res['vf_'+cs]),1))


# In[11]:


import matplotlib.pyplot as plt


# In[13]:


plt.rcParams["figure.figsize"] = (5,5)

for cs in ch:
    plt.plot(res['rad_'+cs], res['vf_'+cs], label=cs)
plt.plot([0,250000], [0,250000], 'r')
plt.legend()
plt.xlim([0,250000])
plt.ylim([0,250000])
plt.xlabel(' Radiance ')
plt.ylabel(' View Factor ')


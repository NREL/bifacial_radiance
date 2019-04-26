# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 12:51:44 2019

@author: sayala
"""

import pandas as pd

nott = r'C:\Users\sayala\Desktop\Copy of results_Cairo_mismatch_1up_noTorqueTube.csv'
yestt = r'C:\Users\sayala\Desktop\Copy of results_Cairo_mismatch_1up_wTorqueTube.csv'


data= pd.read_csv(nott, sep = ',', header = 0, parse_dates=['Timestamp'])
data_NO=data.set_index('Timestamp', drop=True, append=False, inplace=False, verify_integrity=False)

data= pd.read_csv(yestt, sep = ',', header = 0, parse_dates=['Timestamp'])
data_YES=data.set_index('Timestamp', drop=True, append=False, inplace=False, verify_integrity=False)


# In[1]:
# Select IRRADIANCE data from back sensors
backIrradianceNOtt = data_NO.filter(like='Clean_Back_cell')
backIrradianceNOtt.columns = [x.strip().replace('Clean_Back_cell', '') for x in backIrradianceNOtt.columns]  # Colum nindex is now only the number.

backIrradianceWithtt = data_YES.filter(like='Clean_Back_cell')
backIrradianceWithtt.columns = [x.strip().replace('Clean_Back_cell', '') for x in backIrradianceWithtt.columns]  # Colum nindex is now only the number.

import matplotlib.pyplot as plt
import numpy as np

ax = plt.gca()

#x = [i for i in np.arange(0, 100,5.0)]
x = [i for i in np.linspace(0,100,120)]

plt.plot(x, backIrradianceNOtt.loc['12_31_15'],'b', label='No TT')
plt.plot(x, backIrradianceWithtt.loc['12_31_15'],'r', label='W TT')
plt.ylim(0,330)
plt.legend()
plt.title('PLOT 1 '+str(0.15))
plt.xlabel('Position on panel [%]')
plt.ylabel('W/$m^2$')
plt.show()

# In[3]:
# Plotting 4 hours in the Equinoxes and Solstices of the year
# Comparing with and without torquetube.

fig, axes = plt.subplots(4, 4, sharey='row', sharex='col', figsize=(15,15))
axes[0, 0].plot(x, backIrradianceNOtt.loc['03_21_09'],'b', label='No TT')
axes[0, 0].plot(x, backIrradianceWithtt.loc['03_21_09'],'r', label='W TT')
axes[0, 0].set_ylim(0,330)
axes[0, 0].set_ylabel("Spring")
axes[0, 1].plot(x, backIrradianceNOtt.loc['03_21_12'],'b', label='No TT')
axes[0, 1].plot(x, backIrradianceWithtt.loc['03_21_12'],'r', label='W TT')
axes[0, 2].plot(x, backIrradianceNOtt.loc['03_21_15'],'b', label='No TT')
axes[0, 2].plot(x, backIrradianceWithtt.loc['03_21_15'],'r', label='W TT')
axes[0, 3].plot(x, backIrradianceNOtt.loc['03_21_18'],'b', label='No TT')
axes[0, 3].plot(x, backIrradianceWithtt.loc['03_21_18'],'r', label='W TT')

axes[1, 0].plot(x, backIrradianceNOtt.loc['06_21_09'],'b', label='No TT')
axes[1, 0].plot(x, backIrradianceWithtt.loc['06_21_09'],'r', label='W TT')
axes[1, 0].set_ylim(0,330)
axes[1, 0].set_ylabel("Summer")
axes[1, 1].plot(x, backIrradianceNOtt.loc['06_21_12'],'b', label='No TT')
axes[1, 1].plot(x, backIrradianceWithtt.loc['06_21_12'],'r', label='W TT')
axes[1, 2].plot(x, backIrradianceNOtt.loc['06_21_15'],'b', label='No TT')
axes[1, 2].plot(x, backIrradianceWithtt.loc['06_21_15'],'r', label='W TT')
axes[1, 3].plot(x, backIrradianceNOtt.loc['06_21_18'],'b', label='No TT')
axes[1, 3].plot(x, backIrradianceWithtt.loc['06_21_18'],'r', label='W TT')

axes[2, 0].plot(x, backIrradianceNOtt.loc['09_21_09'],'b', label='No TT')
axes[2, 0].plot(x, backIrradianceWithtt.loc['09_21_09'],'r', label='W TT')
axes[2, 0].set_ylim(0,330)
axes[2, 0].set_ylabel("Fall")
axes[2, 1].plot(x, backIrradianceNOtt.loc['09_21_12'],'b', label='No TT')
axes[2, 1].plot(x, backIrradianceWithtt.loc['09_21_12'],'r', label='W TT')
axes[2, 2].plot(x, backIrradianceNOtt.loc['09_21_15'],'b', label='No TT')
axes[2, 2].plot(x, backIrradianceWithtt.loc['09_21_15'],'r', label='W TT')
#axes[2, 3].plot(x, backIrradianceNOtt.loc['09_21_18'],'b', label='No TT')
#axes[2, 3].plot(x, backIrradianceWithtt.loc['09_21_18'],'r', label='W TT')

axes[3, 0].plot(x, backIrradianceNOtt.loc['12_21_09'],'b', label='No TT')
axes[3, 0].plot(x, backIrradianceWithtt.loc['12_21_09'],'r', label='W TT')
axes[3, 0].set_ylim(0,330)
axes[3, 0].set_ylabel("Winter")
axes[3, 1].plot(x, backIrradianceNOtt.loc['12_21_12'],'b', label='No TT')
axes[3, 1].plot(x, backIrradianceWithtt.loc['12_21_12'],'r', label='W TT')
axes[3, 2].plot(x, backIrradianceNOtt.loc['12_21_15'],'b', label='No TT')
axes[3, 2].plot(x, backIrradianceWithtt.loc['12_21_15'],'r', label='W TT')
#axes[3, 3].plot(x, backIrradianceNOtt.loc['12_21_18'],'b', label='No TT')
#axes[3, 3].plot(x, backIrradianceWithtt.loc['12_21_18'],'r', label='W TT')

axes[3, 0].set_xlabel("9 AM")
axes[3, 1].set_xlabel("12 PM")
axes[3, 2].set_xlabel("3 PM")
axes[3, 3].set_xlabel("6 PM")

fig.text(0.5, 0.05, 'Hour', ha='center')
fig.text(0.05, 0.5, 'W/m^2 rear irradiance', va='center', rotation='vertical')


# In[4]:

backIrradianceWithtt.index = pd.to_datetime(backIrradianceWithtt.index, format="%m_%d_%H")
backIrradianceNOtt.index = pd.to_datetime(backIrradianceNOtt.index, format="%m_%d_%H")

morning=backIrradianceWithtt.between_time('9:00','9:00')
A = morning.resample('M').mean()

# 9 AM for January
plt.plot(x, A.iloc[0],label='No TT')
plt.plot(x, A.iloc[1], label='No TT')
plt.plot(x, A.iloc[2], label='No TT')
plt.plot(x, A.iloc[3], label='No TT')
plt.plot(x, A.iloc[4], label='No TT')
plt.plot(x, A.iloc[5], label='No TT')
plt.plot(x, A.iloc[6], label='No TT')
plt.plot(x, A.iloc[7], label='No TT')
plt.plot(x, A.iloc[8], label='No TT')
plt.plot(x, A.iloc[9], label='No TT')
plt.plot(x, A.iloc[10], label='No TT')
plt.plot(x, A.iloc[11], label='No TT')
plt.ylim(0,330)

morning=backIrradianceWithtt.between_time('12:00','12:00')
A = morning.resample('M').mean()

# 9 AM for January
plt.plot(x, A.iloc[0],label='No TT')
plt.plot(x, A.iloc[1], label='No TT')
plt.plot(x, A.iloc[2], label='No TT')
plt.plot(x, A.iloc[3], label='No TT')
plt.plot(x, A.iloc[4], label='No TT')
plt.plot(x, A.iloc[5], label='No TT')
plt.plot(x, A.iloc[6], label='No TT')
plt.plot(x, A.iloc[7], label='No TT')
plt.plot(x, A.iloc[8], label='No TT')
plt.plot(x, A.iloc[9], label='No TT')
plt.plot(x, A.iloc[10], label='No TT')
plt.plot(x, A.iloc[11], label='No TT')
plt.ylim(0,330)


morning=backIrradianceWithtt.between_time('15:00','15:00')
A = morning.resample('M').mean()

# 9 AM for January
plt.plot(x, A.iloc[0],label='No TT')
plt.plot(x, A.iloc[1], label='No TT')
plt.plot(x, A.iloc[2], label='No TT')
plt.plot(x, A.iloc[3], label='No TT')
plt.plot(x, A.iloc[4], label='No TT')
plt.plot(x, A.iloc[5], label='No TT')
plt.plot(x, A.iloc[6], label='No TT')
plt.plot(x, A.iloc[7], label='No TT')
plt.plot(x, A.iloc[8], label='No TT')
plt.plot(x, A.iloc[9], label='No TT')
plt.plot(x, A.iloc[10], label='No TT')
plt.plot(x, A.iloc[11], label='No TT')
plt.ylim(0,330)

# In[6]:

# Plot all days at the same hour for one month: 
morning=backIrradianceWithtt.between_time('12:00','12:00')
df1 = morning[morning.index.month.isin([1])]
df5 = morning[morning.index.month.isin([5])]
df10 = morning[morning.index.month.isin([10])]

# P
for i in range (0, len(df1)):
    plt.plot(x,df1.iloc[i], 'r')
for i in range(0, len(df5)):
    plt.plot(x,df5.iloc[i], 'g')
for i in range(0, len(df10)):
    plt.plot(x,df10.iloc[i], 'b')

plt.ylim(0,330)

# In[5]:
#Sanity check of why Cairo data January for 01_07 to 01-10 there is no value at 8 AM.
# Turns out DNI and DHI is 0 at those times

metdata.datetime[127] # Timestamp('1991-01-06 08:00:00+0200', tz='pytz.FixedOffset(120)')
metdata.dni[127]
metdata.datetime[151] # Timestamp('1991-01-07 08:00:00+0200', tz='pytz.FixedOffset(120)')
metdata.dni[151]
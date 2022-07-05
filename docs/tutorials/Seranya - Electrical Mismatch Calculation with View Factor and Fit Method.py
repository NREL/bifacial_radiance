#!/usr/bin/env python
# coding: utf-8

# # 4 - Mismatch Equation calculation for fixed-tilt setup
# 
# This jupyter journal will walk us through the creation of a basic fixed-tilt simulation possible with bifacialvf, and then use PinPV equation to calculate electrical mismatch for each hour, for hte year, and the factor to use for PVSyst which is applied to Grear on their workflow.
# 
# Electrical mismatch calculation following Progress in PV paper
#     Estimating and parameterizing mismatch power loss in bifacial photovoltaic systems
#     Chris Deline, Silvana Ayala Pelaez,Sara MacAlpine,Carlos Olalla
#     https://doi.org/10.1002/pip.3259 
#     
# 
# THIS JOURNAL IS IN DEVELOPMENT
# 

# In[1]:


from pathlib import Path
import os
import bifacialvf
import bifacial_radiance as br
import pandas as pd
import numpy as np
# IO Files
testfolder = Path().resolve().parent.parent / 'bifacialvf' / 'TEMP' / 'Tutorial_03'
if not os.path.exists(testfolder):
    os.makedirs(testfolder)


# In[2]:


# Download and Read input
TMYtoread=bifacialvf.getEPW(lat=37.5407,lon=-77.4360, path = testfolder)
myTMY3, meta = bifacialvf.readInputTMY(TMYtoread)
deltastyle = 'TMY3'  # 


# In[3]:


# Variables
config=5              # 5-up configuration
panellength = 1*config           #1 meter * 5 modules on 1-up landscape
tilt = 10                   # PV tilt (deg)
sazm = 180                  # PV Azimuth(deg) or tracker axis direction
albedo = 0.62               # ground albedo
clearance_height=1/panellength   # 1m clearance normalized to panel length
pitch = 5/panellength       # row to row spacing in normalized panel lengths. 
rowType = "interior"        # RowType(first interior last single)
transFactor = 0.013         # TransmissionFactor(open area fraction, including x-gaps and y-gaps in the collector surface)
sensorsy = 6*5 # Number of sampling points for the setup. Recommend at least 6 per module. 
PVfrontSurface = "glass"    # PVfrontSurface(glass or ARglass)
PVbackSurface = "glass"     # PVbackSurface(glass or ARglass)

# Calculate PV Output Through Various Methods    
# This variables are advanced and explored in other tutorials.
bififactor = 0.7              # IF monofacial set to 0

# Tracking instructions
tracking=False
backtrack=False
limit_angle = 60


writefiletitle = os.path.join(testfolder, 'Tutorial3_Results.csv')
myTMY3 = myTMY3.iloc[0:24].copy()  # Simulate just the first 24 hours of the data file for speed on this example
bifacialvf.simulate(myTMY3, meta, writefiletitle=writefiletitle, 
         tilt=tilt, sazm=sazm, pitch=pitch, clearance_height=clearance_height, 
         rowType=rowType, transFactor=transFactor, sensorsy=sensorsy, 
         PVfrontSurface=PVfrontSurface, PVbackSurface=PVbackSurface, 
         albedo=albedo, tracking=tracking, backtrack=backtrack, 
         limit_angle=limit_angle, deltastyle=deltastyle)



# ## 2. Load the irradiance results

# In[4]:


from bifacialvf import loadVFresults
mismatchResultstitle = os.path.join(testfolder, 'Tutorial3_Results.csv')
(data, metadata) = loadVFresults(mismatchResultstitle)


# In[5]:


data.keys()


# In[6]:


df = data[(list(data.filter(regex='RowFrontGTI')))]
db = data[(list(data.filter(regex='RowBackGTI')))]

# Stripping names so that I can easily add them
df.columns = [col.strip('_RowFrontGTI') for col in df.columns]
db.columns = [col.strip('_RowBackGTI') for col in db.columns]


# ## 3.  Calculate the Panel Irradiance Input (Front + rear * bifaciality Factor)

# In[7]:


irradiances = df+db*bififactor
irradiances


# ## 4. Calculate a sample module performance to know the yearly derate. 
# This is a proxy for the collector 

# In[8]:


#CEC Parameters for the modules desired can be used here, and can be found through SAM, pvlib, or the California CEC database.

CECMod_longi_df = pd.DataFrame({'alpha_sc': 0.0038991, 'a_ref': 1.78308, 'I_L_ref': 9.51892,'I_o_ref': 2.03E-11, 'R_sh_ref': 411.557, 'R_s': 0.386111,'Adjust': 7.35293}, index=[0])


# In[9]:


# Calculate a reference power using bifacial radiance internal methods
# This corrects for Temperature and Wind
power_ref = br.performance.calculatePerformance(
    irradiances.sum(axis=1),temp_air=data['Tamb'],wind_speed=data['VWind'],
    CECMod=CECMod_longi_df)


# ## 5. Calculate Hourly Mismatch with bifacial radiance internal equation fit

# In[10]:


hourlymismatch=br.mismatch.mismatch_fit3(irradiances.T)/100
#Clipping mismatch for edge cases
hourlymismatch[hourlymismatch>5]=5


# In[11]:


# Calculate power reduction
powerreduced = power_ref*(100-hourlymismatch)/100

# This is the Yearly Mismatch then:
YEARLYMismatch = (power_ref.sum()-powerreduced.sum())*100/power_ref.sum()


# ## 6. Convert the Yearly Mismatch to the Mismatch Loss Factor from PVSyst
# 
# Follows the same journal procedure. ANotehr visual explanation on the slides and poster for the same journal:
# 
#     https://www.nrel.gov/docs/fy19osti/74831.pdf
#     https://www.nrel.gov/docs/fy19osti/74236.pdf

# In[12]:


# Need to calculate hte bifacial gain first:
BifacialGain = db.mean(axis=1).sum()*bififactor*100/df.mean(axis=1).sum()
BifacialGain

PVSyst_Mismatch = YEARLYMismatch/BifacialGain + YEARLYMismatch
print("PVSyst Mismatch applied to Grear", np.round(PVSyst_Mismatch,2))


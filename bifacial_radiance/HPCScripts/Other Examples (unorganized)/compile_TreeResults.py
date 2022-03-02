# -*- coding: utf-8 -*-
"""
mkdir /scratch/sayala/RadianceScenes/Full_Row_40Mods/outputanalysis
mkdir /scratch/sayala/RadianceScenes/Full_Row_40Mods/outputanalysis/dataframes_Gpoat
mkdir /scratch/sayala/RadianceScenes/Full_Row_40Mods/outputanalysis/dataframes_Gfront

"""

# In[1]:
# This section collects the cell by cell irradiance calculated by bifacial_radiance
# into an hourly pickle in format "  irr_1axis_01_01_08.csv "
# and stores them in a folder (i.e. hourly_dataframes_row_FrontOnly)
# It also accumulates up the cell by cell irradiances into a yearly irradiance pickle
# at the end and plots it.
# Each dataframe/pickle has module 20 (Northmost) as the first row (So if you're
# seeing the data it's like you're seeing the array from a top-down view. 
# Note that this is not the way that dataframes get plotted in python so it needs
# to be inverted later for plotting. UGH.)

import os
import pandas as pd
import re
import numpy as np
#from collections import Counter

# Where the 500k results are stored:
savefolder = r'/scratch/sayala/JORDAN/'


# irr_Coffee_ch_1.8_xgap_0.6_tilt_18_pitch_1.6_Front&Back.csv

ch_all = []
xgap_all = []
tilt_all = []
pitch_all = []
NorthIrrad = []
SouthIrrad = []
EastIrrad = []
WestIrrad = []


ft2m = 0.3048
clearance_heights = np.array([6.0, 8.0, 10.0])* ft2m
xgaps = np.array([2, 3, 4]) * ft2m
Ds = np.array([2, 3, 4]) * ft2m    # D is a variable that represents the spacing between rows, not-considering the collector areas.
tilts = [18, 10]
y = 1



for ch in range (0, len(clearance_heights)):
    
    clearance_height = clearance_heights[ch]
    for xx in range (0, len(xgaps)):
        
        xgap = xgaps[xx]

        for tt in range (0, len(tilts)):
        
            tilt = tilts[tt]
            for dd in range (0, len(Ds)):
                pitch = y * np.cos(np.radians(tilt))+Ds[dd]


                folder_name = ('CH_'+str(clearance_height)+
                            '_xgap_'+str(xgap)+\
                            '_tilt_'+str(tilt)+
                            '_pitch_'+str(pitch))

                testfolder = os.path.join(r'/scratch/sayala/JORDAN/PUERTO_RICO/', folder_name)
                resultsfolder = os.path.join(testfolder, 'results')

                sim_name = ('irr_Coffee'+'_ch_'+str(round(clearance_height,1))+
                                '_xgap_'+str(round(xgap,1))+\
                                '_tilt_'+str(round(tilt,1))+
                                '_pitch_'+str(round(pitch,1))+'_North&South.csv')

                sim_name2 = ('irr_Coffee'+'_ch_'+str(round(clearance_height,1))+
                                '_xgap_'+str(round(xgap,1))+\
                                '_tilt_'+str(round(tilt,1))+
                                '_pitch_'+str(round(pitch,1))+'_East&West.csv')

                ch_all.append(clearance_height)
                xgap_all.append(xgap)
                tilt_all.append(tilt)
                pitch_all.append(pitch)
                data = pd.read_csv(os.path.join(resultsfolder, sim_name))
                NorthIrrad.append(data['Wm2Front'].item())
                SouthIrrad.append(data['Wm2Back'].item())
                data = pd.read_csv(os.path.join(resultsfolder, sim_name2))
                EastIrrad.append(data['Wm2Front'].item())
                WestIrrad.append(data['Wm2Back'].item())


ch_all = pd.Series(ch_all, name='clearance_height')
xgap_all = pd.Series(xgap_all, name='xgap')
tilt_all = pd.Series(tilt_all, name='tilt')
pitch_all = pd.Series(pitch_all, name='pitch')
NorthIrrad = pd.Series(NorthIrrad, name='NorthIrrad')
SouthIrrad = pd.Series(SouthIrrad, name='SouthIrrad')
EastIrrad = pd.Series(EastIrrad, name='EastIrrad')
WestIrrad = pd.Series(WestIrrad, name='WestIrrad')

df = pd.concat([ch_all, xgap_all, tilt_all, pitch_all, NorthIrrad, SouthIrrad, EastIrrad, WestIrrad], axis=1)
df.to_csv(os.path.join(savefolder,'TREES.csv'))


print("FINISHED")
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
import bisect
#from collections import Counter

# Where the 500k results are stored:
savefolder=r'/scratch/sayala/JORDAN/'

case = 'CaseC'

if case == 'Case0':
    testfolder=r'/scratch/sayala/JORDAN/JackSolar_Hourly/'
    savefolderGrear=r'/scratch/sayala/JORDAN/dataframes_Grear/'
    savefolderGground=r'/scratch/sayala/JORDAN/dataframes_Gground/'
    savefolderfront =r'/scratch/sayala/JORDAN/dataframes_Gfront'

if case == 'CaseA':
    testfolder=r'/scratch/sayala/JORDAN/JackSolar_CaseA/'
    savefolderGrear=r'/scratch/sayala/JORDAN/dataframes_Grear_CaseA/'
    savefolderGground=r'/scratch/sayala/JORDAN/dataframes_Gground_CaseA/'
    savefolderfront =r'/scratch/sayala/JORDAN/dataframes_Gfront_CaseA'

if case == 'CaseB':
    testfolder=r'/scratch/sayala/JORDAN/JackSolar_CaseB/'
    savefolderGrear=r'/scratch/sayala/JORDAN/dataframes_Grear_CaseB/'
    savefolderGground=r'/scratch/sayala/JORDAN/dataframes_Gground_CaseB/'
    savefolderfront =r'/scratch/sayala/JORDAN/dataframes_Gfront_CaseB'

if case == 'CaseC':
    testfolder=r'/scratch/sayala/JORDAN/JackSolar_CaseC/'
    savefolderGrear=r'/scratch/sayala/JORDAN/dataframes_Grear_CaseC/'
    savefolderGground=r'/scratch/sayala/JORDAN/dataframes_Gground_CaseC/'
    savefolderfront =r'/scratch/sayala/JORDAN/dataframes_Gfront_CaseC'


savefolder = r'/scratch/sayala/JORDAN/'



filelist = sorted(os.listdir(testfolder))
print('{} files in the directory'.format(filelist.__len__()))
#print(filelist[1].partition('_Module_')[0])
hourlist = [x[5:] for x in filelist]

samp='/scratch/sayala/JORDAN/JackSolar_Hourly/Hour_12/results/irr_xloc_0.csv'
# Reading the valuesf or the row array and storing them in dataframes/pickles
a = np.zeros(shape=(22, 105))
df = pd.DataFrame(a)
df_GroundOnly = pd.DataFrame(a)

frontirrad = 0
newdf = True

starts = [2881, 3626, 4346, 5090, 5835]
ends = [3621, 4341, 5085, 5829, 6550]

frontirrads_all = []

for mm in range(0, len(starts)):

    lower_bound = starts[mm]
    upper_bound = ends[mm]
    l = list(map(int, hourlist))
    lower_bound_i = bisect.bisect_left(l, lower_bound)
    upper_bound_i = bisect.bisect_right(l, upper_bound, lo=lower_bound_i)
    subhourlist = l[lower_bound_i:upper_bound_i]

    frontirrad = 0
    newdf = True

    for i in range(0, len(subhourlist)):
        hourfoo = subhourlist[i]
    #for i in range(12,14):
        print("Working on Hour "+str(hourfoo))
        resfolder = os.path.join(testfolder, 'Hour_'+str(hourfoo))
        resfolder = os.path.join(resfolder, 'results/')
        print(resfolder)
        A = sorted(os.listdir(resfolder))
        if len(A) != 0:
            
            rowarray_Grear=[]
            rowarray_Ground=[]

            for ii in range (0, 22):
                filename = 'irr_xloc_'+str(ii)+'.csv'
                data = pd.read_csv(os.path.join(resfolder,filename))
                groundirrad = list(data['Wm2Front'])
                rowarray_Ground.append(groundirrad)

                rearirrad = list(data['Wm2Back'])
                rowarray_Grear.append(rearirrad)
            
            rowarray_Grear=pd.DataFrame(rowarray_Grear)
            resfmt = 'irr_1axis_Hour_{}.pkl'.format(f'{i:04}')
            if newdf: 
                df_all_Grear = rowarray_Grear
            else:
                df_all_Grear = df_all_Grear+rowarray_Grear

            rowarray_Ground=pd.DataFrame(rowarray_Ground)
            if newdf: 
                df_all_Ground = rowarray_Ground
                newdf = False
            else:
                df_all_Ground = df_all_Ground+rowarray_Ground
            
            # Read the 1 front file and compile values
            filename = 'irr_frontSide.csv'
            data = pd.read_csv(os.path.join(resfolder,filename))
            frontirrad = frontirrad + data['Wm2Front']

    compiledsavenameGround = 'All_Ground_'+case+'_month_'+str(mm)+'.csv'
    compiledsavenameGrear = 'All_Grear_'+case+'_month_'+str(mm)+'.csv'
    df_all_Ground.to_csv(os.path.join(savefolder,compiledsavenameGround))
    df_all_Grear.to_csv(os.path.join(savefolder,compiledsavenameGrear))

    frontirrads_all.append(frontirrad)
    #print("Frontirrad Month ", mm, frontirrad)

print (frontirrads_all)
print("FINISHED")
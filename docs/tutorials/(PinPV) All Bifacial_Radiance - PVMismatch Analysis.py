#!/usr/bin/env python
# coding: utf-8

# # (PinPV) All Bifacial_Radiance - PVMismatch Analysis
# 
# ### Uses HPC runs, and bifacial_radiance_master_EUPVSEC branch for the analysis function
# started on 08/10/19
# 
# 
# ANALYSIS Runs include:
# <ul>
#     <li> <a href='#df3_Tracking'>df3_Tracking</a></li>
#     <li> <a href='#df4_FixedTilt'>df4_FixedTilt</a></li>
#     <li> <a href='#df4_b_FixedTilt_PortraitMode'>df4_FixedTilt_PortraitMode</a></li>
#     <li> <a href='#df5_TrackingTT'>df5_Tracking_with_TorqueTube</a></li>
#     <li> <a href='#df6_PVPMCRuns'>df6_PVPMCRuns</a></li>
# </ul>

# In[1]:


import bifacial_radiance


# <a id='df3_Tracking'></a>

# ## df3_Tracking

# In[2]:


Cs = ['0.5', '0.75','1', '1.2']
cities = ['Cairo', 'Shanghai', 'Richmond']

basefolder = r'C:\Users\sayala\Documents\HPC_Scratch\EUPVSEC\new_bifacialRadiance_onVF_results\HPCResults'

for i in range (0, len(cities)):
    for j in range(0, len(Cs)):
    
        resultsfolder = basefolder + '\\Tracking_'+cities[i]+'_C_'+Cs[j]+'\\results'
        writefiletitle = basefolder + '\\BifRad_PVMismatch_'+cities[i]+'_C_'+Cs[j]+'.csv'
        sensorsy=100
        portraitorlandscape='portrait'
        bififactor=1.0
        bifacial_radiance.mismatch.analysisIrradianceandPowerMismatch(resultsfolder, writefiletitle, sensorsy, portraitorlandscape, bififactor)


# <a id='df4_FixedTilt'></a>

# ## df4_FixedTilt

# In[4]:


Cs = ['0.15', '0.25', '0.5', '0.75','1']
cities = ['Cairo', 'Shanghai', 'Richmond']

basefolder = r'C:\Users\sayala\Documents\HPC_Scratch\EUPVSEC\new_bifacialRadiance_onVF_results\HPCResults\FixedTilt'

for i in range (0, len(cities)):
    for j in range(0, len(Cs)):
    
        resultsfolder = basefolder + '\\FixedTilt_'+cities[i]+'_C_'+Cs[j]+'\\results'
        writefiletitle = basefolder + '\\BifRad_PVMismatch_FixedTilt_Landscape_'+cities[i]+'_C_'+Cs[j]+'.csv'
        sensorsy=100
        portraitorlandscape='landscape'
        bififactor=1.0
        bifacial_radiance.mismatch.analysisIrradianceandPowerMismatch(resultsfolder, writefiletitle, sensorsy, portraitorlandscape, bififactor)


# <a id='df4_b_FixedTilt_PortraitMode'></a>

# ## df4_b_FixedTilt_PortraitMode
# 

# In[ ]:


Cs = ['0.15', '0.25', '0.5', '0.75','1']
cities = ['Cairo', 'Shanghai', 'Richmond']

basefolder = r'C:\Users\sayala\Documents\HPC_Scratch\EUPVSEC\new_bifacialRadiance_onVF_results\HPCResults\FixedTilt'

for i in range (0, len(cities)):
    for j in range(0, len(Cs)):
    
        resultsfolder = basefolder + '\\FixedTilt_'+cities[i]+'_C_'+Cs[j]+'\\results'
        writefiletitle = basefolder + '\\BifRad_PVMismatch_FixedTilt_Portrait_'+cities[i]+'_C_'+Cs[j]+'.csv'
        sensorsy=100
        portraitorlandscape='Portrait'
        bififactor=1.0
        bifacial_radiance.mismatch.analysisIrradianceandPowerMismatch(resultsfolder, writefiletitle, sensorsy, portraitorlandscape, bififactor)


# <a id='df5_TrackingTT'></a>

# ## df5_TrackingTT

# In[2]:


Cs = ['0.5', '0.75','1', '1.2']
cities = ['Cairo', 'Shanghai', 'Richmond']

basefolder = r'C:\Users\sayala\Documents\HPC_Scratch\EUPVSEC\new_bifacialRadiance_onVF_results\HPCResults\df5_TrackingTT'

for i in range (0, len(cities)):
    for j in range(0, len(Cs)):
    
        resultsfolder = basefolder + '\\Tracking_'+cities[i]+'_C_'+Cs[j]+'\\results'
        writefiletitle = basefolder + '\\BifRad_PVMismatch_TrackingTT_'+cities[i]+'_C_'+Cs[j]+'.csv'
        sensorsy=100
        portraitorlandscape='portrait'
        bififactor=1.0
        bifacial_radiance.mismatch.analysisIrradianceandPowerMismatch(resultsfolder, writefiletitle, sensorsy, portraitorlandscape, bififactor)


# <a id='df6_PVPMCRuns'></a>

# ## df6_PVPMCRuns
# 
# 

# <div class="alert alert-block alert-info">
# <b>Not doing runs >11</b> because those have y-gap and 2 modules, and analysis function only considers 1 module at the moment.

# In[5]:


cities = ['Cairo', 'Shanghai', 'Richmond']
runs = (['0', '1', '1b', '2', '3', '4', '5', '6', '7', '8', '9', '10'])

# Format of how the resultfolders are stored is a bit different. Example:
# r'C:\Users\sayala\Documents\HPC_Scratch\EUPVSEC\PVPMC_Tracking Results\CAIRO\Bifacial_Radiance Results\PVPMC_0\results'
basefolder = r'C:\Users\sayala\Documents\HPC_Scratch\EUPVSEC\PVPMC_Tracking Results'

for i in range (1, len(cities)): #0, len(cities)):
    for j in range(2, len(runs)): # 0, len(runs)):
    
        resultsfolder = basefolder + '\\'+cities[i]+'\\Bifacial_Radiance Results\\PVPMC_'+runs[j]+'\\results'
        writefiletitle = basefolder + '\\BifRad_PVMismatch_PVPMCRuns_'+cities[i]+'_'+runs[j]+'.csv'
        sensorsy=100
        portraitorlandscape='portrait'
        bififactor=1.0
        bifacial_radiance.mismatch.analysisIrradianceandPowerMismatch(resultsfolder, writefiletitle, sensorsy, portraitorlandscape, bififactor)


# In[6]:


cities = ['Cairo', 'Shanghai', 'Richmond']
runs = (['0', '1', '1b', '2', '3', '4', '5', '6', '7', '8', '9', '10'])

# Format of how the resultfolders are stored is a bit different. Example:
# r'C:\Users\sayala\Documents\HPC_Scratch\EUPVSEC\PVPMC_Tracking Results\CAIRO\Bifacial_Radiance Results\PVPMC_0\results'
basefolder = r'C:\Users\sayala\Documents\HPC_Scratch\EUPVSEC\PVPMC_Tracking Results'

for i in range (2, len(cities)): #0, len(cities)):
    for j in range(0, 2): #2, len(runs)): # 0, len(runs)):
    
        resultsfolder = basefolder + '\\'+cities[i]+'\\Bifacial_Radiance Results\\PVPMC_'+runs[j]+'\\results'
        writefiletitle = basefolder + '\\BifRad_PVMismatch_PVPMCRuns_'+cities[i]+'_'+runs[j]+'.csv'
        sensorsy=100
        portraitorlandscape='portrait'
        bififactor=1.0
        bifacial_radiance.mismatch.analysisIrradianceandPowerMismatch(resultsfolder, writefiletitle, sensorsy, portraitorlandscape, bififactor)


# In[ ]:





# ## Sanity Check Richmond take 2

# In[2]:


Cs = ['0.15']
cities = ['Richmond']
i = 0; j=0

basefolder = r'C:\Users\sayala\Documents\HPC_Scratch\EUPVSEC\SanityCheck_Richmond\FixedTilt_Richmond_C_0.15'


resultsfolder = basefolder + '\\results'
writefiletitle = basefolder + '\\BifRad_PVMismatch_FixedTilt_Landscape_'+cities[i]+'_C_'+Cs[j]+'_REDO.csv'
sensorsy=100
portraitorlandscape='landscape'
bififactor=1.0
bifacial_radiance.mismatch.analysisIrradianceandPowerMismatch(resultsfolder, writefiletitle, sensorsy, portraitorlandscape, bififactor)


# # Test of new Faster Routine for analysis (df4)
# 

# In[3]:


Cs = ['0.15', '0.25', '0.5', '0.75','1']
cities = ['Cairo', 'Shanghai', 'Richmond']

basefolder = r'C:\Users\sayala\Documents\HPC_Scratch\EUPVSEC\PinPV_Bifacial_Radiance_Runs\HPCResults\df4_FixedTilt'
    
for i in range (0, len(cities)):
    for j in range(0, len(Cs)):
    
        resultsfolder = basefolder + '\\FixedTilt_'+cities[i]+'_C_'+Cs[j]+'\\results'
        writefiletitle = basefolder + '\\BifRad_PVMismatch_FixedTilt_Landscape_'+cities[i]+'_C_'+Cs[j]+'.csv'
        portraitorlandscape='landscape'
        bififactor=1.0
        bifacial_radiance.mismatch.analysisIrradianceandPowerMismatch(resultsfolder, writefiletitle, portraitorlandscape, bififactor)


# 

# ## Sanity Check Cairo , H = 0.15, 5 rows only!

# In[2]:



resultsfolder = r'C:\Users\sayala\Documents\HPC_Scratch\EUPVSEC\SanityCheck_Cairo_5Rws\results'
writefiletitle = resultsfolder + '\\BifRad_PVMismatch_FixedTilt_Landscape_Cairo_C_0.15_5nRows.csv'
sensorsy=100
portraitorlandscape='landscape'
bififactor=1.0
numcells=72
downsamplingmethod='byAverage'
bifacial_radiance.mismatch.analysisIrradianceandPowerMismatch(testfolder=resultsfolder, writefiletitle=writefiletitle, portraitorlandscape=portraitorlandscape, bififactor=bififactor, numcells=numcells, downsamplingmethod=downsamplingmethod)


# In[3]:


print("HEllo")


# In[ ]:





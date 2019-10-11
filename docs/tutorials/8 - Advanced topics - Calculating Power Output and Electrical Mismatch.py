#!/usr/bin/env python
# coding: utf-8

# # 8 - Advanced topics - Calculating Power Output and Electrical Mismatch
# 
# Nonuniform rear-irradiance on bifacial PV systems can cause additional mismatch loss, which may not be appropriately captured in PV energy production estimates and software.
# 
# <img src="..\images_wiki\AdvancedJournals\Mismatch_Definition_Example.PNG" width="600">
# 
# The **analysis.py** module in bifacial_radiance comes with functions to calculate power output, electrical mismatch, and some other irradiance calculations. This is the procedure used for this proceedings and submitted journals, which have much more detail on the procedure. 
# 
#         •	Deline, C., Ayala Pelaez, S., MacAlpine, S., Olalla, C. Estimating and Parameterizing Mismatch Power Loss in Bifacial Photovoltaic Systems. (submitted Progress in PV on Sept. 30, 2019)
# 
#         •	Deline C, Ayala Pelaez S, MacAlpine S, Olalla C. Bifacial PV System Mismatch Loss Estimation & Parameterization. Presented in: 36th EU PVSEC, Marseille Fr. Slides: https://www.nrel.gov/docs/fy19osti/74885.pdf. Proceedings: https://www.nrel.gov/docs/fy20osti/73541.pdf
# 
#         •	Ayala Pelaez S, Deline C, MacAlpine S, Olalla C. Bifacial PV system mismatch loss estimation. Poster presented at the 6th BifiPV Workshop, Amsterdam 2019. https://www.nrel.gov/docs/fy19osti/74831.pdf and http://bifipv-workshop.com/index.php?id=amsterdam-2019-program 
# 
# Ideally **mismatch losses M** should be calculated for the whole year, and then the **mismatch loss factor to apply to Grear "Lrear"** required by due diligence softwares can be calculated:
# 
# <img src="..\images_wiki\AdvancedJournals\Lrear_solving.PNG" width="400">
# 
# In this journal we will explore calculating mismatch loss M for a reduced set of hours. A procedure similar to that in Tutorial 3 will be used to generate various hourly irradiance measurements in the results folder, which the mismatch.py module will load and analyze. Analysis is done with PVMismatch, so this must be installed.
# 
# ## STEPS:
#     1. Run an hourly simulation
#     2. Do mismatch analysis on the results.
# 
# 

# <a id='step1'></a>

# ### 1. Run an hourly simulation
# 
# This will generate the results over which we will perform the mismatch analysis

# In[ ]:


import bifacial_radiance
import os 

simulationName = 'Tutorial 8'
testfolder = os.path.abspath(r'..\..\bifacial_radiance\TEMP')
moduletype = "Canadian Solar"
albedo = 0.25 
lat = 37.5   
lon = -77.6

# Scene variables
nMods = 20
nRows = 7
hub_height = 1.5 # meters
gcr = 0.33

# Traking parameters
cumulativesky = False
limit_angle = 60 
angledelta = 0.01 
backtrack = True 

#makeModule parameters
x = 1
y = 2
xgap = 0.01
zgap = 0.05
ygap = 0.0  # numpanels=1 anyways so it doesnt matter anyway
numpanels = 1
torquetube = True
axisofrotationTorqueTube = True
diameter = 0.1
tubetype = 'Oct'    
material = 'black'

startdate = '11/06'     
enddate = '11/06'
demo = bifacial_radiance.RadianceObj(simulationName, path=testfolder)  
demo.setGround(albedo) 
epwfile = demo.getEPW(lat,lon) 
metdata = demo.readWeatherFile(epwfile) 
mymodule = demo.makeModule(name=moduletype, torquetube=torquetube, diameter=diameter, tubetype=tubetype, material=material, 
                x=x, y=y, xgap=xgap, ygap = ygap, zgap=zgap, numpanels=numpanels, 
                axisofrotationTorqueTube=axisofrotationTorqueTube)
pitch = mymodule['sceney']/gcr
sceneDict = {'pitch':pitch,'hub_height':hub_height, 'nMods': nMods, 'nRows': nRows}  
demo.set1axis(limit_angle = limit_angle, backtrack = backtrack, gcr = gcr, cumulativesky = cumulativesky)
demo.gendaylit1axis(startdate=startdate, enddate=enddate)
demo.makeScene1axis(moduletype=moduletype,sceneDict=sceneDict) 
demo.makeOct1axis()
demo.analysis1axis()


# In[ ]:


testfolder =  r'C:\Users\sayala\Documents\HPC_Scratch\EUPVSEC\new_bifacialRadiance_onVF_results\HPCResults'
writefiletitle = r'C:\Users\sayala\Documents\HPC_Scratch\EUPVSEC\new_bifacialRadiance_onVF_results\Mismatch_Results.csv'

        sensorsy=100
        portraitorlandscape='portrait'
        bififactor=1.0
bifacial_radiance.mismatch.analysisIrradianceandPowerMismatch(resultsfolder, writefiletitle, sensorsy, portraitorlandscape, bififactor)


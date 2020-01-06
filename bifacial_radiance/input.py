# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 09:22:46 2019

@author: sayala

Input values for 
"""

# Input/Output file addresses
testfolder = 'TEMP'  # AWS
epwfile = r'EPWs\USA_WY_Jackson.Hole.AP.725776_TMY3.epw' # AWS
# Input/Output file addresses
#testfolder = '/scratch/sayala/RadianceScenes/Foo' 
#epwfile='/scratch/sayala/EPWs/EGY_Cairo.Intl.Airport.623660_ETMY.epw'

simulationname='EUPVSEC'
moduletype = 'EUPVSEC'
hub_height = 1.5
numpanels = 1
torqueTube = False
tubetype='Round'
pitch = 6 # gcr - 0.25
albedo = 0.2     # ground albedo
gcr=0.3333

limit_angle = 60 
diameter = 0.0
xgap=0.01 # 10 centimeters default
ygap=0.0
zgap = 0.0
sensorsy=100

# Variables that don't change
x= 1
y= 2  # module portrait dimension in meters
nMods=20
nRows=7
torqueTubeMaterial='Metal_Grey'
backtrack = True
cumulativesky = False
rewriteModule=True
cellLevelModule = False
hpc=True       
axisofrotationTorqueTube=False
modWanted = 10
rowWanted = 4
axis_azimuth=180
angledelta=0.01
roundTrackerAngle= True
bifi=0.9



torqueTube = True
diameter = 0.10
zgap = 0.05
moduletype = 'EUPVSEC_TT'
torqueTubeMaterial = 'black'
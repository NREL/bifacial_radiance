# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 09:22:46 2019

@author: sayala

Input values for 
"""

# Input/Output file addresses
#TMYfile='EPWs\\724010TYA.CSV'
testfolder = '/scratch/sayala/RadianceScenes/Test1'
epwfile='/scratch/sayala/EPWs/USA_VA_Richmond.Intl.AP.724010_TMY.epw'
simulationname = 'TestHPC1'
moduletype = 'Longi'

# Control Variables
cumulativesky=False
rewriteModule=True
hpc=True

# Scene Variables 
gcr = 0.35   # ground cover ratio,  = module_height / pitch
albedo = 0.3     # ground albedo
nMods = 20  # replicating the unit 3 times
nRows = 7  # only 1 row

# Analysis Variabls
sensorsy = 210  # this will give 70 sensors per module.
modWanted = 10
rowWanted = 3

# Fixed tilt variables
azimuth_ang=180 # Facing south
tilt =20 # tilt. 

# Tracker geometry options
backtrack = True
hub_height = 2   # tracker height at 0 tilt in meters (hub height)
limit_angle = 45 # tracker rotation limit angle
axis_azimuth=180
angledelta=5


# ModuleDict Variables
numpanels = 1
x=0.984  
y = 1.996
bifi=0.9
xgap = 0.01 # 10 centimeters.
ygap = 0.0
zgap = 0.1

# TorqueTube Parameters
torqueTube = True
axisofrotationTorqueTube=False
diameter=0.1
tubetype='Round'
torqueTubeMaterial='Metal_Grey'

# Cell Level Module Parameters
cellLevelModule = False
numcellsx=10
numcellsy=6
xcell=0.156
ycell=0.156
xcellgap=0.02
ycellgap=0.02




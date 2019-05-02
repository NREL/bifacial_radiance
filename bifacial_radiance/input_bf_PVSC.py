# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 09:22:46 2019

@author: sayala

Input values for 
"""

# Input/Output file addresses
testfolder = '/scratch/sayala/RadianceScenes/Richmond_TorqueTube'
epwfile='/scratch/sayala/EPWs/USA_VA_Richmond.Intl.AP.724010_TMY.epw'

x=0.991
y = 1.996  # module portrait dimension in meters
gcr = 0.35   # ground cover ratio,  = module_height / pitch
albedo = 0.3     # ground albedo
hub_height = 1.5   # NREL hub height is 5'1" at 0 tilt in meters (hub height)
limit_angle = 45 # tracker rotation limit angle
cumulativesky = False
backtrack = True
simulationname='Cairo_1up'
moduletype = 'Longi'
diameter = 0.13
zgap = 0.1
nMods=20
nRows=7
sensorsy=120
torqueTube = True


# Control Variables
rewriteModule=True
cellLevelModule = False
hpc=True        # On XandY branch, this allows to use the 'daydate' to restrict gendaylit1axis to 1 day if daydate is passed.
axisofrotationTorqueTube=False

#Time control variables - Depending on simulation run, control variables for time:
timestampstart = 4020 # max is like 8760 for each hour in a weather file. For use with gendaylit
timestampend = 4024
#startdate and enddate slice from hour start to hour end for the days selected. For use with gencumsky
singlekeystart = '01_01_11' # For use with gendaylit1axis for 1 single key in the trackerdict. (all ~4000 .rad still get generated though)
singlekeyend = '01_01_15'
daydate = '02_18' # month _ day. This restricts EPW for gendaylit1axis to 1 day (trackerdict, .rad, .oct and .cal generated only for that day)

# Analysis Variables
modWanted = 11
rowWanted = 4

# Fixed tilt Scene variables
azimuth_ang=180 # Facing south
tilt =20 # tilt. 
clearance_height = 0.5

# Tracker geometry options
axis_azimuth=180
angledelta=0.01
roundTrackerAngle= True

# TorqueTube Parameters
tubetype='Round'
torqueTubeMaterial='Metal_Grey'

# ModuleDict Variables
numpanels = 1
bifi=0.9
xgap=0.01 # 10 centimeters.
ygap=0.0
zgap=0.1

# Cell Level Module Parameters
numcellsx=10
numcellsy=6
xcell=0.156
ycell=0.156
xcellgap=0.02
ycellgap=0.02

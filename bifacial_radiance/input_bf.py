# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 09:22:46 2019

@author: sayala

Input values for 
"""

import datetime

# Input/Output file addresses
#TMYfile='EPWs\\724010TYA.CSV'
testfolder = '/scratch/sayala/RadianceScenes/Test1'
epwfile='/scratch/sayala/EPWs/USA_VA_Richmond.Intl.AP.724010_TMY.epw'
simulationname = 'TestHPC1'
moduletype = 'Longi'

# Control Variables
cumulativesky=False
rewriteModule=True
cellLevelModule = False
hpc=True        # On XandY branch, this allows to use the 'daydate' to restrict gendaylit1axis to 1 day if daydate is passed.
torqueTube = True
axisofrotationTorqueTube=False

#Time control variables - Depending on simulation run, control variables for time:
timestampstart = 4020 # max is like 8760 for each hour in a weather file. For use with gendaylit
timestampend = 4024
#startdate and enddate slice from hour start to hour end for the days selected. For use with gencumsky
startdate= datetime.datetime(2001, 11, 06, 11)     # Year (ignored) Month, day, hour           # Gencumsky startdate
enddate= datetime.datetime(2001, 11, 07, 13)       # Year (ignored) Month, day, hour           # Gencumsky enddate
singlekeystart = '01_01_11' # For use with gendaylit1axis for 1 single key in the trackerdict. (all ~4000 .rad still get generated though)
singlekeyend = '01_01_15'
daydate = '02_18' # month _ day. This restricts EPW for gendaylit1axis to 1 day (trackerdict, .rad, .oct and .cal generated only for that day)

# Analysis Variables
sensorsy = 210  # this will give 70 sensors per module.
modWanted = 10
rowWanted = 3

# Fixed tilt Scene variables
azimuth_ang=180 # Facing south
tilt =20 # tilt. 
clearance_height = 0.5

# Tracking Scene Variables
hub_height = 2   # tracker height at 0 tilt in meters (hub height)

# Tracker geometry options
limit_angle = 45 # tracker rotation limit angle
axis_azimuth=180
angledelta=5
backtrack = True
roundTrackerAngle= True

# TorqueTube Parameters
diameter=0.1
tubetype='Round'
torqueTubeMaterial='Metal_Grey'

# ModuleDict Variables
numpanels = 1
x=0.984  
y=1.996
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

# Scene Variables 
gcr = 0.35   # ground cover ratio,  = collector_width / pitch  (collector width is calculated in makeModule and saved as self.sceney or scene.sceney)
albedo = 0.3     # ground albedo
nMods = 20  # replicating the unit 3 times
nRows = 7  # only 1 row

# Calculated Varaibles for ModuleDict and SceneDict:
if cellLevelModule==True:
    x = numcellsx*xcell + (numcellsx-1)*xcellgap
    y = numcellsy*ycell + (numcellsy-1)*ycellgap
scenex= x+xgap
sceney= y*numpanels + ygap*(numpanels-1)
scenez= zgap+diameter/2.0
moduleoffset = 0
if axisofrotationTorqueTube == True:
    modoffset = zgap + diameter/2.0
pitch = round(scenexy/gcr,3)      # pitch = collectorWidth / gcr , but collector widh gets specified later

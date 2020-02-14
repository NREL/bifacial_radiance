# -*- coding: utf-8 -*-

# Case 1, AUSTRALIA
testfolder = 'TEMP\HPC1'  # AWS
epwfile = r'C:\Users\sayala\Documents\GitHub\bifacial_radiance\bifacial_radiance\TEMP\EPWs\Site1.epw' # AWS

simulationName = 'Case_1'    # For adding a simulation name when defning RadianceObj. This is optional.
moduletype = 'Custom-Module'    # We will define the parameters for this below in Step 4.
lat = -34.91
lon = 146.60

# Scene variables
nMods = 20
nRows = 7
hub_height = 1.3 # meters
gcr = 0.305
albedo = 0.2         
bifi = 0.8

# Traking parameters
cumulativesky = False
limit_angle = 52 # 72.1 # tracker rotation limit angle
angledelta = 0.01 # we will be doing hourly simulation, we want the angle to be as close to real tracking as possible.
backtrack = True 
axisofrotationTorqueTube = False

#Torquetube Params
torqueTube = False
diameter = 0.1
tubetype = 'round'    # This will make an octagonal torque tube.
torqueTubeMaterial = 'black'   # Torque tube of this material (0% reflectivity)
zgap = 0

#makeModule parameters
x = 1
y = 1.98
xgap = 0.01
ygap = 0
numpanels = 1
axis_azimuth = 187 

sensorsy = 9
sensorsy =100 # HPC Value
sensorsy = 2
hpc = True
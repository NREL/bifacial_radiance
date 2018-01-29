'''
 ## 1-Axis tracker example including bifacialVF
 
 Example demonstrating Radiance gencumulativesky for 1-axis tracking and bifacialvf.
 
 #### Prerequisites (Step 0):
 bifacial_radiance requires the previous installation of RADIANCE from https://github.com/NREL/Radiance/releases.
 
 During installation, select "add radiance to the system PATH" so Python can interact with the radiance program

 
 #### STEP 1: Install and import bifacial_radiance
 
  - clone the github.com/cdeline/bifacial_radiance repo to your local directory
  - navigate to the /bifacial_radiance/ directory which contains setup.py
  - run `pip install -e .  `  ( the period . is required, the -e flag is optional and installs in development mode where changes to the bifacial_radiance.py files are immediately incorporated into the module if you re-start the python kernel)
 
 #### STEP 2: Move gencumulativesky.exe
 Copy gencumulativesky.exe from the repo's `/bifacial_radiance/data/` directory and copy into your Radiance install directory.
 This is typically found in `/program files/radiance/bin/`.  
 
 #### STEP 3: Create a local Radiance directory for storing the scene files created
 Keep scene geometry files separate from the bifacial_radiance directory.  Create a local directory somewhere that will be referenced in the next step.
 
 #### STEP 4: Install bifacialvf
  - clone the github.com/cdeline/bifacialvf repo to your local directory
  - navigate to the /bifacialvf directory which contains setup.py
  - run `pip install -e .  `  ( the period . is required, the -e flag is optional and installs in development mode where changes to the bifacialvf.py files are immediately incorporated into the module if you re-start the python kernel)
 

 #### STEP 5: Reboot the computer
 This makes sure the PATH is updated
 
''' 
 

## User custom variables (update this)

testfolder = r'C:\Users\cdeline\Documents\Python Scripts\Test1axisFolder'  #point to an empty directory or existing Radiance directory

# tracker geometry options:
module_height = 1.7  # module portrait dimension in meters
gcr = 0.25   # ground cover ratio,  = module_height / pitch
albedo = 0.4     # ground albedo
hub_height = 2   # tracker height at 0 tilt in meters (hub height)
limit_angle = 45 # tracker rotation limit angle
# Import modules

import numpy as np
import datetime   
try:
    from bifacial_radiance import RadianceObj
except ImportError:
    raise RuntimeError('bifacial_radiance is required. download distribution')


print('starting simulation: {}'.format(datetime.datetime.now()))   
# Example 1-axis tracking system using Radiance.  This takes 5-10 minutes to complete, depending on computer.

demo = RadianceObj(path = testfolder)  # Create a RadianceObj 'object' named 'demo'

demo.setGround(albedo) # input albedo number or material name like 'concrete'.  To see options, run this without any input.

epwfile = demo.getEPW(37.5,-77.6) #Pull TMY weather data for any global lat/lon.  In this case, Richmond, VA
    
metdata = demo.readEPW(epwfile) # read in the weather data

# create separate metdata files for each 1-axis tracker angle (5 degree resolution).  
trackerdict = demo.set1axis(metdata, limit_angle = limit_angle, backtrack = True, gcr = gcr)

# create cumulativesky functions for each tracker angle: demo.genCumSky1axis
trackerdict = demo.genCumSky1axis(trackerdict)
# Create a new moduletype: Prism Solar Bi60. width = .984m height = 1.695m. Bifaciality = 0.90
demo.makeModule(name='Prism Solar Bi60',x=0.984,y=module_height,bifi = 0.90)
# print available module types
demo.printModules()

# create a 1-axis scene using panels in portrait, 2m hub height, 0.33 GCR. NOTE: clearance needs to be calculated at each step. hub height is constant
sceneDict = {'pitch': module_height / gcr,'height':hub_height,'orientation':'portrait'}  
module_type = 'Prism Solar Bi60'
trackerdict = demo.makeScene1axis(trackerdict,module_type,sceneDict, nMods = 20, nRows = 7) #makeScene creates a .rad file with 20 modules per row, 7 rows.

trackerdict = demo.makeOct1axis(trackerdict)
# Now we need to run analysis and combine the results into an annual total.  This can be done by calling scene.frontscan and scene.backscan
trackerdict = demo.analysis1axis(trackerdict)

# the frontscan and backscan include a linescan along a chord of the module, both on the front and back.  
# Return the minimum of the irradiance ratio, and the average of the irradiance ratio along a chord of the module.
print('Annual RADIANCE bifacial ratio for 1-axis tracking: %0.3f - %0.3f' %(min(demo.backRatio), np.mean(demo.backRatio)) )


'''
Now run the analysis using bifacialVF !




'''

print('starting VF simulation: {}'.format(datetime.datetime.now()))  

import bifacialvf    # github.com/cdeline/bifacialvf
import os
# change directory to \bifacialvf\ root
os.chdir(os.path.dirname(bifacialvf.__file__))


#2. Set the Values of your test
# Remember all values are normalized to your panel length (slope, which will equal 1).
# If your slope is different than 1 m, desired C and D (or Cv and rtr in tracking case) will need to be 
# divided by the slope length.
# i.e.: panel 1mx1.59m, in portrait mode means slope = 1.59. For a height C of 1m, C = 1/1.59. 
#         For a rtr of 1.5m, D=0.51519/1.59 if beta tilt angle = 10 

# comparison with bifacial_radiance 1-axis tracking.  0.2 albedo, richmond VA location, 1.7m 1-up portrait, 2m height, 5.1m rtr
# normalized to 1 m panel length: rtr = 3; C (hub height) = 1.176 

# Set mandatory variables * SCALED BY MODULE_HEIGHT *

C = hub_height / module_height                      # GroundClearance(panel slope lengths)
rtr = 1.0 / gcr              # normalized to panel length
#D = 0.51519                 # DistanceBetweenRows(panel slope lengths) this is NOT row to row spacing
TMYtoread = "data/724010TYA.csv"   # VA Richmond
TMYtoread = "data/Albuquerque_723650TYA.CSV"   # ABQ

writefiletitle = "data/Output/1Axis.csv"
sazm = 180                  # azimuth of system. For trackers, this is the tracking axis orientation
beta = 0                    # tilt of the system. For trackers, this can be anything

# Set optional variables.  These are the default values
rowType = "interior"        # RowType(first interior last single)
transFactor = 0         # TransmissionFactor(open area fraction)
cellRows = 6                # CellRows(# hor rows in panel)   This is the number of irradiance values returned along module chord
PVfrontSurface = "glass"    # PVfrontSurface(glass or AR glass)
PVbackSurface = "glass"     # PVbackSurface(glass or AR glass)

# 1-axis tracking instructions (optional)
max_angle = 45       # tracker rotation limit angle
backtrack=True       # backtracking optimization as defined in pvlib
#Cv = 0.05                  # GroundClearance when panel is in vertical position for tracking simulations (panel slope lengths)




#3. Call the function.

bifacialvf.simulate(TMYtoread, writefiletitle, beta, sazm, 
                C=C, rowType=rowType, transFactor=transFactor, cellRows=cellRows,
                PVfrontSurface=PVfrontSurface, PVbackSurface=PVbackSurface, albedo=albedo, 
                tracking=True, backtrack=backtrack, rtr=rtr, max_angle = max_angle)
    



#4. Load the results from the resultfile
(data, metadata) = bifacialvf.loadVFresults(writefiletitle)
#print data.keys()
# calculate average front and back global tilted irradiance across the module chord
data['GTIFrontavg'] = data[['No_1_RowFrontGTI', 'No_2_RowFrontGTI','No_3_RowFrontGTI','No_4_RowFrontGTI','No_5_RowFrontGTI','No_6_RowFrontGTI']].mean(axis=1)
data['GTIBackavg'] = data[['No_1_RowBackGTI', 'No_2_RowBackGTI','No_3_RowBackGTI','No_4_RowBackGTI','No_5_RowBackGTI','No_6_RowBackGTI']].mean(axis=1)

# Print the annual bifacial ratio
frontIrrSum = data['GTIFrontavg'].sum()
backIrrSum = data['GTIBackavg'].sum()
print('Done! {}'.format(datetime.datetime.now()))  
print('The VF bifacial ratio for ground clearance {} and row to row {} is: {:.1f}%'.format(C,rtr,backIrrSum/frontIrrSum*100))



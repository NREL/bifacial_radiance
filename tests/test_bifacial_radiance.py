# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 10:08:25 2018

@author: cdeline

Using pytest to create unit tests for bifacial_radiance.

to run unit tests, run pytest from the command line in the bifacial_radiance directory
to run coverage tests, run py.test --cov-report term-missing --cov=bifacial_radiance

"""

from bifacial_radiance import RadianceObj, SceneObj, AnalysisObj
import numpy as np

# test the readepw on a dummy Boulder EPW file in the /tests/ directory
MET_FILENAME =  r'tests\USA_CO_Boulder.724699_TMY2.epw'
# also test a dummy TMY3 Denver file in /tests/
MET_FILENAME2 = r"tests\724666TYA.CSV"

def test_RadianceObj_set1axis():  
    # test set1axis.  requires metdata for boulder. 
    demo = RadianceObj()
    demo.readEPW(epwfile = MET_FILENAME)
    trackerdict = demo.set1axis()
    assert trackerdict[0]['count'] == 108
    assert trackerdict[45]['count'] == 823
   
def test_RadianceObj_fixed_tilt_end_to_end():
    # just run the demo example.  Rear irradiance fraction roughly 11.8% for 0.95m landscape panel
    # takes 12 seconds
    demo = RadianceObj()  # Create a RadianceObj 'object'
    demo.setGround(0.62) # input albedo number or material name like 'concrete'.  To see options, run this without any input.
  
    metdata = demo.readEPW(epwfile= MET_FILENAME) # read in the EPW weather data from above
    #metdata = demo.readTMY() # select a TMY file using graphical picker
    # Now we either choose a single time point, or use cumulativesky for the entire year. 
    fullYear = False
    if fullYear:
        demo.genCumSky(demo.epwfile) # entire year.
    else:
        demo.gendaylit(metdata,4020)  # Noon, June 17th
    # create a scene using panels in landscape at 10 deg tilt, 1.5m pitch. 0.2 m ground clearance
    sceneDict = {'tilt':10,'pitch':1.5,'height':0.2,'orientation':'landscape'}  
    demo.makeModule(name='simple_panel',x=0.95,y=1.59)
    scene = demo.makeScene('simple_panel',sceneDict, nMods = 10, nRows = 3) #makeScene creates a .rad file with 20 modules per row, 7 rows.
    octfile = demo.makeOct(demo.getfilelist())  # makeOct combines all of the ground, sky and object files into a .oct file.
    analysis = AnalysisObj(octfile, demo.name)  # return an analysis object including the scan dimensions for back irradiance
    analysis.analysis(octfile, demo.name, scene.frontscan, scene.backscan)  # compare the back vs front irradiance  
    assert np.round(np.mean(analysis.backRatio),decimals=2) == 0.12  # NOTE: this value is 0.11 when your module size is 1m, 0.12 when module size is 0.95m

def test_RadianceObj_high_azimuth_angle_end_to_end():
    # modify example for high azimuth angle to test different parts of makesceneNxR.  Rear irradiance fraction roughly 17.3% for 0.95m landscape panel
    # takes 14 seconds for sensorsy = 9, 11 seconds for sensorsy = 2
    demo = RadianceObj()  # Create a RadianceObj 'object'
    demo.setGround('white_EPDM') # input albedo number or material name like 'concrete'.  To see options, run this without any input.
  
    #metdata = demo.readEPW() # read in the EPW weather data from above
    metdata = demo.readTMY(MET_FILENAME2) # select a TMY file using graphical picker
    # Now we either choose a single time point, or use cumulativesky for the entire year. 
    fullYear = False
    if fullYear:
        demo.genCumSky(demo.epwfile) # entire year.  # Don't know how to test this yet in pytest...
    else:
        demo.gendaylit(metdata,4020)  # Noon, June 17th
    # create a scene using panels in landscape at 10 deg tilt, 1.5m pitch. 0.2 m ground clearance
    sceneDict = {'tilt':10,'pitch':1.5,'height':0.2,'orientation':'landscape','azimuth':30}  
    demo.makeModule(name='simple_panel',x=0.95,y=1.59)
    scene = demo.makeScene('simple_panel',sceneDict, nMods = 10, nRows = 3) #makeScene creates a .rad file with 20 modules per row, 7 rows.
    octfile = demo.makeOct(demo.getfilelist())  # makeOct combines all of the ground, sky and object files into a .oct file.
    analysis = AnalysisObj(octfile, demo.name)  # return an analysis object including the scan dimensions for back irradiance
    analysis.analysis(octfile, demo.name, scene.frontscan, scene.backscan)  # compare the back vs front irradiance  
    assert np.round(np.mean(analysis.backRatio),2) == 0.20  # bifi ratio was == 0.22 in v0.2.2
    #assert np.round(np.mean(analysis.Wm2Front),decimals=0) == 912  
    #assert np.round(np.mean(analysis.Wm2Back),decimals=0) == 152

def test_RadianceObj_1axis_gendaylit_end_to_end():
    # 1-axis tracking end-to-end test with torque tube and gap generation.  
    # Takes 20 seconds for 2-sensor scan
    module_height = 1.95 * 2 + 0.1  # module portrait dimension in meters
    gcr = 0.35   # ground cover ratio,  = module_height / pitch
    albedo = 0.3     # ground albedo
    hub_height = 2   # tracker height at 0 tilt in meters (hub height)
    
    demo = RadianceObj()  # Create a RadianceObj 'object'
    demo.setGround(albedo) # input albedo number or material name like 'concrete'.  To see options, run this without any input.
    metdata = demo.readEPW(MET_FILENAME) # read in the EPW weather data from above
    #metdata = demo.readTMY(MET_FILENAME2) # select a TMY file using graphical picker
    # create metdata files for each condition. keys are timestamps for gendaylit workflow
    trackerdict = demo.set1axis(cumulativesky = False)
    # create the skyfiles needed for 1-axis tracking
    demo.gendaylit1axis(metdata = metdata, enddate = '01/01')
    # test modules with gap and rear tube
    demo.makeModule(name='Longi_torquetube',x=0.984,y=1.95,torquetube = True, numpanels = 2, panelgap = 0.1)
    #demo.makeModule(name='Longi_torquetube',x=0.984,y=1.95)
    # set module type to be used and passed into makeScene1axis
    module_type = 'Longi_torquetube'
        
    # Create the scene for the 1-axis tracking
    sceneDict = {'pitch': module_height / gcr,'height':hub_height,'orientation':'portrait'}  
    key = '01_01_11'
    demo.makeScene1axis({key:trackerdict[key]}, module_type,sceneDict, cumulativesky = False, nMods = 10, nRows = 3, modwanted = 3, rowwanted = 3, sensorsy = 2) #makeScene creates a .rad file with 20 modules per row, 7 rows.
    
    demo.makeOct1axis(trackerdict,key) # just run this for one timestep: Jan 1 11am
    demo.analysis1axis(trackerdict,key) # just run this for one timestep: Jan 1 11am

    assert(np.round(np.mean(demo.Wm2Front),0) == 214.0)
    assert(np.round(np.mean(demo.Wm2Back),0) == 40.0)

def test_SceneObj_makeSceneNxR_lowtilt():
    # test makeSceneNxR(tilt, height, pitch, orientation = None, azimuth = 180, nMods = 20, nRows = 7, radname = None)
    # default scene with simple_panel, 10 degree tilt, 0.2 height, 1.5 row spacing, landscape
    scene = SceneObj(moduletype = 'simple_panel')
    scene.makeSceneNxR(tilt=10,height=0.2,pitch=1.5,orientation = 'landscape')
    assert scene.frontscan == {'Nx': 1, 'Ny': 9, 'Nz': 1, 'orient': '0 0 -1', 'xinc': 0, 'xstart': 0, 
                               'yinc': 0.093556736536159757, 'ystart': 0.093556736536159757, 'zinc': 0, 
                               'zstart': 1.3649657687835837}
    assert scene.backscan == {'Nx': 1, 'Ny': 9, 'Nz': 1, 'orient': '0 0 1', 'xinc': 0, 'xstart': 0,
                              'yinc': 0.093556736536159757, 'ystart': 0.093556736536159757, 'zinc': 0.016496576878358378,
                              'zstart': 0.18649657687835838} # zstart was 0.01 and zinc was 0 in v0.2.2
    assert scene.text == '!xform -rz -90 -t -0.795 0.475 0 -rx 10 -t 0 0 0.2 -a 20 -t 1.6 0 0 -a 7 -t 0 1.5 0 -i 1 -t -15.9 -4.5 0 -rz 0 objects\\simple_panel.rad'

def test_SceneObj_makeSceneNxR_hightilt():
    # test makeSceneNxR(tilt, height, pitch, orientation = None, azimuth = 180, nMods = 20, nRows = 7, radname = None)
    # default scene with simple_panel, 50 degree tilt, 0.2 height, 1.5 row spacing, landscape
    scene = SceneObj(moduletype = 'simple_panel')

    scene.makeSceneNxR(tilt=65,height=0.2,pitch=1.5,azimuth=89,orientation = 'landscape')
    assert scene.frontscan == {'Nx': 1, 'Ny': 1, 'Nz': 9, 'orient': '-0.999847695156 -0.0174524064373 0',
                               'xinc': 0, 'xstart': 0, 'yinc': 0, 'ystart': 0, 'zinc': 0.086099239768481745,
                               'zstart': 0.28609923976848173}
    assert scene.backscan == {'Nx': 1, 'Ny': 1, 'Nz': 9, 'orient': '0.999847695156 0.0174524064373 0',
                              'xinc': 0, 'xstart': -0.94985531039857163, 'yinc': 0, 'ystart': -0.016579786115419416,
                              'zinc': 0.086099239768481745, 'zstart': 0.28609923976848173}
    assert scene.text == '!xform -rz -90 -t -0.795 0.475 0 -rx 65 -t 0 0 0.2 -a 20 -t 1.6 0 0 -a 7 -t 0 1.5 0 -i 1 -t -15.9 -4.5 0 -rz 91 objects\\simple_panel.rad'
'''
    # FROM 0.2.2:
    scene.makeSceneNxR(tilt=50,height=0.2,pitch=1.5,azimuth=89,orientation = 'landscape')
    # see if the frontscan dictionary matches what it should.  Start with integer values
    temp_frontscan = dict((k, scene.frontscan[k]) for k in ('Nx', 'Ny', 'Nz','xinc','xstart','yinc','ystart'))
    assert temp_frontscan == {'Nx': 1, 'Ny': 1, 'Nz': 9, 'xinc': 0, 'xstart': 0, 'yinc': 0, 'ystart': 0}
    # check floats (round them first). 'orient', 'zinc', 'zstart'
    assert np.round(float(scene.frontscan['orient'].split()[0]),decimals=9) == -0.999847695
    assert np.round(float(scene.frontscan['orient'].split()[1]),decimals=9) == -0.017452406
    assert scene.frontscan['orient'].split()[2] == '0'
    assert np.round(float(scene.frontscan['zinc']),decimals=9) == 0.072774222
    assert np.round(float(scene.frontscan['zstart']),decimals=9) == 0.272774222

    #look at backscan.  Start with integer values
    temp_backscan = dict((k, scene.backscan[k]) for k in ('Nx', 'Ny', 'Nz','xinc','yinc'))
    assert temp_backscan == {'Nx': 1, 'Ny': 1, 'Nz': 9, 'xinc': 0,  'yinc': 0 }
    # check floats (round them first). 'orient', 'zinc', 'zstart'
    assert np.round(float(scene.backscan['orient'].split()[0]),decimals=9) == 0.999847695
    assert np.round(float(scene.backscan['orient'].split()[1]),decimals=9) == 0.017452406
    assert scene.backscan['orient'].split()[2] == '0'
    assert np.round(float(scene.backscan['zinc']),decimals=9) == 0.072774222
    assert np.round(float(scene.backscan['zstart']),decimals=9) == 0.272774222    
    assert np.round(float(scene.backscan['xstart']),decimals=9) == -0.94985531
    assert np.round(float(scene.backscan['ystart']),decimals=9) == -0.016579786

    assert scene.text == '!xform -rz -90 -t -0.795 0.475 0 -rx 50 -t 0 0 0.2 -a 20 -t 1.6 0 0 -a 7 -t 0 1.5 0 -i 1 -t -15.9 -4.5 0 -rz 91 objects\\simple_panel.rad'
'''
 
def test_AnalysisObj_linePtsMake3D():
    # test linepts = linePtsMake3D(xstart,ystart,zstart,xinc,yinc,zinc,Nx,Ny,Nz,orient):
    analysis = AnalysisObj()
    linepts = analysis.linePtsMake3D(0,0,0,1,1,1,1,2,3,'0 1 0')
    assert linepts == '0 0 0 0 1 0 \r0 1 0 0 1 0 \r0 0 1 0 1 0 \r0 1 1 0 1 0 \r0 0 2 0 1 0 \r0 1 2 0 1 0 \r'
    
 

    
     
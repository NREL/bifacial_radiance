# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 10:08:25 2018

@author: cdeline

Using pytest to create unit tests for bifacial_radiance.

to run unit tests, run pytest from the command line in the bifacial_radiance directory
to run coverage tests, run py.test --cov-report term-missing --cov=bifacial_radiance

"""

#from bifacial_radiance import RadianceObj, SceneObj, AnalysisObj
import bifacial_radiance
import numpy as np
import pytest
import os

# try navigating to tests directory so tests run from here.
try:
    os.chdir('tests')
except:
    pass

TESTDIR = os.path.dirname(__file__)  # this folder

# test the readepw on a dummy Boulder EPW file in the /tests/ directory
MET_FILENAME =  'USA_CO_Boulder.724699_TMY2.epw'
# also test a dummy TMY3 Denver file in /tests/
MET_FILENAME2 = "724666TYA.CSV"

def test_quickExample():
    results = bifacial_radiance.main.quickExample(TESTDIR)
    assert np.mean(results.Wm2Back) == pytest.approx(195380.94444444444, rel = 0.03)  # was 182 in v0.2.2

def test_RadianceObj_set1axis():  
    # test set1axis.  requires metdata for boulder. 
    name = "_test_set1axis"
    demo = bifacial_radiance.RadianceObj(name)
    try:
        epwfile = demo.getEPW(lat=40.01667, lon=-105.25)  # From EPW: {N 40°  1'} {W 105° 15'}
    except: # adding an except in case the internet connection in the lab forbids the epw donwload.
        epwfile = MET_FILENAME
    metdata = demo.readEPW(epwfile = epwfile)
    trackerdict = demo.set1axis()
    assert trackerdict[0]['count'] == 80 #this was 108 < v0.2.4 and 75 < 0.3.2
    assert trackerdict[45]['count'] == 822 #this was 823 < 0.3.2
   
def test_RadianceObj_fixed_tilt_end_to_end():
    # just run the demo example.  Rear irradiance fraction roughly 11.8% for 0.95m landscape panel
    # takes 12 seconds
    name = "_test_fixed_tilt_end_to_end"
    demo = bifacial_radiance.RadianceObj(name)  # Create a RadianceObj 'object'
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
    sceneDict = {'tilt':10,'pitch':1.5,'height':0.2, 'nMods':10, 'nRows':3}  
    demo.makeModule(name='test',y=0.95,x=1.59, xgap=0)
    scene = demo.makeScene('test',sceneDict) #makeScene creates a .rad file with 20 modules per row, 7 rows.
    octfile = demo.makeOct(demo.getfilelist())  # makeOct combines all of the ground, sky and object files into a .oct file.
    analysis = bifacial_radiance.AnalysisObj(octfile, demo.name)  # return an analysis object including the scan dimensions for back irradiance
    (frontscan,backscan) = analysis.moduleAnalysis(scene)
    analysis.analysis(octfile, demo.name, frontscan, backscan)  # compare the back vs front irradiance  
    #assert np.round(np.mean(analysis.backRatio),decimals=2) == 0.12  # NOTE: this value is 0.11 when your module size is 1m, 0.12 when module size is 0.95m
    assert np.mean(analysis.backRatio) == pytest.approx(0.12, abs = 0.01)
    
def test_Radiance_high_azimuth_modelchains():
    # duplicate next example using modelchain
    # high azimuth .ini file

    HIGH_AZIMUTH_INI = os.path.join(TESTDIR, "ini_highAzimuth.ini")

    (Params)= bifacial_radiance.load.readconfigurationinputfile(inifile=HIGH_AZIMUTH_INI)
    Params[0]['testfolder'] = TESTDIR
    # unpack the Params tuple with *Params
    demo2, analysis = bifacial_radiance.modelchain.runModelChain(*Params ) 
    #assert np.round(np.mean(analysis.backRatio),2) == 0.20  # bifi ratio was == 0.22 in v0.2.2
    assert np.mean(analysis.Wm2Front) == pytest.approx(899, rel = 0.005)  # was 912 in v0.2.3
    assert np.mean(analysis.Wm2Back) == pytest.approx(189, rel = 0.03)  # was 182 in v0.2.2
    
"""
def test_RadianceObj_high_azimuth_angle_end_to_end():
    # modify example for high azimuth angle to test different parts of _makeSceneNxR.  Rear irradiance fraction roughly 17.3% for 0.95m landscape panel
    # takes 14 seconds for sensorsy = 9, 11 seconds for sensorsy = 2
    name = "_test_high_azimuth_angle_end_to_end"
    demo = bifacial_radiance.RadianceObj(name)  # Create a RadianceObj 'object'
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
    sceneDict = {'tilt':10,'pitch':1.5,'height':0.2,'azimuth':30, 'nMods':10, 'nRows':3}  
    moduleDict = demo.makeModule(name='test',y=0.95,x=1.59, xgap=0)
    scene = demo.makeScene('test',sceneDict) #makeScene creates a .rad file with 20 modules per row, 7 rows.
    octfile = demo.makeOct(demo.getfilelist())  # makeOct combines all of the ground, sky and object files into a .oct file.
    analysis = bifacial_radiance.AnalysisObj(octfile, demo.name)  # return an analysis object including the scan dimensions for back irradiance
    (frontscan,backscan) = analysis.moduleAnalysis(scene)
    analysis.analysis(octfile, demo.name, frontscan, backscan)  # compare the back vs front irradiance      
    #assert np.round(np.mean(analysis.backRatio),2) == 0.20  # bifi ratio was == 0.22 in v0.2.2
    assert np.mean(analysis.Wm2Front) == pytest.approx(899, rel = 0.005)  # was 912 in v0.2.3
    assert np.mean(analysis.Wm2Back) == pytest.approx(189, rel = 0.02)  # was 182 in v0.2.2
"""

def test_Radiance_1axis_gendaylit_modelchains():
    # duplicate next sample using modelchain
    # 1-axis .ini file
    filename = "ini_1axis.ini"

    (Params)= bifacial_radiance.load.readconfigurationinputfile(inifile=filename)
    Params[0]['testfolder'] = TESTDIR
    # unpack the Params tuple with *Params
    demo2, analysis = bifacial_radiance.modelchain.runModelChain(*Params ) 
    #V 0.2.5 fixed the gcr passed to set1axis. (since gcr was not being passd to set1axis, gcr was default 0.33 default). 
    assert(np.mean(demo2.Wm2Front) == pytest.approx(205.0, 0.01) ) # was 214 in v0.2.3  # was 205 in early v0.2.4  
    assert(np.mean(demo2.Wm2Back) == pytest.approx(43.0, 0.1) )

"""    
def test_RadianceObj_1axis_gendaylit_end_to_end():
    name = "_test_1axis_gendaylit_end_to_end"
    # 1-axis tracking end-to-end test with torque tube and gap generation.  
    # Takes 20 seconds for 2-sensor scan
    gcr = 0.35   # ground cover ratio,  = module_height / pitch
    albedo = 0.3     # ground albedo
    hub_height = 2   # tracker height at 0 tilt in meters (hub height)
    
    demo = bifacial_radiance.RadianceObj(name)  # Create a RadianceObj 'object'
    demo.setGround(albedo) # input albedo number or material name like 'concrete'.  To see options, run this without any input.
    metdata = demo.readEPW(MET_FILENAME, starttime='01_01_01', endtime = '01_01_23') # read in the EPW weather data from above
    #metdata = demo.readTMY(MET_FILENAME2) # select a TMY file using graphical picker
    # set module type to be used and passed into makeScene1axis
    # test modules with gap and rear tube
    moduleDict=demo.makeModule(name='test',x=0.984,y=1.95,torquetube = True, numpanels = 2, ygap = 0.1)
    sceneDict = {'pitch': np.round(moduleDict['sceney'] / gcr,3),'height':hub_height, 'nMods':10, 'nRows':3}  
    key = '01_01_11'
    # create metdata files for each condition. keys are timestamps for gendaylit workflow
    trackerdict = demo.set1axis(cumulativesky = False, gcr=gcr)
    # create the skyfiles needed for 1-axis tracking
    demo.gendaylit1axis(metdata = metdata, enddate = '01/01')
    # Create the scene for the 1-axis tracking
    demo.makeScene1axis({key:trackerdict[key]}, moduletype='test', sceneDict=sceneDict, cumulativesky = False)
    #demo.makeScene1axis({key:trackerdict[key]}, module_type,sceneDict, cumulativesky = False, nMods = 10, nRows = 3, modwanted = 7, rowwanted = 3, sensorsy = 2) #makeScene creates a .rad file with 20 modules per row, 7 rows.
    
    demo.makeOct1axis(trackerdict,key) # just run this for one timestep: Jan 1 11am
    trackerdict = demo.analysis1axis(trackerdict, singleindex=key, modWanted=7, rowWanted=3, sensorsy=2) # just run this for one timestep: Jan 1 11am
    
    #V 0.2.5 fixed the gcr passed to set1axis. (since gcr was not being passd to set1axis, gcr was default 0.33 default). 
    assert(np.mean(demo.Wm2Front) == pytest.approx(205.0, 0.01) ) # was 214 in v0.2.3  # was 205 in early v0.2.4  
    assert(np.mean(demo.Wm2Back) == pytest.approx(43.0, 0.1) )
"""

def test_1axis_gencumSky():
    name = "test_1axis_gencumSky"
    # Takes 20 seconds for 2-sensor scan
    gcr = 0.35   # ground cover ratio,  = module_height / pitch
    albedo = 0.3     # ground albedo
    hub_height = 2   # tracker height at 0 tilt in meters (hub height)
    
    demo = bifacial_radiance.RadianceObj(name)  # Create a RadianceObj 'object'
    demo.setGround(albedo) # input albedo number or material name like 'concrete'.  To see options, run this without any input.
    demo.readEPW(MET_FILENAME, starttime='01_01_01', endtime = '01_01_23') # read in the EPW weather data from above
    moduleDict=demo.makeModule(name='test',x=0.984,y=1.95, numpanels = 2, ygap = 0.1)
    pitch= np.round(moduleDict['sceney'] / gcr,3)
    trackerdict = demo.set1axis(cumulativesky = True, gcr=gcr)
    demo.genCumSky1axis()
    assert trackerdict[-45.0]['skyfile'][0:5] == 'skies' #  # Having trouble with the \ or //    'skies\\1axis_-45.0.rad'
    sceneDict = {'gcr': gcr,'hub_height':hub_height, 'clearance_height':hub_height, 'nMods':10, 'nRows':3}  
    trackerdict = demo.makeScene1axis(sceneDict=sceneDict, moduletype = 'test')
    # Removing all of this other tests for hub_height and height since it's ben identified that
    # a new module to handle hub_height and height in sceneDict needs to be implemented
    # instead of checking inside of makeScene, makeSceneNxR, and makeScene1axis
    assert trackerdict[-5.0]['radfile'][0:7] == 'objects' # 'objects\\1axis-5.0_1.825_11.42_5.0_10x3_origin0,0.rad'
    sceneDict = {'pitch': pitch,'clearance_height':hub_height, 'nMods':10, 'nRows':3}  # testing height filter too
    trackerdict = demo.makeScene1axis(sceneDict=sceneDict, moduletype = 'test')
#    assert trackerdict[-5.0]['radfile'] == 'objects\\1axis-5.0_1.825_11.42_5.0_10x3_origin0,0.rad'
    sceneDict = {'pitch': pitch,'height':hub_height, 'nMods':10, 'nRows':3}  # testing height filter too
    trackerdict = demo.makeScene1axis(sceneDict=sceneDict, moduletype = 'test')
#    assert trackerdict[-5.0]['radfile'] == 'objects\\1axis-5.0_1.825_11.42_5.0_10x3_origin0,0.rad'
    sceneDict = {'pitch': pitch,'height':hub_height, 'clearance_height':hub_height, 'nMods':10, 'nRows':3}  # testing height filter too
    trackerdict = demo.makeScene1axis(sceneDict=sceneDict, moduletype = 'test')
#    assert trackerdict[-5.0]['radfile'] == 'objects\\1axis-5.0_1.825_11.42_5.0_10x3_origin0,0.rad'
    sceneDict = {'pitch': pitch,'height':hub_height, 'hub_height':hub_height, 'nMods':10, 'nRows':3}  # testing height filter too
    trackerdict = demo.makeScene1axis(sceneDict=sceneDict, moduletype = 'test')
    demo.exportTrackerDict(trackerdict, savefile = 'results\exportedTrackerDict')
    assert trackerdict[-5.0]['radfile'][0:7] == 'objects' 
    #assert trackerdict[-5.0]['radfile'] == 'objects\\1axis-5.0_1.825_11.42_5.0_10x3_origin0,0.rad'
#    trackerdict = demo.makeOct1axis(trackerdict=trackerdict) # just run this for one timestep: Jan 1 11am
#    trackerdict = demo.analysis1axis(trackerdict=trackerdict, modWanted=7, rowWanted=3, sensorsy=2) 

def test_SceneObj_makeSceneNxR_lowtilt():
    # test _makeSceneNxR(tilt, height, pitch, azimuth = 180, nMods = 20, nRows = 7, radname = None)
    # default scene with simple_panel, 10 degree tilt, 0.2 height, 1.5 row spacing, landscape
    name = "_test_makeSceneNxR_lowtilt"
    demo = bifacial_radiance.RadianceObj(name) 
    demo.makeModule(name='test',y=0.95,x=1.59)
    #scene = bifacial_radiance.SceneObj(moduletype = name)
    #scene._makeSceneNxR(tilt=10,height=0.2,pitch=1.5)
    sceneDict={'tilt':10, 'height':0.2, 'pitch':1.5}
    scene = demo.makeScene(moduletype='test', sceneDict=sceneDict)
    analysis = bifacial_radiance.AnalysisObj()
    (frontscan,backscan) = analysis.moduleAnalysis(scene)
    
    assert frontscan.pop('orient') == '-0.000 0.174 -0.985'# was 0,0,-11 in v0.2.4
    assert frontscan == pytest.approx({'Nx': 1, 'Ny': 9, 'Nz': 1,  'xinc': 0,  'yinc': 0.093556736536159757,
                              'xstart': 4.627616431348303e-17,'ystart': -0.3778735578756446, 'zinc': 0.016496576878358378, 'zstart': 0.23717753969161476})
                               
    assert backscan.pop('orient') == '0.000 -0.174 0.985' # was 0,0,1 in v0.2.4
    assert backscan == pytest.approx({'Nx': 1, 'Ny': 9, 'Nz': 1,  'xinc': 0, 'yinc': 0.093556736536159757,
                              'xstart': 4.580831740657635e-17,  'ystart': -0.3740532979669721, 'zinc': 0.016496576878358378,
                              'zstart': 0.21551176912534617}) # zstart was 0.01 and zinc was 0 in v0.2.2
    #assert scene.text == '!xform -rz -90 -t -0.795 0.475 0 -rx 10 -t 0 0 0.2 -a 20 -t 1.6 0 0 -a 7 -t 0 1.5 0 -i 1 -t -15.9 -4.5 0 -rz 0 objects\\simple_panel.rad'
    assert scene.text[0:116] == '!xform -rx 10 -t 0 0 0.2824828843917919 -a 20 -t 1.6 0 0 -a 7 -t 0 1.5 0 -i 1 -t -14.4 -4.5 0 -rz 0 -t 0 0 0 objects' #linux has different directory structure and will error here.

def test_SceneObj_makeSceneNxR_hightilt():
    # test _makeSceneNxR(tilt, height, pitch, orientation = None, azimuth = 180, nMods = 20, nRows = 7, radname = None)
    # default scene with simple_panel, 50 degree tilt, 0.2 height, 1.5 row spacing, landscape
    name = "_test__makeSceneNxR_hightilt"
    demo = bifacial_radiance.RadianceObj(name) 
    demo.makeModule(name='test',y=0.95,x=1.59)
    #scene = bifacial_radiance.SceneObj(moduletype = name)
    #scene._makeSceneNxR(tilt=65,height=0.2,pitch=1.5,azimuth=89)
    sceneDict={'tilt':65, 'height':0.2, 'pitch':1.5, 'azimuth':89}
    scene = demo.makeScene(moduletype='test', sceneDict=sceneDict)
    analysis = bifacial_radiance.AnalysisObj()
    (frontscan,backscan) = analysis.moduleAnalysis(scene)
    
    
    temp = frontscan.pop('orient')
    '''
    assert [float(x) for x in temp.split(' ')] == pytest.approx([-0.999847695156, -0.0174524064373, 0])

    assert frontscan == pytest.approx({'Nx': 1, 'Ny': 1, 'Nz': 9, 'xinc': 0, 'xstart': 0, 'yinc': 0,
                                'ystart': 0, 'zinc': 0.086099239768481745,'zstart': 0.28609923976848173})
                               
    temp2 = backscan.pop('orient')
    assert [float(x) for x in temp2.split(' ')] == pytest.approx([0.999847695156, 0.0174524064373, 0])
    assert backscan == pytest.approx({'Nx': 1, 'Ny': 1, 'Nz': 9, 'xinc': 0, 'xstart': -0.94985531039857163, 
                            'yinc': 0, 'ystart': -0.016579786115419416, 'zinc': 0.086099239768481745, 'zstart': 0.28609923976848173})
    #assert scene.text == '!xform -rz -90 -t -0.795 0.475 0 -rx 65 -t 0 0 0.2 -a 20 -t 1.6 0 0 -a 7 -t 0 1.5 0 -i 1 -t -15.9 -4.5 0 -rz 91 objects\\simple_panel.rad'
    assert scene.text[0:93] == '!xform -rx 65 -t 0 0 0.2 -a 20 -t 1.6 0 0 -a 7 -t 0 1.5 0 -i 1 -t -16.0 -4.5 0 -rz 91 objects'
    '''   
    assert [float(x) for x in temp.split(' ')] == pytest.approx([-0.906, -0.016, -0.423]) #was 0,0,-1 in v0.2.4

    assert frontscan == pytest.approx({'Nx': 1, 'Ny': 9, 'Nz': 1, 'xinc': -0.040142620018581696, 'xstart': 0.1796000448657153, 'yinc': -0.0007006920388131139,
                                'ystart': 0.0031349304442418674, 'zinc': 0.08609923976848174,'zstart':  0.2949742232650364})
                               
    temp2 = backscan.pop('orient')
    assert [float(x) for x in temp2.split(' ')] == pytest.approx([0.906, 0.016, 0.423]) #was 0,0,1 in v0.2.4
    assert backscan == pytest.approx({'Nx': 1, 'Ny': 9, 'Nz': 1, 'xinc': -0.040142620018581696, 'xstart': 0.15966431032235584, 
                            'yinc': -0.0007006920388131139, 'ystart': 0.0027869509033958163, 'zinc': 0.08609923976848174, 'zstart': 0.28567662150674106})
    #assert scene.text == '!xform -rz -90 -t -0.795 0.475 0 -rx 65 -t 0 0 0.2 -a 20 -t 1.6 0 0 -a 7 -t 0 1.5 0 -i 1 -t -15.9 -4.5 0 -rz 91 objects\\simple_panel.rad'
    assert scene.text[0:117] == '!xform -rx 65 -t 0 0 0.6304961988424087 -a 20 -t 1.6 0 0 -a 7 -t 0 1.5 0 -i 1 -t -14.4 -4.5 0 -rz 91 -t 0 0 0 objects'
    

 
def test_AnalysisObj_linePtsMake3D():
    # test linepts = linePtsMake3D(xstart,ystart,zstart,xinc,yinc,zinc,Nx,Ny,Nz,orient):
    analysis = bifacial_radiance.AnalysisObj()
    linepts = analysis._linePtsMake3D(0,0,0,1,1,1,1,2,3,'0 1 0')
    assert linepts == '0 0 0 0 1 0 \r1 1 1 0 1 0 \r0 0 0 0 1 0 \r1 1 1 0 1 0 \r0 0 0 0 1 0 \r1 1 1 0 1 0 \r' # v2.5.0 new linepts because now x and z also increase not only y.
    #assert linepts == '0 0 0 0 1 0 \r0 1 0 0 1 0 \r0 0 1 0 1 0 \r0 1 1 0 1 0 \r0 0 2 0 1 0 \r0 1 2 0 1 0 \r'

def test_CellLevelModule():
    # test the cell-level module generation 
    name = "_test_CellLevelModule"
    demo = bifacial_radiance.RadianceObj(name)  # Create a RadianceObj 'object'
    cellParams = {'xcell':0.156, 'ycell':0.156, 'numcellsx':6, 'numcellsy':10,  
                   'xcellgap':0.02, 'ycellgap':0.02}
    #moduleDict = demo.makeModule(name=name, cellLevelModule=True, xcell=0.156, rewriteModulefile=True, ycell=0.156,  
    #                             numcellsx=6, numcellsy=10, xcellgap=0.02, ycellgap=0.02)
    moduleDict = demo.makeModule(name='test', rewriteModulefile=True, cellLevelModuleParams = cellParams)
    assert moduleDict['x'] == 1.036
    assert moduleDict['y'] == 1.74
    assert moduleDict['scenex'] == 1.046
    assert moduleDict['sceney'] == 1.74
    assert moduleDict['text'] == '! genbox black cellPVmodule 0.156 0.156 0.02 | xform -t -0.44 -0.87 0 -a 6 -t 0.176 0 0 -a 10 -t 0 0.176 0 -a 1 -t 0 1.74 0'
    
def test_TorqueTubes_Module():
    name = "_test_TorqueTubes"
    demo = bifacial_radiance.RadianceObj(name)  # Create a RadianceObj 'object'
    moduleDict = demo.makeModule(name='square', y=0.95,x=1.59, rewriteModulefile=True, torquetube=True, tubetype='square')
    assert moduleDict['x'] == 1.59
    assert moduleDict['text'] == '! genbox black square 1.59 0.95 0.02 | xform -t -0.795 -0.475 0 -a 1 -t 0 0.95 0\r\n! genbox Metal_Grey tube1 1.6 0.1 0.1 | xform -t -0.8 -0.05 -0.2'
    moduleDict = demo.makeModule(name='round', y=0.95,x=1.59, rewriteModulefile=True, torquetube=True, tubetype='round')
    assert moduleDict['text'][0:30] == '! genbox black round 1.59 0.95'
    moduleDict = demo.makeModule(name='hex', y=0.95,x=1.59, rewriteModulefile=True, torquetube=True, tubetype='hex')
    assert moduleDict['text'][0:30] == '! genbox black hex 1.59 0.95 0'
    moduleDict = demo.makeModule(name='oct', y=0.95,x=1.59, rewriteModulefile=True, torquetube=True, tubetype='oct')
    assert moduleDict['text'][0:30] == '! genbox black oct 1.59 0.95 0'

def test_gendaylit2manual():
    name = "_test_gendaylit2manual"
    demo = bifacial_radiance.RadianceObj(name)
    demo.setGround('litesoil') 
    skyname = demo.gendaylit2manual(dni = 700, dhi = 100, sunalt = 67, sunaz = 180) # Invented values.
    assert skyname[0:5] == 'skies' # Having trouble with the \ or // with 'skies\sky2__test_gendaylit2manual.rad'


    
def test_SingleModule_end_to_end():
    # 1 module for STC conditions. DNI:900, DHI:100, sun angle: 33 elevation 0 azimuth
    name = "_test_SingleModule_end_to_end"
    demo = bifacial_radiance.RadianceObj(name)  # Create a RadianceObj 'object'
    demo.setGround('litesoil') 
    metdata = demo.readEPW(epwfile= MET_FILENAME)
    demo.gendaylit(metdata,4020,debug=True)  # 1pm, June 17th
    # create a scene using panels in landscape at 10 deg tilt, 1.5m pitch. 0.2 m ground clearance
    tilt=demo.getSingleTimestampTrackerAngle(metdata=metdata, timeindex=4020, gcr=0.33)
    assert tilt == pytest.approx(-6.7, abs = 0.4)
    sceneDict = {'tilt':0,'pitch':1.5,'clearance_height':1, 'nMods':1, 'nRows':1}  
    demo.makeModule()
    demo.makeModule(name='test',y=0.95,x=1.59, xgap=0)
    scene = demo.makeScene('test',sceneDict) 
   
    #objname='Marker'
    #text='! genbox white_EPDM mymarker 0.02 0.02 2.5 | xform -t -.01 -.01 0'   
    #customObject = demo.makeCustomObject(objname,text)
    #demo.appendtoScene(scene.radfiles, customObject, '!xform -rz 0')
    octfile = demo.makeOct(demo.getfilelist(), hpc=True)  # makeOct combines all of the ground, sky and object files into a .oct file.
    analysis = bifacial_radiance.AnalysisObj(octfile, demo.name)  # return an analysis object including the scan dimensions for back irradiance
    (frontscan,backscan) = analysis.moduleAnalysis(scene, sensorsy=1)
    analysis.analysis(octfile, demo.name, frontscan, backscan)  # compare the back vs front irradiance  
    assert analysis.mattype[0][:12] == 'a0.0.a0.test'
    assert analysis.rearMat[0][:12] == 'a0.0.a0.test'
    assert analysis.x == [0]
    assert analysis.y == [0]
    assert np.mean(analysis.Wm2Front) == pytest.approx(1025, abs = 2)
    analysis.makeImage('side.vp', hpc=True)
    analysis.makeFalseColor('side.vp') #TODO: this works on silvanas computer, 
    # side.vp must exist inside of views folder in test folder... make sure this works 
    # in other computers
    assert np.mean(analysis.Wm2Back) == pytest.approx(166, abs = 6)
    
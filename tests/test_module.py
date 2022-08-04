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
import pandas as pd

# try navigating to tests directory so tests run from here.
try:
    os.chdir('tests')
except:
    pass

#TESTDIR = os.path.dirname(__file__)  # this folder

cellParams = {'xcell':0.156, 'ycell':0.156, 'numcellsx':6, 'numcellsy':10,  
               'xcellgap':0.02, 'ycellgap':0.02}

frameParams = {'frame_material' : 'Metal_Grey', 
               'frame_thickness' : 0.003,
               'frame_z' : 0.03,
               'nSides_frame' : 4,
               'frame_width' : 0.05}


omegaParams = {'omega_material': 'litesoil',
                'x_omega1' : 0.10,
                'mod_overlap' : 0.5,
                'y_omega' : 1.5,
                'x_omega3' : 0.05,
                'omega_thickness' : 0.01,
                'inverted' : False}

def test_CellLevelModule():
    # test the cell-level module generation 
    name = "_test_CellLevelModule"
    demo = bifacial_radiance.RadianceObj(name)  # Create a RadianceObj 'object'

    module = demo.makeModule(name='test-module', rewriteModulefile=True, cellModule=cellParams, customtext=r'!xform -rz 0 customTT.rad | xform -rz 90 -t 0.5 0 -0.15')
    assert module.x == 1.036
    assert module.y == 1.74
    assert module.scenex == 1.046
    assert module.sceney == 1.74
    assert module.text == '! genbox black cellPVmodule 0.156 0.156 0.02 | xform -t -0.44 -0.87 0 -a 6 -t 0.176 0 0 -a 10 -t 0 0.176 0 -a 1 -t 0 1.74 0\n!xform -rz 0 customTT.rad | xform -rz 90 -t 0.5 0 -0.15'
    module.addCellModule(**cellParams, centerJB=0.01)  #centerJB simulations still under development.
#    assert module.text == '! genbox black cellPVmodule 0.156 0.156 0.02 | xform -t -0.44 -0.87 0 -a 6 -t 0.176 0 0 -a 5.0 -t 0 0.176 0 -a 2 -t 0 0.772 0 | xform -t 0 0.181 0 -a 1 -t 0 1.73 0'

    
def test_TorqueTubes_Module():
    name = "_test_TorqueTubes"
    demo = bifacial_radiance.RadianceObj(name)  # Create a RadianceObj 'object'
    module = demo.makeModule(name='square', y=0.95,x=1.59, tubeParams={'tubetype':'square', 'axisofrotation':False}, hpc=True) #suppress saving .json
    assert module.x == 1.59
    assert module.text == '! genbox black square 1.59 0.95 0.02 | xform -t -0.795 -0.475 0 -a 1 -t 0 0.95 0\r\n! genbox Metal_Grey tube1 1.6 0.1 0.1 | xform -t -0.8 -0.05 -0.2'
    module = demo.makeModule(name='round', y=0.95,x=1.59, tubeParams={'tubetype':'round', 'axisofrotation':False}, hpc=True)
    assert module.text[0:30] == '! genbox black round 1.59 0.95'
    module = demo.makeModule(name='hex', y=0.95,x=1.59,  tubeParams={'tubetype':'hex', 'axisofrotation':False}, hpc=True)
    assert module.text[0:30] == '! genbox black hex 1.59 0.95 0'
    module = demo.makeModule(name='oct', y=0.95,x=1.59, hpc=True)
    module.addTorquetube(tubetype='oct', axisofrotation=False, recompile=False)
    module.compileText(rewriteModulefile=False, json=False)
    assert module.text[0:30] == '! genbox black oct 1.59 0.95 0'

def test_moduleFrameandOmegas():  
    # test moduleFrameandOmegas. Requires metdata for boulder. 

    name = "_test_moduleFrameandOmegas"
    demo = bifacial_radiance.RadianceObj(name)
    #demo.setGround(0.2)
    zgap = 0.10
   

    
    loopaxisofRotation = [True, True, True, True, True, True, True, True]
    loopTorquetube = [True, True, True, True, False, False, False, False ]
    loopOmega = [omegaParams, omegaParams, None, None, omegaParams, omegaParams, None, None]
    loopFrame = [frameParams, None, frameParams, None, frameParams,  None, frameParams, None]
    expectedModuleZ = [3.179, 3.149, 3.179, 3.149, 3.129, 3.099, 3.129, 3.099]
    
    # test inverted=True on the first test
    loopOmega[0]['inverted'] = True
    sceneDict = {'tilt':0, 'pitch':3, 'clearance_height':3,'azimuth':90,
                 'nMods': 1, 'nRows': 1}

    for ii in range (0, len(loopOmega)):

        if loopTorquetube[ii] is False:
            diam = 0.0
        else:  diam = 0.1

        module = bifacial_radiance.ModuleObj(name='test-module',x=2, y=1, zgap = zgap,
                                             )
        module.addTorquetube(diameter=diam, axisofrotation=loopaxisofRotation[ii],
                             visible = loopTorquetube[ii]) 
        if loopFrame[ii]:
            module.addFrame(**loopFrame[ii])
                       
        if loopOmega[ii]:
            module.addOmega(**loopOmega[ii])  #another way to add omega parameters
        scene = demo.makeScene(module,sceneDict)
        analysis = bifacial_radiance.AnalysisObj()  # return an analysis object including the scan dimensions for back irradiance
        frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=1) # Gives us the dictionaries with coordinates
        assert backscan['zstart'] == expectedModuleZ[ii]
        
        # read the data back from module.json and check again
        module = demo.makeModule(name='test-module')
        scene = demo.makeScene('test-module',sceneDict)
        analysis = bifacial_radiance.AnalysisObj()  # return an analysis object including the scan dimensions for back irradiance
        frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=1)
        assert backscan['zstart'] == expectedModuleZ[ii]
    # do it again by passing everying at once
    module = bifacial_radiance.ModuleObj(name='test-module',x=2, y=1, zgap = zgap,
                                          frameParams=frameParams, omegaParams=omegaParams,
                                          tubeParams={'diameter':0.1,
                                                      'axisofrotation':True})
    scene = demo.makeScene(module, sceneDict)
    analysis = bifacial_radiance.AnalysisObj()  # return an analysis object including the scan dimensions for back irradiance
    frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=1) # Gives us the dictionaries with coordinates
    assert backscan['zstart'] == expectedModuleZ[0]
    
    # omega default values
    module.addOmega()
    assert module.omega.x_omega1==0.003; assert module.omega.y_omega==0.5; assert module.omega.x_omega3==0.005; 
    module.addOmega(inverted=True)
    assert module.omega.x_omega1==0.005; assert module.omega.y_omega==0.5; assert module.omega.x_omega3==0.0015; 
   
    # test cellModulescan (sensorsy = numellsy)
    module.glass=True
    module.addCellModule(**cellParams)
    scene = demo.makeScene(module, sceneDict)
    analysis = bifacial_radiance.AnalysisObj()  # return an analysis object including the scan dimensions for back irradiance
    frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=10) # Gives us the dictionaries with coordinates
    assert backscan['xstart'] == pytest.approx(0.792)
# -*- coding: utf-8 -*-
"""
Created 2/19/19

@author: cdeline

Using pytest to create unit tests for load.py

to run unit tests, run pytest from the command line in the bifacial_radiance directory

"""

import bifacial_radiance
import os, pytest

# try navigating to tests directory so tests run from here.
try:
    os.chdir('tests')
except:
    pass

MET_FILENAME = 'USA_CO_Boulder.724699_TMY2.epw'
TEST_FILE = os.path.join('results','test_01_01_10.csv')



# test load function on a dummy csv file in the /tests/ directory

def test_save_load_pickle():
    # quick save and re-load the entire RadianceObj as a pickle
    demo = bifacial_radiance.RadianceObj(name = 'test')
    demo.save('save.pickle')
    demo2 = bifacial_radiance.load.loadRadianceObj('save.pickle')
    assert demo2.name == 'test'

def test_load_trackerdict():
    # example of saving and loading files in /results/ for 1-axis hourly workflow.
    # this requires some pre-saved files in 
    demo = bifacial_radiance.RadianceObj(name = 'test')
    demo.readEPW(MET_FILENAME)
    trackerdict = demo.set1axis(cumulativesky = False)
    demo.loadtrackerdict(trackerdict,fileprefix = 'test_')
    assert demo.Wm2Front[0] == pytest.approx(166.3, abs = 0.01)

def test_cleanResult():
    # example of setting NaN's when the scan intersects undesired material
    # test_01_01_10.csv has some ground and sky references
    import numpy as np
    resultsDF = bifacial_radiance.load.read1Result(TEST_FILE)
    cleanedDF = bifacial_radiance.load.cleanResult(resultsDF)
    assert np.isnan(cleanedDF.Wm2Front.loc[4]) 

def test_read1Result():
    # example of loading file in /results/ 
    # this requires one pre-saved files in  
    resultsDict=bifacial_radiance.load.read1Result(TEST_FILE)
    assert resultsDict['rearMat'][0] == 'a10.3.a0.PVmodule.2310'

def test_deepcleanResult():
    # example of loading file in /results/ 
    # this requires one pre-saved files in  
    resultfile=os.path.join("results", "test_2UP_torque_tube_hex_4020.csv")
    resultsDict=bifacial_radiance.load.read1Result(resultfile)
    Frontresults, Backresults=bifacial_radiance.load.deepcleanResult(resultsDict, 110, 2, 270, automatic=True)
    assert len(Frontresults) == 110
    assert Backresults[54] == pytest.approx(245.3929333333333, rel = 0.01) 

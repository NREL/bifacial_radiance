# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 10:08:25 2018

@author: cdeline

Using pytest to create unit tests for mismatch.py.

to run unit tests, run pytest from the command line in the bifacial_radiance directory
to run coverage tests, run py.test --cov-report term-missing --cov=bifacial_radiance

"""

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

TESTDIR = os.path.dirname(__file__)  # this folder
TEST_ARRAY = np.array([[ 0, 23, 24, 47, 48, 71],
       [ 1, 22, 25, 46, 49, 70],
       [ 2, 21, 26, 45, 50, 69],
       [ 3, 20, 27, 44, 51, 68],
       [ 4, 19, 28, 43, 52, 67],
       [ 5, 18, 29, 42, 53, 66],
       [ 6, 17, 30, 41, 54, 65],
       [ 7, 16, 31, 40, 55, 64],
       [ 8, 15, 32, 39, 56, 63],
       [ 9, 14, 33, 38, 57, 62],
       [10, 13, 34, 37, 58, 61],
       [11, 12, 35, 36, 59, 60]])

def test_setupforPVMismatch():

    out = bifacial_radiance.mismatch._setupforPVMismatch(
            portraitorlandscape='portrait',
            sensorsy=12,
            numcells=72)
    np.testing.assert_array_equal(out[0], TEST_ARRAY)
    
    assert out[1] == 6
    assert out[2] == 12


def test_MAD():
    
    assert bifacial_radiance.mismatch.mad_fn(TEST_ARRAY) == \
        pytest.approx(2433.333,abs = 0.001)
        
    temp = bifacial_radiance.mismatch.mad_fn(pd.DataFrame(TEST_ARRAY))
    ans = pd.Series([15706.061,4936.190,2928.249,2081.526,1614.642,1318.8295])
    pd.testing.assert_series_equal(temp,ans,check_less_precise=True)
#    assert temp == \
#        pytest.approx(2433.333,abs = 0.001)    

"""

#from bifacial_radiance import RadianceObj, SceneObj, AnalysisObj
import bifacial_radiance
import bifacial_radiance.modelchain as mc
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

def test_append_dicts():
    z = mc._append_dicts({'a':True},{'b':'hello'})
    assert z['a']==True
    assert z['b']=='hello'
    
def test_returnTimeVals():
    t = {'MonthStart':1, 'DayStart':1, 'HourStart':11, 'MonthEnd':1,
         'DayEnd':1,'HourEnd':11}
    trackerdict = dict.fromkeys(['01_01_09','01_01_10','01_01_11','01_01_12'])
    startday, endday, timelist = mc._returnTimeVals(t,trackerdict)
    assert startday == '01_01'
    assert endday == '01_01'
    assert timelist == {'01_01_11'}
    
def test_Radiance_high_azimuth_modelchains2():
    # duplicate next example using modelchain
    # high azimuth .ini file
    HIGH_AZIMUTH_INI = os.path.join(TESTDIR, "ini_highAzimuth.ini")

    (Params)= bifacial_radiance.load.readconfigurationinputfile(inifile=HIGH_AZIMUTH_INI)
    Params[0]['testfolder'] = TESTDIR
    Params[0]['daydateSimulation'] = True
    Params[2].update({'MonthStart': 6, 'MonthEnd':6, 'DayStart':17, 
                      'DayEnd':17, 'HourStart':13, 'HourEnd':13}); 
    # change params to 
    # unpack the Params tuple with *Params
    demo2, analysis = bifacial_radiance.modelchain.runModelChain(*Params ) 
    #assert np.round(np.mean(analysis.backRatio),2) == 0.20  # bifi ratio was == 0.22 in v0.2.2
    assert np.mean(analysis.Wm2Front) == pytest.approx(899, rel = 0.005)  # was 912 in v0.2.3
    assert np.mean(analysis.Wm2Back) == pytest.approx(189, rel = 0.02)  # was 182 in v0.2.2

"""
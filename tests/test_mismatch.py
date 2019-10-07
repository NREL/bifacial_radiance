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

def test_analysisIrradianceandPowerMismatch():
    #analysisIrradianceandPowerMismatch(testfolder, writefiletitle, 
    #                                   portraitorlandscape, bififactor, 
    #                                   numcells=72, downsamplingmethod='byCenter'):
    
    #testfolder = r'C:\Users\cdeline\Documents\Python Scripts\Bifacial_Radiance\tests\results_mismatch'
    #writefiletitle = r'C:\Users\cdeline\Documents\Python Scripts\Bifacial_Radiance\tests\mismatch.txt'
    testfolder = os.path.join(TESTDIR,'results_mismatch')
    writefiletitle = os.path.join(TESTDIR,'mismatch.txt')
    bififactor = 1
    bifacial_radiance.mismatch.analysisIrradianceandPowerMismatch(testfolder, writefiletitle, 
                                       'portrait', bififactor=1, 
                                       numcells=72, downsamplingmethod='byCenter')
    df_all = pd.read_csv(writefiletitle)
    assert df_all.Mismatch_rel[0] == pytest.approx(0.410, abs = 0.001)
    assert df_all["MAD/G_Total"][0] == pytest.approx(2.135, abs = 0.001)
    
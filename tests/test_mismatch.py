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
    ans_T = pd.Series([ 70.892019,  69.953052, 69.014085,  68.075117,
                      67.136150,  66.197183, 65.258216,  64.319249,
                      63.380282,  62.441315, 61.502347,  60.563380])    
    ans = pd.Series([72.222222, 22.698413, 13.465160,  
                       9.571620,  7.424714,   6.064461])
    
    assert bifacial_radiance.mismatch.mad_fn(TEST_ARRAY) == \
        pytest.approx(ans.to_numpy(), abs = 0.001)
        
    assert bifacial_radiance.mismatch.mad_fn(TEST_ARRAY, axis='columns') == \
        pytest.approx(ans_T.to_numpy(), abs = 0.001)        
        
    temp = bifacial_radiance.mismatch.mad_fn(pd.DataFrame(TEST_ARRAY))
    temp2 = bifacial_radiance.mismatch.mad_fn(pd.DataFrame(TEST_ARRAY), axis=1)
    pd.testing.assert_series_equal(temp, ans)
    pd.testing.assert_series_equal(temp2, ans_T)
    # test pd.Series objects are correctly handled
    assert bifacial_radiance.mismatch.mad_fn(ans_T) == \
        pytest.approx(5.674, abs = 0.001)
    assert bifacial_radiance.mismatch.mad_fn(ans_T.to_numpy()) == \
        pytest.approx(5.674, abs = 0.001)

   

def test_analysisIrradianceandPowerMismatch():
    #analysisIrradianceandPowerMismatch(testfolder, writefiletitle, 
    #                                   portraitorlandscape, bififactor, 
    #                                   numcells=72, downsamplingmethod='byCenter'):
    
    #testfolder = r'C:\Users\cdeline\Documents\Python Scripts\Bifacial_Radiance\tests\results_mismatch'
    #writefiletitle = r'C:\Users\cdeline\Documents\Python Scripts\Bifacial_Radiance\tests\mismatch.txt'
    testfolder = os.path.join(TESTDIR,'results_mismatch')
    writefiletitle = os.path.join(TESTDIR,'mismatch.txt')
    bifacial_radiance.mismatch.analysisIrradianceandPowerMismatch(testfolder, writefiletitle, 
                                       'portrait', bififactor=1, 
                                       numcells=72, downsamplingmethod='byCenter')
    df_all = pd.read_csv(writefiletitle)
    assert df_all.Mismatch_rel[0] == pytest.approx(0.376, abs = 0.001)
    assert df_all["MAD/G_Total"][0] == pytest.approx(1.987, abs = 0.001)


def test_mismatch_fit3():
    ans = pd.Series([358.5913580, 36.2605341, 13.0562351, 6.7467491, 4.1495287, 2.8283640])
    pd.testing.assert_series_equal( bifacial_radiance.mismatch.mismatch_fit3(TEST_ARRAY),  ans, atol=1e-6)
    pd.testing.assert_series_equal( bifacial_radiance.mismatch.mismatch_fit3(pd.DataFrame(TEST_ARRAY)),  ans, atol=1e-6)
    assert bifacial_radiance.mismatch.mismatch_fit3(TEST_ARRAY[:,0]) == pytest.approx(ans[0], abs = 0.001)


def test_mismatch_fit2():
    ans = pd.Series([177.1691358, 19.7101486, 7.7139898, 4.2908790, 2.8183537, 2.0380396])
    pd.testing.assert_series_equal( bifacial_radiance.mismatch.mismatch_fit2(TEST_ARRAY),  ans, atol=1e-6)
    pd.testing.assert_series_equal( bifacial_radiance.mismatch.mismatch_fit2(pd.DataFrame(TEST_ARRAY)),  ans, atol=1e-6)
    assert bifacial_radiance.mismatch.mismatch_fit2(TEST_ARRAY[:,0]) == pytest.approx(ans[0], abs = 0.001)

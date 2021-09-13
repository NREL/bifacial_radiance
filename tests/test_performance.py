# -*- coding: utf-8 -*-
"""
Created on Fri Jun 27 10:08:25 2021

@author: sayala

Using pytest to create unit tests for performance.py.

to run unit tests, run pytest from the command line in the bifacial_radiance directory
to run coverage tests, run py.test --cov-report term-missing --cov=bifacial_radiance

"""

import pvlib
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
E0 = 1000  # W/m^2
T0 = 25  # degC


def test_calculatePerformance():

    # set the IEC61853 test matrix
    effective_irradiances = [1000, 1100, 1200, 900]  # irradiances [W/m^2]
    cell_temp = [25, 25, 25, 25]  # temperatures [degC]
    s1 = pd.Series(effective_irradiances, name='effective_irradiance')
    s2 = pd.Series(cell_temp, name='temp_cell')
    df = pd.concat([s1, s2], axis=1)

    #CECMODS = pvlib.pvsystem.retrieve_sam(name='CECMod')
    #CECMod = CECMODS['Canadian_Solar_Inc__CS5P_220M']
    CECMod = pd.read_csv('Canadian_Solar_Inc__CS5P_220M.csv',index_col=0).iloc[:,0]
    df = bifacial_radiance.performance.calculatePerformance(df, CECMod)

    assert df['p_mp'][0] == pytest.approx(219.96093865) 

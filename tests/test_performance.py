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

TESTDIR = os.path.dirname(__file__)  # this folder
E0 = 1000  # W/m^2
T0 = 25  # degC


def test_calculatePerformance():

    # set the IEC61853 test matrix
    effective_irradiances = [1000, 1100, 1200, 900]  # irradiances [W/m^2]
    cell_temp = [25, 25, 25, 25]  # temperatures [degC]
    temp_amb = [20, 20, 20, 20]
    s1 = pd.Series(effective_irradiances, name='effective_irradiance')
    s2 = pd.Series(cell_temp, name='temp_cell')
    s3 = pd.Series(temp_amb, name='temp_amb')
    #df = pd.concat([s1, s2], axis=1)

    #CECMODS = pvlib.pvsystem.retrieve_sam(name='CECMod')
    #CECMod = CECMODS['Canadian_Solar_Inc__CS5P_220M']
    CECMod = pd.read_csv(os.path.join(TESTDIR, 'Canadian_Solar_Inc__CS5P_220M.csv'),
                         index_col=0).iloc[:,0]
    p_mp_celltemp = bifacial_radiance.performance.calculatePerformance(s1, CECMod=CECMod, 
                                                            temp_cell=s2)

    assert p_mp_celltemp[0] == pytest.approx(219.96093865) 
    p_mp_tamb = bifacial_radiance.performance.calculatePerformance(s1, CECMod=CECMod, 
                                                            temp_air=s3, wind_speed=1, glassglass=True)
    assert p_mp_tamb[0] == pytest.approx(190.4431, abs=.0001)
    # test passing CECMod as a DF
    
    p_mp_celltemp2 = bifacial_radiance.performance.calculatePerformance(s1, pd.DataFrame([CECMod]), 
                                                            temp_cell=s2)
    p_mp_celltemp3 = bifacial_radiance.performance.calculatePerformance(s1, pd.DataFrame([CECMod, CECMod]), 
                                                            temp_cell=s2)
    assert p_mp_celltemp3.all()==p_mp_celltemp2.all()==p_mp_celltemp.all()

def test_MBD():
    from bifacial_radiance import performance 
    meas=np.linspace(-1,10,10)
    model=np.linspace(-2,11,10)
    assert performance.MBD(meas,model) == pytest.approx(2.174, abs=.01)
    assert performance.MBD(meas,meas) == 0
    assert performance.RMSE(meas,model) == pytest.approx(11.435, abs=.01)
    assert performance.RMSE(meas,meas) == 0
    assert performance.MBD_abs(meas,model) == pytest.approx(0.111, abs=.01)
    assert performance.MBD_abs(meas,meas) == 0
    assert performance.RMSE_abs(meas,model) == pytest.approx(0.584, abs=.01)
    assert performance.RMSE(meas,meas) == 0
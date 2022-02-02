# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 10:08:25 2018

@author: cdeline

Using pytest to create unit tests for modelchain.

to run unit tests, run pytest from the command line in the bifacial_radiance directory
to run coverage tests, run py.test --cov-report term-missing --cov=bifacial_radiance

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
"""       
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
    assert np.mean(analysis.Wm2Front) == pytest.approx(898, rel = 0.005)  # was 912 in v0.2.3
    assert np.mean(analysis.Wm2Back) == pytest.approx(189, rel = 0.02)  # was 182 in v0.2.2
"""
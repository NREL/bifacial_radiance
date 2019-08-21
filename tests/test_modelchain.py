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
    

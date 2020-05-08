# -*- coding: utf-8 -*-
"""
Created 2/19/19

@author: cdeline

Using pytest to create unit tests for GroundObj

to run unit tests, run pytest from the command line in the bifacial_radiance directory

"""

import bifacial_radiance
import os, pytest
import numpy as np

# try navigating to tests directory so tests run from here.
try:
    os.chdir('tests')
except:
    pass

MET_FILENAME = 'USA_CO_Boulder.724699_TMY2.epw'
#TEST_FILE = os.path.join('results','test_01_01_10.csv')

# also test a dummy TMY3 Denver file in /tests/
MET_FILENAME2 = "724666TYA.CSV"

# return albedo values in GroundObj
def _groundtest(groundobj):
    if type(groundobj) != bifacial_radiance.main.GroundObj:
        raise TypeError('bifacial_radiance.GroundObj not passed')
    
    return(groundobj.Rrefl, groundobj.Grefl, groundobj.Brefl, groundobj.ReflAvg)
        

def test_albedo_cases_orig():
    # test 'litesoil', constant albedo
    demo = bifacial_radiance.RadianceObj(name = 'test')
    demo.setGround('litesoil')
    testvals_litesoil = (.29, .187, .163, .213)
    np.testing.assert_allclose(_groundtest(demo.ground), testvals_litesoil, atol=.001)
    
    demo.setGround(0.2)
    testvals_const = (.2, .2, .2, .2)
    np.testing.assert_allclose(_groundtest(demo.ground), testvals_const, atol=.001)

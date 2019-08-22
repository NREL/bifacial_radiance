# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 10:08:25 2018

@author: cdeline

Using pytest to create unit tests for readepw.

to run unit tests, run pytest from the command line in the bifacial_radiance directory

"""

import bifacial_radiance
import os

# try navigating to tests directory so tests run from here.
try:
    os.chdir('tests')
except:
    pass

# test the readepw on a dummy Boulder EPW file in the /tests/ directory
TESTDIR = os.path.dirname(__file__)
TESTDATA_FILENAME =  os.path.join(TESTDIR, 'USA_CO_Boulder.724699_TMY2.epw')

def test_readepw_metadata():  
    # Is this returning correct metadata?
    (EPW_DATA, EPW_METADATA) = bifacial_radiance.readepw(filename = TESTDATA_FILENAME)  # this is done outside of an assert, but maybe that's ok?

    assert EPW_METADATA == {'Name': 'BOULDER',
                         'State': 'USA',
                         'TZ': -7.0,
                         'USAF': 724699,
                         'altitude': 1634.0,
                         'latitude': 40.02,
                         'longitude': -105.25} 


def test_readepw_data_length():
    # Is this returning the correct amount of data?  34 x 8760
    (EPW_DATA, EPW_METADATA) = bifacial_radiance.readepw(filename = TESTDATA_FILENAME)  # this is done outside of an assert, but maybe that's ok?
    assert EPW_DATA.__len__() == 8760
    assert EPW_DATA.columns.__len__() == 34
    
def test_readepw_data_values():
    # Is this returning the correct data maxima?
    (EPW_DATA, EPW_METADATA) = bifacial_radiance.readepw(filename = TESTDATA_FILENAME)  # this is done outside of an assert, but maybe that's ok?
    assert EPW_DATA['Dry bulb temperature in C'].max() == 36.7
    assert EPW_DATA['Global horizontal radiation in Wh/m2'].max() == 1029
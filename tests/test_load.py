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
MET_FILENAME2 = "724666TYA.CSV"


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
    
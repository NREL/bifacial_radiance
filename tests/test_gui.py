# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 10:08:25 2018

@author: cdeline

Attempt to do some sort of test of the gui.  Unsure how to do this exactly..

to run unit tests, run pytest from the command line in the bifacial_radiance directory
to run coverage tests, run py.test --cov-report term-missing --cov=bifacial_radiance

"""

from bifacial_radiance.gui import Window
import matplotlib as mpl

def test_GuiWindow():
    mpl.use('Agg') # set up display backend
    # this doesn't  do much at the moment, but gives us 50% coverage of gui.py! 
    root = Window()
    root.__init__()
    
    

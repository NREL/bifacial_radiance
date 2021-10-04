#!/usr/bin/env python
# coding: utf-8

"""
Created on Wed Sept 22 18:09:22 2021

@author: cdeline

Using pytest to create unit tests for bifacial_radiance.

to run unit tests, run pytest from the command line in the bifacial_radiance directory
to run coverage tests, run py.test --cov-report term-missing --cov=bifacial_radiance


"""

#from bifacial_radiance import RadianceObj, SceneObj, AnalysisObj
import bifacial_radiance as br
#import pytest
import os
import pandas as pd

# try navigating to tests directory so tests run from here.
try:
    os.chdir('tests')
except:
    pass

TESTDIR = os.path.dirname(__file__)  # this folder

MET_FILENAME = os.path.join(TESTDIR,"724666TYA.CSV")
SPECTRA_FOLDER = os.path.join(TESTDIR,'Spectra')
os.makedirs(SPECTRA_FOLDER, exist_ok=True)
#testfolder = r'C:\Users\cdeline\Documents\python scripts\bifacial_radiance\bifacial_radiance\TEMP'
#weatherfile = r'C:\Users\cdeline\Documents\python scripts\bifacial_radiance\tests\USA_CO_Boulder.724699_TMY2.epw' 
#spectrafolder = r'C:\Users\cdeline\Documents\python scripts\bifacial_radiance\tests\spectra'


# # 1 ) Generate Spectra for 1 timestamp
# 
def test_generate_spectra():  
    # test set1axis.  requires metdata for boulder. 
    name = "_test_generate_spectra"
    rad_obj = br.RadianceObj(name, TESTDIR)
    metdata = rad_obj.readWeatherFile(MET_FILENAME, 
                                      starttime='2001-06-16',
                                      endtime='2001-06-18',
                                      coerce_year=2001)
    idx = metdata.datetime.index(pd.to_datetime('2001-06-17 12:0:0 -7'))
    
    (spectral_alb, spectral_dni, spectral_dhi) = br.generate_spectra(idx, 
                                                                 rad_obj.metdata, 
                                                                 material='Grass', 
                                                                 spectra_folder=SPECTRA_FOLDER)
    assert spectral_alb.data.__len__() == 1962
    assert spectral_dhi.data.index[1961] == 4000.0
    assert spectral_dni.data.iloc[0,0] == 0.003805


def _other_cruft():
    # In[3]:
    
    
    # Improvements: 
    # Create new SPECTRA Folder on the Radiance Scene Folder to save spectras in automatically
    # Search for metdata internally if not passed
    # Start using timestamps instead of indexes
    # generate spectras and save values internally as part of the rad_obj ~ 
    # generate spectras for all indexes in metdata automatically (might take a while for the year if readWeatherFile is not restricted)
    # pySMARTS: interactive folder selectro to choose where Smarts executable is at, in case it doesn't find it in the Environment Variables
    
    
    # # 2) Call spectra for that timestamp
    
    # In[14]:
        
    
    wavelength = 700
    
    
    # In[ ]:
    
    
    # spectral_utils generates files with this suffix
    suffix = f'_{idx:04}.txt'
    
    # Load albedo
    alb_file = Path(spectra_folder, "alb"+suffix)
    spectral_alb = br.spectral_utils.spectral_property.load_file(alb_file)
    
    # Generate/Load dni and dhi
    dni_file = os.path.join(spectra_folder, "dni"+suffix)
    dhi_file = os.path.join(spectra_folder, "dhi"+suffix)
    ghi_file = os.path.join(spectra_folder, "ghi"+suffix)
    spectral_dni = br.spectral_utils.spectral_property.load_file(dni_file)
    spectral_dhi = br.spectral_utils.spectral_property.load_file(dhi_file)
    spectral_ghi = br.spectral_utils.spectral_property.load_file(ghi_file)
    
    alb = spectral_alb[wavelength]
    dni = spectral_dni[wavelength]
    dhi = spectral_dhi[wavelength]
    ghi = spectral_ghi[wavelength]
    
    rad_obj.setGround(alb) # this option is for spectral-albedo
    solpos = rad_obj.metdata.solpos.iloc[idx]
    zen = float(solpos.zenith)
    azm = float(solpos.azimuth) - 180
    rad_obj.gendaylit2manual(dni, dhi, 90 - zen, azm)
    
    sceneDict = {'tilt':tilt, 'pitch':0.0001, 'clearance_height':2.0,
                         'azimuth':180, 'nMods':1, 'nRows':1}
    sceneObj = rad_obj.makeScene(moduletype=module_type,sceneDict=sceneDict) 
    
    # Build oct file            
    octfile = rad_obj.makeOct(octname=f'Oct_{idx:04}')
    analysis = br.AnalysisObj(octfile, rad_obj.basename)  
    frontscan, backscan = analysis.moduleAnalysis(sceneObj, sensorsy=3)
    res_name = f'CenterRow_Center_{idx:04}'
    frontdict, backdict = analysis.analysis(octfile, res_name, frontscan, backscan)


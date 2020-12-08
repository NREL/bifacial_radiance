import numpy as np
import pandas as pd

from collections.abc import Iterable

class spectral_property(object):
    def load_file(filepath):
        with open(filepath, 'r') as infile:
            meta = next(infile)[:-1]
            data = pd.read_csv(infile)
        
        return spectral_property(data['value'], data['wavelength'],
                                 interpolation=meta.split(':')[1])
    
    def to_nm(wavelength, units):
        unit_conversion = { 'nm': 1,
                            'um': 1000 }
        
        # Verify units are in conversion table
        if units not in unit_conversion:
            print("Warning: Unknown unit specified. Options are {}.".format(
                unit_conversion.keys()))
            units = 'nm'
            
        return wavelength * unit_conversion[units]
    
    def _linear_interpolation(self, wavelength_nm):
        # Find upper and lower index
        upper_bound = self.df[self.df.index > wavelength_nm].index.min()
        lower_bound = self.df[self.df.index < wavelength_nm].index.max()
        
        # Determine values of surrounding indices
        upper_val = self.df['value'][upper_bound]
        lower_val = self.df['value'][lower_bound]
        
        # Calculate deltas
        delta_lambda = upper_bound - lower_bound
        delta_val = upper_val - lower_val
        
        return lower_val + delta_val*(wavelength_nm - lower_bound)/delta_lambda
    
    def _nearest_interpolation(self, wavelength_nm):
        # Find upper and lower index
        upper_bound = self.df[self.df.index > wavelength_nm].index.min()
        lower_bound = self.df[self.df.index < wavelength_nm].index.max()
        
        # Determine which index is closer
        if (upper_bound - wavelength_nm) < (wavelength_nm - lower_bound):
            return self.df['value'][upper_bound]
        return self.df['value'][lower_bound]
    
    def _lower_interpolation(self, wavelength_nm):
        # Find lower index
        lower_bound = self.df[self.df.index < wavelength_nm].index.max()
        
        return self.df['value'][lower_bound]
    
    def _upper_interpolation(self, wavelength_nm):
        # Find upper index
        upper_bound = self.df[self.df.index > wavelength_nm].index.min()
        
        return self.df['value'][upper_bound]
    
    interpolation_methods = {
        'linear':   _linear_interpolation,
        'nearest':  _nearest_interpolation,
        'lower':    _lower_interpolation,
        'upper':    _upper_interpolation
    }
    
    def __init__(self, values, index, index_units='nm', interpolation=None):
        # Verify lengths match
        if len(values) != len(index):
            print("Warning: Length of values and index must match.")
            return
        
        # Convert inputs to list
        values = [ val for val in values ]
        index = [ spectral_property.to_nm(idx, index_units) for idx in index ]
        
        # Create DataFrame
        self.df = pd.DataFrame()
        self.df['value'] = values
        self.df['wavelength'] = index
        self.df = self.df.set_index('wavelength')
        
        self.interpolation = None
        if interpolation in spectral_property.interpolation_methods:
            self.interpolation = \
                    spectral_property.interpolation_methods[interpolation]
            self.interpolation_type = interpolation
        elif interpolation:
            print("Warning: Specified interpolation type unknown.")
            
    def _get_single(self, wavelength, units):
        # Convert wavelength to nm
        wavelength = spectral_property.to_nm(wavelength, units)
        
        if wavelength in self.df.index:
            # If the value for that wavelength is known, return it
            return self.df['value'][wavelength]
        elif self.interpolation:
            # Check wavelength is within range
            if wavelength < self.df.index.min() or \
               wavelength > self.df.index.max():
                print("Warning: Requested wavelength outside spectrum.")
                return None
            
            # Return interpolated value
            return self.interpolation(self, wavelength)
        
        return None
    
    def __getitem__(self, wavelength, units='nm'):
        if isinstance(wavelength, Iterable):
            return np.array([ self._get_single(wl, units) for wl in wavelength ])
        return self._get_single(wavelength, units)
    
    def to_file(self, filepath, append=False):
        mode = 'w'
        if append:
            mode = 'a'
            
        with open(filepath, mode) as outfile:
            outfile.write(f"interpolation:{self.interpolation_type}\n")
            self.df.to_csv(outfile)
    
    def range(self):
        # Find upper and lower index
        upper_bound = self.df.index.max()
        lower_bound = self.df.index.min()
        
        return (lower_bound, upper_bound)
    
    def scale_values(self, scaling_factor):
        self.df['value'] *= scaling_factor
    
def spectral_albedo_smarts(zen, azm, material, min_wavelength=300,
                           max_wavelength=4000):
    try:
        from pySMARTS.smarts import SMARTSSpectraZenAzm
    except:
        print("Warning: Could not load pySMARTS module.")
        return None
    
    smarts_res = SMARTSSpectraZenAzm('30 31', str(zen), str(azm), material,
                                     min_wvl=str(min_wavelength),
                                     max_wvl=str(max_wavelength))
    
    return spectral_property(smarts_res['Zonal_ground_reflectance'],
                             smarts_res['Wvlgth'], interpolation='linear')

def spectral_irradiance_smarts(zen, azm):
    try:
        from pySMARTS.smarts import SMARTSSpectraZenAzm
    except:
        print("Warning: Could not load pySMARTS module.")
        return None
    
    smarts_res = SMARTSSpectraZenAzm('2 3 4', str(zen), str(azm))
    
    dni_spectrum = spectral_property(smarts_res['Direct_normal_irradiance'],
                                     smarts_res['Wvlgth'], interpolation='linear')
    dhi_spectrum = spectral_property(smarts_res['Difuse_horizn_irradiance'],
                                     smarts_res['Wvlgth'], interpolation='linear')
    ghi_spectrum = spectral_property(smarts_res['Global_horizn_irradiance'],
                                     smarts_res['Wvlgth'], interpolation='linear')
    
    return (dni_spectrum, dhi_spectrum, ghi_spectrum)



def spectral_irradiance_smarts_SRRL( YEAR='2020', MONTH='10', DAY='21',
        HOUR='12.75', LATIT='39.74', LONGIT='-105.17', ALTIT='1.0',
        ZONE='-7', W='0', RH='24.93', TAIR='19.89', SEASON='WINTER',
        TDAY='12.78', SPR='810.373', TAU5='0.1858', TILT='0.0',
        WAZIM='180.0', RHOG='0.2195', HEIGHT='0', 
        material='DryGrass', min_wvl='280', max_wvl='4000',
        IOUT='2 3 4'):

    try:
        from pySMARTS.smarts import SMARTSSRRL
    except:
        print("Warning: Could not load pySMARTS module.")
        return None
    
    smarts_res = SMARTSSRRL(IOUT=IOUT, YEAR=YEAR,MONTH=MONTH,DAY=DAY,HOUR=HOUR, LATIT=LATIT, LONGIT=LONGIT, ALTIT=ALTIT, 
                        ZONE=ZONE, W=W, RH=RH, TAIR=TAIR, SEASON=SEASON, TDAY=TDAY, SPR=SPR, TAU5=TAU5, TILT=TILT, WAZIM=WAZIM,
               RHOG=RHOG, HEIGHT=HEIGHT, material=material, min_wvl=min_wvl, max_wvl=max_wvl)
    
    dni_spectrum = spectral_property(smarts_res['Direct_normal_irradiance'],
                                     smarts_res['Wvlgth'], interpolation='linear')
    dhi_spectrum = spectral_property(smarts_res['Difuse_horizn_irradiance'],
                                     smarts_res['Wvlgth'], interpolation='linear')
    ghi_spectrum = spectral_property(smarts_res['Global_horizn_irradiance'],
                                     smarts_res['Wvlgth'], interpolation='linear')
    
    return (dni_spectrum, dhi_spectrum, ghi_spectrum)



def spectral_albedo_smarts_SRRL(YEAR='2020', MONTH='10', DAY='21',
        HOUR='12.75', LATIT='39.74', LONGIT='-105.17', ALTIT='1.0',
        ZONE='-7', W='0', RH='24.93', TAIR='19.89', SEASON='WINTER',
        TDAY='12.78', SPR='810.373', TAU5='0.1858', TILT='0.0',
        WAZIM='180.0', RHOG='0.2195', HEIGHT='0', 
        material='DryGrass', min_wvl='280', max_wvl='4000',
        IOUT='30 31'):

    try:
        from pySMARTS.smarts import SMARTSSRRL
    except:
        print("Warning: Could not load pySMARTS module.")
        return None

    smarts_res = SMARTSSRRL(IOUT=IOUT, YEAR=YEAR,MONTH=MONTH,DAY=DAY,HOUR=HOUR, LATIT=LATIT, LONGIT=LONGIT, ALTIT=ALTIT, 
                        ZONE=ZONE, W=W, RH=RH, TAIR=TAIR, SEASON=SEASON, TDAY=TDAY, SPR=SPR, TAU5=TAU5, TILT=TILT, WAZIM=WAZIM,
               RHOG=RHOG, HEIGHT=HEIGHT, material=material, min_wvl=min_wvl, max_wvl=max_wvl)
    
    return spectral_property(smarts_res['Zonal_ground_reflectance'],
                             smarts_res['Wvlgth'], interpolation='linear')
    
    

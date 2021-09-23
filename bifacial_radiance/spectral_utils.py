import numpy as np
import pandas as pd
from collections.abc import Iterable
import os
from scipy import integrate


class spectral_property(object):
    """
    WRITE DOCSTRING HERE
    """
    
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
        upper_bound = self.data[self.data.index > wavelength_nm].index.min()
        lower_bound = self.data[self.data.index < wavelength_nm].index.max()
        
        # Determine values of surrounding indices
        upper_val = self.data['value'][upper_bound]
        lower_val = self.data['value'][lower_bound]
        
        # Calculate deltas
        delta_lambda = upper_bound - lower_bound
        delta_val = upper_val - lower_val
        
        return lower_val + delta_val*(wavelength_nm - lower_bound)/delta_lambda
    
    def _nearest_interpolation(self, wavelength_nm):
        # Find upper and lower index
        upper_bound = self.data[self.data.index > wavelength_nm].index.min()
        lower_bound = self.data[self.data.index < wavelength_nm].index.max()
        
        # Determine which index is closer
        if (upper_bound - wavelength_nm) < (wavelength_nm - lower_bound):
            return self.data['value'][upper_bound]
        return self.data['value'][lower_bound]
    
    def _lower_interpolation(self, wavelength_nm):
        # Find lower index
        lower_bound = self.data[self.data.index < wavelength_nm].index.max()
        
        return self.data['value'][lower_bound]
    
    def _upper_interpolation(self, wavelength_nm):
        # Find upper index
        upper_bound = self.data[self.data.index > wavelength_nm].index.min()
        
        return self.data['value'][upper_bound]
    
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
        self.data = pd.DataFrame()
        self.data['value'] = values
        self.data['wavelength'] = index
        self.data = self.data.set_index('wavelength')
        
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
        
        if wavelength in self.data.index:
            # If the value for that wavelength is known, return it
            return self.data['value'][wavelength]
        elif self.interpolation:
            # Check wavelength is within range
            if wavelength < self.data.index.min() or \
               wavelength > self.data.index.max():
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
            self.data.to_csv(outfile)
    
    def range(self):
        # Find upper and lower index
        upper_bound = self.data.index.max()
        lower_bound = self.data.index.min()
        
        return (lower_bound, upper_bound)
    
    def scale_values(self, scaling_factor):
        self.data['value'] *= scaling_factor
    
def spectral_albedo_smarts(zen, azm, material, min_wavelength=300,
                           max_wavelength=4000):

    import pySMARTS
    
    smarts_res = pySMARTS.SMARTSSpectraZenAzm('30 31', str(zen), str(azm), material,
                                     min_wvl=str(min_wavelength),
                                     max_wvl=str(max_wavelength))
    
    return spectral_property(smarts_res['Zonal_ground_reflectance'],
                             smarts_res['Wvlgth'], interpolation='linear')

def spectral_irradiance_smarts(zen, azm, material='LiteSoil', min_wavelength=300,
                           max_wavelength=4000):

    import pySMARTS

    smarts_res = pySMARTS.SMARTSSpectraZenAzm('2 3 4', str(zen), str(azm),
                                     material=material,
                                     min_wvl=str(min_wavelength),
                                     max_wvl=str(max_wavelength))
    
    dni_spectrum = spectral_property(smarts_res['Direct_normal_irradiance'],
                                     smarts_res['Wvlgth'], interpolation='linear')
    dhi_spectrum = spectral_property(smarts_res['Difuse_horizn_irradiance'],
                                     smarts_res['Wvlgth'], interpolation='linear')
    ghi_spectrum = spectral_property(smarts_res['Global_horizn_irradiance'],
                                     smarts_res['Wvlgth'], interpolation='linear')
    
    return (dni_spectrum, dhi_spectrum, ghi_spectrum)



def spectral_irradiance_smarts_SRRL(YEAR, MONTH, DAY, HOUR, ZONE,
                                LATIT, LONGIT, ALTIT,
                                RH, TAIR, SEASON, TDAY, SPR, W,
                                TILT, WAZIM, HEIGHT,
                                ALPHA1, ALPHA2, OMEGL, GG, BETA, TAU5,
                                RHOG, material,
                                IOUT='2 3 4', min_wvl='280', max_wvl='4000'):
    
    import pySMARTS

    smarts_res = pySMARTS.SMARTSSRRL(IOUT=IOUT, YEAR=YEAR,MONTH=MONTH,DAY=DAY,HOUR=HOUR, ZONE=ZONE,
                            LATIT=LATIT, LONGIT=LONGIT, ALTIT=ALTIT, 
                             RH=RH, TAIR=TAIR, SEASON=SEASON, TDAY=TDAY, SPR=SPR, W=W, 
                             TILT=TILT, WAZIM=WAZIM, HEIGHT=HEIGHT,
                             ALPHA1 = ALPHA1, ALPHA2 = ALPHA2, OMEGL = OMEGL,
                             GG = GG, BETA = BETA, TAU5= TAU5, 
                             RHOG=RHOG, material=material, 
                             min_wvl=min_wvl, max_wvl=max_wvl)
    

    dni_spectrum = spectral_property(smarts_res[smarts_res.keys()[1]],
                                     smarts_res['Wvlgth'], interpolation='linear')
    dhi_spectrum = spectral_property(smarts_res[smarts_res.keys()[2]],
                                     smarts_res['Wvlgth'], interpolation='linear')
    ghi_spectrum = spectral_property(smarts_res[smarts_res.keys()[3]],
                                     smarts_res['Wvlgth'], interpolation='linear')
    
    return (dni_spectrum, dhi_spectrum, ghi_spectrum)



def spectral_albedo_smarts_SRRL(YEAR, MONTH, DAY, HOUR, ZONE,
                                LATIT, LONGIT, ALTIT,
                                RH, TAIR, SEASON, TDAY, SPR, W,
                                TILT, WAZIM, HEIGHT, 
                                ALPHA1, ALPHA2, OMEGL, GG, BETA, TAU5,
                                RHOG, material,
                                IOUT='30 31', min_wvl='280', max_wvl='4000'):
 
    import pySMARTS

    smarts_res = pySMARTS.SMARTSSRRL(IOUT=IOUT, YEAR=YEAR,MONTH=MONTH,DAY=DAY,HOUR=HOUR, ZONE=ZONE,
                            LATIT=LATIT, LONGIT=LONGIT, ALTIT=ALTIT, 
                             RH=RH, TAIR=TAIR, SEASON=SEASON, TDAY=TDAY, SPR=SPR, W=W, 
                             TILT=TILT, WAZIM=WAZIM, HEIGHT=HEIGHT,
                             ALPHA1 = ALPHA1, ALPHA2 = ALPHA2, OMEGL = OMEGL,
                             GG = GG, BETA = BETA, TAU5= TAU5,
                             RHOG=RHOG, material=material, 
                             min_wvl=min_wvl, max_wvl=max_wvl)
    
    return spectral_property(smarts_res['Zonal_ground_reflectance'],
                             smarts_res['Wvlgth'], interpolation='linear')
    

def generate_spectra(idx, metdata, material=None, spectra_folder=None, scale_spectra=False,
                scale_albedo=False, scale_albedo_nonspectral_sim=False):
    """
    generate spectral curve for particular material.  Requires pySMARTS 

    Parameters
    ----------
    idx : int
        index of the metdata file to run pySMARTS.
    metdata : bifacial_radiance MetObj
        DESCRIPTION.
    material : string, optional
        type of material for spectral simulation. Options include: Grass, 
        Gravel, etc.     The default is None.
    spectra_folder : path, optional
        location to save spectral data. The default is None.
    scale_spectra : bool, optional
        DESCRIPTION. The default is False.
    scale_albedo : bool, optional
        DESCRIPTION. The default is False.
    scale_albedo_nonspectral_sim : bool, optional
        DESCRIPTION. The default is False.

    Returns
    -------
    spectral_alb : spectral_property class
        spectral_alb.data:  dataframe with frequency and magnitude data.
    spectral_dni : spectral_property class
        spectral_dni.data:  dataframe with frequency and magnitude data.
    spectral_dhi : spectral_property class
        spectral_dhi.data:  dataframe with frequency and magnitude data.

    """
    
    if material is None:
        material = 'Gravel'
    
    # Extract data from metdata
    dni = metdata.dni[idx]
    dhi = metdata.dhi[idx]
    ghi = metdata.ghi[idx]
    try:
        alb = metdata.albedo[idx]
    except TypeError:
        raise Exception("Error - No 'metdata.albedo' value passed.")

    solpos = metdata.solpos.iloc[idx]
    zen = float(solpos.zenith)
    azm = float(solpos.azimuth) - 180
    #lat = metdata.latitude
    #lon = metdata.longitude
    #elev = metdata.elevation / 1000
    #t = metdata.datetime[idx]
    
    # Verify sun up
    if zen > 90:
        print("Sun below horizon. Skipping.")
        return None
    
    # Define file suffix
    # -- CHANGE --
    suffix = f'_{idx:04}.txt'
    
    # Generate/Load dni and dhi
    dni_file = os.path.join(spectra_folder, "dni"+suffix)
    dhi_file = os.path.join(spectra_folder, "dhi"+suffix)
    ghi_file = os.path.join(spectra_folder, "ghi"+suffix)
    spectral_dni, spectral_dhi, spectral_ghi = spectral_irradiance_smarts(zen, azm, min_wavelength=300)
    
    # SCALING:
    # If specifed, scale the irradiance spectra based on their respective
    # measured value.
    if scale_spectra:
        
        dni_scale = dni / spectral_dni.data.apply(lambda g: integrate.trapz(spectral_dni.data.value, x=spectral_dni.data.index))
        dhi_scale = dhi / spectral_dhi.data.apply(lambda g: integrate.trapz(spectral_dhi.data.value, x=spectral_dhi.data.index))
        ghi_scale = ghi / spectral_ghi.data.apply(lambda g: integrate.trapz(spectral_ghi.data.value, x=spectral_ghi.data.index))
        # dni_scale = dni / (10*np.sum(spectral_dni[range(280, 4000, 10)]))
        # dhi_scale = dhi / (10*np.sum(spectral_dhi[range(280, 4000, 10)]))
        # ghi_scale = ghi / (10*np.sum(spectral_ghi[range(280, 2501, 10)]))
        spectral_dni.scale_values(dni_scale.value)
        spectral_dhi.scale_values(dhi_scale.value)
        spectral_ghi.scale_values(ghi_scale.value)
    
    # Write irradiance spectra
    #'''
    spectral_dni.to_file(dni_file)
    spectral_dhi.to_file(dhi_file)
    spectral_ghi.to_file(ghi_file)
    #'''
    
    # Generate/Load albedo
    alb_file = os.path.join(spectra_folder, "alb"+suffix)
    
    if material == 'Seasonal':
        MONTH = metdata.datetime[idx].month
        if 4 <= MONTH <= 7:
            material = 'Grass'
        else:
            material = 'DryGrass'
    spectral_alb = spectral_albedo_smarts(zen, azm, material, min_wavelength=300)
 
    # If specifed, scale the spectral albedo to have a mean value matching the
    # measured albedo.
    if scale_albedo:
        # option A
        denom = spectral_alb.data.value * spectral_ghi.data.value
        # option B
        #denom = spectral_alb.data

        # TODO:
        # Add test to
        if alb > 1 or alb == 0:
            print("albedo measured is an incorrect number, not scaling albedo generated")
        else:
            alb_scale = alb / denom.apply(lambda g: integrate.trapz(denom.values, x=spectral_alb.data.index))
            spectral_alb.scale_values(alb_scale.values)

    if scale_albedo_nonspectral_sim:
        sim_alb = np.sum(spectral_alb[range(280, 2501, 10)] * spectral_ghi[range(280, 2501, 10)])/np.sum(spectral_ghi[range(280, 2501, 10)])
        
        if alb > 1:
            print("albedo measured is an incorrect number, not scaling albedo generated")
        else:
            alb_scale = alb / sim_alb
            spectral_alb.scale_values(alb_scale)
            print(alb, sim_alb, alb_scale)
    
    # Write albedo file
    spectral_alb.to_file(alb_file)
    
    return (spectral_alb, spectral_dni, spectral_dhi)
# -*- coding: utf-8 -*-
"""
Created on Tue April 27 06:29:02 2021

@author: sayala
"""

import pvlib


def calculatePerformance(effective_irradiance, CECMod, temp_amb=None, windspeed=1, temp_cell=None,  glassglass=False):
    '''
    The module parameters are given at the reference condition. 
    Use pvlib.pvsystem.calcparams_cec() to generate the five SDM 
    parameters at your desired irradiance and temperature to use 
    with pvlib.pvsystem.singlediode() to calculate the IV curve information.:
    
    Inputs
    ------
    effective_irradiance : numeric
        Dataframe or single value to calculate. Must be same length as temp_cell
    CECMod : Dict
        Dictionary with CEC Module PArameters for the module selected. Must 
        contain at minimum  alpha_sc, a_ref, I_L_ref, I_o_ref, R_sh_ref,
        R_s, Adjust
    temp_amb : numeric
        Ambient temperature in Celsius. Dataframe or single value to calculate. 
        Must be same length as effective_irradiance.  Default = 20C
    windspeed : numeric
        Wind speed at a height of 10 meters [m/s].  Default = 1 m/s
    temp_cell : numeric
        Back of module temperature.  If provided, overrides temp_amb and 
        windspeed calculation.  Default = None
    glassglass : boolean
        If module is glass-glass package (vs glass-polymer) to select correct
        thermal coefficients for module temperature calculation

    '''
    
    from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS

    if glassglass:
        temp_model_params = ( TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']) # temperature_model_parameters
    else:
        temp_model_params = ( TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_polymer']) # temperature_model_parameters

    if temp_cell is None:
        if temp_amb is None:
            temp_amb  = 20
            
        temp_cell = pvlib.temperature.sapm_cell(effective_irradiance, temp_amb, windspeed, 
                                                temp_model_params['a'], temp_model_params['b'], temp_model_params['deltaT'])

    IL, I0, Rs, Rsh, nNsVth = pvlib.pvsystem.calcparams_cec(
        effective_irradiance=effective_irradiance,
        temp_cell=temp_cell,
        alpha_sc=float(CECMod.alpha_sc),
        a_ref=float(CECMod.a_ref),
        I_L_ref=float(CECMod.I_L_ref),
        I_o_ref=float(CECMod.I_o_ref),
        R_sh_ref=float(CECMod.R_sh_ref),
        R_s=float(CECMod.R_s),
        Adjust=float(CECMod.Adjust)
        )
    
    IVcurve_info = pvlib.pvsystem.singlediode(
        photocurrent=IL,
        saturation_current=I0,
        resistance_series=Rs,
        resistance_shunt=Rsh,
        nNsVth=nNsVth 
        )
    
    return IVcurve_info['p_mp']

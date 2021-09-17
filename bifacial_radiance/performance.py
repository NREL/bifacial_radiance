# -*- coding: utf-8 -*-
"""
Created on Tue April 27 06:29:02 2021

@author: sayala
"""

import pvlib


def calculatePerformance(df, CECMod):
    r'''
    The module parameters are given at the reference condition. 
    Use pvlib.pvsystem.calcparams_cec() to generate the five SDM 
    parameters at your desired irradiance and temperature to use 
    with pvlib.pvsystem.singlediode() to calculate the IV curve information.:
    
    Inputs
    ------
    df : dataframe
        Dataframe with the 'effective_irradiance' columns and 'temp_cell'
        columns.
    CECMod : Dict
        Dictionary with CEC Module PArameters for the module selected. Must 
        contain at minimum  alpha_sc, a_ref, I_L_ref, I_o_ref, R_sh_ref,
        R_s, Adjust
    '''
    
    IL, I0, Rs, Rsh, nNsVth = pvlib.pvsystem.calcparams_cec(
        effective_irradiance=df['effective_irradiance'],
        temp_cell=df['temp_cell'],
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
    
    df['p_mp'] = IVcurve_info['p_mp']
    
    return df

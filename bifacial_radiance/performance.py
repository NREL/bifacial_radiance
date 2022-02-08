# -*- coding: utf-8 -*-
"""
Created on Tue April 27 06:29:02 2021

@author: sayala
"""

import pvlib


def calculatePerformance(effective_irradiance, CECMod, temp_air=None, wind_speed=1, temp_cell=None,  glassglass=False):
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
    temp_air : numeric
        Ambient temperature in Celsius. Dataframe or single value to calculate. 
        Must be same length as effective_irradiance.  Default = 20C
    wind_speed : numeric
        Wind speed at a height of 10 meters [m/s].  Default = 1 m/s
    temp_cell : numeric
        Back of module temperature.  If provided, overrides temp_air and 
        wind_speed calculation.  Default = None
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
        if temp_air is None:
            temp_air  = 25 # STC
            
        temp_cell = pvlib.temperature.sapm_cell(effective_irradiance, temp_air, wind_speed, 
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

def MBD(meas,model):
    """
    This function calculates the MEAN BIAS DEVIATION of measured vs. modeled
    data and returns it as a Percentage [%].

    MBD=100∙[((1⁄(m)∙∑〖(y_i-x_i)]÷[(1⁄(m)∙∑〖x_i]〗)〗)

    Parameters
    ----------
    meas : numeric list
        Measured data.
    model : numeric list
        Modeled data

    Returns
    -------
    out : numeric
        Percentage [%] Mean Bias Deviation between the measured and the modeled data.

    """
    import pandas as pd
    df = pd.DataFrame({'model':model,'meas':meas})
    # rudimentary filtering of modeled irradiance
    df = df.dropna()
    minirr = meas.min()
    df = df[df.model>minirr]
    m = df.__len__()
    out = 100*((1/m)*sum(df.model-df.meas))/df.meas.mean()
    return out

def RMSE(meas,model):
    """
    This function calculates the ROOT MEAN SQUARE ERROR of measured vs. modeled
    data and returns it as a Percentage [%].

    RMSD=100∙〖[(1⁄(m)∙∑▒(y_i-x_i )^2 )]〗^(1⁄2)÷[(1⁄(m)∙∑▒〖x_i]〗)

    Parameters
    ----------
    meas : numeric list
        Measured data.
    model : numeric list
        Modeled data

    Returns
    -------
    out : numeric
        Percentage [%] Root Mean Square Error between the measured and the modeled data.

    """
    
    import numpy as np
    import pandas as pd
    df = pd.DataFrame({'model':model,'meas':meas})
    df = df.dropna()
    minirr = meas.min()
    df = df[df.model>minirr]
    m = df.__len__()
    out = 100*np.sqrt(1/m*sum((df.model-df.meas)**2))/df.meas.mean()
    return out

# residuals absolute output (not %) 
def MBD_abs(meas,model):
    """
    This function calculates the ABSOLUTE MEAN BIAS DEVIATION of measured vs. modeled
    data and returns it as a Percentage [%].

    MBD=100∙[((1⁄(m)∙∑〖(y_i-x_i)]÷[(1⁄(m)∙∑〖x_i]〗)〗)

    Parameters
    ----------
    meas : numeric list
        Measured data.
    model : numeric list
        Modeled data

    Returns
    -------
    out : numeric
        Absolute output residual of the Mean Bias Deviation between the 
        measured and the modeled data.

    """
    
    import pandas as pd
    df = pd.DataFrame({'model':model,'meas':meas})
    # rudimentary filtering of modeled irradiance
    df = df.dropna()
    minirr = meas.min()
    df = df[df.model>minirr]
    m = df.__len__()
    out = ((1/m)*sum(df.model-df.meas))
    return out

def RMSE_abs(meas,model):
    """
    This function calculates the ABSOLUTE ROOT MEAN SQUARE ERROR of measured 
    vs. modeled data and returns it as a Percentage [%].

    RMSD=100∙〖[(1⁄(m)∙∑▒(y_i-x_i )^2 )]〗^(1⁄2)÷[(1⁄(m)∙∑▒〖x_i]〗)

    Parameters
    ----------
    meas : numeric list
        Measured data.
    model : numeric list
        Modeled data

    Returns
    -------
    out : numeric
        Absolute output residual of the Root Mean Square Error between the 
        measured and the modeled data.

    """
    
    #
    import numpy as np
    import pandas as pd
    df = pd.DataFrame({'model':model,'meas':meas})
    df = df.dropna()
    minirr = meas.min()
    df = df[df.model>minirr]
    m = df.__len__()
    out = np.sqrt(1/m*sum((df.model-df.meas)**2))
    return out

    def MAD():
        '''
        Placeholder for MAD function

        Returns
        -------
        None.

        '''
        
        return    

    def electricalMismatch():
        '''
        Placeholder for Electrical Mismatch Equation from PinPV
        Estimating and parameterizing mismatch power loss in bifacial photovoltaic systems
        Chris Deline, Silvana Ayala Pelaez,Sara MacAlpine,Carlos Olalla
        https://doi.org/10.1002/pip.3259 

        '''

    
        return    
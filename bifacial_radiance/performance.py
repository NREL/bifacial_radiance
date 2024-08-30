# -*- coding: utf-8 -*-
"""
Created on Tue April 27 06:29:02 2021

@author: sayala
"""

import pvlib
import pandas as pd

"""
def calculatePerformance(effective_irradiance, CECMod, temp_air=None,
                         wind_speed=1, temp_cell=None,  glassglass=False):
    '''
    DEPRECATED IN FAVOR OF `module.calculatePerformance`
    The module parameters are given at the reference condition.
    Use pvlib.pvsystem.calcparams_cec() to generate the five SDM
    parameters at your desired irradiance and temperature to use
    with pvlib.pvsystem.singlediode() to calculate the IV curve information.:

    Inputs
    ------
    effective_irradiance : numeric
        Dataframe or single value. Must be same length as temp_cell
    CECMod : Dict
        Dictionary with CEC Module Parameters for the module selected. Must
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

    # Setting temperature_model_parameters
    if glassglass:
        temp_model_params = (
            TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass'])
    else:
        temp_model_params = (
            TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_polymer'])

    if temp_cell is None:
        if temp_air is None:
            temp_air = 25  # STC
            
        temp_cell = pvlib.temperature.sapm_cell(effective_irradiance, temp_air, wind_speed, 
                                                temp_model_params['a'], temp_model_params['b'], temp_model_params['deltaT'])
        
    if isinstance(CECMod, pd.DataFrame):
        #CECMod.to_pickle("CECMod.pkl")  
        if len(CECMod) == 1:
            CECMod1 = CECMod.iloc[0] 
        else: 
            print("More than one Module passed. Error, using 1st one")
            CECMod1 = CECMod.iloc[0] 
    else:
        CECMod1 = CECMod
        
    IL, I0, Rs, Rsh, nNsVth = pvlib.pvsystem.calcparams_cec(
        effective_irradiance=effective_irradiance,
        temp_cell=temp_cell,
        alpha_sc=float(CECMod1.alpha_sc),
        a_ref=float(CECMod1.a_ref),
        I_L_ref=float(CECMod1.I_L_ref),
        I_o_ref=float(CECMod1.I_o_ref),
        R_sh_ref=float(CECMod1.R_sh_ref),
        R_s=float(CECMod1.R_s),
        Adjust=float(CECMod1.Adjust)
        )
    
    IVcurve_info = pvlib.pvsystem.singlediode(
        photocurrent=IL,
        saturation_current=I0,
        resistance_series=Rs,
        resistance_shunt=Rsh,
        nNsVth=nNsVth
        )

    return IVcurve_info['p_mp']
"""

def MBD(meas, model):
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
        Percentage [%] Mean Bias Deviation between the measured and the modeled
        data.

    """
    import pandas as pd
    df = pd.DataFrame({'model': model, 'meas': meas})
    # rudimentary filtering of modeled irradiance
    df = df.dropna()
    minirr = meas.min()
    df = df[df.model > minirr]
    m = df.__len__()
    out = 100*((1/m)*sum(df.model-df.meas))/df.meas.mean()
    return out


def RMSE(meas, model):
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
        Percentage [%] Root Mean Square Error between the measured and the
        modeled data.

    """

    import numpy as np
    import pandas as pd
    df = pd.DataFrame({'model': model, 'meas': meas})
    df = df.dropna()
    minirr = meas.min()
    df = df[df.model > minirr]
    m = df.__len__()
    out = 100*np.sqrt(1/m*sum((df.model-df.meas)**2))/df.meas.mean()
    return out


# residuals absolute output (not %)
def MBD_abs(meas, model):
    """
    This function calculates the ABSOLUTE MEAN BIAS DEVIATION of measured vs.
    modeled data and returns it as a Percentage [%].

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
    df = pd.DataFrame({'model': model, 'meas': meas})
    # rudimentary filtering of modeled irradiance
    df = df.dropna()
    minirr = meas.min()
    df = df[df.model > minirr]
    m = df.__len__()
    out = ((1/m)*sum(df.model-df.meas))
    return out


def RMSE_abs(meas, model):
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
    df = pd.DataFrame({'model': model, 'meas': meas})
    df = df.dropna()
    minirr = meas.min()
    df = df[df.model > minirr]
    m = df.__len__()
    out = np.sqrt(1/m*sum((df.model-df.meas)**2))
    return out


def _cleanDataFrameResults(mattype, rearMat, Wm2Front, Wm2Back,
                           fillcleanedSensors=False, agriPV=False):

    import numpy as np

    if agriPV:
        matchers = ['sky', 'pole', 'tube', 'bar', '3267', '1540']
    else:
        matchers = ['sky', 'pole', 'tube', 'bar', 'ground', '3267', '1540']

    maskfront = np.column_stack([mattype[col].str.contains('|'.join(matchers),
                                                           na=False) for col in
                                 mattype])
    Wm2Front[maskfront] = np.nan

    maskback = np.column_stack([rearMat[col].str.contains('|'.join(matchers),
                                                          na=False) for col in
                                rearMat])
    Wm2Back[maskback] = np.nan

    # Filling Nans...
    filledFront = Wm2Front.mean(axis=1)

    if fillcleanedSensors:
        filledBack = Wm2Back.copy().interpolate()
    else:
        filledBack = Wm2Back.copy()  # interpolate()

    return filledFront, filledBack


def calculateResults(module, csvfile=None, results=None,
                     temp_air=None, wind_speed=1, temp_cell=None,
                     CECMod2=None,
                     fillcleanedSensors=False, agriPV=False, **kwargs):
    '''
    Calculate Performance and Mismatch for timestamped data. This routine requires
    CECMod details to have been set with the module using ModuleObj.addCEC.


    Parameters
    ----------
    module : bifacial_radiance.module.ModuleObj
        module object with CEC Module data as dictionary
    csvfile : numeric list
        Compiled Results data
    results : numeric list
        compiled Results data
    temp_air : value or list
        Air temperature for calculating module temperature
    wind_speed : value or list
        Wind tempreatuer for calcluating module temperature
    temp_cell : value or list
        Cell temperature for calculating module performance. If none, module
        temperature is calculated using temp_air and wind_speed
    CECMod2 : dict, optional
        CEC Module data as dictionary, for a monofacial module to be used as
        comparison for Bifacial Gain in Energy using only the calculated front
        Irradiance. If none, same module as CECMod
        is used.
    agriPV : Bool
        Turns off cleaning for ground material

    Returns
    -------
    dfst : dataframe
    Dataframe with the complied and calculated results for the sim, including:
        POA_eff: mean of [(mean of clean Gfront) + clean Grear * bifaciality
                          factor]
        Gfront_mean: mean of clean Gfront
        Grear_mean: mean of clean Grear
        Mismatch: mismatch calculated from the MAD distribution of
                  POA_total
        Pout_raw: power output calculated from POA_total, considers
              wind speed and temp_amb if in trackerdict.
        Pout: power output considering electrical mismatch
        BGG: Bifacial Gain in Irradiance, [Grear_mean*100*bifacialityfactor/
                                           Gfront_mean]
        BGE: Bifacial Gain in Energy, when power is calculated with CECMod2 or
            same module but just the front irradiance as input, so that
            [Pout-Pout_Gfront/Pout_Gfront]

    '''

    from bifacial_radiance import mismatch

    import pandas as pd


    dfst = pd.DataFrame()

    if csvfile is not None:
        data = pd.read_csv(csvfile)
        Wm2Front = data['Wm2Front'].str.strip(
            '[]').str.split(',', expand=True).astype(float)
        Wm2Back = data['Wm2Back'].str.strip(
            '[]').str.split(',', expand=True).astype(float)
        mattype = data['mattype'].str.strip('[]').str.split(',', expand=True)
        rearMat = data['rearMat'].str.strip('[]').str.split(',', expand=True)

        if 'timestamp' in data:
            dfst['timestamp'] = data['timestamp']
        if 'modNum' in data:
            dfst['Module'] = data['modNum']
        if 'rowNum' in data:
            dfst['Row'] = data['rowNum']
        if 'sceneNum' in data:
            dfst['sceneNum'] = data['sceneNum']
    else:
        if results is not None:
            Wm2Front = pd.DataFrame.from_dict(dict(zip(
                results.index, results['Wm2Front']))).T
            Wm2Back = pd.DataFrame.from_dict(dict(zip(
                results.index, results['Wm2Back']))).T
            mattype = pd.DataFrame.from_dict(dict(zip(
                results.index, results['mattype']))).T
            rearMat = pd.DataFrame.from_dict(dict(zip(
                results.index, results['rearMat']))).T

            if 'timestamp' in results:
                dfst['timestamp'] = results['timestamp']
            if 'modNum' in results:
                dfst['module'] = results['modNum']
            if 'rowNum' in results:
                dfst['row'] = results['rowNum']
            if 'sceneNum' in results:
                dfst['sceneNum'] = results['sceneNum']

        else:
            print("Data or file not passed. Ending arrayResults")
            return

    filledFront, filledBack = _cleanDataFrameResults(
        mattype, rearMat, Wm2Front, Wm2Back,
        fillcleanedSensors=fillcleanedSensors, agriPV=agriPV)

    POA = filledBack.apply(lambda x: x*module.bifi + filledFront)

    # Statistics Calculations
    # dfst['MAD/G_Total'] = bifacial_radiance.mismatch.mad_fn(POA.T)
    # 'MAD/G_Total
    dfst['POA_eff'] = POA.mean(axis=1)
    dfst['Grear_mean'] = Wm2Back.mean(axis=1)
    dfst['Gfront_mean'] = Wm2Front.mean(axis=1)

    # dfst['MAD/G_Total**2'] = dfst['MAD/G_Total']**2
    # dfst['stdev'] = POA.std(axis=1)/ dfst['poat']

    dfst['Pout_raw'] = module.calculatePerformance(
        effective_irradiance=dfst['POA_eff'], 
        temp_air=temp_air, wind_speed=wind_speed, temp_cell=temp_cell)
    dfst['Pout_Gfront'] = module.calculatePerformance(
        effective_irradiance=dfst['Gfront_mean'], CECMod=CECMod2,
        temp_air=temp_air, wind_speed=wind_speed, temp_cell=temp_cell)
    dfst['BGG'] = dfst['Grear_mean']*100*module.bifi/dfst['Gfront_mean']
    dfst['BGE'] = ((dfst['Pout_raw'] - dfst['Pout_Gfront']) * 100 /
                   dfst['Pout_Gfront'])
    dfst['Mismatch'] = mismatch.mismatch_fit3(POA.T)
    dfst['Pout'] = dfst['Pout_raw']*(1-dfst['Mismatch']/100)
    dfst['Wind Speed'] = wind_speed
    if "dni" in kwargs:
        dfst['DNI'] = kwargs['dni']
    if "dhi" in kwargs:
        dfst['DHI'] = kwargs['dhi']
    if "ghi" in kwargs:
        dfst['GHI'] = kwargs['ghi']
    dfst['Wind Speed'] = wind_speed

    return dfst


def calculateResultsGencumsky1axis(csvfile=None, results=None,
                                   bifacialityfactor=1.0,
                                   fillcleanedSensors=True, agriPV=False):
    '''
    Compile calculate results for cumulative 1 axis tracking routine

    Parameters
    ----------
    csvfile : numeric list
        Compiled Results data
    results : numeric list
        compiled Results data
    agriPV : Bool
        Turns off cleaning for ground material

    Returns
    -------
    dfst : dataframe
        Dataframe with the complied and calculated results for the sim,
        including: POA_eff: Avg of [(mean of clean Gfront) + clean Grear *
                                    bifaciality factor]
        Gfront_mean: mean of clean Gfront
        Grear_mean: mean of clean Grear
        BGG: Bifacial Gain in Irradiance, [Grear_mean * 100 *
                                           bifacialityfactor/Gfront_mean

    '''

    import pandas as pd

    dfst = pd.DataFrame()

    if csvfile is not None:
        data = pd.read_csv(csvfile)
        Wm2Front = data['Wm2Front'
                        ].str.strip('[]').str.split(',',
                                                    expand=True).astype(float)
        Wm2Back = data['Wm2Back'
                       ].str.strip('[]').str.split(',',
                                                   expand=True).astype(float)
        mattype = data['mattype'
                       ].str.strip('[]').str.split(',',
                                                   expand=True)
        rearMat = data['rearMat'
                       ].str.strip('[]').str.split(',',
                                                   expand=True)

        if 'modNum' in data:
            dfst['module'] = data['modNum']
        if 'rowNum' in data:
            dfst['row'] = data['rowNum']
        if 'sceneNum' in data:
            dfst['sceneNum'] = data['sceneNum']
    else:
        if results is not None:
            Wm2Front = pd.DataFrame.from_dict(dict(zip(
                results.index, results['Wm2Front']))).T
            Wm2Back = pd.DataFrame.from_dict(dict(zip(
                results.index, results['Wm2Back']))).T
            mattype = pd.DataFrame.from_dict(dict(zip(
                results.index, results['mattype']))).T
            rearMat = pd.DataFrame.from_dict(dict(zip(
                results.index, results['rearMat']))).T

            if 'modNum' in results:
                dfst['module'] = results['modNum']
            if 'rowNum' in results:
                dfst['row'] = results['rowNum']
            if 'sceneNum' in results:
                dfst['sceneNum'] = results['sceneNum']
                

        else:
            print("Data or file not passed. Ending calculateResults")
            return

    # Data gets cleaned but need to maintain same number of sensors
    # due to adding for the various tracker angles.
    filledFront, filledBack = _cleanDataFrameResults(
        mattype, rearMat, Wm2Front, Wm2Back,
        fillcleanedSensors=fillcleanedSensors, agriPV=agriPV)
    cumFront = []
    cumBack = []
    cumRow = []
    cumMod = []
    Grear_mean = []
#    Gfront_mean = []
    POA_eff = []

    # NOTE change 26.07.22 'row' -> 'rowNum' and 'mod' -> 'ModNumber
    # NOTE change March 13 2024 ModNumber -> modNum
    for rownum in results['rowNum'].unique():
        for modnum in results['modNum'].unique():
            mask = (results['rowNum'] == rownum) & (
                results['modNum'] == modnum)
            cumBack.append(list(filledBack[mask].sum(axis=0)))
            cumFront.append(filledFront[mask].sum(axis=0))
            cumRow.append(rownum)
            cumMod.append(modnum)

            # Maybe this would be faster by first doing the DF with the above,
            # exploding the column and calculating.
            POA_eff.append(list(
                (filledBack[mask].apply(lambda x: x*bifacialityfactor +
                                        filledFront[mask])).sum(axis=0)))
            Grear_mean.append(filledBack[mask].sum(axis=0).mean())
            # Gfront_mean.append(filledFront[mask].sum(axis=0).mean())

    dfst = pd.DataFrame(zip(cumRow, cumMod, cumFront, cumBack, Grear_mean,
                            POA_eff), columns=('row', 'module', 'Gfront_mean',
                                               'Wm2Back', 'Grear_mean',
                                               'POA_eff'))

    dfst['BGG'] = dfst['Grear_mean']*100*bifacialityfactor/dfst['Gfront_mean']

    # Reordering columns
    cols = ['row', 'module', 'BGG', 'Gfront_mean', 'Grear_mean', 'POA_eff',
            'Wm2Back']
    dfst = dfst[cols]

    return dfst

# -*- coding: utf-8 -*-


def readepw(filename=None):
    '''
    Reads an EPW file into a pandas dataframe.
    
    Function tested with EnergyPlus weather data files: 
    https://energyplus.net/weather

    Parameters
    ----------
    filename : None or string
        If None, attempts to use a Tkinter file browser. A string can be
        a relative file path, absolute file path, or url.

    Returns
    -------
    Tuple of the form (data, metadata).

    data : DataFrame
        A pandas dataframe with the columns described in the table
        below. 

    metadata : dict
        The site metadata available in the file.

    Notes
    -----

    The returned structures have the following fields.

    =======================================================================
    Data field                       
    =======================================================================
    Datetime data
    Dry bulb temperature in Celsius at indicated time
    Dew point temperature in Celsius at indicated time
    Relative humidity in percent at indicated time
    Atmospheric station pressure in Pa at indicated time
    Extraterrestrial horizontal radiation in Wh/m2
    Extraterrestrial direct normal radiation in Wh/m2
    Horizontal infrared radiation intensity in Wh/m2
    Global horizontal radiation in Wh/m2
    Direct normal radiation in Wh/m2
    Diffuse horizontal radiation in Wh/m2
    Averaged global horizontal illuminance in lux during minutes preceding the indicated time
    Direct normal illuminance in lux during minutes preceding the indicated time
    Diffuse horizontal illuminance in lux  during minutes preceding the indicated time
    Zenith luminance in Cd/m2 during minutes preceding the indicated time
    Wind direction at indicated time. N=0, E=90, S=180, W=270
    Wind speed in m/s at indicated time
    Total sky cover at indicated time
    Opaque sky cover at indicated time
    Visibility in km at indicated time
    Ceiling height in m
    Present weather observation
    Present weather codes
    Precipitable water in mm
    Aerosol optical depth
    Snow depth in cm
    Days since last snowfall
    Albedo
    Liquid precipitation depth in mm at indicated time
    Liquid precipitation quantity
    =======================================================================

    ===============   ======  ===================
    key               format  description
    ===============   ======  ===================
    altitude          Float   site elevation
    latitude          Float   site latitudeitude
    longitude         Float   site longitudeitude
    Name              String  site name
    State             String  state
    TZ                Float   UTC offset
    USAF              Int     USAF identifier
    ===============   ======  ===================
    
    S. Quoilin, October 2017
    Downloaded from PVLib issue tracker on 3/16/18
    https://github.com/pvlib/pvlib-python/issues/261
    '''
    import pandas as pd
    def _interactive_load():
        import Tkinter
        from tkFileDialog import askopenfilename
        Tkinter.Tk().withdraw() #Start interactive file input
        return askopenfilename()

    if filename is None:
        try:
            filename = _interactive_load()
        except:
            raise Exception('Interactive load failed. Tkinter not supported on this system. Try installing X-Quartz and reloading')

    head = ['dummy0', 'Name', 'dummy1', 'State', 'dummy2', 'USAF', 'latitude', 'longitude', 'TZ', 'altitude']

    csvdata = open(filename, 'r')

    # read in file metadata
    temp = dict(zip(head, csvdata.readline().rstrip('\n').split(",")))

    # convert metadata strings to numeric types
    meta = {}
    meta['Name'] = temp['Name']
    meta['State'] = temp['State']
    meta['altitude'] = float(temp['altitude'])
    meta['latitude'] = float(temp['latitude'])
    meta['longitude'] = float(temp['longitude'])
    meta['TZ'] = float(temp['TZ'])
    try:
        meta['USAF'] = int(temp['USAF'])
    except:
        meta['USAF'] = None

    headers = ["year","month","day","hour","min","Dry bulb temperature in C","Dew point temperature in C","Relative humidity in percent","Atmospheric pressure in Pa","Extraterrestrial horizontal radiation in Wh/m2","Extraterrestrial direct normal radiation in Wh/m2","Horizontal infrared radiation intensity in Wh/m2","Global horizontal radiation in Wh/m2","Direct normal radiation in Wh/m2","Diffuse horizontal radiation in Wh/m2","Averaged global horizontal illuminance in lux during minutes preceding the indicated time","Direct normal illuminance in lux during minutes preceding the indicated time","Diffuse horizontal illuminance in lux  during minutes preceding the indicated time","Zenith luminance in Cd/m2 during minutes preceding the indicated time","Wind direction. N=0, E=90, S=180, W=270","Wind speed in m/s","Total sky cover","Opaque sky cover","Visibility in km","Ceiling height in m","Present weather observation","Present weather codes","Precipitable water in mm","Aerosol optical depth","Snow depth in cm","Days since last snowfall","Albedo","Liquid precipitation depth in mm","Liquid precipitation quantity"]
    Data = pd.read_csv(filename, skiprows=8,header=None)
    del Data[5]
    Data.columns = headers
    Data.index = pd.to_datetime(Data[["year","month","day","hour"]])

    Data = Data.tz_localize(int(meta['TZ']*3600))

    return Data, meta
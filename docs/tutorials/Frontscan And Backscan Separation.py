#!/usr/bin/env python
# coding: utf-8

# ## Separating Frontscan and Backscan for different number of Sensors

# The key ideas here are:
# 
# - Functions like moduleAnalysis() returns two identically structured dictionaries that contain the keys like xstart, ystart, zstart, xinc, yinc, zinc, Nx, Ny, Nz, orientation. For the function arguments like sensorsy or sensorsx, there is an assumption that those will be equal for both the front and back surface.
# 
# - We need to develop a separate function, pretty much functionally parallel with moduleAnalysis() to bring out the frontscan and backscan separately.....may be two distinct functions with distinct arguments for frontscan() and backscan()
# 
# - The new functions will have variables passed on as arguments which can be different for front and back

# In[20]:


import bifacial_radiance
import numpy as np
import os
from pathlib import Path

testfolder = str(Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP')


# In[2]:


demo = bifacial_radiance.RadianceObj('SimRowScan', testfolder) 


# In[3]:


x = 2
y = 1
xgap = 0.02
ygap = 0.15
zgap = 0.10
numpanels = 1
offsetfromaxis = True
Ny = numpanels
axisofrotationTorqueTube = True
frameParams = None
omegaParams = None
diam = 0.1


# In[4]:


module_type = 'TEST'
nMods = 3
nRows = 2
sceneDict = {'tilt':0, 'pitch':6, 'clearance_height':3,'azimuth':90, 'nMods': nMods, 'nRows': nRows} 


# In[5]:


demo.setGround(0.2)
epwfile = demo.getEPW(lat = 37.5, lon = -77.6)
metdata = demo.readWeatherFile(epwfile, coerce_year = 2021)
demo.gendaylit(4020)


# In[9]:


demo.makeModule(name=module_type,x=x, y=y, torquetube = True, 
                    diameter = diam, xgap = xgap, ygap = ygap, zgap = zgap, 
                    numpanels = Ny, omegaParams=None,
                    axisofrotationTorqueTube=axisofrotationTorqueTube)


# In[10]:


scene = demo.makeScene(module_type,sceneDict)
octfile = demo.makeOct()
analysis = bifacial_radiance.AnalysisObj()  # return an analysis object including the scan dimensions for back irradiance


# In[29]:


name = 'FrontScanTest'
rowWanted = 1
modWanted = 2
sensorsy = 3
sensorsx = 3


# In[30]:


def frontscan(scene, modWanted=None, rowWanted=None,
                       sensorsy=9.0, sensorsx = 1, frontsurfaceoffset=0.001, 
                        modscanfront=None, debug=False):
    if sensorsy >0:
            sensorsy = sensorsy * 1.0
    else:
        raise Exception('input sensorsy must be numeric >0')

    dtor = np.pi/180.0

    # Internal scene parameters are stored in scene.sceneDict. Load these into local variables
    sceneDict = scene.sceneDict
    #moduleDict = scene.moduleDict  # not needed?


    azimuth = sceneDict['azimuth']
    tilt = sceneDict['tilt']
    nMods = sceneDict['nMods']
    nRows = sceneDict['nRows']
    originx = sceneDict['originx']
    originy = sceneDict['originy']

   # offset = moduleDict['offsetfromaxis']
    offset = scene.offsetfromaxis
    sceney = scene.sceney
    scenex = scene.scenex

    ## Check for proper input variables in sceneDict
    if 'pitch' in sceneDict:
        pitch = sceneDict['pitch']
    elif 'gcr' in sceneDict:
        pitch = sceney / sceneDict['gcr']
    else:
        raise Exception("Error: no 'pitch' or 'gcr' passed in sceneDict" )

    if 'axis_tilt' in sceneDict:
        axis_tilt = sceneDict['axis_tilt']
    else:
        axis_tilt = 0

    if 'z' in scene.moduleDict:
        modulez = scene.moduleDict['z']
    else:
        print ("Module's z not set on sceneDict internal dictionary. Setting to default")
        modulez = 0.02

    if frontsurfaceoffset is None:
        frontsurfaceoffset = 0.001

    # The Sensor routine below needs a "hub-height", not a clearance height.
    # The below complicated check checks to see if height (deprecated) is passed,
    # and if clearance_height or hub_height is passed as well.

    # height internal variable defined here is equivalent to hub_height.
    if 'hub_height' in sceneDict:
        height = sceneDict['hub_height']

        if 'height' in sceneDict:
            print ("sceneDict warning: 'height' is deprecated, using "
                   "'hub_height' and deleting 'height' from sceneDict.")
            del sceneDict['height']

        if 'clearance_height' in sceneDict:
            print ("sceneDict warning: 'hub_height' and 'clearance_height"
                   "' passed to moduleAnalysis(). Using 'hub_height' "
                   "instead of 'clearance_height'")
    else:
        if 'clearance_height' in sceneDict:
            height = sceneDict['clearance_height'] + 0.5*                 np.sin(abs(tilt) * np.pi / 180) *                 sceney - offset*np.sin(abs(tilt)*np.pi/180)

            if 'height' in sceneDict:
                print("sceneDict warning: 'height' is deprecated, using"
                      " 'clearance_height' for moduleAnalysis()")
                del sceneDict['height']
        else:
            if 'height' in sceneDict:
                print("sceneDict warning: 'height' is deprecated. "
                      "Assuming this was clearance_height that was passed"
                      " as 'height' and renaming it in sceneDict for "
                      "moduleAnalysis()")
                height = (sceneDict['height'] + 0.5* np.sin(abs(tilt) * 
                                  np.pi / 180) * sceney - offset * 
                                  np.sin(abs(tilt)*np.pi/180) )
            else:
                print("Isue with moduleAnalysis routine. No hub_height "
                      "or clearance_height passed (or even deprecated "
                      "height!)")

    if debug:
        print("For debug:\n hub_height, Azimuth, Tilt, nMods, nRows, "
              "Pitch, Offset, SceneY, SceneX")
        print(height, azimuth, tilt, nMods, nRows,
              pitch, offset, sceney, scenex)

    if modWanted == 0:
        print( " FYI Modules and Rows start at index 1. "
              "Reindexing to modWanted 1"  )
        modWanted = modWanted+1  # otherwise it gives results on Space.

    if rowWanted ==0:
        print( " FYI Modules and Rows start at index 1. "
              "Reindexing to rowWanted 1"  )
        rowWanted = rowWanted+1

    if modWanted is None:
        modWanted = round(nMods / 1.99)
    if rowWanted is None:
        rowWanted = round(nRows / 1.99)

    if debug is True:
        print( f"Sampling: modWanted {modWanted}, rowWanted {rowWanted} "
              "out of {nMods} modules, {nRows} rows" )
    
    x0 = (modWanted-1)*scenex - (scenex*(round(nMods/1.99)*1.0-1))
    y0 = (rowWanted-1)*pitch - (pitch*(round(nRows / 1.99)*1.0-1))

    x1 = x0 * np.cos ((180-azimuth)*dtor) - y0 * np.sin((180-azimuth)*dtor)
    y1 = x0 * np.sin ((180-azimuth)*dtor) + y0 * np.cos((180-azimuth)*dtor)
    z1 = 0
    
    if axis_tilt != 0 and azimuth == 90:
            print ("fixing height for axis_tilt")
            #TODO check might need to do half a module more?
            z1 = (modWanted-1)*scenex * np.sin(axis_tilt*dtor)

    # Edge of Panel
    x2 = (sceney/2.0) * np.cos((tilt)*dtor) * np.sin((azimuth)*dtor)
    y2 = (sceney/2.0) * np.cos((tilt)*dtor) * np.cos((azimuth)*dtor)
    z2 = -(sceney/2.0) * np.sin(tilt*dtor)


    # Axis of rotation Offset (if offset is not 0) for the front of the module
    x3 = (offset + modulez + frontsurfaceoffset) * np.sin(tilt*dtor) * np.sin((azimuth)*dtor)
    y3 = (offset + modulez + frontsurfaceoffset) * np.sin(tilt*dtor) * np.cos((azimuth)*dtor)
    z3 = (offset + modulez + frontsurfaceoffset) * np.cos(tilt*dtor)

    xstartfront = x1 + x2 + x3 + originx

    ystartfront = y1 + y2 + y3 + originy

    zstartfront = height + z1 + z2 + z3

    #Adjust orientation of scan depending on tilt & azimuth
    zdir = np.cos((tilt)*dtor)
    ydir = np.sin((tilt)*dtor) * np.cos((azimuth)*dtor)
    xdir = np.sin((tilt)*dtor) * np.sin((azimuth)*dtor)

    front_orient = '%0.3f %0.3f %0.3f' % (-xdir, -ydir, -zdir)

    #IF cellmodule:
    if scene.moduleDict['cellModule'] is not None and sensorsy == scene.moduleDict['cellModule']['numcellsy']*1.0:
        xinc = -((sceney - scene.moduleDict['cellModule']['ycell']) / (scene.moduleDict['cellModule']['numcellsy']-1)) * np.cos((tilt)*dtor) * np.sin((azimuth)*dtor)
        yinc = -((sceney - scene.moduleDict['cellModule']['ycell']) / (scene.moduleDict['cellModule']['numcellsy']-1)) * np.cos((tilt)*dtor) * np.cos((azimuth)*dtor)
        zinc = ((sceney - scene.moduleDict['cellModule']['ycell']) / (scene.moduleDict['cellModule']['numcellsy']-1)) * np.sin(tilt*dtor)
        
        firstsensorxstartfront = xstartfront  - scene.moduleDict['cellModule']['ycell']/2 * np.cos((tilt)*dtor) * np.sin((azimuth)*dtor)
        firstsensorystartfront = ystartfront - scene.moduleDict['cellModule']['ycell']/2 * np.cos((tilt)*dtor) * np.cos((azimuth)*dtor)
        firstsensorzstartfront = zstartfront + scene.moduleDict['cellModule']['ycell']/2  * np.sin(tilt*dtor)

    else:        
        xinc = -(sceney/(sensorsy + 1.0)) * np.cos((tilt)*dtor) * np.sin((azimuth)*dtor)
        yinc = -(sceney/(sensorsy + 1.0)) * np.cos((tilt)*dtor) * np.cos((azimuth)*dtor)
        zinc = (sceney/(sensorsy + 1.0)) * np.sin(tilt*dtor)
        
        firstsensorxstartfront = xstartfront+xinc
        
        if sensorsx>1:
            start_shift = -x/(sensorsx+1)
            if azimuth == 180:
                firstsensorxstartfront += x/2 + start_shift
                
        firstsensorystartfront = ystartfront+yinc
        
        if sensorsx>1:
            start_shift = -x/(sensorsx+1)
            if azimuth == 90:
                firstsensorystartfront += x/2 + start_shift
                
        firstsensorzstartfront = zstartfront + zinc
        
    
    frontscan = {'xstart':firstsensorxstartfront, 'ystart': firstsensorystartfront,
                 'zstart': firstsensorzstartfront,
                 'xinc':xinc, 'yinc': yinc,
                 'zinc':zinc, 'Nx':sensorsx, 'Ny':sensorsy, 'Nz':1, 'orient':front_orient }

    if modscanfront is not None:
        frontscan = _modDict(frontscan, modscanfront)
        
    return frontscan


# In[31]:


front_dict = backscan(scene = scene, modWanted=modWanted, rowWanted=rowWanted,
                       sensorsy=sensorsy, sensorsx=sensorsx)


# In[32]:


front_dict


# In[11]:


name = 'BackScanTest'
rowWanted = 2
modWanted = 2
sensorsy = 2
sensorsx = 2


# In[22]:


def backscan(scene, modWanted=None, rowWanted=None,
                       sensorsy=9.0, sensorsx = 1, backsurfaceoffset=0.001, 
                        modscanback=None, debug=False):
    if sensorsy >0:
            sensorsy = sensorsy * 1.0
    else:
        raise Exception('input sensorsy must be numeric >0')

    dtor = np.pi/180.0

    # Internal scene parameters are stored in scene.sceneDict. Load these into local variables
    sceneDict = scene.sceneDict
    #moduleDict = scene.moduleDict  # not needed?


    azimuth = sceneDict['azimuth']
    tilt = sceneDict['tilt']
    nMods = sceneDict['nMods']
    nRows = sceneDict['nRows']
    originx = sceneDict['originx']
    originy = sceneDict['originy']

   # offset = moduleDict['offsetfromaxis']
    offset = scene.offsetfromaxis
    sceney = scene.sceney
    scenex = scene.scenex

    ## Check for proper input variables in sceneDict
    if 'pitch' in sceneDict:
        pitch = sceneDict['pitch']
    elif 'gcr' in sceneDict:
        pitch = sceney / sceneDict['gcr']
    else:
        raise Exception("Error: no 'pitch' or 'gcr' passed in sceneDict" )

    if 'axis_tilt' in sceneDict:
        axis_tilt = sceneDict['axis_tilt']
    else:
        axis_tilt = 0

    if 'z' in scene.moduleDict:
        modulez = scene.moduleDict['z']
    else:
        print ("Module's z not set on sceneDict internal dictionary. Setting to default")
        modulez = 0.02

    if backsurfaceoffset is None:
        backsurfaceoffset = 0.001

    # The Sensor routine below needs a "hub-height", not a clearance height.
    # The below complicated check checks to see if height (deprecated) is passed,
    # and if clearance_height or hub_height is passed as well.

    # height internal variable defined here is equivalent to hub_height.
    if 'hub_height' in sceneDict:
        height = sceneDict['hub_height']

        if 'height' in sceneDict:
            print ("sceneDict warning: 'height' is deprecated, using "
                   "'hub_height' and deleting 'height' from sceneDict.")
            del sceneDict['height']

        if 'clearance_height' in sceneDict:
            print ("sceneDict warning: 'hub_height' and 'clearance_height"
                   "' passed to moduleAnalysis(). Using 'hub_height' "
                   "instead of 'clearance_height'")
    else:
        if 'clearance_height' in sceneDict:
            height = sceneDict['clearance_height'] + 0.5*                 np.sin(abs(tilt) * np.pi / 180) *                 sceney - offset*np.sin(abs(tilt)*np.pi/180)

            if 'height' in sceneDict:
                print("sceneDict warning: 'height' is deprecated, using"
                      " 'clearance_height' for moduleAnalysis()")
                del sceneDict['height']
        else:
            if 'height' in sceneDict:
                print("sceneDict warning: 'height' is deprecated. "
                      "Assuming this was clearance_height that was passed"
                      " as 'height' and renaming it in sceneDict for "
                      "moduleAnalysis()")
                height = (sceneDict['height'] + 0.5* np.sin(abs(tilt) * 
                                  np.pi / 180) * sceney - offset * 
                                  np.sin(abs(tilt)*np.pi/180) )
            else:
                print("Isue with moduleAnalysis routine. No hub_height "
                      "or clearance_height passed (or even deprecated "
                      "height!)")

    if debug:
        print("For debug:\n hub_height, Azimuth, Tilt, nMods, nRows, "
              "Pitch, Offset, SceneY, SceneX")
        print(height, azimuth, tilt, nMods, nRows,
              pitch, offset, sceney, scenex)

    if modWanted == 0:
        print( " FYI Modules and Rows start at index 1. "
              "Reindexing to modWanted 1"  )
        modWanted = modWanted+1  # otherwise it gives results on Space.

    if rowWanted ==0:
        print( " FYI Modules and Rows start at index 1. "
              "Reindexing to rowWanted 1"  )
        rowWanted = rowWanted+1

    if modWanted is None:
        modWanted = round(nMods / 1.99)
    if rowWanted is None:
        rowWanted = round(nRows / 1.99)

    if debug is True:
        print( f"Sampling: modWanted {modWanted}, rowWanted {rowWanted} "
              "out of {nMods} modules, {nRows} rows" )
    
    x0 = (modWanted-1)*scenex - (scenex*(round(nMods/1.99)*1.0-1))
    y0 = (rowWanted-1)*pitch - (pitch*(round(nRows / 1.99)*1.0-1))

    x1 = x0 * np.cos ((180-azimuth)*dtor) - y0 * np.sin((180-azimuth)*dtor)
    y1 = x0 * np.sin ((180-azimuth)*dtor) + y0 * np.cos((180-azimuth)*dtor)
    z1 = 0
    
    if axis_tilt != 0 and azimuth == 90:
            print ("fixing height for axis_tilt")
            #TODO check might need to do half a module more?
            z1 = (modWanted-1)*scenex * np.sin(axis_tilt*dtor)

    # Edge of Panel
    x2 = (sceney/2.0) * np.cos((tilt)*dtor) * np.sin((azimuth)*dtor)
    y2 = (sceney/2.0) * np.cos((tilt)*dtor) * np.cos((azimuth)*dtor)
    z2 = -(sceney/2.0) * np.sin(tilt*dtor)


    # Axis of rotation Offset, for the back of the module 
    x4 = (offset - backsurfaceoffset) * np.sin(tilt*dtor) * np.sin((azimuth)*dtor)
    y4 = (offset - backsurfaceoffset) * np.sin(tilt*dtor) * np.cos((azimuth)*dtor)
    z4 = (offset - backsurfaceoffset) * np.cos(tilt*dtor)

    xstartback = x1 + x2 + x4 + originx

    ystartback = y1 + y2 + y4 + originy

    zstartback = height + z1 + z2 + z4

    #Adjust orientation of scan depending on tilt & azimuth
    zdir = np.cos((tilt)*dtor)
    ydir = np.sin((tilt)*dtor) * np.cos((azimuth)*dtor)
    xdir = np.sin((tilt)*dtor) * np.sin((azimuth)*dtor)

    back_orient = '%0.3f %0.3f %0.3f' % (xdir, ydir, zdir)

    #IF cellmodule:
    if scene.moduleDict['cellModule'] is not None and sensorsy == scene.moduleDict['cellModule']['numcellsy']*1.0:
        xinc = -((sceney - scene.moduleDict['cellModule']['ycell']) / (scene.moduleDict['cellModule']['numcellsy']-1)) * np.cos((tilt)*dtor) * np.sin((azimuth)*dtor)
        yinc = -((sceney - scene.moduleDict['cellModule']['ycell']) / (scene.moduleDict['cellModule']['numcellsy']-1)) * np.cos((tilt)*dtor) * np.cos((azimuth)*dtor)
        zinc = ((sceney - scene.moduleDict['cellModule']['ycell']) / (scene.moduleDict['cellModule']['numcellsy']-1)) * np.sin(tilt*dtor)
        
        firstsensorxstartback = xstartback  - scene.moduleDict['cellModule']['ycell']/2 * np.cos((tilt)*dtor) * np.sin((azimuth)*dtor)
        firstsensorystartback = ystartback - scene.moduleDict['cellModule']['ycell']/2 * np.cos((tilt)*dtor) * np.cos((azimuth)*dtor)
        firstsensorzstartback = zstartback + scene.moduleDict['cellModule']['ycell']/2  * np.sin(tilt*dtor)

    else:        
        xinc = -(sceney/(sensorsy + 1.0)) * np.cos((tilt)*dtor) * np.sin((azimuth)*dtor)
        yinc = -(sceney/(sensorsy + 1.0)) * np.cos((tilt)*dtor) * np.cos((azimuth)*dtor)
        zinc = (sceney/(sensorsy + 1.0)) * np.sin(tilt*dtor)
        
        firstsensorxstartback = xstartback+xinc
        
        if sensorsx>1:
            start_shift = -x/(sensorsx+1)
            if azimuth == 180:
                firstsensorxstartback += x/2 + start_shift
                
        firstsensorystartback = ystartback+yinc
        
        if sensorsx>1:
            start_shift = -x/(sensorsx+1)
            if azimuth == 90:
                firstsensorystartback += x/2 + start_shift
                
        firstsensorzstartback = zstartback + zinc
        
    
    backscan = {'xstart':firstsensorxstartback, 'ystart': firstsensorystartback,
                 'zstart': firstsensorzstartback,
                 'xinc':xinc, 'yinc': yinc,
                 'zinc':zinc, 'Nx':sensorsx, 'Ny':sensorsy, 'Nz':1, 'orient':back_orient }

    if modscanback is not None:
        backscan = _modDict(backscan, modscanback)
        
    return backscan


# In[23]:


back_dict = backscan(scene = scene, modWanted=modWanted, rowWanted=rowWanted,
                       sensorsy=sensorsy, sensorsx=sensorsx)


# In[24]:


back_dict


# In[ ]:





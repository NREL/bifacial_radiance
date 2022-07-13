#!/usr/bin/env python
# coding: utf-8

# In[ ]:


rtrace
-reflux matrix on top of rcontrib ??
-Sesnor points and sky -- -coefficient based mehtods, instead of 
-Then animate the sky 
-View factor 3D

-
-
--> 

bug fi

-gendaymatrix --> -a option that gendaymatrix works like gencumsky (cumulate averaged sky) 
-rcontrib 



# In[ ]:


rcontrib --> 

--Finding the example of performance for the CEC -- :


# In[ ]:


1-ad      number of bounces (rtrace)
coefficient base: every ray samles enough to get exposure otherwise view is very noisy.. values lower than get from rtrace.
    get_ipython().set_next_input('    Set up parameters correctly');get_ipython().run_line_magic('pinfo2', 'correctly')
    -secret link to parametric jobs to see effect.

-radiance_image prep --->  image parameters

github.com/ladybug-tools/honeybee

ladybug.tools/radiance/image-parameters 

ab = real...  c not even a parameters. ab is not as important as use to be 

rtrace
rcontrib ---> 
rflux matrix


Mostapha Roudsari --> 
Chris -->  

-Perofrmance py example           -=-- CEC ... etc .
-Send some slides of the PAR calculations and metrics that we use
-Mostapha - send link to sample files for running two-phase biphase --- PDF. (just two-phase)
-View Factor --> ::: dynamic. 
-Pre-sampling         




# # Single hour or Cumulative Approach

# In[ ]:


demo = bifacial_radiance.RadianceObj('Example_AgriPV', r'C:\users\sayala\Documents\Examples\')   # Title of the simulation and path to save files
epwfile = demo.getEPW(lat = 37.5, lon = -77.6)  # Pull in meteorological data using pyEPW for any global lat/lon
demo.setGround(0.2)  # Albedo -- grass is around 20% reflectance. If empty it'll use the hourly default in the weather file for hourly sims.                                                                     
metdata = demo.readWeatherFile(epwfile, coerce_year=2021) 
fullYear = False
if fullYear:
    demo.genCumSky() # entire year.
else:
    timeindex = metdata.datetime.index(pd.to_datetime('2001-06-17 12:0:0 -7'))
    demo.gendaylit(timeindex) 
module = demo.makeModule(name='Longi',x=1.695, y=0.984)  # Many more characteristics can be addedp rogramatically
sceneDict = {'tilt':10,'pitch':3,'clearance_height':0.2,'azimuth':180, 'nMods': 1, 'nRows': 1}  # Some other roptions of inputs availalbe as well
scene = demo.makeScene(module,sceneDict)
octfile = demo.makeOct()  
analysis = AnalysisObj(octfile, demo.basename)
frontscan, backscan = analysis.moduleAnalysis(scene=scene,sensorsx = [1, 1],sensorsy=[10, 10])

# This part needs is set to become an internal routine for Ground study:
groundscan = frontscan.copy() 
groundscan['zstart'] = 0.05 # Place sensors close to the ground
groundscan['zinc'] = 0  # Do not move sensors up following the tilt of the panel, as the ground is flat.
groundscan['orient'] = '0 0 -1'  # Orient sensors excatly down 
groundscan['yinc'] = 3/9  # 3 pitch divided by (10-1) sensors -- increase the spacing between samples so it goes from one row to the next. 

analysis.analysis(octfile, name=sim_name+'_Module_Analysis', frontscan=frontscan, backscan=backscan)
analysis.analysis(octfile, name=sim_name+'_Ground_Analysis', frontscan=groundscan, backscan=backscan)                                     


# Other things that you can do on this approach:
#     <ul>
# <li>    xgap, ygap, number of modules in collector (i.e. 3-up), automatic torquetube addition
# <li>    Have multiple configurations of rows, using a sceneObj for each one with different originx and originy locations
# <li>    Routines to add piles and custom objects
# <li>    Routines for analyzing irradinace on the slope or the full area of any panel in the array, etc. with as much resolution as wanted (defualt is slope, 9 sampling points (a.k.a. 'sensors') 
# <li>    Irradiance to Performance routines (need to read results and call function)

# # Single hour or Cumulative Approach

# Other things that you can do on this approach:
# 
# <ul> 
#     <li> Improvements:
# <ul> 
#         <li>  Automatic Irradiance to Performance routines, Shading Factor and Edge Effecs calculations, which get saved nicely in a 'compiled results' excel
# </ul> 
#         
# <li>     Same as above
# <ul> 
#    <li>  -xgap, ygap, number of modules in collector (i.e. 3-up), automatic torquetube addition
#     <li> -Routines for analyzing irradinace on the slope or the full area of any panel in the array, etc. with as much resolution as wanted (defualt is slope, 9 sampling points (a.k.a. 'sensors') 
# </ul> 
#                                                                                                                                         
# <li>     Not as above:
# <ul> 
#     <li>     -Can't have multiple configurations of rows (no multiple sceneObj supported at the moment)
#     <li> -xgap, ygap, number of modules in collector (i.e. 3-up), automatic torquetube addition
#     <li> -Have multiple configurations of rows, using a sceneObj for each one with different originx and originy locations
#     <li> -Routines to add piles and custom objects
#     <li> -Automatic routines for analyzing irradinace on the slope, the fun panel, etc. 
# </ul> 
# 

# In[ ]:





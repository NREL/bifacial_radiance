.. _introexamples:

Intro Examples
==============

Usage
~~~~~

This page contains introductory examples of bifacial_radiance usage. We recommend to look at the Jupyter Notebook tutorials for more updated and better documented examples.

.. code-block:: python

   from bifacial_radiance import RadianceObj  # the main container for working with radiance

Now that the module is loaded, let's use it.


.. code-block:: python

   demo = RadianceObj(name = 'Testrun', path = 'myfolder')  #create a new demo run. Files will have the Testrun prefix, and be saved to 'myfolder'
    
   demo.setGround(0.3) # input albedo number or material name like 'concrete'.  To see options, run this without any input.
    
   # Now download an EPW climate file for any global lat/lon value :
   epwfile = demo.getEPW(37.5,-77.6) # pull EPW data for any global lat/lon
    
   # let's load this epw file into our MetObj container class.
   metdata = demo.readEPW(epwfile) # read in the EPW weather data as metdata object. Run this with no input parameters to load a graphical picker
   # if you'd rather use a TMY3 file, select one that you've already downloaded:
   metdata = demo.readTMY()        # select an existing TMY3 climate file. return metdata object.

Now that we have ground albedo and a climate file loaded, we need to start designing the PV system.
Fixed tilt systems can have hourly simulations with gendaylit, or annual simulations with gencumulativesky


.. code-block:: python

   # create cumulativesky skyfiles and save it to the \skies\ directory, along with a .cal file in root
   demo.genCumSky(demo.epwfile)  

--- optionally ----


.. code-block:: python

   demo.gendaylit(metdata,4020) # pass in the metdata object, plus the integer number of the hour in the year you want to run (0 to 8759)
   # note that for genCumSky, you pass the *name* of the EPW file. for gendaylit you pass the metdata object.


The nice thing about the RadianceObject is that it keeps track of where all of your skyfiles and calfiles are being saved.
Next let's put a PV system together. The details are saved in a dictionary and passed into makeScene. Let's start with a PV module:


.. code-block:: python

   # Create a new moduletype: Prism Solar Bi60. width = .984m height = 1.695m. 
   demo.makeModule(name='Prism Solar Bi60',x=0.984,y=1.695)  #x is assumed module width, y is height.
    
   # Let's print the available module types
   demo.printModules()

the module details are stored in a module.json file in the bifacial_radiance\data directory so you can re-use module parameters.  
Each unit module generates a corresponding .RAD file in \objects\ which is referenced in our array scene.

There are some nifty module generation options including stacking them (e.g. 2-up or 3-up but any number) with a gap, and torque tube down the middle of the string. See the :py:func:`~bifacial_radiance.RadianceObj.makeModule` documentation for all the options, or the Jupyter Notebook tutorials for examples and visualizations of what is possible.

To define the orientation it has to be done in the makeModule step, assigning the correct values to the x and y of the module. x is the size of the module along the row, therefore for a landscape module x > y.

.. code-block:: python

   # make a 72-cell module 2m x 1m arranged 2-up in portrait with a 10cm torque tube behind.
   # a 5cm offset between panels and the tube, along with a 5cm array gap between the modules:
    
   demo.makeModule(name = '1axis_2up', x = 1.995, y = 0.995, torquetube = True, tubetype = 'round', 
        diameter = 0.1, zgap = 0.05, ygap = 0.05, numpanels = 2)

Now we make a sceneDict with details of our PV array.  We'll make a rooftop array of Prism Solar modules in landscape
at 10 degrees tilt.


.. code-block:: python

   module_name = 'Prism Solar Bi60'
   sceneDict = {'tilt':10,'pitch':1.5,'clearance_height':0.2,'azimuth':180, 'nMods': 20, 'nRows': 7}  
   # this is passed into makeScene to generate the RADIANCE .rad file
   scene = demo.makeScene(module_name,sceneDict) #makeScene creates a .rad file with 20 modules per row, 7 rows.

OK, we're almost done.  RADIANCE has to combine the skyfiles, groundfiles, material (\*.mtl) files, and scene geometry (.rad) files
into an OCT file using makeOct.  Instead of having to remember where all these files are, the RadianceObj keeps track. Or call .getfilelist()


.. code-block:: python

   octfile = demo.makeOct(demo.getfilelist()) # the input parameter is optional - maybe you have a custom file list you want to use

The final step is to query the front and rear irradiance of our array.  The default is a 9-point scan through the center module of the center row of the array.  The actual scan values are set up by .makeScene and returned in your sceneObj (sceneObj.frontscan, sceneObj.backscan).  To do this we use an AnalysisObj.


.. code-block:: python

   analysis = AnalysisObj(octfile, demo.name)  # return an analysis object including the scan dimensions for back irradiance
   analysis.analysis(octfile, demo.name, scene.frontscan, scene.backscan)  # compare the back vs front irradiance  
   print('Annual bifacial ratio average:  %0.3f' %( sum(analysis.Wm2Back) / sum(analysis.Wm2Front) ) )

We can also query specific scans along the array:


.. code-block:: python

   # Do a 4-point scan along the 5th module in the 2nd row of the array.
   scene = demo.makeScene(module_name,sceneDict)
   octfile = demo.makeOct()
   analysis = AnalysisObj(octfile, demo.name)
   frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy = 4, modWanted = 5, rowWanted = 2)
   frontresults,backresults = analysis.analysis(octfile, demo.name, scene.frontscan, scene.backscan) 
   print('Annual bifacial ratio on 5th Module average:  %0.3f' %( sum(analysis.Wm2Back) / sum(analysis.Wm2Front) ) )
    
   # And you can run the scanning for another module.
   frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy = 4, modWanted = 1, rowWanted = 2)
   frontresults,backresults = analysis.analysis(octfile, demo.name, scene.frontscan, scene.backscan) 
   print('Annual bifacial ratio average on 1st Module:  %0.3f' %( sum(analysis.Wm2Back) / sum(analysis.Wm2Front) ) )


For more usage examples including 1-axis tracking examples, carport examples, and examples of scenes with multiple sceneObjects (different trackers/modules/etc) see the Jupyter notebooks in \docs\


Functions
~~~~~~~~~

`RadianceObj(basename,path)`:  This is the basic container for radiance projects.
Pass in a `basename` string to name your radiance scene and append to various
result and image files.  `path` points to an existing or empty Radiance directory.
If the directory is empty it will be populated with appropriate ground.rad and view 
files.
Default behavior: basename defaults to current date/time, and path defaults to current directory

`RadianceObj.getfilelist()` : return list of material, sky and rad files for the scene

`RadianceObj.returnOctFiles()` : return files in the root directory with .oct extension

`RadianceObj.setGround(material_or_albedo, material_file)`: set the ground to either
a material type (e.g. 'litesoil') or albedo value e.g. 0.25.  'material_file' is a 
filename for a specific material RAD file to load with your material description 

`RadianceObj.getEPW(lat,lon)` :  download the closest EnergyPlus EPW file for a give lat / lon value. 
return: filename of downloaded file 

`RadianceObj.readWeatherFile(weatherFile)` : call readEPW or readTMY functions to read in a epw or tmy file. Return: metdata

`RadianceObj.readEPW(epwfilename)` : use pyepw to read in a epw file. Return: metdata

`RadianceObj.readTMY(tmyfilename)` : use pvlib to read in a tmy3 file. Return: metdata

`RadianceObj.gendaylit(metdata,timeindex)` : pass in data read from a EPW file.
Select a single time slice of the annual timeseries to conduct gendaylit Perez model
for that given time

`RadianceObj.gencumsky(epwfilename, startdt, enddt)` : use gencumulativesky.exe to do an entire year simulation.
If no epwfilename is passed, the most recent EPW file read by `readEPW` will be used. startdt and enddt are optional
start and endtimes for the gencumulativesky.  NOTE: if you don't have gencumulativesky.exe loaded, 
look in bifacial_radiance/data/ for a copy 

`RadianceObj.makeOct(filelist, octname)`: create a .oct file from the scene .RAD files. By default
this will use RadianceObj.getfilelist() to build the .oct file, and use RadianceObj.basename as the filename.

`RadianceObj.makeScene(moduletype, sceneDict)` : create a PV array scene with nMods modules per row and nRows number of rows. moduletype specifies the type of module which be one of the options saved in module.JSON (makeModule adds a customModule to the Json file). Pre-loaded module options are 'simple_panel', which generates a simple 0.95m x 1.59m module, or 'monopanel' which looks for 'objects/monopanel_1.rad'. sceneDict is a dictionary containing the following keys: 'tilt','pitch','clearance_height','azimuth', 'nMods', 'nRows'. 
 Return: SceneObj which includes details about the PV scene including frontscan and backscan details 

`RadianceObj.getTrackingGeometryTimeIndex(metdata, timeindex, angledelta, roundTrackerAngleBool, backtrack, gcr, hubheight, sceney)`: returns tracker tilt and clearance height for a specific point in time. 
 Return: tracker_theta, tracker_height, tracker_azimuth_ang 

`AnalysisObj(octfile,basename)` : Object for conducting analysis on a .OCT file.

`AnalysisObj.makeImage(viewfile,octfile, basename)` : create visual render of scene 'octfile' from view 'views/viewfile'

`AnalysisObj.makeFalseColor(viewfile,octfile, basename)` : create false color Wm-2 
render of scene 'octfile' from view 'views/viewfile'

`AnalysisObj.analysis(octfile, basename, frontscan, backscan)` : conduct a general front / back ratio
analysis of a .oct file.  frontscan, backscan: dictionary input for linePtsMakeDict that
is passed from AnalysisObj.makeScene.

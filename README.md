# bifacial_radiance

## Introduction

bifacial_radiance contains a series of Python wrapper functions to make working with 
RADIANCE easier, particularly for the PV researcher interested in bifacial PV 
performance.

## Install using pip


 #### PREREQUISITES (Step 0):
 This software requires the previous installation of RADIANCE from https://github.com/NREL/Radiance/releases.
 
 Make sure you add radiance to the system PATH so Python can interact with the radiance program
 
 If you are on a PC you should also copy the Jaloxa radwinexe-5.0.a.8-win64.zip executables into `program files/radiance/bin`: http://www.jaloxa.eu/resources/radiance/radwinexe.shtml
 
 The software is written in Python 2.7.  Download the Anaconda Python 2.7 environment for best compatibility.
 
 #### STEP 1: Install and import bifacial_radiance
 
  - clone the bifacial_radiance repo to your local directory or download and unzip the .zip file
  - navigate to the \bifacial_radiance directory using anaconda command line
  - run `pip install -e .  `  ( the period . is required, the -e flag is optional and installs in development mode where changes to the bifacial_radiance.py files are immediately incorporated into the module if you re-start the python kernel)
 
 #### STEP 2: Move gencumulativesky.exe
 Copy gencumulativesky.exe from the repo's `/bifacial_radiance/data/` directory and copy into your Radiance install directory.
 This is typically found in `/program files/radiance/bin/`.  
 
 #### STEP 3: Create a local Radiance directory for storing the scene files created
 Keep scene geometry files separate from the bifacial_radiance directory.  Create a local directory somewhere to be used for storing scene files.
 
 #### STEP 4: Reboot the computer
 This makes sure the PATH is updated

## Usage

```
from bifacial_radiance import *
```
For more usage examples, see the Jupyter notebooks in \docs\




## Functions
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

`RadianceObj.readEPW(epwfilename)` : use pyepw to read in a epw file. Return: metdata

`RadianceObj.gendaylit(metdata,timeindex)` : pass in data read from a EPW file.
Select a single time slice of the annual timeseries to conduct gendaylit Perez model
for that given time

`RadianceObj.gencumsky(epwfilename, startdt, enddt)` : use gencumulativesky.exe to do an entire year simulation.
If no epwfilename is passed, the most recent EPW file read by `readEPW` will be used. startdt and enddt are optional
start and endtimes for the gencumulativesky.  NOTE: if you don't have gencumulativesky.exe loaded, 
look in bifacial_radiance/data/ for a copy 

`RadianceObj.makeOct(filelist, octname)`: create a .oct file from the scene .RAD files. By default
this will use RadianceObj.getfilelist() to build the .oct file, and use RadianceObj.basename as the filename.

`RadianceObj.makeScene(moduletype, sceneDict)` : create a PV array scene with 10
modules per row, and 3 rows.  Input moduletype is either 'simple_panel', which generates a simple 0.95m x 1.59m
module, or 'monopanel' which looks for 'objects/monopanel_1.rad' . sceneDict is a
dictionary containing the following keys: 'tilt','pitch','height','orientation','azimuth'
 Return: SceneObj
which includes details about the PV scene including frontscan and backscan details 



`AnalysisObj(octfile,basename)` : Object for conducting analysis on a .OCT file.

`AnalysisObj.makeImage(viewfile,octfile, basename)` : create visual render of scene 'octfile' from view 'views/viewfile'

`AnalysisObj.makeFalseColor(viewfile,octfile, basename)` : create false color Wm-2 
render of scene 'octfile' from view 'views/viewfile'

`AnalysisObj.analysis(octfile, basename, frontscan, backscan)` : conduct a general front / back ratio
analysis of a .oct file.  frontscan, backscan: dictionary input for linePtsMakeDict that
is passed from AnalysisObj.makeScene.


MORE DOCS TO COME:



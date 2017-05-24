# bifacial_radiance

## Introduction

bifacial_radiance contains a series of Python wrapper functions to make working with 
RADIANCE easier, particularly for the PV researcher interested in bifacial PV 
performance.

## Install using pip

1. Clone or download the bifacial_radiance repository.
2. Navigate to repository: `cd bifacial_radiance`
3. Install via pip: `pip install .`
4. Alternate installation development mode: `pip install -e .`

## Usage

```
from bifacial_radiance import *
```

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
module, or 'monopanel' which looks for 'objects/monopanel_1.rad' 


`AnalysisObj(octfile,basename)` : Object for conducting analysis on a .OCT file.

`AnalysisObj.makeImage(viewfile,octfile, basename)` : create visual render of scene 'octfile' from view 'views/viewfile'

`AnalysisObj.makeFalseColro(viewfile,octfile, basename)` : create false color Wm-2 
render of scene 'octfile' from view 'views/viewfile'


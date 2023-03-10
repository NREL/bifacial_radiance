.. currentmodule:: bifacial_radiance

#############
API reference
#############
.. _manualapi:

GUI
==========

.. autosummary::
   :toctree: generated/
   :caption: GUI

   gui


Classes
=======

This is a collection of classes used by bifacial_radiance for users that prefer object-oriented programming.

.. autosummary::
   :toctree: generated/
   :caption: Classes

   MetObj
   RadianceObj
   GroundObj
   ModuleObj
   SceneObj
   AnalysisObj


Sky 
====

Functions and methods for dealing with weather, calculating solar position and generating the skies for the raytrace simulations.

Weather
-------

.. autosummary:: 
   :toctree: generated/
   :caption: Weather


   RadianceObj.getEPW
   RadianceObj.readWeatherFile
 
Sky Dome
--------
Functions and methods for establishing the sources or sky domes for the simulation

.. autosummary::
   :toctree: generated/
   :caption: Sky Dome

   RadianceObj.genCumSky
   RadianceObj.genCumSky1axis
   RadianceObj.gendaylit
   RadianceObj.gendaylit2manual
   RadianceObj.gendaylit1axis
   
Geometry
========

Modules
-------
Functions and methods to generate modules

.. autosummary::
   :toctree: generated/
   :caption: Modules

   RadianceObj.makeModule
   ModuleObj.addTorquetube
   ModuleObj.addCellModule
   ModuleObj.addFrame
   ModuleObj.addOmega
   ModuleObj.showModule
   ModuleObj.readModule
   ModuleObj.compileText
   RadianceObj.returnMaterialFiles

Scene
-----
Functions and methods to generate the scene.

.. autosummary::
   :toctree: generated/
   :caption: Scene

   RadianceObj.setGround
   RadianceObj.set1axis
   RadianceObj.makeScene
   RadianceObj.makeScene1axis
   RadianceObj.makeOct
   RadianceObj.makeOct1axis

Support methods for scene

.. autosummary::
   :toctree: generated/
   

   SceneObj.showScene
   RadianceObj.makeCustomObject
   RadianceObj.appendtoScene

Analysis
==========

Methods for irradiance calculations
-----------------------------------

.. autosummary::
   :toctree: generated/
   :caption: Irradiance Analysis

   AnalysisObj.moduleAnalysis
   AnalysisObj.analysis
   RadianceObj.analysis1axis

Mismatch
--------

.. autosummary::
   :toctree: generated/
   :caption: Mismatch Analysis
   
   mismatch.analysisIrradianceandPowerMismatch

Support
=======

Input / Output
--------------

.. autosummary::
   :toctree: generated/
   :caption: Input / Output

   load
   load.loadRadianceObj
   load.loadTrackerDict
   RadianceObj.loadtrackerdict
   load.read1Result
   load.cleanResult
   load.deepcleanResult
   RadianceObj.exportTrackerDict
   RadianceObj.save

Visualization
-------------

Functions for visualizing irradiance results

.. autosummary::
   :toctree: generated/
   :caption: Visualization

   AnalysisObj.makeFalseColor
   AnalysisObj.makeImage
   SceneObj.showScene
   SceneObj.saveImage
   ModuleObj.saveImage

Others
------

.. autosummary::
   :toctree: generated/
   :caption: Other

   RadianceObj.getfilelist
   RadianceObj.getSingleTimestampTrackerAngle
   RadianceObj.returnOctFiles

ModelChain
----------

.. autosummary::
   :toctree: generated/
   :caption: ModelChain

   load.readconfigurationinputfile
   modelchain.runModelChain
   load.savedictionariestoConfigurationIniFile

Spectral Analysis
-----------------

.. autosummary::
   :toctree: generated/
   :caption: Spectral Analysis

   spectral_utils
   spectral_utils.generate_spectra
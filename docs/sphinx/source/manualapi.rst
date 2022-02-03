.. currentmodule:: bifacial_radiance

#############
API reference
#############
.. _manualapi:

GUI
==========

.. autosummary::
   :toctree: generated/

   gui


Classes
=======

This is a collection of classes used by bifacial_radiance for users that prefer object-oriented programming.

.. autosummary::
   :toctree: generated/

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

   RadianceObj.getEPW
   RadianceObj.readWeatherFile
 
Sky Dome
--------
Functions and methods for establishing the sources or sky domes for the simulation

.. autosummary::
   :toctree: generated/

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

   AnalysisObj.moduleAnalysis
   AnalysisObj.analysis
   RadianceObj.analysis1axis

Mismatch
--------

.. autosummary::
   :toctree: generated/
   
   mismatch.analysisIrradianceandPowerMismatch

Support
=======

Input / Output
--------------

.. autosummary::
   :toctree: generated/

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

Functions for visualizing iirradiance results

.. autosummary::
   :toctree: generated/

   AnalysisObj.makeFalseColor
   AnalysisObj.makeImage
   SceneObj.showScene

Others
------

.. autosummary::
   :toctree: generated/

   RadianceObj.getfilelist
   RadianceObj.getSingleTimestampTrackerAngle
   RadianceObj.returnOctFiles

ModelChain
----------

.. autosummary::
   :toctree: generated/

   load.readconfigurationinputfile
   modelchain.runModelChain
   load.savedictionariestoConfigurationIniFile

Spectral Analysis
----------

.. autosummary::
   :toctree: generated/

   spectral_utils
   spectral_utils.generate_spectra
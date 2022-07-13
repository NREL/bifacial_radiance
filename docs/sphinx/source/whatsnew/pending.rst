.. _whatsnew_0420:

v0.4.2 (XX / XX / 2022)
------------------------
Release of new version including ...


API Changes
~~~~~~~~~~~~
*A new function can now be called to compile results and report out final irradiance and performance data: :py:class:`~bifacial_radiance.RadianceObj.compileResults`.
*Multiple modules and rows can now be selected in a single analysis scan. ``modWanted`` and ``rowWanted`` inputs in :py:class:`~bifacial_radiance.RadianceObj.analysis1axis` can now be a list, to select multiple rows and modules for scans. (:issue:`405`)(:pull:`408`)
*To support multiple modules and row scans for 1axis simulations, outputs like Wm2Front are now stored in ``trackerdict``.``Results``  (:issue:`405`)(:pull:`408`)


Enhancements
~~~~~~~~~~~~
* Adds new functions ModuleObj.saveImage and SceneObj.saveImage to save .hdr images of a module or scene. These are run by default in the modelchain if simulationParamsDict['saveImage'] = True. The gui will set saveImage = True by default.


Bug fixes
~~~~~~~~~
* Fixed typo on Opacity calculation factor (:issue:`426`)

Documentation
~~~~~~~~~~~~~~
* Edge effects evaluation tutorial 23, with the new functionality of multiple modules/rows on the same analysis scan.


Contributors
~~~~~~~~~~~~
* Silvana Ayala (:ghuser:`shirubana`)
* Chris Deline (:ghuser:`cdeline`)
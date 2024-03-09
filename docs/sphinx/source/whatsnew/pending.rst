.. _whatsnew_050:

v0.5.0 (4 / XX / 2024)
------------------------
Release of new version including ...

Deprecations
~~~~~~~~~~~~
* :py:class:`~bifacial_radiance.RadianceObj.appendtoScene` is deprecated in favor of :py:class:`~bifacial_radiance.SceneObj.appendtoScene`
* :py:class:`~bifacial_radiance.RadianceObj.makeScene`.`appendtoScene` is deprecated in favor of :py:class:`~bifacial_radiance.makeScene`.`customtext` 
* :py:class:`~bifacial_radiance.RadianceObj.makeScene1axis`.`appendtoScene` is deprecated in favor of :py:class:`~bifacial_radiance.makeScene1axis`.`customtext` 


API Changes
~~~~~~~~~~~~
* A new function can now be called to compile results and report out final irradiance and performance data: :py:class:`~bifacial_radiance.RadianceObj.compileResults`.
* Results generated with the above can be saved with the :py:class:`~bifacial_radiance.RadianceObj.exportTrackerDict`, which saves an Hourly, Monthly and Yearly .csvs in the results folder.
* Multiple modules and rows can now be selected in a single analysis scan. ``modWanted`` and ``rowWanted`` inputs in :py:class:`~bifacial_radiance.RadianceObj.analysis1axis` can now be a list, to select multiple rows and modules for scans. (:issue:`405`)(:pull:`408`)
* To support multiple modules and row scans for 1axis simulations, outputs like Wm2Front are now stored in ``trackerdict``.``Results``  (:issue:`405`)(:pull:`408`)
* ``mismatch.mad_fn`` has new functionality and input parameter `axis`. If a 2D matrix or dataframe is passed in as data, MAD is calculated along the row (default) or along the columns by passing 'axis=1' (:issue:`449`)(:pull:`485`)
* NSRDB weather data can now be loaded using :py:class:`~bifacial_radiance.RadianceObj.NSRDBWeatherData`.
* :py:class:`~bifacial_radiance.makeScene`.`append` added to allow multiple scenes to be attached to a single RadianceObj.  Default: False (over-write the scene)
* :py:class:`~bifacial_radiance.makeScene1axis`.`append` added to allow multiple scenes to be attached to a single RadianceObj.  Default: False (over-write the scene)
* ``scene.appendtoscene`` functionality added (add more detail here, fix hyperlinks)


Enhancements
~~~~~~~~~~~~
* :py:class:`~bifacial_radiance.RadianceObj` and :py:class:`~bifacial_radiance.GroundObj` and :py:class:`~bifacial_radiance.MetObj` now have `self.columns` and `self.methods` introspection to list data columsn and methods available
* multiple sceneObjects are tracked by the RadianceObj now.  New function :py:class:`~bifacial_radiance.RadianceObj.sceneNames` will return the list of scenes being tracked.



Bug fixes
~~~~~~~~~
* Fixed  Pandas 2.0 errors by re-factoring ``mismatch.mad_fn``  (:issue:`449`)
* Fixed typo on Opacity calculation factor (:issue:`426`)

Documentation
~~~~~~~~~~~~~~
* Edge effects evaluation tutorial 23, with the new functionality of multiple modules/rows on the same analysis scan.


Contributors
~~~~~~~~~~~~
* Silvana Ayala (:ghuser:`shirubana`)
* Chris Deline (:ghuser:`cdeline`)
* Kevin Anderson (:ghuser:`kandersolar`)
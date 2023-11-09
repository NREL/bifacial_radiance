.. _whatsnew_0430:

v0.4.3 (XX / XX / 2023)
------------------------
Release of new version including ...


API Changes
~~~~~~~~~~~~
*A new function can now be called to compile results and report out final irradiance and performance data: :py:class:`~bifacial_radiance.RadianceObj.compileResults`.
* Results generated with the above can be saved with the :py:class:`~bifacial_radiance.RadianceObj.exportTrackerDict`, which saves an Hourly, Monthly and Yearly .csvs in the results folder.
*Multiple modules and rows can now be selected in a single analysis scan. ``modWanted`` and ``rowWanted`` inputs in :py:class:`~bifacial_radiance.RadianceObj.analysis1axis` can now be a list, to select multiple rows and modules for scans. (:issue:`405`)(:pull:`408`)
*To support multiple modules and row scans for 1axis simulations, outputs like Wm2Front are now stored in ``trackerdict``.``Results``  (:issue:`405`)(:pull:`408`)
* ``mismatch.mad_fn`` has new functionality and input parameter `axis`. If a 2D matrix or dataframe is passed in as data, MAD is calculated along the row (default) or along the columns by passing 'axis=1'

Enhancements
~~~~~~~~~~~~




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
.. _whatsnew_0430:

v0.4.3 (XX / XX / 2023)
------------------------
Bugfix Release  ...


API Changes
~~~~~~~~~~~~
*A new function can now be called to compile results and report out final irradiance and performance data: :py:class:`~bifacial_radiance.RadianceObj.compileResults`.
*Multiple modules and rows can now be selected in a single analysis scan. ``modWanted`` and ``rowWanted`` inputs in :py:class:`~bifacial_radiance.RadianceObj.analysis1axis` can now be a list, to select multiple rows and modules for scans. (:issue:`405`)(:pull:`408`)
*To support multiple modules and row scans for 1axis simulations, outputs like Wm2Front are now stored in ``trackerdict``.``Results``  (:issue:`405`)(:pull:`408`)
* ``mismatch.mad_fn`` has new functionality and input parameter `axis`. If a 2D matrix or dataframe is passed in as data, MAD is calculated along the row (default) or along the columns by passing 'axis=1'
* :func:`bifacial_radiance.mismatch.mismatch_fit3` has been deprecated in favour of :func:`bifacial_radiance.mismatch.mismatch_fit2` which has a greater agreement with anual energy yield data (:issue:`520`)

Enhancements
~~~~~~~~~~~~
* Added :func:`bifacial_radiance.mismatch.mismatch_fit2`, similar to :func:`bifacial_radiance.mismatch.mismatch_fit3`, with the recommended coefficients of the original publication. (:pull:`520`)

Bug fixes
~~~~~~~~~
* Fixed  Pandas 2.0 errors by re-factoring ``mismatch.mad_fn``  (:issue:`449`)
* Switch from un-supported Versioneer to setuptools_scm  (:issue:`519`)
* Numpy 2.0 compatibility bug  (:issue:`521`)
* Fixed bug in :func:`bifacial_radiance.mismatch.mismatch_fit3` where the function was not returning the correct values. It has also been deprecated in favour of :func:`bifacial_radiance.mismatch.mismatch_fit2` which has a greater agreement with anual energy yield data (:issue:`520`)
* Updated Github Actions to checkout@v4 and setup-python@v5 (:pull:`517`)
* Fix PerformanceWarning and SettingWithCopyWarning (:issue:`515`)

Documentation
~~~~~~~~~~~~~~
* Edge effects evaluation tutorial 23, with the new functionality of multiple modules/rows on the same analysis scan.
* Updates to example notebooks 

Contributors
~~~~~~~~~~~~
* Silvana Ayala (:ghuser:`shirubana`)
* Chris Deline (:ghuser:`cdeline`)
* Kevin Anderson (:ghuser:`kandersolar`)
* Echedey Luis (:ghuser:`echedey-ls`)

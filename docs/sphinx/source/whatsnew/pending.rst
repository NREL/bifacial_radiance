.. _whatsnew_0440:

v0.4.4 (XX / XX / 2024)
------------------------
Bugfix Release  ...


API Changes
~~~~~~~~~~~~
* 

Enhancements
~~~~~~~~~~~~
* Conduct an automated check for proper radiance RAYPATH setting (:issue:`525`)(:pull:`537`)


Bug fixes
~~~~~~~~~
* versioning with setuptools_scm- set fallback_version to bifirad v0.4.3 to prevent crashes if git is not present (:issue:`535`)(:pull:`539`)

Documentation
~~~~~~~~~~~~~~
* No longer provide a warning message when both `hub_height` and `clearance_height` are passed to :py:class:`~bifacial_radiance.AnalysisObj.moduleAnalysis`  (:pull:`540`)

Contributors
~~~~~~~~~~~~
* Silvana Ayala (:ghuser:`shirubana`)
* Chris Deline (:ghuser:`cdeline`)

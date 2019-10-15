---
title: 'bifacial_radiance: a python package for modeling bifacial solar photovoltaic systems'
tags:
  - Python
  - solar energy
  - photovoltaics
  - renewable energy
  - bifacial solar panels
authors:
  - name: Silvana Ayala Pelaez
    orcid: 0000-0003-0180-728X
    affiliation: 1
  - name: Chris Deline
    orcid: 0000-0002-9867-8930
    affiliation: 1
affiliations:
 - name: National Renewable Energy Laboratory (NREL)
   index: 1
date: 15 October 2019
bibliography: paper.bib
---

# Summary

bifacial_radiance is a national laboratory and community-supported open source tool that provides a set of functions and classes for simulating the performance of bifacial photovoltaic systems. bifacial_radiance aims to provide reference implementations of models relevant to bifacial performance, including for example algorithms for sky irradiance simulation, DC power, and irradiance calculation at the modules. bifacial_radiance is an important component of a growing ecosystem of open source tools for solar energy  [@Holmgren2018].

bifacial_radiance is developed on Github by contributors from academia, national laboratories, and private industry. Bifacial_Radiance is released copyrighted by the Alliance for Sustainable Energy with a BSD 3-clause license allowing permissive use with attribution. Bifacial_radiance is extensively tested for functional and algorithm consistency. Continuous integration services check each pull request on multiple platforms and Python versions. The bifacial_radiance API is thoroughly documented and detailed tutorials are provided for many features. The documentation includes help for installation and guidelines for contributions. The documentation is hosted at readthedocs.org as of this writing. Github’s issue trackers, a google group and StackOverflow tag provide venues for user discussions and help.

The bifacial_radiance API and visual user interface (GUI) were designed to serve the various needs of the many subfields of bifacial solar panel power research and engineering. It is implemented in three layers: core Analysis or raytrace functions; ``Radiance``, ``Meteorological``, ``Scene``, and ``Analysis`` classes; and the ``GUI`` and ``model-chain`` classes. The core API consists of a collection of functions that implement commands for Radiance software. These commands are typical implementations of algorithms and models described in peer-reviewed publications. The functions provide maximum user flexibility, however some of the function arguments require an unwieldy number of parameters. The next API level contains the ``Radiance``, ``Meteorological``, ``Scene``, and ``Analysis`` classes. These abstractions provide simple methods that wrap the core function API layer and communicate with the Radiance software, which provides the raytrace processing capabilities. The method API simplification is achieved by separating the data that represents the object (object attributes) from the data that the object methods operate on (method arguments). For example a ``Radiance`` object is represented by a ``module`` object, meteorological data, and ``scene`` objects. The ``gendaylit`` method operates on the meteorological data to calculate solar position and generate corresponding sky-files, linking them to the ``Radiance`` object. Then ``makeOct`` method combines the sky files, ``module`` and ``scene`` objects when calling the function layer, then return the results from an ``Analysis`` object to the user. The final level of API is the ``ModelChain`` class, designed to simplify and standardize the process of stitching together the many modeling steps necessary to convert a time series of weather data to AC solar power generation, given a PV system and a location. The ``ModelChain`` also powers the ``GUI``, which provides a cohesive visualization of all the input parameters and options for most common modeling needs.

bifacial_radiance was first coded in python and released as a stable version in Github in 2017 [@MacAlpine2017], and was submitted as a DOE Code on December of the same year [@Deline2017]. Efforts to make the project more pythonic were undertaken in 2018 [@Ayala2018]. Additional features continue to be added [@Ayala2019, @Stein2019], and the documentation’s “What’s New” section.

bifacial_radiance has been used in numerous studies, for example, of modeling and validation of rear irradiance for fixed tilt systems [@Ayala2019-2], estimation of energy gain and performance ratio for single-axis tracked bifacial systems [@Berrian-2019, @Ayala2019-3], as well as study of edge effects [@Ayala2019-3] and smart tracking algorithms [@Ayala2018-2]; benchmarking with other rear-irradiance calculation softwares [@Ayala2018-2, @DiOrio2018; @Capelle2019], estimation of shading factor from racking structures [@Ayala2019-4], and parameterization of electrical mismatch power losses due to irradiance non-uniformity in bifacial systems [@Deline2019, @Deline2019-2, @Ayala2019-5]. Sensitivity studies of installation and simulation parameters [@Asgharzadeh2018] and optimization for bifacial fields with the aid of high performance computing [@Stein2019, @Stein2019-2] have also been performed with bifacial_radiance.

Plans for bifacial_radiance development include the implementation of new and existing models, addition of functionality to assist with input/output, and improvements to API consistency.

The source code for each bifacial_radiance version is archived with Github (Contributors, n.d.)

pvlib python was ported from the PVLib MATLAB toolbox in 2014
[@Stein2012, @Andrews2014].

# Acknowledgements

The authors acknowledge and thank the code, documentation, and discussion contributors to the project.

SAP and CD acknowledge support from the U.S. Department of Energy’s Solar Energy Technology Office.

The National Renewable Energy Laboratory is a national laboratory of the U.S. Department of Energy, Office of Energy Efficiency and Renewable Energy, operated by the Alliance for Sustainable Energy, LLC.

# References

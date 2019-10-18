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

bifacial_radiance is a national laboratory developed, community-supported open-source toolkit that provides a set of functions and classes for simulating the performance of bifacial photovoltaic (PV) systems. (Bifacial PV modules collect light on the front AND rear side). bifacial_radiance atuomates calculations of PV system layout and performance, to use along with the popular ray-tracing software tool RADIANCE [@Ward1994]. Specific algorithms include design and layout of PV modules, reflective ground surfaces, shading obstructions, and irradiance calculations throughout the system, among others. bifacial_radiance is an important component of a growing ecosystem of open source tools for solar energy [@Holmgren2018].

bifacial_radiance is hosted on Github and PyPi, and developed by contributors from national laboratories, academia, and private industry. bifacial_radiance is copyrighted by the Alliance for Sustainable Energy with a BSD 3-clause license allowing permissive use with attribution. bifacial_radiance is extensively tested for functional and algorithm consistency. Continuous integration services check each pull request on multiple platforms and Python versions. The bifacial_radiance API is thoroughly documented, and detailed tutorials are provided for many features. The documentation includes help for installation and guidelines for contributions. The documentation is hosted at readthedocs.org as of this writing. Github’s issue trackers, a google group and StackOverflow tag provide venues for user discussions and help.

<figure>
    <img src='Alderman.PNG' />
    <figcaption> Visualization of a bifacial photovoltaic array generated through bifacial_radiance. Courtesy of J. Alderman. </figcaption>
</figure>

The bifacial_radiance API and graphical user interface (GUI) were designed to serve the various needs of the many subfields of bifacial solar panel power research and engineering. It is implemented in three layers: core RADIANCE-interface functions; ``Bifacial-Radiance``, ``Meteorological``, ``Scene``, and ``Analysis`` classes; and the ``GUI`` and ``model-chain`` classes. The core API consists of a collection of functions that implement commands directly to the RADIANCE software. These commands are typical implementations of algorithms and models described in peer-reviewed publications. The functions provide maximum user flexibility, however some of the function arguments require an unwieldy number of parameters. The next API level contains the ``Bifacial-Radiance``, ``Meteorological``, ``Scene``, and ``Analysis`` classes. These abstractions provide simple methods that wrap the core function API layer and communicate with the RADIANCE software, which provides ray-trace processing capabilities. The method API simplification is achieved by separating the data that represents the object (object attributes) from the data that the object methods operate on (method arguments). For example, a ``Bifacial-Radiance`` object is represented by a ``module`` object, meteorological data, and ``scene`` objects. The ``gendaylit`` method operates on the meteorological data to calculate solar position and generate corresponding sky-files, linking them to the ``Bifacial-Radiance`` object. Then the ``makeOct`` method combines the sky files, ``module`` and ``scene`` objects when calling the function layer, returning the results from an ``Analysis`` object to the user. The final level of API is the ``ModelChain`` class, designed to simplify and standardize the process of stitching together the many modeling steps necessary to convert a time series of weather data to AC solar power generation, given a PV system and a location. The ``ModelChain`` also powers the ``GUI``, which provides a cohesive visualization of all the input parameters and options for most common modeling needs.

bifacial_radiance was first coded in python and released as a stable version in Github in 2017 [@MacAlpine2017], and was submitted as a DOE Code project on December of the same year [@Deline2017]. Efforts to make the project more pythonic were undertaken in 2018 [@Ayala2018]. Additional features continue to be added as described in [@Ayala2019, @Stein2019], and the documentation’s “What’s New” section.

bifacial_radiance has been used in numerous studies, for example, of modeling and validation of rear irradiance for fixed tilt systems [@Ayala2019b], estimation of energy gain and performance ratio for single-axis tracked bifacial systems [@Berrian2019, @Ayala2019c], as well as study of edge effects [@Ayala2019c] and smart tracking algorithms [@Ayala2018b]; benchmarking with other rear-irradiance calculation softwares [@Ayala2018b, @DiOrio2018, @Capelle2019], estimation of shading factor from racking structures [@Ayala2019d], and parameterization of electrical mismatch power losses due to irradiance non-uniformity in bifacial systems [@Deline2019, @Deline2019b, @Ayala2019e]. Sensitivity studies of installation and simulation parameters [@Asgharzadeh2018] and optimization for bifacial fields with the aid of high performance computing [@Stein2019, @Stein2019b] have also been performed with bifacial_radiance.

Plans for bifacial_radiance development include the implementation of new and existing models, addition of functionality to assist with input/output, and improvements to API consistency.

The source code for each bifacial_radiance version is archived with Github (Contributors, n.d.).

# Acknowledgements

The authors acknowledge and thank the code, documentation, and discussion contributors to the project.

SAP and CD acknowledge support from the U.S. Department of Energy’s Solar Energy Technology Office. This work was authored, in part, by the National Renewable Energy Laboratory, operated by Alliance for Sustainable Energy, LLC, for the U.S. Department of Energy (DOE) under Contract No. DE-AC36-08GO28308. Funding was provided by the U.S. Department of Energy’s Office of Energy Efficiency and Renewable Energy (EERE) under Solar Energy Technologies Office (SETO) Agreement Number 34910.

The National Renewable Energy Laboratory is a national laboratory of the U.S. Department of Energy, Office of Energy Efficiency and Renewable Energy, operated by the Alliance for Sustainable Energy, LLC.

# References

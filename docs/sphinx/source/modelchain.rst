
ModelChain
==========

The :py:class:`~.modelchain.runModelChain` class provides a high-level
interface for standardized bifacial PV modeling. The class aims to automate much
of the modeling process while providing user-control and remaining
extensible. This guide aims to build users' understanding of the
ModelChain class. It assumes some familiarity with object-oriented
code in Python, but most information should be understandable even
without a solid understanding of classes.

Modeling with a :py:class:`~.runModelChain` typically involves 3 steps:

1. Creating the :py:class:`~.runModelChain`.

A simple ModelChain example
---------------------------

Before delving into the intricacies of ModelChain, we provide a brief
example of the modeling steps using ModelChain. First, we import pvlib’s
objects, module data, and inverter data.

.. ipython:: python

    import pandas as pd
    import numpy as np

    # pvlib imports
    import bifacial_radiance

    # load some module and inverter specifications
    # sandia_module = sandia_modules['Canadian_Solar_CS5P_220M___2009_']

Now we create a Location object, a PVSystem object, and a ModelChain
object.

.. ipython:: python

    #location = Location(latitude=32.2, longitude=-110.9)
 
The remainder of this guide examines the ModelChain functionality and
explores common pitfalls.

Defining a ModelChain
---------------------

ModelChain uses the keyword arguments passed to it to determine the
models for the simulation. The documentation describes the allowed
values for each keyword argument. If a keyword argument is not supplied,
ModelChain will attempt to infer the correct set of models by inspecting
the Location and PVSystem attributes.

Below, we show some examples of how to define a ModelChain.

Let’s make the most basic Location and PVSystem objects and build from
there.

.. ipython:: python

    # something here
    
Alternatively, we could have specified single diode or PVWatts related
information in the PVSystem construction. 

User-supplied keyword arguments override ModelChain’s inspection
methods. For example, we can tell ModelChain to use different loss
functions for a PVSystem that contains SAPM-specific parameters.

Of course, these choices can also lead to failure when executing
:py:meth:`~bifacial_radiance.modelchain.runModelChain` if your system objects
do not contain the required parameters for running the model.

Demystifying ModelChain internals
---------------------------------

The ModelChain class has a lot going in inside it in order to make
users' code as simple as possible.

The key parts of ModelChain are:

    2. A set of methods that wrap and call the PVSystem methods.
    3. A set of methods that inspect user-supplied objects to determine
       the appropriate default models.

run_model
~~~~~~~~~

Most users will only interact with the
:py:meth:`~bifacial_radiance.modelchain.runModelChain` method and :ref:`gencumsky` for methods and functions that can help fully define
the irradiance inputs.

The methods called by :py:meth:`~bifacial_radiance.modelchain.runModelChain`
store their results in a series of ModelChain attributes: ``times``,
``solar_position``, ``airmass``, ``irradiance``, ``total_irrad``,
``effective_irradiance``, ``weather``, ``temps``, ``aoi``,
``aoi_modifier``, ``spectral_modifier``, ``dc``, ``ac``, ``losses``.

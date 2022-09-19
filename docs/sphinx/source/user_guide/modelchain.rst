
ModelChain
==========

The :py:class:`~bifacial_radiance.modelchain.runModelChain` class provides a high-level
interface for standardized bifacial PV modeling. The class aims to automate much
of the modeling process while providing user-control and remaining
extensible. This guide aims to build users' understanding of the
ModelChain class. It assumes some familiarity with object-oriented
code in Python, but most information should be understandable even
without a solid understanding of classes.

Modeling with a :py:class:`~bifacial_radiance.modelchain.runModelChain` typically involves 2 steps:

1. Establishing all your desired values on an .ini file or in the form of dictionaries.
2. Runnin the modelchain.

The use of the GUI is based on an internal ModelChain. In future releases, we hope to
improve the functionality of ModelChain for easiness of use in the python console.

Defining a ModelChain
---------------------

ModelChain uses the keyword arguments passed to it to determine the
models for the simulation. The documentation describes the allowed
values for each keyword argument. If a keyword argument is not supplied,
ModelChain will attempt to infer the correct set of models by inspecting
the Location and PVSystem attributes.

Below, we show some examples of how to define a ModelChain.

Let’s make the most basic simulation for a fixed tilt scenario

.. code-block:: python

    # CREATE AN EXMAPLE HEREe
    
Some of the choices can also lead to failure when executing
:py:meth:`~bifacial_radiance.modelchain.runModelChain` if your system objects
do not contain the required parameters for running the model.

We are improving these methods, so if you find a bug or case that does not work please consider
contributing (see :ref:`contributing` page.)

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
:py:meth:`~bifacial_radiance.modelchain.runModelChain` method and ``gencumsky`` for methods and functions that can help fully define
the irradiance inputs.

The methods called by :py:meth:`~bifacial_radiance.modelchain.runModelChain`
store their results in a series of ModelChain Dictionary attributes: ``settingParamsSimul``, etc.

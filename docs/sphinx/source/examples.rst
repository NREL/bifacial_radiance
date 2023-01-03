.. _examples:

Examples
========

.. To select a thumbnail image, you need to edit the metadata of the cell with the
   desired image to include a special tags value:
        "metadata": {"tags": ["nbsphinx-thumbnail"]},

.. note that linking to notebooks outside of the sphinx source directory is
   currently not possible without using a sphinx extension like "nbsphinx-link",
   but maintaining those link files is annoying and error-prone.  Another option
   is to use filesystem symlinks, but those don't work on windows.
   Instead, what we do here is to have conf.py copy the tutorials folder
   into the source directory so that its files can be referenced directly here.


Introductory Examples
---------------------

.. nbgallery::

    tutorials/1 - Introductory Example - Fixed Tilt simple setup
    tutorials/2 - Introductory Example - Single Axis Tracking with cumulative Sky


Medium Level Examples
---------------------

.. nbgallery::

    tutorials/3 - Medium Level Example - Single Axis Tracking - hourly
    tutorials/4 - Medium Level Example - Debugging your Scene with Custom Objects (Fixed Tilt 2-up with Torque Tube + CLEAN Routine + CustomObject)
    tutorials/5 - Medium Level Example - Bifacial Carports and Canopies + sampling across a module!
    tutorials/13 - Medium Level Example - Modeling Modules with Glass


Advanced Topcs
--------------

.. nbgallery::

    tutorials/6 - Advanced topics - Understanding trackerdict structure
    tutorials/7 - Advanced topics - Multiple SceneObjects Example
    tutorials/8 - Advanced topics - Calculating Power Output and Electrical Mismatch
    tutorials/9 - Advanced topics - 1 axis torque tube Shading for 1 day (Research documentation)
    tutorials/14 - Advanced topics - Cement Pavers albedo example


AgriPV
------

.. nbgallery::

    tutorials/11 - Advanced topics - AgriPV Systems
    tutorials/12 - Advanced topics - AgriPV Clearance Height Evaluation
    tutorials/16 - AgriPV - 3-up and 4-up collector optimization
    tutorials/17 - AgriPV - Jack Solar Site Modeling
    tutorials/18 - AgriPV - Coffee Plantation with Tree Modeling


Other
-----

.. nbgallery::

    tutorials/15 - New Functionalities Examples
    tutorials/19 - Example Simulation - East West Sheds
    tutorials/20 - Example Simulation - I Beams
    tutorials/21 - Example Simulation - Modeling Module Performance, an End to End Simulation
    tutorials/22 - Example simulation - Mirrors and Modules
    tutorials/Variety of Routines

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

    tutorials/1 - Fixed Tilt Yearly Results
    tutorials/2 - Single Axis Tracking Yearly Simulation
    tutorials/21 - Weather to Module Performance


Medium Level Examples
---------------------

.. nbgallery::

    tutorials/3 - Single Axis Tracking Hourly
    tutorials/4 - Debugging with Custom Objects
    tutorials/5 - Bifacial Carports and Canopies
    tutorials/7 - Multiple Scene Objects
    tutorials/13 - Modeling Modules with Glass


Advanced Topcs
--------------

.. nbgallery::

    tutorials/6 - Exploring Trackerdict Structure
    tutorials/8 - Electrical Mismatch Method
    tutorials/9 - Torquetube Shading
    tutorials/11 - AgriPV Systems
    tutorials/14 - Cement Racking Albedo Improvements


AgriPV
------

.. nbgallery::

    tutorials/11 - AgriPV Systems
    tutorials/12 - AgriPV Clearance Height Evaluation
    tutorials/16 - AgriPV - 3-up and 4-up collector optimization
    tutorials/17 - AgriPV - Jack Solar Site Modeling
    tutorials/18 - AgriPV - Coffee Plantation with Tree Modeling


Other Examples
------=-------

.. nbgallery::

    tutorials/15 - New Functionalities Examples
    tutorials/19 - East & West Facing Sheds
    tutorials/20 - Racking I Beams
    tutorials/22 - Mirrors and Modules

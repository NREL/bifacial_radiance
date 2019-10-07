.. _installation:

Installation
============

Video Instructions
~~~~~~~~~~~~~~~~~~

`https://youtu.be/4A9GocfHKyM <https://youtu.be/4A9GocfHKyM>`_ This video shows how to install the bifacial_radiance software and all associated softwares needed. More info on the Wiki. Instructions are also shown below.


PREREQUISITES (Step 0)
~~~~~~~~~~~~~~~~~~~~~~~
This software requires the previous installation of ``RADIANCE`` from https://github.com/NREL/Radiance/releases.
 
Make sure you add radiance to the system PATH so Python can interact with the radiance program
 
If you are on a PC you should also copy the `Jaloxa radwinexe-5.0.a.8-win64.zip  <http://www.jaloxa.eu/resources/radiance/radwinexe.shtml>`_ executables into ``program files/radiance/bin`` 

**Note: bifacial_radiance is not endorsed by or officially connected with the Radiance software package or its development team.**
  
STEP 1
~~~~~~
Install and Import bifacial_radiance

* clone the bifacial_radiance repo to your local directory or download and unzip the .zip file
* navigate to the \bifacial_radiance directory using anaconda command line
* run:: 

        pip install -e .

The period ``.`` is required, the ``-e`` flag is optional and installs in development mode where changes to the `bifacial_radiance.py` files are immediately incorporated into the module if you re-start the python kernel)

For best compatibility, deploy in an `Anaconda 2.7` environment, or run::

        pip install -r requirements.txt


STEP 2
~~~~~~
Move gencumulativesky.exe

* Copy gencumulativesky.exe from the repo's ``/bifacial_radiance/data/`` directory and copy into your Radiance install directory.
  This is typically found in ``/program files/radiance/bin/``.  
 
.. note::
        GenCumulativeSky is detailed in the publication "Robinson, D., Stone, A., Irradiation modeling made simple: the cumulative sky approach and its applications, Proc. PLEA 2004, Eindhoven 2004."   

The source is `available from the authors here <https://documents.epfl.ch/groups/u/ur/urbansimulation/www/GenCumSky/GenCumSky.zip>`_
 

STEP 3
~~~~~~
Create a local Radiance directory for storing the scene files created

Keep scene geometry files separate from the bifacial_radiance directory.  Create a local directory somewhere to be used for storing scene files.
 
STEP 4
~~~~~~
Reboot the computer
This makes sure the ``PATH`` is updated

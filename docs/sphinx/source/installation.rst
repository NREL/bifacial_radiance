.. _installation:

Installation
============

Compatibility
~~~~~~~~~~~~~

bifacial_radiance is coded and tested in Windows, but can also work on Linux and Mac OSX, particularly after improvements in the latest release :ref:`whatsnew_0302` which solved some of the binary issues for gencumsky. However, the functionalities in Linux are still being improved, for example the GUI requires special QT installation described in (:issue:`130`:).


Video Instructions
~~~~~~~~~~~~~~~~~~

`https://youtu.be/4A9GocfHKyM <https://youtu.be/4A9GocfHKyM>`_ This video shows how to install the bifacial_radiance software and all associated softwares needed. More info on the Wiki. Instructions are also shown below.


PREREQUISITES (Step 0)
~~~~~~~~~~~~~~~~~~~~~~~
This software requires the previous installation of ``RADIANCE`` from https://github.com/NREL/Radiance/releases.
 
Make sure you add radiance to the system PATH so Python can interact with the radiance program
 
If you are on a PC you should also copy the `Jaloxa radwinexe-5.0.a.8-win64.zip  <http://www.jaloxa.eu/resources/radiance/radwinexe.shtml>`_ executables into ``program files/radiance/bin`` 

**Note: bifacial_radiance is not endorsed by or officially connected with the Radiance software package or its development team.**
  

Prerequisite: PYTHON:
~~~~~~~~~~~~~~~~~~~~~~
You will need python installed to run bifacial_radiance. We suggest using the latest release of `Anaconda with Python 3.7 <https://www.anaconda.com/distribution/>`_ (Python 2.7 is still supported but in the process of being deprecated). Anaconda will install ``Spyder`` to work with the python scripts, and also it will install ``Jupyter``, which is the tool we use for our `tutorial trainings <https://github.com/NREL/bifacial_radiance/tree/master/docs/tutorials>`_


STEP 1
~~~~~~

The simplest option is to open a command prompt and run::

        pip install bifacial_radiance
        
       
An alternative which is shown in the Video Instructions, if you want to install bifacial_radiance in a local folder of your choosing and/or be able to modify the internal code to suit your needs, you can do the following:

* clone the bifacial_radiance repo to your local directory or download and unzip the .zip file
* navigate to the \bifacial_radiance directory using anaconda command line
* run:: 

        pip install -e .

The period ``.`` is required, the ``-e`` flag is optional and installs in development mode where changes to the `bifacial_radiance.py` files are immediately incorporated into the module if you re-start the python kernel)

For best compatibility, deploy in an `Anaconda 2.7` environment, or run::

        pip install -r requirements.txt


STEP 2
~~~~~~
Windows:

* Copy gencumulativesky.exe from the repo's ``/bifacial_radiance/data/`` directory and copy into your Radiance install directory.
  This is typically found in ``/program files/radiance/bin/``.  
 
Linux/Mac OSX:

* A make_gencumskyexe.py script that builds gencumsky executable on pultiple platforms (Linux, Mac OSX, and Windows too) is included in bifacial_radiance release. More details on the use of this script on readme.txt or on thread (:issue:`1821`).
* For Linux/Mac OSX, you will need to install QT for the GUI to work properly. Installation and details described in (:issue:`130`:).


.. note::
        GenCumulativeSky is detailed in the publication "Robinson, D., Stone, A., Irradiation modeling made simple: the cumulative sky approach and its applications, Proc. PLEA 2004, Eindhoven 2004."   

The source is `available from the authors here <https://documents.epfl.ch/groups/u/ur/urbansimulation/www/GenCumSky/GenCumSky.zip>`_
 

STEP 3
~~~~~~
Create a local directory for storing your simulations and runs results. 
If run in the default directory, simulation results will be saved in the TEMP folder, but will also be overwritten with every run. We recommend to keep the simulation files (scene geometry, skies, results, etc) separate from the bifacial_radiance directory by creating a local directory somewhere to be used for storing those files.


STEP 4
~~~~~~
Reboot the computer
This makes sure the ``PATH`` is updated

.. _installation:

Installation
============

Compatibility
~~~~~~~~~~~~~

bifacial_radiance is coded and tested in Windows, but can also work on Linux and Mac OSX, particularly after improvements in the latest release :ref:`whatsnew_0302` which solved some of the binary issues for gencumsky. However, the functionalities in Linux are still being improved, for example the GUI requires special QT installation described in (:issue:`130`:).


Video Instructions
~~~~~~~~~~~~~~~~~~

`https://youtu.be/4A9GocfHKyM <https://youtu.be/4A9GocfHKyM>`_ This video shows how to install the bifacial_radiance software and all associated softwares needed for Windows. More info on the Wiki. Instructions for Windows and Linux-based OS are also shown below.


PREREQUISITES (Step 0)
~~~~~~~~~~~~~~~~~~~~~~~
This software requires the previous installation of ``RADIANCE`` from https://github.com/NREL/Radiance/releases.
 
Make sure you add radiance to the system PATH so Python can interact with the radiance program
 
Windows:

If you are on a Windows computer you should also copy the `Jaloxa radwinexe-5.0.a.8-win64.zip  <http://www.jaloxa.eu/resources/radiance/radwinexe.shtml>`_ executables into ``program files/radiance/bin``. This executables allow for some nifty visualization options of your generated scene inside of bifacial_radiance, like falsecolor images.

Linux/Mac OSX:

* For Linux/Mac OSX, you will need to install QT for the GUI to work properly. Installation and details described in (:issue:`131`:):

1. Install ``qt5-default`` from Ubuntu using ``apt``,
2. get the official Radiance 5.2 source tarball with auxiliary libraries ``rad5R2all.tar.gz`` from either `RADIANCE <https://www.radiance-online.org/download-install/radiance-source-code/latest-release>`_ online or `LBL <https://floyd.lbl.gov/radiance/framed.html>`_ - do _not_clone the GitHub repo as it doesn't have the auxiliary libraries which you may also need. Finally extract the tarball.
3. you may also need to install ``csh`` and ``cmake`` 
4. make directories where you want to install radiance, for example ``~/.local/opt/radiance``
5. read the README and run ``./makeall install clean`` and choose where you want ``bin`` and ``lib``

You can test it by rendering the daffodil.


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

For best compatibility, deploy in an `Anaconda 2019.10` environment, or run::

        pip install -r requirements.txt


STEP 2
~~~~~~
Windows:

* Copy gencumulativesky.exe from the repo's ``/bifacial_radiance/data/`` directory and copy into your Radiance install directory.
  This is typically found in ``/program files/radiance/bin/``.  
 
Linux/Mac OSX:

* Copy the gencumulativesky executable from the repo's ``/bifacial_radiance/data/`` directory and copy into your Radiance install directory.
  This is typically found in ``/usr/local/radiance/bin/``. 


.. note::
        GenCumulativeSky is detailed in the publication "Robinson, D., Stone, A., Irradiation modeling made simple: the cumulative sky approach and its applications, Proc. PLEA 2004, Eindhoven 2004."   

        The gencumsky source is included in the repo's ``/bifacial_radiance/data/gencumsky`` directory along with a make_gencumskyexe.py script which builds the multi-platform gencumulativesky executables. More details on the use of this script in readme.txt or on thread (:issue:`182`).


STEP 3
~~~~~~
Create a local directory for storing your simulations and runs results. 
If run in the default directory, simulation results will be saved in the TEMP folder, but will also be overwritten with every run. We recommend to keep the simulation files (scene geometry, skies, results, etc) separate from the bifacial_radiance directory by creating a local directory somewhere to be used for storing those files.


STEP 4
~~~~~~
Reboot the computer
This makes sure the ``PATH`` is updated

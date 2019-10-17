#! /usr/bin/env python
"""
Download, patch, and build gencumulativesky
"""

import io
import logging
import os
import sys
import shutil
try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib import urlretrieve
import zipfile

try:
    from setuptools import distutils
except ImportError:
    sys.exit('setuptools was not detected - please install setuptools and pip')

import patch

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

# compiler options for linux, macosx
LIBRARIES = ['m']  # use math library
# include extra definitions for functions in X/Open Portability Guide
# https://www.gnu.org/software/libc/manual/html_node/XPG.html
MACROS = [('_XOPEN_SOURCE', None)]
# full path to this file
GENCUMSKY_DIR = os.path.abspath(os.path.dirname(__file__))
EXE_FILE = 'gencumulativesky'  # name of compiled executable file
# use g++ executables instead of "cc"
LINKER_EXE = COMPILER = COMPILER_CXX = ['g++']

# platform specific constants
PLATFORM = sys.platform
if PLATFORM == 'win32':
    LIBRARIES = None
    MACROS = [('WIN32', None)]
elif PLATFORM == 'darwin':
    pass
elif PLATFORM in ['linux', 'linux2']:
    PLATFORM = 'linux'
else:
    sys.exit('Platform "%s" is unknown or unsupported.' % PLATFORM)

# $ mkdir -p ~/Downloads/GenCumSky
# $ cd ~/Downloads/GenCumSky
# ~/Downloads/GenCumSky $ wget https://documents.epfl.ch/groups/u/ur/urbansimulation/www/GenCumSky/GenCumSky.zip
# ~/Downloads/GenCumSky $ unzip GenCumSky.zip
# ~/Downloads/GenCumSky $ rm gencumulativesky.exe
GENCUMSKY_URL = r'https://documents.epfl.ch/groups/u/ur/urbansimulation/www/'
GENCUMSKY_URL += r'GenCumSky/GenCumSky.zip'
GENCUMSKY_EXE = 'gencumulativesky.exe'


def get_gencumsky_src(path, url=GENCUMSKY_URL, exe=GENCUMSKY_EXE, logger=None):
    """
    Get the source code for genCumulativeSky and unzip to specified path. Also
    removes the ``gencumulativesky.exe`` exe from the extracted contents. If
    ``path`` exists it will be deleted, and a new folder created. If ``path``
    does not already exist, then it will be created.

    Parameters
    ----------
    path : str
        path to which archive contents are unzipped
    url : str
        URL of the genCumulativeSky archive (default:
        https://documents.epfl.ch/groups/u/ur/urbansimulation/www/GenCumSky/GenCumSky.zip)

    Returns
    -------
    request

    Raises
    ------
    :class:`zipfile.BadZipfile`, :class:`requests.exceptions.HTTPError`

    """
    clean_gencumsky_src(path, logger=logger)
    if logger is not None:
        logger.debug('get gencumsky zip from URL')
    locfile, _ = urlretrieve(url)
    if locfile:
        if logger is not None:
            logger.debug('extracting gencumsky zip to src path')
        with open(locfile, 'rb') as content:
            bstr = io.BytesIO(content.read())
        with zipfile.ZipFile(bstr) as zfile:
            zfile.extractall(path)
        os.remove(os.path.join(path, exe))
    else:
        raise RuntimeError('GenCumSky could not be downloaded or extracted.')


# ~/Downloads/GenCumSky $ mv cSkyVault.h cSkyVault.h.old
# ~/Downloads/GenCumSky $ sed s/ClimateFile.h/climateFile.h/g cSkyVault.h.old > cSkyVault.h
# ~/Downloads/GenCumSky $ diff -u cSkyVault.h.old cSkyVault.h
GENCUMSKY_PATCH = os.path.join(GENCUMSKY_DIR, 'gencumulativesky_update.patch')


def patch_gencumsky(path, patches=GENCUMSKY_PATCH, logger=None):
    """
    Patch genCumulativeSky at path. Patches is a dictionary of files as keys
    and tuple of old strings to replace with new strings.
    """
    if logger is not None:
        logger.debug('apply patch %s', patches)
    pset = patch.fromfile(patches)
    pset.apply()
    # fix capitalization of climateFile.h in cSkyVault.h
    kfile, vals = 'cSkyVault.h', ('ClimateFile.h', 'climateFile.h')
    if logger is not None:
        logger.debug(
            'replace %s -> %s, in file %s', *vals, kfile)
    kpath = os.path.join(path, kfile)
    kold = kfile + '.old'
    koldpath = os.path.join(path, kold)
    if logger is not None:
        logger.debug('reading: %s', kpath)
    with open(kpath) as patchf:
        src = patchf.read()
    shutil.move(kpath, koldpath)
    if logger is not None:
        logger.debug('moved old path to %s', koldpath)
    with open(kpath, 'w') as patchf:
        if logger is not None:
            logger.debug('replace: %s -> %s', *vals)
        src = src.replace(*vals)
        patchf.write(src)


def clean_gencumsky_src(path, logger=None):
    """clean the source tree"""
    for srcf in os.listdir(path):
        if srcf in ('dummy.c', 'patch.py', 'gencumulativesky_update.patch'):
            continue
        elif srcf.startswith('_'):
            continue
        elif srcf != os.path.basename(__file__):
            if logger is not None:
                logger.debug('remove %s', srcf)
            os.remove(os.path.join(path, srcf))


# ~/Downloads/GenCumSky $ cat README.txt
# ~/Downloads/GenCumSky $ g++ -D_XOPEN_SOURCE *.cpp -lm -o gencumulativesky
# ~/Downloads/GenCumSky $ cp gencumulativesky path/to/radiance/bin
CC = distutils.ccompiler.new_compiler()  # initialize compiler object
if PLATFORM in ['linux', 'darwin']:
    CC.set_executables(
        linker_exe=LINKER_EXE, compiler=COMPILER, compiler_cxx=COMPILER_CXX)


def compile_gencumsky(complier=CC, output_dir=GENCUMSKY_DIR, macros=None,
                      output_progname=EXE_FILE, libraries=None, logger=None):
    """Create platform specific gencumulativesky executable from download."""
    if macros is None:
        macros = MACROS
    if libraries is None:
        libraries = LIBRARIES
    get_gencumsky_src(path=output_dir, logger=logger)
    patch_gencumsky(path=output_dir, logger=logger)
    src = [os.path.join(output_dir, f) for f in os.listdir(output_dir)
           if f.endswith('.cpp')]
    if logger is not None:
        logger.debug('source:\n%r', src)
    # root of this file, used for compiler output directory
    root, _ = os.path.splitdrive(output_dir)
    root += os.sep  # append platform specific path separator
    # compile source to objects in build directory
    objs = complier.compile(src, output_dir=root, macros=macros)
    if logger is not None:
        logger.debug('objects:\n%r', objs)
    # link objects to executable in build directory
    complier.link_executable(
        objs, output_progname, output_dir=output_dir, libraries=libraries)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'clean':
            LOGGER.debug('clean gencumsky')
            clean_gencumsky_src(GENCUMSKY_DIR, logger=LOGGER)
        elif sys.argv[1] == 'build':
            LOGGER.debug('building gencumsky')
            compile_gencumsky(logger=LOGGER)
        sys.exit(0)
    sys.stdout.write('build or clean?\n')

#! /usr/bin/env python
"""
build helper for setup
"""

import io
import logging
import os
import sys
import shutil
import zipfile

import requests
try:
    from setuptools import distutils
except ImportError:
    sys.exit('setuptools was not detected - please install setuptools and pip')

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

# compiler options for linux, macosx
LIBRARIES = ['m']  # use math library
# include extra definitions for functions in X/Open Portability Guide
# https://www.gnu.org/software/libc/manual/html_node/XPG.html
MACROS = [('_XOPEN_SOURCE', None)]
EXE_FILE = '%s'  # name of compiled executable file
# use g++ executables instead of "cc"
LINKER_EXE = COMPILER = COMPILER_CXX = ['g++']

# platform specific constants
PLATFORM = sys.platform
if PLATFORM == 'win32':
    EXE_FILE = '%s.exe'
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
    if logger is not None:
        logger.debug('checking gencumsky src path existance')
    if os.path.exists(path):
        shutil.rmtree(path)  # delete entire directory tree
        if logger is not None:
            logger.debug('remove existing gencumsky src path')
    if logger is not None:
        logger.debug('make new gencumsky src path')
    os.mkdir(path)  # make build directory
    if logger is not None:
        logger.debug('get gencumsky zip from URL')
    req = requests.get(url)
    if req.ok:
        if logger is not None:
            logger.debug('extracting gencumsky zip to src path')
        bstr = io.BytesIO(req.content)
        with zipfile.ZipFile(bstr) as zfile:
            zfile.extractall(path)
        os.remove(os.path.join(path, exe))
    else:
        req.raise_for_status()
    return req


# ~/Downloads/GenCumSky $ mv cSkyVault.h cSkyVault.h.old
# ~/Downloads/GenCumSky $ sed s/ClimateFile.h/climateFile.h/g cSkyVault.h.old > cSkyVault.h
# ~/Downloads/GenCumSky $ diff -u cSkyVault.h.old cSkyVault.h
GENCUMSKY_PATCH = {
    'cSkyVault.h': [('replace', ('ClimateFile.h', 'climateFile.h'))]}


def patch_gencumsky(path, patches=None, logger=None):
    """
    Patch genCumulativeSky at path. Patches is a dictionary of files as keys
    and tuple of old strings to replace with new strings.
    """
    if patches is None:
        patches = GENCUMSKY_PATCH
    for k, val in patches.items():
        if logger is not None:
            logger.debug(
                'patching file: %s <- "%r"', k, val)
        kpath = os.path.join(path, k)
        kold = k + '.old'
        koldpath = os.path.join(path, kold)
        if logger is not None:
            logger.debug('reading: %s', kpath)
        with open(kpath) as patchf:
            src = patchf.read()
        shutil.move(kpath, koldpath)
        if logger is not None:
            logger.debug('moved old path to %s', koldpath)
        with open(kpath, 'w') as patchf:
            for ptype, pval in val:
                if ptype == 'replace':
                    if logger is not None:
                        logger.debug('replace: %s -> %s', *pval)
                    src = src.replace(*pval)
            patchf.write(src)


# use dummy to get correct platform metadata
GENCUMSKY_DIR = os.path.dirname(__file__)
GENCUMSKY = 'gencumulativesky'
EXE_FILE = EXE_FILE % GENCUMSKY

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
    # compile source to objects in build directory
    objs = complier.compile(src, macros=macros)
    if logger is not None:
        logger.debug('objects:\n%r', objs)
    # link objects to executable in build directory
    complier.link_executable(
        objs, output_progname, output_dir=output_dir, libraries=libraries)


if __name__ == '__main__':
    if sys.argv[1] == 'clean':
        LOGGER.debug('clean gencumsky')
        for f in os.listdir(GENCUMSKY_DIR):
            if f != os.path.basename(__file__):
                LOGGER.debug('remove %s', f)
                os.remove(os.path.join(GENCUMSKY_DIR, f))
        sys.exit(0)
    LOGGER.debug('building gencumsky')
    compile_gencumsky(logger=LOGGER)

#! /usr/bin/env python
"""
Multiplatform make gencumulativesky executable for Windows, Linux, & Mac OS X
"""

import logging
import os
import sys
try:
    from setuptools import distutils
except ImportError:
    sys.exit('setuptools was not detected - please install setuptools and pip')

# setup basic logging
logging.basicConfig()
LOGGER = logging.getLogger(__name__)

# compiler options
CC = distutils.ccompiler.new_compiler()  # initialize compiler object
LIBRARIES = ['m']  # use math library
# include extra definitions for functions in X/Open Portability Guide
# https://www.gnu.org/software/libc/manual/html_node/XPG.html
MACROS = [('_XOPEN_SOURCE', None)]
# full path to this file
GENCUMSKY_DIR = os.path.abspath(os.path.dirname(__file__))
EXE_FILE = 'gencumulativesky'  # name of compiled executable file
# use g++ executables instead of gcc
LINKER_EXE = COMPILER = COMPILER_CXX = ['g++']

# platform specific constants
PLATFORM = sys.platform
if PLATFORM == 'win32':
    # math library and XOPG macro are not used on Windows
    LIBRARIES = None
    MACROS = [('WIN32', None)]
elif PLATFORM == 'darwin':
    pass
elif PLATFORM in ['linux', 'linux2']:
    PLATFORM = 'linux'  # consolidate linux names
else:
    sys.exit('Platform "%s" is unknown or unsupported.' % PLATFORM)
# on linux and mac set the compiler and linker to use g++ instead of gcc
if PLATFORM in ['linux', 'darwin']:
    CC.set_executables(
        linker_exe=LINKER_EXE, compiler=COMPILER, compiler_cxx=COMPILER_CXX)


def compile_gencumsky(compiler=CC, output_dir=GENCUMSKY_DIR, macros=None,
                      output_progname=EXE_FILE, libraries=None, logger=LOGGER):
    """
    Create platform specific gencumulativesky executable from download.
    
    Parameters
    ----------
    compiler : `distutils.ccompiler.CCompiler`
        defaults has linker and cc set to g++ for linux and mac os x
    output_dir : str
        path to output folder, default is absolute path to this folder
    macros : list of 2-item tuples
        if ``None`` then defaults to ``[('WIN32', None)]`` on Windows, and
        ``[('_XOPEN_SOURCE', None)]`` for linux and mac os x
    output_progname : str
        default is ``'gencumulativesky'``, windows automatically adds ``.exe``
    libraries : list
        if ``None`` then defualts to ``['m']`` for linux and mac os x
    logger : `logging.Logger`
        default is only critical logging
    
    Raises
    ------
    `distutils.errors.UnknownFileError`, `distutils.errors.CompileError`,
    `distutils.errors.LinkError`
    """
    logger.debug('compiler: %r', compiler)
    logger.debug('output directory: %s', output_dir)
    logger.debug('output program name: %s', output_progname)
    if macros is None:
        macros = MACROS  # use default macros
    logger.debug('macros: %r', macros)
    if libraries is None:
        libraries = LIBRARIES  # use default libraries
    logger.debug('libraries: %r', libraries)
    # a list of *.cpp source code to compile
    src = [os.path.join(output_dir, f) for f in os.listdir(output_dir)
           if f.endswith('.cpp')]
    # log *.cpp source to compile
    logger.debug('*.cpp source files:\n\t%s', '\n\t'.join(src))
    # root of this file, used for compiler output directory
    root, _ = os.path.splitdrive(output_dir)
    root += os.sep  # append platform specific path separator
    logger.debug('root: %s', root)
    # compile source to objects in build directory
    objs = compiler.compile(src, output_dir=root, macros=macros)
    # log objects to compile
    logger.debug('compiled objects:\n\t%s', '\n\t'.join(objs))
    # link objects to executable in build directory
    compiler.link_executable(
        objs, output_progname, output_dir=output_dir, libraries=libraries)


if __name__ == '__main__':
    LOGGER.setLevel(logging.DEBUG)  # set logging level to debug
    LOGGER.debug('compiling gencumsky ...\n')
    compile_gencumsky(logger=LOGGER)  # compile
    LOGGER.debug(' ... %s successfully compiled!\n', EXE_FILE)
    os.system(os.path.join(GENCUMSKY_DIR, EXE_FILE))
    sys.exit(0)  # successful exit!

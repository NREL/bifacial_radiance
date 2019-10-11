"""
build helper for setup
"""

import difflib
import logging
import io
import zipfile
import sys
import os
import shutil
from distutils import unixccompiler
try:
    from setuptools import setup, distutils, Extension
except ImportError:
    sys.exit('setuptools was not detected - please install setuptools and pip')
import requests
from bifacial_radiance import __name__ as NAME

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger('SETUP')

# set platform constants
CCFLAGS, RPATH, INSTALL_NAME, LDFLAGS, MACROS = None, None, None, None, None
PYVERSION = sys.version_info
PLATFORM = sys.platform
if PLATFORM == 'win32':
    LIB_FILE = '%s.dll'
    MACROS = [('WIN32', None)]
    if PYVERSION.major >= 3 and PYVERSION.minor >= 5:
        LDFLAGS = ['/DLL']
elif PLATFORM == 'darwin':
    LIB_FILE = 'lib%s.dylib'
    RPATH = "-Wl,-rpath,@loader_path/"
    INSTALL_NAME = "@rpath/" + LIB_FILE
    CCFLAGS = LDFLAGS = ['-fPIC']
elif PLATFORM in ['linux', 'linux2']:
    PLATFORM = 'linux'
    LIB_FILE = 'lib%s.so'
    RPATH = "-Wl,-rpath,${ORIGIN}"
    CCFLAGS = LDFLAGS = ['-fPIC']
else:
    sys.exit('Platform "%s" is unknown or unsupported.' % PLATFORM)


def make_ldflags(ldflags=LDFLAGS, rpath=RPATH):
    """
    Make LDFLAGS with rpath, install_name and lib_name.
    """
    if ldflags and rpath:
        ldflags.extend([rpath])
    elif rpath:
        ldflags = [rpath]
    return ldflags


def make_install_name(lib_name, install_name=INSTALL_NAME):
    """
    Make INSTALL_NAME with and lib_name.
    """
    if install_name:
        return ['-install_name', install_name % lib_name]
    return None


def dylib_monkeypatch(self):
    """
    Monkey patch :class:`distutils.UnixCCompiler` for darwin so libraries use
    '.dylib' instead of '.so'.
    """

    def link_dylib_lib(self, objects, output_libname, output_dir=None,
                       libraries=None, library_dirs=None,
                       runtime_library_dirs=None, export_symbols=None,
                       debug=0, extra_preargs=None, extra_postargs=None,
                       build_temp=None, target_lang=None):
        """implementation of link_shared_lib"""
        self.link("shared_library", objects,
                  self.library_filename(output_libname, lib_type='dylib'),
                  output_dir,
                  libraries, library_dirs, runtime_library_dirs,
                  export_symbols, debug,
                  extra_preargs, extra_postargs, build_temp, target_lang)
    self.link_so = self.link_shared_lib
    self.link_shared_lib = link_dylib_lib
    return self


# $ mkdir -p ~/Downloads/GenCumSky
# $ cd ~/Downloads/GenCumSky
# ~/Downloads/GenCumSky $ wget https://documents.epfl.ch/groups/u/ur/urbansimulation/www/GenCumSky/GenCumSky.zip
# ~/Downloads/GenCumSky $ unzip GenCumSky.zip
# ~/Downloads/GenCumSky $ rm gencumulativesky.exe
GENCUMSKY_URL = r'https://documents.epfl.ch/groups/u/ur/urbansimulation/www/'
GENCUMSKY_URL += r'GenCumSky/GenCumSky.zip'
GENCUMSKY_EXE = 'gencumulativesky.exe'


def get_gencumsky_src(path, url=GENCUMSKY_URL, exe=GENCUMSKY_EXE):
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
    request status code

    Raises
    ------
    :class:`zipfile.BadZipfile`

    """
    if os.path.exists(path):
        shutil.rmtree(path)  # delete entire directory tree
    os.mkdir(path)  # make build directory
    req = requests.get(url)
    if req.ok:
        bstr = io.BytesIO(req.content)
        with zipfile.ZipFile(bstr) as zfile:
            zfile.extractall(path)
        os.remove(os.path.join(path, exe))
    return req.status_code


# ~/Downloads/GenCumSky $ mv cSkyVault.h cSkyVault.h.old
# ~/Downloads/GenCumSky $ sed s/ClimateFile.h/climateFile.h/g cSkyVault.h.old > cSkyVault.h
# ~/Downloads/GenCumSky $ diff -u cSkyVault.h.old cSkyVault.h
GENCUMSKY_PATCH = {'cSkyVault.h': ('ClimateFile.h', 'climateFile.h')}


def patch_gencumsky(path, patches=None):
    """
    Patch genCumulativeSky at path. Patches is a dictionary of files as keys
    and tuple of old strings to replace with new strings.
    """
    if patches is None:
        patches = GENCUMSKY_PATCH
    retv = dict.fromkeys(patches)
    for k, val in patches:
        kpath = os.path.join(path, k)
        kold = k + '.old'
        koldpath = os.path.join(path, kold)
        with open(kpath) as patchf:
            src = patchf.read()
        shutil.move(kpath, koldpath)
        with open(kpath, 'w') as patchf:
            newsrc = src.replace(*val)
            patchf.write(newsrc)
        retv[k] = difflib.unified_diff(src, newsrc, koldpath, kpath)
    return retv


# use dummy to get correct platform metadata
FILE = os.path.dirname(__file__)
PKG_DATA = []
DUMMY = Extension(
    '%s.dummy' % NAME, sources=[os.path.join(FILE, NAME, 'dummy.c')])
SRC_DIR = os.path.join(FILE, NAME, 'src')
BUILD_DIR = os.path.join(FILE, NAME, 'build')
GENCUMSKY = 'gencumulativesky'

# ~/Downloads/GenCumSky $ cat README.txt
# ~/Downloads/GenCumSky $ g++ -D_XOPEN_SOURCE *.cpp -lm -o gencumulativesky
# ~/Downloads/GenCumSky $ cp gencumulativesky path/to/radiance/bin

# clean build directory
if os.path.exists(BUILD_DIR):
    shutil.rmtree(BUILD_DIR)  # delete entire directory tree
os.mkdir(BUILD_DIR)  # make build directory
req = get_gencumsky_src(path=SRC_DIR)
# compile NREL source code
if PLATFORM == 'darwin':
    CCOMPILER = unixccompiler.UnixCCompiler
    OSXCCOMPILER = dylib_monkeypatch(CCOMPILER)
    CC = OSXCCOMPILER(verbose=3)
else:
    CC = distutils.ccompiler.new_compiler()  # initialize compiler object
CC.add_include_dir(SRC_DIR)  # set includes directory
# compile solpos and solposAM objects into build directory
OBJS = CC.compile([SOLPOS, SOLPOSAM], output_dir=BUILD_DIR,
                  extra_preargs=CCFLAGS, macros=MACROS)
# link objects and make shared library in build directory
CC.link_shared_lib(OBJS, SOLPOSAM_LIB, output_dir=BUILD_DIR,
                   extra_preargs=make_ldflags(),
                   extra_postargs=make_install_name(SOLPOSAM_LIB))
# compile spectrl2 objects into build directory
OBJS = CC.compile([SPECTRL2, SPECTRL2_2, SOLPOS], output_dir=BUILD_DIR,
                  extra_preargs=CCFLAGS, macros=MACROS)
CC.add_library(SOLPOSAM_LIB)  # set linked libraries
CC.add_library_dir(BUILD_DIR)  # set library directories
# link objects and make shared library in build directory
CC.link_shared_lib(OBJS, SPECTRL2_LIB, output_dir=BUILD_DIR,
                   extra_preargs=make_ldflags(),
                   extra_postargs=make_install_name(SPECTRL2_LIB))
# copy files from build to library folder
shutil.copy(os.path.join(BUILD_DIR, SOLPOSAM_LIB_FILE), NAME)
shutil.copy(os.path.join(BUILD_DIR, SPECTRL2_LIB_FILE), NAME)
LIB_FILES_EXIST = True


# Tests will require these packages
test_requires = ['numpy', 'nose']

setup(
    name='SolarUtils',
    version=VERSION,
    description='Python wrappers around NREL SOLPOS and SPECTRL2',
    long_description=README,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    license='BSD 3-Clause',
    platforms=['win32', 'linux', 'linux2', 'darwin'],
    packages=[NAME, TESTS],
    package_data={NAME: PKG_DATA, TESTS: TEST_DATA},
    ext_modules=[DUMMY],
    extras_require={'testing': test_requires}
)

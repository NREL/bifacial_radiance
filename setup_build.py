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


# ~/Downloads/GenCumSky $ cat README.txt
# ~/Downloads/GenCumSky $ g++ -D_XOPEN_SOURCE *.cpp -lm -o gencumulativesky
# ~/Downloads/GenCumSky $ cp gencumulativesky path/to/radiance/bin

GENCUMSKY_URL = r'https://documents.epfl.ch/groups/u/ur/urbansimulation/www/'
GENCUMSKY_URL += r'GenCumSky/GenCumSky.zip'
GENCUMSKY_EXE = 'gencumulativesky.exe'

# $ mkdir -p ~/Downloads/GenCumSky
# $ cd ~/Downloads/GenCumSky
# ~/Downloads/GenCumSky $ wget https://documents.epfl.ch/groups/u/ur/urbansimulation/www/GenCumSky/GenCumSky.zip
# ~/Downloads/GenCumSky $ unzip GenCumSky.zip
# ~/Downloads/GenCumSky $ rm gencumulativesky.exe


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
    req = requests.get(GENCUMSKY_URL)
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
    if patches is None:
        patches = GENCUMSKY_PATCH
    retv = dict.fromkeys(patches)
    for k, v in patches:
        kpath = os.path.join(path, k)
        kold = k + '.old'
        koldpath = os.path.join(path, kold)
        with open(kpath, 'rb') as f:
            src = f.read()
        shutil.move(kpath, koldpath)
        with open(kpath, 'wb') as f:
            newsrc = src.replace(*v)
            f.write(newsrc)
        retv[k] = difflib.unified_diff(src, newsrc, koldpath, kpath)


# use dummy to get correct platform metadata
FILE = os.path.dirname(__file__)
PKG_DATA = []
DUMMY = Extension(
    '%s.dummy' % NAME, sources=[os.path.join(FILE, NAME, 'dummy.c')])
SRC_DIR = os.path.join(FILE, NAME, 'src')
BUILD_DIR = os.path.join(FILE, NAME, 'build')
GENCUMSKY = 'gencumulativesky'
#TESTS = '%s.tests' % NAME
#TEST_DATA = ['test_spectrl2_data.json']
#SOLPOS = 'solpos.c'
#SOLPOSAM = 'solposAM.c'
#SOLPOSAM_LIB = 'solposAM'
#SOLPOSAM_LIB_FILE = LIB_FILE % SOLPOSAM_LIB
#SPECTRL2 = 'spectrl2.c'
#SPECTRL2_2 = 'spectrl2_2.c'
#SPECTRL2_LIB = 'spectrl2'
#SPECTRL2_LIB_FILE = LIB_FILE % SPECTRL2_LIB
#SOLPOS = os.path.join(SRC_DIR, SOLPOS)
#SOLPOSAM = os.path.join(SRC_DIR, SOLPOSAM)
#SPECTRL2 = os.path.join(SRC_DIR, SPECTRL2)
#SPECTRL2_2 = os.path.join(SRC_DIR, SPECTRL2_2)
#SOLPOSAM_LIB_PATH = os.path.join(NAME, SOLPOSAM_LIB_FILE)
#SPECTRL2_LIB_PATH = os.path.join(NAME, SPECTRL2_LIB_FILE)
LIB_FILES_EXIST = all([
    os.path.exists(SOLPOSAM_LIB_PATH),
    os.path.exists(SPECTRL2_LIB_PATH)
])

# run clean or build libraries if they don't exist
if 'clean' in sys.argv:
    try:
        os.remove(SOLPOSAM_LIB_PATH)
        os.remove(SPECTRL2_LIB_PATH)
    except OSError as err:
        sys.stderr.write('%s\n' % err)
elif 'sdist' in sys.argv:
    for plat in ('win32', 'linux', 'darwin'):
        PKG_DATA.append('%s.mk' % plat)
    PKG_DATA.append(os.path.join('src', '*.*'))
    PKG_DATA.append(os.path.join('src', 'orig', 'solpos', '*.*'))
    PKG_DATA.append(os.path.join('src', 'orig', 'spectrl2', '*.*'))
elif not LIB_FILES_EXIST:
    # clean build directory
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)  # delete entire directory tree
    os.mkdir(BUILD_DIR)  # make build directory
    get_gencumsky_src(path=SRC_DIR)
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
if LIB_FILES_EXIST and 'sdist' not in sys.argv:
    PKG_DATA += [SOLPOSAM_LIB_FILE, SPECTRL2_LIB_FILE]

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

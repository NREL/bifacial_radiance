"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject

usage: `pip install -e .`

GenCumulativeSky was conceived, developed and validated by Darren Robinson and Andrew Stone for efficient solar irradiation modelling using RADIANCE
When using GenCumulativeSky they would be pleased if you would acknowledge their work by referring to the following article: "Robinson, D., Stone, A., 
Irradiation modeling made simple – the cumulative sky approach and its applications, Proc. PLEA 2004, Eindhoven 2004."

"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages, Extension
# To use a consistent encoding
from codecs import open
from os import path

import versioneer

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# gencumsky c++ source can (theoretically) be compiled at pip install runtime
gencumskymodule = Extension('gencumulativesky',
                            sources = ['GenCumSky/*.cpp'])

setup(
    name='bifacial_radiance',
    #ext_modules = [gencumskymodule],
    # Visual C++ build tools required: https://visualstudio.microsoft.com/visual-cpp-build-tools/
    # enable the above to automatically compile GenCumSky source code as part of 
    # setup.py.  Not really recommended for now...
    
    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    # version='0.3.4',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),

    description='Tools to interface with Radiance for the PV researcher',
    long_description=long_description,
    long_description_content_type="text/markdown",

    # The project's main homepage.
    url='https://github.com/NREL/bifacial_radiance',

    # Author details
    author='Chris Deline',
    author_email='chris.deline@nrel.gov',

    # Choose your license
    license='BSD License (3 clause)',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Science/Research',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: BSD License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
            ],

    # What does your project relate to?
    keywords='bifacial radiance photovoltaics pv ray tracing',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    #packages=find_packages(exclude=['contrib', 'docs', 'tests']) + ['data'],
    packages = ['bifacial_radiance'],
    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #py_modules=["bifacial_radiance"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'pandas',
        'pvlib >= 0.8.0',
        'pvmismatch',
        'configparser',
        'requests',
        
        ],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    

    extras_require={
        'all': [
            'ipython',
            'jupyter',
            'sphinx >= 1.8.0',
            'sphinx-autoapi>=1.1.0',
            'sphinx-rtd-theme>=0.4.3',
            'pytest',
            'pytest-cov',
            'pySMARTS',
            ],
    },
    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={
        'bifacial_radiance': [
            'data/ground.rad',
            'data/gencumulativesky.exe',
            'data/module.json',
            'data/default.ini',
            'images/*'],
    },
    include_package_data=True,
    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    #data_files=[('my_data', ['data/data_file'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    #entry_points={
    #    'console_scripts': [
    #        'sample=sample:main',
    #    ],
    #},
)

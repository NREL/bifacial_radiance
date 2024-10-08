try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    # for python < 3.8 (remove when dropping 3.7 support)
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version(__package__)
except PackageNotFoundError:
    __version__ = "0+unknown"


from bifacial_radiance.main import AnalysisObj, GroundObj, MetObj, RadianceObj, SceneObj
#from bifacial_radiance.readepw import readepw
from bifacial_radiance.module import ModuleObj
from bifacial_radiance import load
from bifacial_radiance import modelchain
from bifacial_radiance.gui import gui
from bifacial_radiance import mismatch
from bifacial_radiance.spectral_utils import generate_spectra
from bifacial_radiance import performance
#from ._version import get_versions
#__version__ = get_versions()['version']
#del get_versions

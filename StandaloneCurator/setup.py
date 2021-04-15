import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
includefiles = ['curation.ini', 'icon.ico', 'noimage.bin', 
    'lib/mkl_intel_thread.dll', 'lib/mkl_def.dll','lib/mkl_core.dll',
    'lib/libiomp5md.dll']

exclude_libs = ['_ssl', 'pyreadline', 'doctest', 'matplotlib', 'BaseHTTPServer', 
    'SocketServer', 'httplib', 'dateutil', 'itertools', 'mpl_toolkits', 'numpy.f2py', 
    'pydoc_data', 'urllib2', 'zipimport', 'scipy.sparse.linalg.eigen.arpack', 
    'scipy.sparse._sparsetools', 'scipy','unittest']

#
packages = ['numpy.core', 'numpy.lib', 'xmltodict','CameraCurator','UFOHandler','configparser']

includes = []
 
build_exe_options = {"packages": packages, 
    "optimize": 0, 'include_files':includefiles, "excludes":exclude_libs, 
    "includes":includes, "include_msvcr":False}


# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

setup(name = 'UFOCurator',
        version = '1.0',
        options = {'build_exe': build_exe_options},
        executables = [
            Executable('curateUFO.py', 
                base=base, 
                icon='icon.ico')]
      )

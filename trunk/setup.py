from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES
from os import sys
import os
import re

for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']


from imp import find_module
try:
    find_module('numpy')
except:
    sys.exit('### Error: python module numpy not found')
    
try:
    find_module('pyfits')
except:
    sys.exit('### Error: python module pyfits not found')

try:
    find_module('pyraf')
except:
    sys.exit('### Error: python module pyraf not found')

try:
    find_module('matplotlib')
except:
    sys.exit('### Error: python module matplotlib not found')

try:
    find_module('ephem')
except:
    sys.exit('### Error: python module ephem not found')

#try: find_module('MySQLdb')
#except: sys.exit('### Error: python module MySQLdb not found')


verstr = "unknown"
try:
    parentdir = os.getcwd()+'/'
    verstrline = open(parentdir+'/src/agnkey/_version.py', "rt").read()
except EnvironmentError:
    pass # Okay, there is no version file.
else:
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        verstr = mo.group(1)
    else:
        raise RuntimeError("unable to find version in " + parentdir + "+src/agnkey/_version.py")


setup(
    name = 'agnkey',
    version = verstr,#'0.1.3',
    author = 'S. Valenti',
    author_email = 'svalenti@lcogt.net',
    scripts=['bin/queryipac.py', 'bin/agnabsphot.py', 'bin/runagn.py', 'bin/agndiff.py', 'bin/agnarchivingspec.py',
             'bin/agnastro.py', 'bin/agncatalogue.py', 'bin/agncheck.py', 'bin/agnloop.py','bin/agnpsf2.py',
             'bin/agnmerge.py', 'bin/agnmaketempl.py', 'bin/agnfloyds.py', 'bin/agnnewcalib.py','bin/downloaddata.py',
             'bin/agnmaglocal.py', 'bin/agnmag.py', 'bin/agnpsf.py', 'bin/agnsn.py','bin/agntestheader.py'],
    url = 'lcogt.net',
    license = 'LICENSE.txt',
    description = 'agnkey is a package to reduce 1m0 SN data',
    long_description = open('README.txt').read(),
    requires = ['numpy','pyfits','pyraf','matplotlib','MySQLdb','ephem'],
    packages = ['agnkey'],
    package_dir = {'':'src'},
    package_data = {'agnkey' : ["standard/astrometry/*cat","standard/astrometry/*cfg", "standard/*txt", "standard/stdlist/*txt",
                                 "standard/cat/*dat", "standard/cat/*cat", 'webpagescript/*',
                                 "standard/cat/sloan/*cat", "standard/cat/landolt/*cat",
                                 "standard/cat/sloan/*cat", "standard/cat/apass/*cat",
                                 "standard/cat/sloanprime/*cat", "standard/cat/sloannatural/*cat",
                                 "standard/cat/landoltnatural/*cat", "standard/sex/*"]}
)

print('0')
import agnkey.util
print('1')
import agnkey.agnsqldef
print('2')
import agnkey.agnastrodef
print('3')
import agnkey.agnabsphotdef
print('4')
import agnkey.agnsnoopy
print('5')
import agnkey.sqlcl
print('6')
import agnkey.sites 
import agnkey.agnloopdef 
import agnkey.cosmics 
import agnkey.agndefin
import agnkey.zscale

__version__ = "unknown"
try:
    from _version import __version__
except ImportError:
    # We're running in a tree that doesn't have a _version.py, so we don't know what our version is.
    pass

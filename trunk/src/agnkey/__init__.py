import agnkey.util 
import agnkey.agnsqldef 
import agnkey.agnastrodef 
import agnkey.agnabsphotdef 
import agnkey.agnsnoopy 
import agnkey.sqlcl 
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

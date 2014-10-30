import util 
import agnsqldef 
import agnastrodef 
import agnabsphotdef 
import agnsnoopy 
import sqlcl 
import sites 
import agnloopdef 
import cosmics 
import agndefin

__version__ = "unknown"
try:
    from _version import __version__
except ImportError:
    # We're running in a tree that doesn't have a _version.py, so we don't know what our version is.
    pass

import agnsqldef 
import util 
import agnastrodef 
import agnabsphotdef 
import agnsnoopy 
import sqlcl 
import sites 
import agnloopdef 
import cosmics 
import agndefin

#from agnsqldef import *
#from util import *
#from agnastrodef import *
#from agnabsphotdef import *
#from agnsnoopy import *
#from sqlcl import *
#from sites import *
#from agnloopdef import *
#from cosmics import *

__version__ = "unknown"
try:
    from _version import __version__
except ImportError:
    # We're running in a tree that doesn't have a _version.py, so we don't know what our version is.
    pass

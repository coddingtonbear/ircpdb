"""Remote Python Debugger (pdb wrapper)."""

__author__ = "Adam Coddington <me@adamcoddington.net>"

# Note -- *must* set version in setup.py, too, since were (because
# of tradition) importing `set_trace` below, and that success isn't
# guaranteed.
__version__ = "1.8.0"


from .debugger import set_trace

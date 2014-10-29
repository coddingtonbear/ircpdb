#!/usr/bin/python

import os
from distutils.core import setup


here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = CHANGES = ''

setup(
    name="ircpdb",
    version="0.1",
    description="Remotely debug your Python application via IRC.",
    long_description=README + "\n\n" + CHANGES,
    author="Adam Coddington",
    author_email="me@adamcoddington.net",
    url="http://github.com/coddingtonbear/ircpdb",
    packages=["ircpdb"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.1",
        "Topic :: Software Development :: Debuggers",
    ]
)

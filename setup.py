"""Setup script for RxLab-Instruments.

Usage (from root folder):

python -m pip install .

Or to install in developer mode (allows changes to take effect immediately):

python -m pip install -e .

"""

import io
from os import path

from setuptools import find_packages, setup

import labinstruments


root = path.abspath(path.dirname(__file__))

def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(path.join(root, filename), encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.md')

setup(
    name = "RxLab-Instruments",
    version = labinstruments.__version__,
    author = "John Garrett",
    author_email = "john.garrett@cfa.harvard.edu",
    description = (
        "Control instruments in the Receiver Lab over Ethernet"
    ),
    license = "MIT",
    keywords = [
        "SCPI", 
        "Ethernet", 
        "Lab equipment", 
        "Signal generator",
        "DC power supply", 
        "Oscilloscope",
        "Multimeter"
    ],
    url = "https://github.com/Smithsonian/RxLab-Instruments",
    packages=find_packages(),
    install_requires=[
        'sockets',
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    platforms='any',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering",
    ],
    project_urls={
        'Changelog': 'https://github.com/Smithsonian/RxLab-Instruments/CHANGES.md',
        'Issue Tracker': 'https://github.com/Smithsonian/RxLab-Instruments/issues',
    },
    # scripts=[],
)

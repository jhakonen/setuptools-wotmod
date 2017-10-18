"""
This file contains setuptools setup script. Provides means to generate a wotmod
package for World of Tanks game.
"""

from setuptools import setup, find_packages
import os

script_dir = os.path.dirname(__file__)

setup(
    # Name is also mod-id of the wotmod package
    name = 'helloworld',
    # Each dot separated version fragment will be, by default, at least two
    # characters wide, padded with zero if not wide enough, f.e. 1.0 becomes 01.00.
    version = '1.0',
    # Description will also be available in a auto generated meta.xml file
    # within the wotmod archive.
    description = 'Mod for embracing the world',
    long_description = open(os.path.join(script_dir, 'README.txt')).read(),
    # Author is also author-id of the wotmod archive, if not defined,
    # maintainer's name is is used
    author = 'johndoe',
    license = 'MIT License',
    url = 'http://example.com/',
    # Tell setuptools to build and include 'helloworld' package and the
    # individual mod_helloworld module in the final distribution of .wotmod.
    # These files will end up by default to res/scripts/client/gui/mods within
    # the wotmod package.
    packages = find_packages(),
    py_modules = ['mod_helloworld'],
    # Include also name.txt data file in the wotmod package. The file will end
    # up by default to res/mods/<author_id>.<mod_id> within the package.
    data_files = ['data/name.txt'],
    # These requires will install wotdisttools on first execution if it not
    # yet installed
    setup_requires = ['wotdisttools'],
    install_requires = ['wotdisttools'],
    # Required as wotdisttools is not yet in PyPI
    dependency_links = [
        'https://github.com/jhakonen/wotdisttools/tarball/master#egg=wotdisttools'
    ],
)

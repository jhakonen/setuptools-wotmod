"""
This file contains setuptools setup script. Provides means to generate a wotmod
package for World of Tanks game.
"""

from setuptools import setup, find_packages

setup(
    # Name is also mod-id of the wotmod package
    name = 'helloworld',
    # Each dot separated version fragment will be, by default, at least two
    # characters wide, padded with zero if not wide enough, f.e. 1.0 becomes 01.00.
    version = '1.0',
    # Description will also be available in a auto generated meta.xml file
    # within the wotmod archive.
    description = 'Mod for embracing the world',
    # Author is also author-id of the wotmod archive, if not defined,
    # maintainer's name is is used
    author = 'johndoe',
    license = 'WTFPL License',
    # Tell setuptools to build and include 'helloworld' package and the
    # individual mod_helloworld module in the final distribution of .wotmod.
    # These files will end up by default to res/scripts/client/gui/mods within
    # the wotmod package.
    packages = find_packages(),
    py_modules = ['mod_helloworld'],
    # Include also name.txt data file in the wotmod package. The file will end
    # up by default to res/mods/<author_id>.<mod_id> within the package.
    data_files = [
        ('data', ['data/name.txt'])
    ],
    # This require will install setuptools-wotmod on first execution if it not
    # yet installed
    setup_requires = ['setuptools-wotmod'],
    # Required as setuptools-wotmod is not yet in PyPI
    dependency_links = [
        'https://github.com/jhakonen/setuptools-wotmod/tarball/master#egg=setuptools-wotmod'
    ],
)

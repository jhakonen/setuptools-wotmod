#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='wotdisttools',
    version='0.1',
    packages=find_packages(),
    description='distutils/setuptools integration for creating World of Tanks mods',
    long_description=open('README.md').read(),
    author='jhakonen',
    url='https://github.com/jhakonen/wot-teamspeak-mod/',
    license='MIT License',
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    entry_points={
        "distutils.commands": [
            "bdist_wotmod = wotdisttools.bdist_wotmod:bdist_wotmod",
        ],
    },
)

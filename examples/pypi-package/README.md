# PyPI packaging example

This example demonstrates how to download 3rd party project from PyPI and
package it to a wotmod archive, ready to be used in World of Tanks.

## Prerequisites

You need to install setuptools-wotmod package by changing to this project's
root directory and issuing command:

```bash
python setup.py install
```

## Installation

This directory contains two example scripts, one for Windows/Powershell and
another for Linux/Bash, both do the same thing, which is to download pydash
(see: https://pypi.python.org/pypi/pydash/4.2.1) and build a wotmod package out
of it.

After executing the script you can copy the built wotmod package to
`mods\<version>` directory in game's directory.

Then, with debugging tools (e.g. https://github.com/juho-p/wot-debugserver) you
can enter game's Python interpreter and import the package:

```python
>>> import pydash as _
>>> _.flatten_deep([1, 2, [3, [4, 5, [6, 7]]]])
[1, 2, 3, 4, 5, 6, 7]
```

## License

This example is licensed under WTFPL license, for more info, see:
  http://www.wtfpl.net/about/

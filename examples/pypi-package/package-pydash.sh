#!/bin/bash

# This script fetches pydash 4.2.1 from PyPI and builds and packages it into a
# wotmod package. After script execution you should have package with name
# com.github.dgilland.pydash_04.02.01.wotmod.

SCRIPT_DIR=$(dirname $(readlink -f "$0"))

# Download pydash source package from PyPI
pip download pydash==4.2.1 --no-binary=:all:
tar -zxvf pydash-4.2.1.tar.gz

# Build and package pydash as wotmod package
#  - with install-lib put pydash to PYTHONPATH (other PYTHONPATH choices are
#    scripts/client and scripts/common/Lib)
#  - with author-id change defined author to domain-ish format to better
#    describe where the package is gotten from
#  - with dist-dir output wotmod to same folder where this script is
pushd pydash-4.2.1
python setup.py bdist_wotmod \
    --install-lib=res/scripts/common \
    --author-id=com.github.dgilland \
    --dist-dir=$SCRIPT_DIR
popd

# This script fetches pydash 4.2.1 from PyPI and builds and packages it into a
# wotmod package. After script execution you should have package with name
# com.github.dgilland.pydash_04.02.01.wotmod. This you can insert to game's
# mods\<version> folder and then in game's interpreter simply do:
#
#   import pydash
#

# Since Windows 10 doesn't come tools to extract tar.gz archive, you will need
# to install 7-Zip first (see: http://www.7-zip.org/)

# In addition, you need to install bdist_wotmod command, cd to this project's
# root folder and give command:
#   python setup.py install

# Adjust this path if you installed 7-Zip somewhere else
$SEVENZIP_PATH="C:\Program Files\7-Zip"

$env:PATH="$env:PATH;$SEVENZIP_PATH"

# Download pydash source package from PyPI
pip download pydash==4.2.1 --no-binary=:all:
7z -y e pydash-4.2.1.tar.gz
7z -y x pydash-4.2.1.tar

# Build and package pydash as wotmod package
#  - with install-lib put pydash to PYTHONPATH (other PYTHONPATH choices are
#    scripts/client and scripts/common/Lib)
#  - with author-id change defined author to domain-ish format to better
#    describe where the package is gotten from
#  - with dist-dir output wotmod to same folder where this script is
Push-Location -Path pydash-4.2.1
python setup.py bdist_wotmod `
    --install-lib=res/scripts/common `
    --author-id=com.github.dgilland `
    --dist-dir=$PSScriptRoot
Pop-Location

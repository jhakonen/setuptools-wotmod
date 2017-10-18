Hello World mod example
=======================
This example demonstrates how to create a simple World of Tanks modification.
The code shows how to:
 - Print to python.log,
 - Load files from within wotmod package, and
 - React to game start up and shutdown

Prerequisites
-------------
You will need Python 2.7 interpreter, do not use older (-2.6) or newer (3.0+)
versions as the compiled Python byte code files (pyc) must be compatible with
World of Tanks's own embedded Python interpreter which is also based on
version 2.7.

Installation
------------
Within the example's directory execute command::

    python setup.py bdist_wotmod

This will produce 'johndoe.helloworld_01.00.wotmod' file to 'dist' subdirectory.
Copy the created wotmod file to '$ROOT\mods\$VERSION', where:
 - $ROOT is WoT's root folder e.g. C:\Games\World_of_Tanks, and
 - $VERSION is game's current version

You may also install the wotmod to the game with one command by changing the
default dist directory::

    python setup.py bdist_wotmod --dist-dir=$ROOT\mods\$VERSION

Now start following python.log to see what the mods prints. In Powershell::

    Get-Content $ROOT\python.log -Tail 3 -Wait

Start the game, and after a while shut it down, and you should see HelloWorld
embracing the world :)


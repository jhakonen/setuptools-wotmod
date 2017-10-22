"""
Main entry point for mods.
World of Tanks will load any module from a wotmod package, as long as:
 - module is in res/scripts/client/gui/mods,
 - module's name starts with 'mod_', and
 - module has extension 'pyc'.

Once loaded, the game will call several functions from the module if they are
defined, most notably init() and fini().
"""

from helloworld import resources

def init():
    """
    Mod initialization function.
    Called by World of Tanks when the game starts up.
    """
    name = resources.read_file('mods/johndoe.helloworld/data/name.txt')
    # Print statements end up to python.log in game's root directory
    print 'Hello %s!' % name

def fini():
    """
    Mod deinitialization function.
    Called by World of Tanks when the game shuts down.
    """
    name = resources.read_file('mods/johndoe.helloworld/data/name.txt')
    print 'Bye bye %s!' % name

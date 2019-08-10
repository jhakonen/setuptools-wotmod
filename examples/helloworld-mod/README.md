# Hello World mod example

This example demonstrates how to create a simple World of Tanks modification.
The code shows how to:
 - Print to python.log,
 - Load files from within wotmod package, and
 - React to game start up and shutdown

## Installation

Within the example's directory execute command:

```bash
python setup.py bdist_wotmod
```

This will produce `johndoe.helloworld_01.00.wotmod` file to `dist` subdirectory.
Copy the file to `mods/<current version>` directory under game's directory.

You may also install the wotmod to the game with one command by changing the
default dist directory:

```bash
    python setup.py bdist_wotmod --dist-dir='<game dir>/mods/<current version>'
```

Now start following `python.log` to see what the mods prints.

In Powershell:

```powershell
    Get-Content <game dir>\python.log -Tail 3 -Wait
```

Or in bash:

```bash
    tail -f '<game dir>/python.log'
```

Start the game, and after a while shut it down, and you should see HelloWorld
embracing the world :)

## License

This example is licensed under WTFPL license, for more info, see:
  http://www.wtfpl.net/about/

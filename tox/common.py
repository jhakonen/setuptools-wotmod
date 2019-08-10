from __future__ import print_function

import os
import shutil
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
PROJECT_DIR = os.path.realpath(os.path.join(SCRIPT_DIR, '..'))
HELLOWORLD_DIR = os.path.join(PROJECT_DIR, 'examples', 'helloworld-mod')
PYPIPACKAGE_DIR = os.path.join(PROJECT_DIR, 'examples', 'pypi-package')

def exec_command(args, cwd):
    process = subprocess.Popen(args, cwd=cwd)
    code = process.wait()
    if code != 0:
        raise RuntimeError('Process failed with error code: %d' % code)

def print_header(message):
    message = '%s (%s)' % (message, os.environ.get('TOX_ENV_NAME', 'unknown env'))
    print('')
    print('=' * (len(message) + 8))
    print('   ', message)
    print('=' * (len(message) + 8))
    print('')

def remove_file(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)

def remove_dir(dirpath):
    if os.path.exists(dirpath):
        shutil.rmtree(dirpath, ignore_errors=True)

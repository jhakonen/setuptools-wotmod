import os

from common import *

print_header('Cleaning projects')
exec_command(['python', 'setup.py', '-q', 'clean'], PROJECT_DIR)
exec_command(['python', 'setup.py', '-q', 'clean', '--dist', '--eggs', '--pycache'], HELLOWORLD_DIR)
remove_dir(os.path.join(PYPIPACKAGE_DIR, 'pydash-4.2.1'))
remove_file(os.path.join(PYPIPACKAGE_DIR, 'pydash-4.2.1.tar.gz'))
remove_file(os.path.join(PYPIPACKAGE_DIR, 'com.github.dgilland.pydash_04.02.01.wotmod'))

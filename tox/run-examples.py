import platform

from common import *

exec_command(['pip', 'install', '-q', '.'], PROJECT_DIR)
try:
    exec_command(['python', 'setup.py', '-q', 'clean', '--dist', '--eggs', '--pycache'], HELLOWORLD_DIR)
    print_header('Building example at %s' % HELLOWORLD_DIR)
    exec_command(['python', 'setup.py', 'bdist_wotmod'], HELLOWORLD_DIR)
    print_header('Building example at %s' % PYPIPACKAGE_DIR)
    if platform.system() == 'Linux':
        exec_command(['./package-pydash.sh'], PYPIPACKAGE_DIR)
    else:
        # TODO
        pass
finally:
    exec_command(['pip', 'uninstall', '-q', '-y', 'setuptools-wotmod'], PROJECT_DIR)

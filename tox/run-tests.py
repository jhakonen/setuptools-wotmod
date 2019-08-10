from common import *

print_header('Running tests')
exec_command(['python', 'setup.py', 'test'], PROJECT_DIR)

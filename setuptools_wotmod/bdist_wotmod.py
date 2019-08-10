"""
Implements setuptools 'bdist_wotmod' command.
The command builds python files, installs them to a temp dir and creates a
wotmod package of them.
"""

from distutils import log
from distutils.dir_util import mkpath, remove_tree
from distutils.file_util import copy_file
import distutils.util
from setuptools import Command
from setuptools.extern import packaging

from contextlib import contextmanager
from functools import partial
import os
import posixpath
import re
import struct
from tempfile import NamedTemporaryFile
import warnings
import xml.etree.ElementTree as ET
from xml.dom import minidom
import zipfile

class bdist_wotmod(Command):

    description = 'create .wotmod mod package for World of Tanks'

    # List of option tuples: long name, short name (None if no short
    # name), and help string.
    user_options = [
        ('bdist-dir=', 'd',
         "temporary directory for creating the distribution"),
        ('dist-dir=', 'd',
         "directory to put final built distributions in"),
        ('author-id=', None,
         "developer's nickname or website (f.e. com.example) [default: setup author or maintainer]"),
        ('mod-id=', None,
         "modification identifier [default: setup name]"),
        ('mod-version=', None,
         "modification version [default: setup version]"),
        ('mod-description=', None,
         "modification description [default: setup description]"),
        ('version-padding=', None,
         "number of zeros to use to pad each version fragment [default: 2]"),
        ('install-lib=', None,
         "installation directory for module distributions [default: 'res/scripts/client/gui/mods']"),
        ('install-data=', None,
         "installation directory for data files [default: 'res/mods/<author_id>.<mod_id>']"),
        ('python27=', None,
         "Path to Python 2.7 executable (required when command is executed with non-2.7 Python interpreter) "
         "[default: BDIST_WOTMOD_PYTHON27 environment variable]"),
    ]

    def initialize_options(self):
        self.bdist_dir       = None
        self.dist_dir        = None
        self.author_id       = None
        self.mod_id          = None
        self.mod_version     = None
        self.mod_description = None
        self.version_padding = None
        self.install_lib     = None
        self.install_data    = None
        self.python27        = None

    def finalize_options(self):
        # Resolve install directory
        if self.bdist_dir is None:
            bdist_base = self.get_finalized_command('bdist').bdist_base
            self.bdist_dir = os.path.join(bdist_base, 'wotmod')
        # Resolve version_padding
        if self.version_padding is None:
            self.version_padding = 2
        # Resolve author_id
        if self.author_id is None:
            self.author_id = self.distribution.get_author()
        if self.author_id == 'UNKNOWN':
            self.author_id = self.distribution.get_maintainer()
        self.author_id = re.sub(r'[^\w.]', '', self.author_id)
        # Resolve mod_id
        if self.mod_id is None:
            self.mod_id = self.distribution.get_name()
        self.mod_id = re.sub(r'[^\w.]', '', self.mod_id)
        # Resolve mod_version and pad each version fragment with zeros
        if self.mod_version is None:
            self.mod_version = self.distribution.get_version()
        # Try to pick only major, minor and patch parts from the input version.
        # Using any of the other parts (e.g. rc1, -alpha, -beta) might lead to
        # issues when author leaves them out at time of creating a release
        # version. As WoT determines the wotmod file to load using strcmp() it
        # is not safe to add optional parts at the end of the version string as
        # those prerelease wotmod packages would be loaded instead of the
        # release version.
        version = self.distribution.get_version()
        version_obj = packaging.version.Version(version)
        release_parts = version_obj._version.release
        release_str = '.'.join(str(x) for x in release_parts)
        if release_str != version:
            warnings.warn(
                'bdist_wotmod: Using only release part %s of the version %s to form '
                'the wotmod package version' % (repr(release_str), repr(version))
            )
        parts = release_parts
        if len(parts) == 1:
            warnings.warn('bdist_wotmod: Minor part of the version is missing, setting it to zero')
            parts += (0,)
        if len(parts) == 2:
            warnings.warn('bdist_wotmod: Patch part of the version is missing, setting it to zero')
            parts += (0,)
        self.mod_version =  '.'.join(str(part).rjust(self.version_padding, '0') for part in parts)
        # Resolve mod_description
        if self.mod_description is None:
            self.mod_description = self.distribution.get_description()
        self.mod_description = re.sub(r'\W', '', self.mod_description)
        # Resolve where py/pyc files should be placed in
        if self.install_lib is None:
            self.install_lib = 'res/scripts/client/gui/mods'
        # Resolve where data files should be placed in
        if self.install_data is None:
            self.install_data = 'res/mods/%s.%s' % (self.author_id, self.mod_id)
        if self.python27 is None and 'BDIST_WOTMOD_PYTHON27' in os.environ:
            self.python27 = os.environ['BDIST_WOTMOD_PYTHON27']

        self.set_undefined_options('bdist', ('dist_dir', 'dist_dir'))

    def run(self):
        self.distribution.get_command_obj('install_data').warn_dir = 0
        self.build_files()
        self.verify_pyc_files()
        self.install_files()
        self.create_metaxml()
        self.include_other_documents()
        self.mkpath(self.dist_dir)
        package_path = self.create_wotmod_package()

        self.distribution.dist_files.append(('bdist_wotmod', 'any', package_path))
        if os.path.isdir(self.bdist_dir):
            remove_tree(self.bdist_dir)

    def build_files(self):
        """
        Compiles .py files.
        """
        # By default build_py just copies already built pyc files from
        # a cache. Set compile=1 to force recreation of those files.
        build = self.reinitialize_command('build_py', reinit_subcommands=1)
        build.compile=1

        if self.python27:
            # Monkey patch byte_compile() with custom function that delegates
            # the byte compilation to a separate Python 2.7 interpreter.
            # This is required when setuptools-wotmod is executed with Python
            # 3.x. The pyc files must still be Python 2.7 based for them to
            # succesfully load into World of Tanks's embedded Python interpreter.
            with patch_func(distutils.util, 'byte_compile', partial(python27_byte_compile, self.python27)):
                self.run_command('build')
        else:
            self.run_command('build')

    def verify_pyc_files(self):
        """
        Ensures that compiled pyc files are loadable by Python 2.7.
        """
        for root, dirs, files in os.walk(self.get_finalized_command('build_py').build_lib):
            for filename in files:
                if os.path.splitext(filename)[1] == '.pyc':
                    filepath = os.path.join(root, filename)
                    assert is_python27_pyc_file(filepath), \
                        'File "%s" is not valid Python 2.7 byte-compiled ' \
                        'file, ensure that command line argument --python27 ' \
                        'or env variable BDIST_WOTMOD_PYTHON27 points to ' \
                        'Python 2.7 interpreter' % filepath

    def install_files(self):
        """
        Installs files defined in setup.py to bdist-dir.
        """
        install = self.reinitialize_command('install', reinit_subcommands=1)
        install.root = self.bdist_dir
        install.install_lib = self.install_lib
        install.install_data = self.install_data
        install.warn_dir = 0
        # Compiling is already done in build-step, no need to recompile. This
        # doesn't even work with Python 3 if source files contain Python 2
        # spesific syntax
        install.compile = 0
        # No need for egg metadata and executable scripts in wotmod package
        install.sub_commands = [cmd for cmd in install.sub_commands if cmd[0] != 'install_egg_info']
        install.sub_commands = [cmd for cmd in install.sub_commands if cmd[0] != 'install_scripts']
        log.info("installing to %s" % self.bdist_dir)
        self.run_command('install')

    def create_metaxml(self):
        """
        Creates meta.xml file to root of bdist-dir.
        """
        metaxml_path = os.path.join(self.bdist_dir, 'meta.xml')
        log.info("Writing %s", metaxml_path)
        with open(metaxml_path, 'wb') as metaxml_file:
            root = ET.Element('root')
            id = ET.SubElement(root, 'id')
            id.text = '%s.%s' % (self.author_id, self.mod_id)
            version = ET.SubElement(root, 'version')
            version.text = self.mod_version
            name = ET.SubElement(root, 'name')
            name.text = self.distribution.get_name()
            description = ET.SubElement(root, 'description')
            description.text = self.distribution.get_description()
            xml_contents = ET.tostring(root, encoding='utf-8')
            xml_contents = minidom.parseString(xml_contents).toprettyxml(encoding='utf-8')
            metaxml_file.write(xml_contents)

    def include_other_documents(self):
        """
        Copies other documents (license, changelog, readme) files to root of
        bdist-dir.
        """
        patterns = ['readme', 'license', 'changes']
        entries = os.listdir('.')
        entries = filter(os.path.isfile, entries)
        matches = filter(lambda e: any(p in e.lower() for p in patterns), entries)
        for match in matches:
            copy_file(match, self.bdist_dir)

    def create_wotmod_package(self):
        """
        Inserts files from bdist-dir to .wotmod package and stores it to dist-dir.
        :return: path to wotmod package file
        """
        zip_filename = self.get_output_file_path()
        mkpath(os.path.dirname(zip_filename))

        log.info("creating '%s' and adding '%s' to it", zip_filename, self.bdist_dir)

        archive_root = to_posix_separators(self.bdist_dir)

        with zipfile.ZipFile(zip_filename, 'w') as zip:
            for dirpath, dirnames, filenames in os.walk(archive_root):
                dirpath = to_posix_separators(dirpath)

                # Build relative path from bdist_dir forward
                archive_dirpath = dirpath.replace(posixpath.commonprefix(
                    [dirpath, archive_root]), '').strip('/')

                # Create files
                for name in filenames:
                    archive_path = posixpath.join(archive_dirpath, name)
                    path = posixpath.normpath(posixpath.join(dirpath, name))
                    if posixpath.isfile(path):
                        log.info("adding '%s'" % archive_path)
                        zip.write(path, archive_path)

                # Set correct flags for directories
                for name in dirnames:
                    archive_path = posixpath.join(archive_dirpath, name) + '/'
                    log.info("adding '%s'" % archive_path)
                    zip.writestr(archive_path, '')

        return zip_filename

    def get_output_file_path(self):
        """
        Returns path to the wotmod file. This method can be called either
        before or after running the command. When executed before the returned
        file path hasn't been created yet.
        :return: path to the wotmod package file
        """
        zip_filename = "%s.%s_%s.wotmod" % (
            self.author_id, self.mod_id, self.mod_version)
        return os.path.abspath(os.path.join(self.dist_dir, zip_filename))

def to_posix_separators(win_path):
    return win_path.replace('\\', '/') if os.sep == '\\' else win_path

@contextmanager
def patch_func(module, function_name, replacement):
    """
    Helper function that patches a function in a module with a replacement
    function. The returned value must be used in with-statement where the
    patching will happen upon entering the inner block and the patching is
    undone when execution leaves the block.

    :param module: target module to modify
    :param function_name: target function name to modify
    :param replacement: replacement function
    :return: context manager
    """
    original = getattr(module, function_name)
    setattr(module, function_name, replacement)
    try:
        yield
    finally:
        setattr(module, function_name, original)

def python27_byte_compile(python27, files, optimize, force, prefix, dry_run):
    """
    Replacement function for distutils.util.byte_compile() which delegates call
    to external Python interpreter, given as the first argument.
    """
    with NamedTemporaryFile(suffix='.py', delete=False) as script_file:
        script_file.write('\n'.join([
            'from distutils.util import byte_compile',
            'files = [',
            ',\n'.join(map(repr, files)),
            ']',
            'byte_compile(files, optimize=%r, force=%r, prefix=%r)' % (optimize, force, prefix)
        ]).encode('utf-8'))
    try:
        distutils.util.spawn([python27, script_file.name], dry_run=dry_run)
    finally:
        distutils.util.execute(os.remove, (script_file.name,), "removing %s" % script_file.name, dry_run=dry_run)

def is_python27_pyc_file(filepath):
    with open(filepath, 'rb') as pyc_file:
        magic_number = struct.unpack('BBBB', pyc_file.read(4))
        return magic_number == (0x03, 0xf3, 0x0d, 0x0a)
    return False

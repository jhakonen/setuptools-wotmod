"""
Implements setuptools 'bdist_wotmod' command.
The command builds python files, installs them to a temp dir and creates a
wotmod package of them.
"""

from distutils import log
from distutils.dir_util import mkpath, remove_tree
from distutils.file_util import copy_file
from setuptools import Command

import os
import posixpath
import re
import zipfile
import xml.etree.ElementTree as ET
from xml.dom import minidom

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
        self.mod_version = '.'.join(part.rjust(self.version_padding, '0') for part in self.mod_version.split('.'))
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
        self.set_undefined_options('bdist', ('dist_dir', 'dist_dir'))

    def run(self):
        self.build_files()
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
        self.run_command('build')

    def install_files(self):
        """
        Installs files defined in setup.py to bdist-dir.
        """
        install = self.reinitialize_command('install', reinit_subcommands=1)
        install.root = self.bdist_dir
        install.install_lib = self.install_lib
        install.install_data = self.install_data
        install.warn_dir = 0
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
        with open(metaxml_path, 'w') as metaxml_file:
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
        zip_filename = "%s.%s_%s.wotmod" % (
            self.author_id, self.mod_id, self.mod_version)
        zip_filename = os.path.abspath(os.path.join(self.dist_dir, zip_filename))
        mkpath(os.path.dirname(zip_filename))

        log.info("creating '%s' and adding '%s' to it", zip_filename, self.bdist_dir)

        archive_root = self.to_posix_separators(self.bdist_dir)

        with zipfile.ZipFile(zip_filename, 'w') as zip:
            for dirpath, dirnames, filenames in os.walk(archive_root):
                dirpath = self.to_posix_separators(dirpath)

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

    def to_posix_separators(self, win_path):
        return win_path.replace('\\', '/') if os.sep == '\\' else win_path
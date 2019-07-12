"""
Unit tests for bdist_wotmod command.
"""

import unittest
import sys
import os
import zipfile
import xml.etree.ElementTree as ET

from setuptools import Distribution
from distutils.tests import support
from nose.tools import assert_equal
import pytest

from setuptools_wotmod.bdist_wotmod import bdist_wotmod

@pytest.mark.filterwarnings("ignore:bdist_wotmod")
@pytest.mark.filterwarnings("ignore:Normalizing .+ to .+")
class BuildWotmodTestCase(support.TempdirManager, unittest.TestCase):

    def setUp(self):
        super(BuildWotmodTestCase, self).setUp()
        self.old_location = os.getcwd()
        self.old_sys_argv = sys.argv, sys.argv[:]
        self.pkg_dir = self.mkdtemp()
        os.chdir(self.pkg_dir)
        sys.argv = ['setup.py']

    def tearDown(self):
        os.chdir(self.old_location)
        sys.argv = self.old_sys_argv[0]
        sys.argv[:] = self.old_sys_argv[1]
        super(BuildWotmodTestCase, self).tearDown()

    def assertFileInZip(self, zip_path, arcname, contents=None):
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            self.assertIn(arcname, zip_file.namelist())
            if contents is not None:
                self.assertEqual(contents, zip_file.read(arcname))

    def assertDirInZip(self, zip_path, arcname):
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            self.assertIn(arcname, zip_file.namelist())
            dir_attributes = zip_file.getinfo(arcname).external_attr
            self.assertTrue(dir_attributes & (0o40000 << 16))

    def assertXmlXPath(self, xml_contents, xpath, text_value):
        root = ET.fromstring(xml_contents)
        self.assertEqual(root.findtext(xpath), text_value)

    def test_common_package_creation(self):
        # Setup test project
        self.write_file((self.pkg_dir, 'setup.py'), '#')
        self.write_file((self.pkg_dir, 'foo.py'), '#')
        self.write_file((self.pkg_dir, 'README'), 'README contents')
        self.write_file((self.pkg_dir, 'LICENSE'), 'LICENSE contents')
        self.write_file((self.pkg_dir, 'CHANGES'), 'CHANGES contents')
        dist = create_distribution()
        cmd = bdist_wotmod(dist)
        cmd.install_lib = 'res/scripts/common'
        cmd.author_id = 'com.github.jhakonen'
        # Execute command to produce wotmod file
        cmd.ensure_finalized()
        cmd.run()
        # Test that produced wotmod file looks ok
        wotmod_path = os.path.join(self.pkg_dir, 'dist', 'com.github.jhakonen.foo_00.01.00.wotmod')
        self.assertIn(os.path.basename(wotmod_path), os.listdir(os.path.dirname(wotmod_path)))
        self.assertDirInZip(wotmod_path, 'res/')
        self.assertDirInZip(wotmod_path, 'res/scripts/')
        self.assertDirInZip(wotmod_path, 'res/scripts/common/')
        self.assertFileInZip(wotmod_path, 'README', 'README contents')
        self.assertFileInZip(wotmod_path, 'LICENSE', 'LICENSE contents')
        self.assertFileInZip(wotmod_path, 'CHANGES', 'CHANGES contents')
        self.assertFileInZip(wotmod_path, 'meta.xml')
        self.assertFileInZip(wotmod_path, 'res/scripts/common/foo.py', '#')
        self.assertFileInZip(wotmod_path, 'res/scripts/common/foo.pyc')
        contents = get_file_in_zip_contents(wotmod_path, 'meta.xml')
        self.assertXmlXPath(contents, './id', 'com.github.jhakonen.foo')
        self.assertXmlXPath(contents, './version', '00.01.00')
        self.assertXmlXPath(contents, './name', 'foo')
        self.assertXmlXPath(contents, './description', 'has cool stuff')

@pytest.mark.filterwarnings("ignore:bdist_wotmod")
@pytest.mark.filterwarnings("ignore:Normalizing .+ to .+")
class GetOutputFilePathTestCase(support.TempdirManager, unittest.TestCase):

    def setUp(self):
        super(GetOutputFilePathTestCase, self).setUp()
        self.test_dir = self.mkdtemp()

    def create_command(self, **kwargs):
        dist = create_distribution(**kwargs)
        cmd = bdist_wotmod(dist)
        cmd.dist_dir = self.test_dir
        cmd.ensure_finalized()
        return cmd

    def test_wotmod_file_is_in_dist_dir(self):
        cmd = self.create_command()
        assert_equal(os.path.dirname(cmd.get_output_file_path()), self.test_dir)

    def test_returns_padded_release_version(self):
        cmd = self.create_command(version='0.1.2')
        assert_equal(cmd.get_output_file_path(), os.path.join(self.test_dir, 'jhakonen.foo_00.01.02.wotmod'))

    def test_adds_missing_patch_version(self):
        cmd = self.create_command(version='0.1')
        assert_equal(cmd.get_output_file_path(), os.path.join(self.test_dir, 'jhakonen.foo_00.01.00.wotmod'))

    def test_adds_missing_minor_version(self):
        cmd = self.create_command(version='1')
        assert_equal(cmd.get_output_file_path(), os.path.join(self.test_dir, 'jhakonen.foo_01.00.00.wotmod'))

    def test_adds_missing_version(self):
        cmd = self.create_command(version=None)
        assert_equal(cmd.get_output_file_path(), os.path.join(self.test_dir, 'jhakonen.foo_00.00.00.wotmod'))

    def test_drops_non_release_fragments(self):
        cmd = self.create_command(version='0.1.2-rc1')
        assert_equal(cmd.get_output_file_path(), os.path.join(self.test_dir, 'jhakonen.foo_00.01.02.wotmod'))

def create_distribution(**kwargs):
    dist = Distribution(dict({
        'name': 'foo',
        'version': '0.1',
        'py_modules': ['foo'],
        'url': 'https://github.com/jhakonen/',
        'author': 'jhakonen',
        'author_email': 'me@example.fi',
        'description': 'has cool stuff'
    }, **kwargs))
    dist.script_name = 'setup.py'
    return dist

def get_file_in_zip_contents(zip_path, arcname):
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        return zip_file.read(arcname)

if __name__ == '__main__':
    unittest.main()

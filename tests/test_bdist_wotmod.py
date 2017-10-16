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

from wotdisttools.bdist_wotmod import bdist_wotmod

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

    def getFileInZipContents(self, zip_path, arcname):
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            return zip_file.read(arcname)

    def test_common_package_creation(self):
        # Setup test project
        self.write_file((self.pkg_dir, 'setup.py'), '#')
        self.write_file((self.pkg_dir, 'foo.py'), '#')
        self.write_file((self.pkg_dir, 'README'), 'README contents')
        self.write_file((self.pkg_dir, 'LICENSE'), 'LICENSE contents')
        self.write_file((self.pkg_dir, 'CHANGES'), 'CHANGES contents')
        dist = Distribution({
            'name': 'foo',
            'version': '0.1',
            'py_modules': ['foo'],
            'url': 'https://github.com/jhakonen/',
            'author': 'jhakonen',
            'author_email': 'me@example.fi',
            'description': 'has cool stuff'
        })
        dist.script_name = 'setup.py'
        cmd = bdist_wotmod(dist)
        cmd.install_lib = 'res/scripts/common'
        cmd.author_id = 'com.github.jhakonen'
        # Execute command to produce wotmod file
        cmd.ensure_finalized()
        cmd.run()
        # Test that produced wotmod file looks ok
        wotmod_path = os.path.join(self.pkg_dir, 'dist', 'com.github.jhakonen.foo_00.01.wotmod')
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
        contents = self.getFileInZipContents(wotmod_path, 'meta.xml')
        self.assertXmlXPath(contents, './id', 'com.github.jhakonen.foo')
        self.assertXmlXPath(contents, './version', '00.01')
        self.assertXmlXPath(contents, './name', 'foo')
        self.assertXmlXPath(contents, './description', 'has cool stuff')

if __name__ == '__main__':
    unittest.main()

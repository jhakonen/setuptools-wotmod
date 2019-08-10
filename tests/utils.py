import os
import shutil
import tempfile
import zipfile

class TempdirManager(object):
    """
    Copied from distutils.tests. Avoids nasty dependency to tests package
    which usually doesn't exist in Ubuntu system interpreters.
    """

    def setUp(self):
        super(TempdirManager, self).setUp()
        self.old_cwd = os.getcwd()
        self.tempdirs = []

    def tearDown(self):
        os.chdir(self.old_cwd)
        super(TempdirManager, self).tearDown()
        while self.tempdirs:
            d = self.tempdirs.pop()
            shutil.rmtree(d, os.name in ('nt', 'cygwin'))

    def mkdtemp(self):
        d = tempfile.mkdtemp()
        self.tempdirs.append(d)
        return d

    def write_file(self, path, content='xxx'):
        if isinstance(path, (list, tuple)):
            path = os.path.join(*path)
        f = open(path, 'w')
        try:
            f.write(content)
        finally:
            f.close()


def get_file_in_zip_contents(zip_path, arcname):
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        return zip_file.read(arcname)

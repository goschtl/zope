import os
import shutil
import urllib2
import urlparse
import zipfile

BASEURL = "http://slimbox.googlecode.com/files/"
VERSION = '2.03'
FULL = 'slimbox-%s.zip' % VERSION

CODE = """from hurry.resource import Library, ResourceInclusion, GroupInclusion
from hurry.jquery import jquery

SlimboxLibrary = Library('SlimboxLibrary')

slimbox_css = ResourceInclusion(
    SlimboxLibrary, 'slimbox-%(version)s/css/slimbox2.css')

slimbox_js = ResourceInclusion(
    SlimboxLibrary, 'slimbox-%(version)s/js/slimbox2.js', depends=[jquery])

slimbox = GroupInclusion([slimbox_css, slimbox_js])
"""


def unzip_file_into_dir(file, dir):
    zfobj = zipfile.ZipFile(file)
    for name in zfobj.namelist():
        if name.endswith('/'):
            os.mkdir(os.path.join(dir, name))
        else:
            outfile = open(os.path.join(dir, name), 'wb')
            outfile.write(zfobj.read(name))
            outfile.close()


def prepare_slimbox():
    package_dir = os.path.dirname(__file__)
    slimbox_dest_path = os.path.join(package_dir, 'slimbox-download')

    # remove previous slimbox library build
    print 'recursivly removing "%s"' % slimbox_dest_path
    shutil.rmtree(slimbox_dest_path, ignore_errors=True)
    print 'create new "%s"' % slimbox_dest_path
    os.mkdir(slimbox_dest_path)

    for filename in [FULL]:
        url = urlparse.urljoin(BASEURL, FULL)
        print 'downloading "%s"' % url
        f = urllib2.urlopen(url)
        file_data = f.read()
        f.close()
        dest_filename = os.path.join(slimbox_dest_path, filename)
        dest = open(dest_filename, 'wb')
        print 'writing data to "%s"' % dest_filename
        dest.write(file_data)
        dest.close()

        unzip_file_into_dir(dest_filename, slimbox_dest_path)
        os.remove(dest_filename)

    py_path = os.path.join(package_dir, '_lib.py')
    module = open(py_path, 'w')
    module.write(CODE % {'version': VERSION})
    module.close()

def main():
    prepare_slimbox()


def entrypoint(data):
    """Entry point for zest.releaser's prerelease script"""
    prepare_slimbox()

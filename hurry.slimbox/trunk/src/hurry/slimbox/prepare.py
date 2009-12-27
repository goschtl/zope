import os
import shutil
import urllib2
import urlparse
import zipfile

BASEURL = "http://slimbox.googlecode.com/files/"
VERSION = '2.03'
FULL = 'slimbox-%s.zip' % VERSION

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
    slimbox_dest_path = os.path.dirname(__file__)
    library_path = os.path.join(slimbox_dest_path, "slimbox-build")

    # remove previous slimbox library
    print 'recursivly removing "%s"' % library_path
    shutil.rmtree(library_path, ignore_errors=True)

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

        download_path = os.path.join(slimbox_dest_path, "slimbox-" + VERSION)
        shutil.move(download_path, library_path)


def main():
    prepare_slimbox()


def entrypoint(data):
    """Entry point for zest.releaser's prerelease script"""
    prepare_slimbox()

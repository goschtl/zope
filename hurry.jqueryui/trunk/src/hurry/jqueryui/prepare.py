import os
import shutil
import sys
import urllib2
import urlparse
from hurry.resource import generate_code, ResourceInclusion, Library

from hurry.jquery import jquery

BASEURL = 'http://ajax.googleapis.com/ajax/libs/jqueryui/'
MINIFIED = "jquery-ui.min.js"
FULL = "jquery-ui.js"

def main():
    try:
        version = sys.argv[1]
    except IndexError:
        print "Usage: jqueryuiprepare <jQuery UI version>"
        return

    package_dir = os.path.dirname(__file__)
    jquery_dest_path = os.path.join(package_dir, 'jqueryui-build')

    # remove previous jquery library build
    print 'recursively removing "%s"' % jquery_dest_path
    shutil.rmtree(jquery_dest_path, ignore_errors=True)
    print 'create new "%s"' % jquery_dest_path
    os.mkdir(jquery_dest_path)

    for filename in [MINIFIED, FULL]:
        url = urlparse.urljoin(BASEURL + version + '/', filename)
        print 'downloading "%s"' % url
        f = urllib2.urlopen(url)
        file_data = f.read()
        f.close()
        dest_filename = os.path.join(jquery_dest_path, filename)
        dest = open(dest_filename, 'wb')
        print 'writing data to "%s"' % dest_filename
        dest.write(file_data)
        dest.close()

import os
import shutil
import sys
import urllib2
import urlparse
from hurry.resource import generate_code, ResourceInclusion, Library

BASEURL = "http://jqueryjs.googlecode.com/files/"
MINIFIED = "jquery-1.3.2.min.js"
FULL = "jquery-1.3.2.js"

def main():
    try:
        version = sys.argv[1]
    except IndexError:
        print "Usage: jqueryprepare <jQuery version>"
        return

    package_dir = os.path.dirname(__file__)
    jquery_dest_path = os.path.join(package_dir, 'jquery-build')

    # remove previous jquery library build
    print 'recursivly removing "%s"' % jquery_dest_path
    shutil.rmtree(jquery_dest_path, ignore_errors=True)
    print 'create new "%s"' % jquery_dest_path
    os.mkdir(jquery_dest_path)

    for filename in [MINIFIED, FULL]:
        url = urlparse.urljoin(BASEURL, filename)
        print 'downloading "%s"' % url
        f = urllib2.urlopen(url)
        file_data = f.read()
        f.close()
        dest_filename = os.path.join(jquery_dest_path, filename)
        dest = open(dest_filename, 'wb')
        print 'writing data to "%s"' % dest_filename
        dest.write(file_data)
        dest.close()

    py_path = os.path.join(package_dir, '_lib.py')
    print 'Generating inclusion module "%s"' % py_path

    library = Library('jquery')
    inclusion_map = {}
    inclusion = inclusion_map['jquery'] = ResourceInclusion(library, FULL)
    inclusion.modes['minified'] = ResourceInclusion(library, MINIFIED)
    code = generate_code(**inclusion_map)
    module = open(py_path, 'w')
    module.write(code)
    module.close()

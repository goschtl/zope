import os, sys
import shutil

from hurry.wforms.download import download

def main():
    try:
        version = sys.argv[1]
    except IndexError:
        print "Usage: wformsprepare <wforms version>"
        return

    # download library into package
    package_dir = os.path.dirname(__file__)
    dest_path = os.path.join(package_dir, 'resources')

    # remove previous library
    shutil.rmtree(dest_path, ignore_errors=True)

    def copy(ex_path):
        """Copy to location 'resources' in package."""
        build_path = os.path.join(ex_path, 'tinymce', 'jscripts', 'tiny_mce')
        shutil.copytree(build_path, dest_path)

    download(version, copy)

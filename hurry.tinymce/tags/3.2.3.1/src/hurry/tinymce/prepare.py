import os, sys
import shutil

from hurry.tinymce.download import download

def main():
    try:
        version = sys.argv[1]
    except IndexError:
        print "Usage: tinymceprepare <tinyMCE version>"
        return

    # download tinymce library into package
    package_dir = os.path.dirname(__file__)
    dest_path = os.path.join(package_dir, 'tinymce-build')

    # remove previous tinymce
    shutil.rmtree(dest_path, ignore_errors=True)

    def copy_tinymce(ex_path):
        """Copy to location 'tinymce-build' in package."""
        build_path = os.path.join(ex_path, 'tinymce', 'jscripts', 'tiny_mce')
        if not os.path.exists(build_path):
            # Some versions of tinyMCE are packaged without a
            # top-level ``tinymce`` directory.
            build_path = os.path.join(ex_path, 'jscripts', 'tiny_mce')
        shutil.copytree(build_path, dest_path)

    download(version, copy_tinymce)

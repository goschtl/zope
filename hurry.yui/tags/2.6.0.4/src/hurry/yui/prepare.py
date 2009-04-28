import os, sys
import shutil

from hurry.yui.depend import depend
from hurry.yui.download import download

def main():
    try:
        version = sys.argv[1]
    except IndexError:
        print "Usage: yuiprepare <YUI version>"
        return

    # download YUI library into package
    package_dir = os.path.dirname(__file__)
    yui_dest_path = os.path.join(package_dir, 'yui-build')

    # remove previous yui library
    shutil.rmtree(yui_dest_path, ignore_errors=True)

    def copy_yui(ex_path):
        """Copy YUI to location 'yui-build' in package."""
        yui_build_path = os.path.join(ex_path, 'yui', 'build')
        shutil.copytree(yui_build_path, yui_dest_path)

    download(version, copy_yui)

    # get dependency structure and create 'yui.py' into package
    code = depend(version)
    yui_py_path = os.path.join(package_dir, 'yui.py')
    f = open(yui_py_path, 'w')
    f.write(code)
    f.close()

import os, sys
import shutil

YUI_VERSION = '2.7.0'
YUI_DOWNLOAD_VERSION = '2.7.0b' # argh, download file version isn't actual version

from hurry.yui.depend import depend
from hurry.yui.download import download

def main():
    try:
        version = sys.argv[1]
    except IndexError:
        print "Usage: yuiprepare <YUI version> [<download version>]"
        return

    try:
        download_version = sys.argv[2]
    except IndexError:
        download_version = version

    # download YUI library into package
    package_dir = os.path.dirname(__file__)

    prepare(YUI_DOWNLOAD_VERSION, package_dir)

def working_entrypoint(data):
    if data['name'] != 'hurry.yui':
        return
    prepare(YUI_DOWNLOAD_VERSION, os.path.dirname(__file__))

def tag_entrypoint(data):
    if data['name'] != 'hurry.yui':
        return
    prepare(YUI_DOWNLOAD_VERSION, data['tagdir'] + 'src/hurry/yui')
    
def prepare(download_version, package_dir):
    yui_dest_path = os.path.join(package_dir, 'yui-build')

    # remove previous yui library
    shutil.rmtree(yui_dest_path, ignore_errors=True)

    def copy_yui(ex_path):
        """Copy YUI to location 'yui-build' in package."""
        yui_build_path = os.path.join(ex_path, 'yui', 'build')
        shutil.copytree(yui_build_path, yui_dest_path)

    download(download_version, copy_yui)

    # get dependency structure and create 'yui.py' into package
    code = depend(version)
    yui_py_path = os.path.join(package_dir, 'yui.py')
    f = open(yui_py_path, 'w')
    f.write(code)
    f.close()

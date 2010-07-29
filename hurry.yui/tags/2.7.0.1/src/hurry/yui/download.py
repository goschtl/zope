import urllib2
import tempfile, shutil
import os

URL_TEMPLATE = 'http://yuilibrary.com/downloads/yui2/yui_%s.zip'

def download(version, callback):
    """Download a yui of version.

    When downloaded, call callback with path to directory
    with an extracted YUI. The callback will then be able to copy
    this to the appropriate location.
    """
    download_url = URL_TEMPLATE % version
   
    f = urllib2.urlopen(download_url)
    file_data = f.read()
    f.close()

    dirpath = tempfile.mkdtemp()
    try:
        yui_path = os.path.join(dirpath, 'yui.zip')
        ex_path = os.path.join(dirpath, 'yui_ex')
        g = open(yui_path, 'wb')
        g.write(file_data)
        g.close()
        os.system('unzip -qq "%s" -d "%s"' % (yui_path, ex_path))
        callback(ex_path)
    finally:
        shutil.rmtree(dirpath, ignore_errors=True)

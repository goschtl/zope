import urllib2
import tempfile, shutil
import os

GH_URL_TEMPLATE = 'https://github.com/downloads/tinymce/tinymce/tinymce_%s.zip'

def download(version, callback):
    """Download a tinymce of version.

    When downloaded, call callback with path to directory
    with an extracted tinymce. The callback will then be able to copy
    this to the appropriate location.
    """
    url = GH_URL_TEMPLATE % version
    f = urllib2.urlopen(url)
    file_data = f.read()
    f.close()

    dirpath = tempfile.mkdtemp()
    import pdb; pdb.set_trace() 
    try:
        tinymce_path = os.path.join(dirpath, 'tinymce.zip')
        ex_path = os.path.join(dirpath, 'tinymce_ex')
        g = open(tinymce_path, 'wb')
        g.write(file_data)
        g.close()
        os.system('unzip -qq "%s" -d "%s"' % (tinymce_path, ex_path))
        callback(ex_path)
    finally:
        shutil.rmtree(dirpath, ignore_errors=True)

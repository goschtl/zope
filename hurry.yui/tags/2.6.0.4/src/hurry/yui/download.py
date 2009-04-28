import urllib2
import tempfile, shutil
import os

SF_URL_TEMPLATE = 'http://sourceforge.net/project/downloading.php?group_id=165715&filename=yui_%s.zip'

def download(version, callback):
    """Download a yui of version.

    When downloaded, call callback with path to directory
    with an extracted YUI. The callback will then be able to copy
    this to the appropriate location.
    """
    url = SF_URL_TEMPLATE % version
    f = urllib2.urlopen(url)
    data = f.read()
    f.close()

    download_url = find_a_href(data, 'direct link')

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

def find_a_href(data, content):
    """Given start of content of the <a href="">content</a> find href.
    """
    i = data.find(content)
    a = '<a href="'
    href_start = data.rfind(a, 0, i)
    href_start += len(a)
    href_end = data.find('"', href_start)
    return data[href_start:href_end]

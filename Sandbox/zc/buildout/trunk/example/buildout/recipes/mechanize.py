import re, os
import buildout

class Default(buildout.DownloadSource, buildout.DistUtilsPackage):
    name = 'mechanize'
    version = buildout.getVersion(name) 
    download_url = (
        'http://wwwsearch.sourceforge.net/mechanize/src/'
        'mechanize-%s.tar.gz' % version
        )
    unarchived_name = 'mechanize-%s' % version

    def build(self):
        RE = 'from mechanize import __version__'
        REPLACEMENT = '__version__ = (0, 0, 9, "a", None)  # 0.0.9a'

        # fix mechanize's setup.py to not depend on ClientCookie
        target = os.path.join(buildout.getSourcePath('mechanize'), 'setup.py')
        f = open(target, 'rU')
        text = f.read()
        f.close()
        rx = re.compile(RE, re.DOTALL)
        new_text = rx.sub(REPLACEMENT, text, 1)
        if new_text != text:
            f = open(target, 'wt')
            f.write(new_text)
            f.close()

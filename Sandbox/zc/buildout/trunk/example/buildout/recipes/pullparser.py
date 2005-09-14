import buildout

class Default(buildout.DownloadSource, buildout.DistUtilsPackage):

    name = 'pullparser'
    version = buildout.getVersion(name)
    download_url = ('http://wwwsearch.sourceforge.net/pullparser/src/'
                    'pullparser-%s.tar.gz' % version)
    unarchived_name = 'pullparser-%s' % version

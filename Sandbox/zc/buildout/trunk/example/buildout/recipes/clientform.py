import buildout

class Default(buildout.DownloadSource, buildout.DistUtilsPackage):

    name = 'clientform'
    version = buildout.getVersion(name)
    download_url = ('http://wwwsearch.sourceforge.net/ClientForm/src/'
                    'ClientForm-%s.tar.gz' % version)
    unarchived_name = 'ClientForm-%s' % version

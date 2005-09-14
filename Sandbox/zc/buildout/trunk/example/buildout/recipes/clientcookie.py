import buildout

class Default(buildout.DownloadSource, buildout.DistUtilsPackage):
        name = 'clientcookie'
        version = buildout.getVersion(name) 
        download_url = (
            'http://wwwsearch.sourceforge.net/ClientCookie/src/'
            'ClientCookie-%s.tar.gz'
            % version
            )
        unarchived_name = 'ClientCookie-%s' % version

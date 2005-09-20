import os, sys, shutil

import buildout

def getShortVersion(version):
    if version[-2:-1] in ['a', 'b', 'c']:
        short_version = version[:-2]
    else:
        short_version = version

    return short_version


class Default(buildout.DownloadSource):
    def __init__(self):
        self.name = 'python'
        version = buildout.getVersion(self.name)
        self.download_url= (
                'http://python.org/ftp/python/%s/Python-%s.tgz'
                % (getShortVersion(version), version))
        self.unarchived_name='Python-%s' % version

    def build(self):
        cache_file = os.path.abspath(
                        buildout.queryOption('configure', 'cache_file'))
        prefix = buildout.getBuildPath(self.name)

        def helper():
            buildout.runCommand(
                os.path.join(buildout.getSourcePath(self.name), 'configure'),
                ['--cache-file='+cache_file, '--prefix='+prefix])
            buildout.runCommand('make')
            buildout.runCommand('make', ['install'])

        buildout.dirBuildHelper(os.path.join(prefix, 'build'), helper)

    def freshen(self):
        pass

    def install(self):
        pass


class Windows(buildout.DownloadFile, buildout.WindowsMsi):
    def __init__(self):
        self.name = 'python'
        version = buildout.getVersion(self.name)
        self.download_url = (
            'http://python.org/ftp/python/%s/python-%s.msi'
            % (getShortVersion(version), version))
        self.install_marker = buildout.getPathToBinary(self.name)

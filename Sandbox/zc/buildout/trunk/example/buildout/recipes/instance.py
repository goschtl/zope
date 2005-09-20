import os, sys

import buildout

class Default(object):
    def get(self):
        pass

    def build(self):
        pass

    def install(self):
        if not os.path.exists('instance'):
            mkzopeinstancePath = os.path.join(
                    buildout.getSourcePath('zope3'), 'bin', 'mkzopeinstance')
            zopeskelPath = os.path.join(
                    buildout.getBasePath(), 'zopeskel')
            pythonPath = buildout.getPathToBinary('python')
            buildout.runCommand(pythonPath, [mkzopeinstancePath, 
                                '-d', 'instance', 
                                '-u', 'admin:tuesday', 
                                '-s', zopeskelPath])

        # Link commands into bin directorys.
        buildout.mkdir('bin')
        pathToPython = buildout.getPathToBinary('python')
        if sys.platform.startswith('win'):
            buildout.linkOrCopy('../instance/bin/runzope.bat', 'bin/runzope.bat')
            buildout.linkOrCopy('../instance/bin/test.bat', 'bin/test.bat')
            buildout.linkOrCopy('../instance/bin/selenium.bat', 'bin/selenium.bat')
            buildout.linkOrCopy(pathToPython, 'bin/python.exe')
            buildout.linkOrCopy(pathToPython, 'instance/bin/python.exe')
        else:
            buildout.linkOrCopy('../instance/bin/runzope', 'bin/runzope')
            buildout.linkOrCopy('../instance/bin/test', 'bin/test')
            buildout.linkOrCopy('../instance/bin/selenium', 'bin/selenium')
            buildout.linkOrCopy('../instance/bin/zopectl', 'bin/zopectl')
            buildout.linkOrCopy(pathToPython, 'bin/python')
            buildout.linkOrCopy(pathToPython, 'instance/bin/python')

    def freshen(self):
        pass

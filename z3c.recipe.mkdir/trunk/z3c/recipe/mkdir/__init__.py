import logging
import os
import zc.buildout

class Recipe:
    def __init__(self, buildout, name, options):
        self.buildout=buildout
        self.name=name
        self.options=options
        self.logger=logging.getLogger(self.name)

        paths = None
        
        if 'path' in options.keys():
            self.logger.warn(
                "Use of 'path' option is deprectated. Use 'paths' instead.")
            paths = options['path']

        if "paths" in options:
            paths = options["paths"]
        else:
            paths = os.path.join(
                buildout['buildout']['parts-directory'], name)
        paths = [x.strip() for x in paths.split('\n')]
        paths = [os.path.abspath(x) for x in paths]
        paths = [os.path.normpath(x) for x in paths]
        self.paths = paths

    def install(self):
        for path in self.paths:
            self.createIntermediatePaths(path)
            self.options.created(path)
            self.logger.info('created path: %s' % path)
        return self.options.created()


    def update(self):
        return self.install()

    def createIntermediatePaths(self, path):
        parent = os.path.dirname(path)
        if os.path.exists(path) and not os.path.isdir(path):
            raise zc.buildout.UserError(
                "Cannot create directory: %s. It's a file." % path)
        if os.path.exists(path) or parent == path:
            return
        self.createIntermediatePaths(parent)
        os.mkdir(path)
        self.options.created(path)

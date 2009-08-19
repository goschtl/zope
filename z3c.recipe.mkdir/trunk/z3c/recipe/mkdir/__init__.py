import logging
import os
import re
import stat
import zc.buildout

class Recipe:
    def __init__(self, buildout, name, options):
        self.buildout=buildout
        self.name=name
        self.options=options
        self.logger=logging.getLogger(self.name)

        path = None
        if "path" in options:
            path = options["path"]
        else:
            path = os.path.join(
                buildout['buildout']['parts-directory'], name)
        path = [x.strip() for x in path.split('\n')]
        path = [os.path.abspath(x) for x in path]
        path = [os.path.normpath(x) for x in path]
        self.path = path

    def install(self):
        for path in self.path:
            self.createIntermediatePaths(path)
            self.options.created(path)
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

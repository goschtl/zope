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

        self.path = None
        if "path" in options:
            self.path = options["path"]
        else:
            self.path = os.path.join(
                buildout['buildout']['parts-directory'], name)
        self.path = os.path.abspath(self.path)

    def install(self):
        self.createIntermediatePaths(self.path)
        self.options.created(self.path)
        return self.options.created()


    def update(self):
        return self.install()

    def createIntermediatePaths(self, path):
        parent = os.path.dirname(path)
        if os.path.exists(path) or parent == path:
            return
        self.createIntermediatePaths(parent)
        os.mkdir(path)
        self.options.created(path)

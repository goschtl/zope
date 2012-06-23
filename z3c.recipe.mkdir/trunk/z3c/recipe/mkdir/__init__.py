import logging
import os
import zc.buildout

class Recipe:
    def __init__(self, buildout, name, options):
        self.buildout=buildout
        self.name=name
        self.options=options
        self.logger=logging.getLogger(self.name)
        self.remove_on_update = string_to_bool(
            options.get('remove-on-update', 'no'))

        if 'path' in options.keys():
            self.logger.warn(
                "Use of 'path' option is deprectated. Use 'paths' instead.")

        paths = options.get(
            'paths', options.get('path', os.path.join(
                buildout['buildout']['parts-directory'], name)))
        self.paths = [os.path.normpath(os.path.abspath(
            x.strip())) for x in paths.split('\n')]

        # Update options to be referencable...
        options['path'] = options['paths'] = '\n'.join(self.paths)

    def install(self):
        for path in self.paths:
            self.createIntermediatePaths(path)
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
        self.logger.info('created path: %s' % path)
        if self.remove_on_update:
            self.options.created(path)

def string_to_bool(value):
    if value is True or value is False:
        return value
    value = value.lower()
    return value in ['yes', 'on', 'true', '1']

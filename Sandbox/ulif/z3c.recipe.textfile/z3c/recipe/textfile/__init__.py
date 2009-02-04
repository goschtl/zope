# -*- coding: utf-8 -*-
"""Recipe recipe"""

import logging, os, zc.buildout

class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options

        # Normalize paths and check that their parent
        # directories exist:
        paths = []
        if options.get('path') is None:
            options['path'] = ''
        for path in options['path'].split():
            path = os.path.join(buildout['buildout']['directory'], path)
            if not os.path.isdir(os.path.dirname(path)):
                logging.getLogger(self.name).error(
                    'Cannot create %s. %s is not a directory.',
                    options['path'], os.path.dirname(options['path']))
                raise zc.buildout.UserError('Invalid Path')
            paths.append(path)
        options['path'] = ' '.join(paths)
        for filename in self.options.keys():
            if not '.' in filename:
                continue
            if filename.endswith('-template'):
                non_template_option = filename.rsplit('-', 2)[0]
                if non_template_option in self.options.keys():
                    logging.getLogger(self.name).error(
                        'You cannot use both, `%s` and `%s` in '
                        'the same recipe.' % (
                            non_template_option, filename))
                    raise zc.buildout.UserError(
                        'Duplicate file content definition')
                

                # Read file contents from template...
                template = self.options[filename]
                if not os.path.exists(template):
                    logging.getLogger(self.name).error(
                        'No such template file: %s' %
                        template)
                    raise zc.buildout.UserError(
                        'No such template file: %s' %template )

        
    def install(self):
        """Installer"""
        paths = self.options['path'].split()
        for path in paths:
            logging.getLogger(self.name).info(
                'Creating directory %s', os.path.basename(path))
            os.mkdir(path)
        self.options.created(paths)
        for filename in self.options.keys():
            if not '.' in filename:
                continue
            if filename.endswith('-template'):
                # Read file contents from template...
                template = self.options[filename]
                filename = filename.rsplit('-', 2)[0]
                if not os.path.exists(template):
                    logging.getLogger(self.name).error(
                        'No such template file: %s' %
                        template)
                    raise zc.buildout.UserError(
                        'No such template file: %s' %template )
                logging.getLogger(self.name).info(
                    'Creating file %s', filename)
                raw = open(template, 'rb').read()
                try:
                    content = self.options._sub(raw, None)
                except:
                    pass

                self.writeFile(self.options['path'], filename,
                               content)
                continue

                
            logging.getLogger(self.name).info(
                'Creating file %s', filename)
            self.writeFile(self.options['path'], filename,
                           self.options[filename])
            # The file will be removed when buildout reinstalls...
            paths.append(os.path.join(self.options['path'], filename))
            
        return paths
       

    update = install

    def writeFile(self, path, filename, contents):
        fullpath = os.path.join(path, filename)
        open(fullpath, 'wb').write(contents)
        return fullpath

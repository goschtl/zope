import pwd
import pprint
import os
import os.path
import sys

TEMPLATE = """#!%(interpreter)s
import os
import sys
env = {}
env.update(os.environ)
newenv = %(env)s
env.update(newenv)
target = '%(target)s'
base = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
base = os.path.dirname(base)
path = os.path.join(
    *([os.sep,] + base.split(os.sep) + target.split(os.sep)))
args = [sys.executable] + [path] + sys.argv[1:]
os.execve(sys.executable, args, env)"""

def get_platform():
    # Monkeypatch me for tests.
    return sys.platform

class Wrapper(object):
    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        self.supported_os = self.options.get('if-os', '').split() or ['ANY']

    def install(self):
        if set(['ANY'] + [get_platform()]) & set(self.supported_os):
            options = {}
            options.update(self.options)
            options['deployment'] = self.options.get('deployment', '')
            options['if-os'] = self.options.get('if-os', 'ANY')
            options['name'] = self.options.get('name', self.name)
            if 'deployment' in self.options:
                deployment = self.buildout[self.options['deployment']]
                path = deployment['rc-directory']
                user = deployment['user']
            else:
                path = self.buildout['buildout']['directory']
                user = pwd.getpwuid(os.geteuid()).pw_name

            options['path'] = os.path.join(
                os.sep, path, 'bin', options['name'])
            self.options.update(options)

            parameters = dict(
                env = pprint.pformat(
                    self.buildout[self.options['environment']]),
                interpreter = self.buildout['buildout']['executable'],
                target = self.options['target'],)
            wrapper = open(self.options['path'], 'w')
            wrapper.write(TEMPLATE % parameters)
            wrapper.close()
            os.chmod(options['path'], 0755)
            os.chown(options['path'], *(pwd.getpwnam(user)[2:4]))
        return ()
    update = install

    def uninstall(self):
        if set(['ANY'] + [get_platform()]) & set(self.supported_os):
            os.remove(self.options['path'])


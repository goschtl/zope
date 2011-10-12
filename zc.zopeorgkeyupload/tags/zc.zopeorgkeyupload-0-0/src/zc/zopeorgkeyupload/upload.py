import logging
import os
import pwd
import re
import ZEO
import zope.app.security.basicauthadapter
import zope.component
import zope.publisher.http
import zope.security.interfaces

logging.basicConfig()

zope.component.provideAdapter(zope.publisher.http.HTTPCharsets)

v1re = re.compile(r'\d+ \d+ \d+').match
command = r'command="/usr/local/bin/scm $SSH_ORIGINAL_COMMAND" '

class Publication:

    def __init__(self, global_config, keydir, zeo):
        self.keydir = keydir
        self.tmp = os.path.join(keydir, '.tmp')
        self.db = ZEO.DB(int(zeo), read_only=True)

    def beforeTraversal(self, request):
        pass

    def getApplication(self, request):
        return self

    def callTraversalHooks(self, request, ob):
        pass

    def traverseName(self, request, ob, name):
        return self

    def afterTraversal(self, request, ob):
        pass

    def callObject(self, request, ob):
        cred = zope.app.security.basicauthadapter.BasicAuthAdapter(request)
        login = cred.getLogin()

        authorized = False
        if login is not None:
            with self.db.transaction() as conn:
                users = conn.root.zaam_users
                user = users.authenticateCredentials(dict(
                    domain = 'svn.zope.org',
                    login = login,
                    password = cred.getPassword(),
                    ))
                if user is not None:
                    authorized = True

        if not authorized:
            cred.needLogin('ZopeCVSAdmin')
            return ("You need to become a registered user.")

        try:
            pwd.getpwnam(login)
        except KeyError:
            return "You are not yet a contributor"

        if 'key' not in request.form:
            return key_form % ''

        key = request.form['key'].read(10000)
        if len(key) >= 10000:
            return key_form % 'The key you uploaded is too long!<br />'

        v1keys = []
        v2keys = []
        for line in key.split('\n'):
            if not line.strip():
                continue
            if line.strip().startswith('#'):
                continue
            if line.strip().split()[0] in ('ssh-dss', 'ssh-rsa'):
                v2keys.append(command+line+'\n')
            elif v1re(line):
                v1keys.append(command+line+'\n')
            else:
                return key_form % (
                    'The key you uploaded is not properly formatted!<br />')

        if not (v1keys or v2keys):
                return key_form % 'The file you uploaded had no keys!<br />'


        if v1keys:
            writef(self.tmp, ''.join(v1keys))
            os.rename(self.tmp, os.path.join(self.keydir, login+'-1'))

        if v2keys:
            writef(self.tmp, ''.join(v2keys))
            os.rename(self.tmp, os.path.join(self.keydir, login+'-2'))

        return ("Your keys have been uploaded.\n"
                "It may take a few minutes for them to become effective.")

    def afterCall(self, request, ob):
        pass

    def handleException(self, object, request, exc_info, retry_allowed=1):
        raise exc_info[0], exc_info[1], exc_info[2]

    def endRequest(self, request, ob):
        pass

    def getDefaultTraversal(self, request, ob):
        return self, ()

def writef(path, data):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT, 0600)
    os.write(fd, data)
    os.close(fd)


key_form = """
<html>
  <head>
    <title>Upload your public SSH key</title>
  </head>
  <body>
    %s
    <form method="POST" enctype="multipart/form-data">
      Upload your public SSH key(s):
      <input type="file" name="key" size="40" /><br />
      <input type="submit" value="submit" />
    </form>
</html>
"""


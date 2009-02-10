import os
import shutil
import sys

from zope.i18n.compile import compile_mo_file

def makecatalog():
    if len(sys.argv) < 3:
        print 'Usage: %s <domain> <target directory>' % sys.argv[0]
        sys.exit(0)

    domain = sys.argv[1]
    target = sys.argv[2]

    import zope.app.locales
    zope_locales_path = os.path.dirname(zope.app.locales.__file__)
    languages = [d for d in os.listdir(zope_locales_path) \
                 if os.path.isdir(os.path.join(zope_locales_path, d))]

    if not os.path.exists(target):
        os.makedirs(target)

    pot_file = os.path.join(zope_locales_path, 'zope.pot')
    target_pot = os.path.join(target, domain+'.pot')
    shutil.copyfile(pot_file, target_pot)

    for language in languages:
        lang_path = os.path.join(target, language, 'LC_MESSAGES')
        if not os.path.exists(lang_path):
            os.makedirs(lang_path)
        src = os.path.join(zope_locales_path, language, 'LC_MESSAGES', 'zope.po')
        dst = os.path.join(lang_path, domain+'.po')
        shutil.copyfile(src, dst)
        compile_mo_file(domain, lang_path)

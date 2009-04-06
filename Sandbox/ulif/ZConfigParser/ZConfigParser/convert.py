"""Convert ZConfig configurations/files to ConfigParser style.
"""
from ZConfigParser import schemaless


def convertFile(filepath):
    config = schemaless.loadConfigFile(open(filepath, 'rb'))
    return convertSection(config)

def convertSection(section, prefix='zope'):
    body = ''
    if section.type:
        prefix = '%s/%s' % (prefix, section.type)
        body = '\n[%s]\n' % (prefix)
    for key in list(section):
        body += '%s = %s\n' % (key, section[key][0])
    for section in section.sections:
        body += '%s = %s/%s\n' % (section.type, prefix, section.type)
        body += convertSection(section, prefix)
    return body

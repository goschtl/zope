import os

for dirname, directories, files in os.walk('.'):
    start, last = os.path.split(dirname)
    if last.startswith('.svn'):
        continue
    for file in files:
        filename = os.path.join(dirname, file)
        name, extension = os.path.splitext(filename)
        if extension == '.txt':
            os.system('rst2html %s > %s' % (filename, name + '.html'))
        

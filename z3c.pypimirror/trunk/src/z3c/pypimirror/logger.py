import logging

def getLogger(filename='/tmp/pypymirror.log'):

    LOG = logging.getLogger()
    LOG.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)-6s %(message)s')
    filehandler = logging.FileHandler(filename)
    filehandler.setFormatter(formatter)
    LOG.addHandler(filehandler)
    return LOG

if __name__ == '__main__':
    LOG = getLogger()
    LOG.info('hello')
    LOG.error('hello')

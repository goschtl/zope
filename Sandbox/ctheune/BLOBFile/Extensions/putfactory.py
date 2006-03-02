from Products.BLOBFile.file import BLOBFile

def PUT_factory(name, typ, body):
    item = BLOBFile(name, '', '', typ, '')
    return item

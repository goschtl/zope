from OFS.Folder import Folder

class Book(Folder):

    meta_type = "Book"

    barcode = ""
    title = ""
    author = ""

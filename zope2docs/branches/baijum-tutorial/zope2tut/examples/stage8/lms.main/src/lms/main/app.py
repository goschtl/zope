from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from lms.main.book import Book

addLmsMain_form =  PageTemplateFile('addLmsMain_form', globals())


def addLmsMain(dispatcher, id):
    """Add LMS"""
    lms = LmsMain(id)
    lms.manage_addFolder('books')
    dispatcher._setObject(id, lms)
    return "LMS Installed: %s" % id


class LmsMain(Folder):

    meta_type = "LMS"

    index_html = PageTemplateFile('index_html', globals())

    add_book = PageTemplateFile('add_book', globals())

    show_books = PageTemplateFile('show_books', globals())

    def insert_book(self):
        """Insert book"""
        request = self.REQUEST

        barcode = request.form['barcode']
        title = request.form['title']
        author = request.form['author']

        book = Book()
        book.barcode = barcode
        book.title = title
        book.author = author
        self.books._setObject(barcode, book)
        return "Book added: %s" % barcode

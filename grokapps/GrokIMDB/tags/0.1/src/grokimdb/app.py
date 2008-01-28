import imdb
import grok
from zope import schema
from zope.interface import Interface, implements

class GrokIMDB(grok.Application, grok.Container):
    pass

class Index(grok.View):
    grok.context(GrokIMDB)

class IMovie(Interface):
    """Infos about a movie.
    """
    id = schema.TextLine(title=u'IMDb ID', required=False)
    title = schema.TextLine(title=u'Title', required=False)
    year = schema.Int(title=u'Year', required=False)
    summary = schema.Text(title=u'Summary', required=False)

class Movie(grok.Model):
    """Infos about a movie.

    We can easily create movies::

    >>> from grokimdb.app import Movie
    >>> movie = Movie()
    >>> movie
    <grokimdb.app.Movie object at 0x...>

    """
    implements(IMovie)


class AddMovie(grok.AddForm):
    grok.context(GrokIMDB)
    form_fields = grok.AutoFields(IMovie)
    @grok.action("Add movie")
    def add(self, **data):
        movie = Movie()
        self.applyData(movie, **data)
        self.context[str(data['id'])] = movie
        self.redirect(self.url(movie))
    @grok.action("Lookup IMDb")
    def lookup(self, **data):
        movie = Movie()
        imdb_query = imdb.IMDb(accessSystem='http')
        results = imdb_query.search_movie(data['title'])
        if not results:
            self.redirect(self.url(context) + '/@@addmovie')
            return
        result = results[0] # Consider only the first result
        imdb_query.update(result)
        data['id'], data['year'], data['title'] = (
            result.getID(), result['year'], result['title']
            )
        data['summary'] = ' '.join(result['plot'])
        self.applyData(movie, **data)
        self.context[str(data['id'])] = movie
        self.redirect(self.url(movie) + '/@@edit')


class DisplayMovie(grok.DisplayForm):
    grok.context(IMovie)
    grok.name('index')
    form_fields = grok.AutoFields(IMovie)


class EditMovie(grok.EditForm):
    grok.context(IMovie)
    grok.name('edit')
    form_fields = grok.AutoFields(IMovie)

    @grok.action("Apply changes")
    def applyChanges(self, **data):
        self.applyData(self.context, **data)
        
    @grok.action("Return to index")
    def returnToIndex(self, **data):
        self.applyData(self.context, **data)
        self.redirect(self.url(self.context.__parent__))

    
class DeleteMovie(grok.View):
    grok.context(GrokIMDB)
    grok.name('delete')

    def update(self, id):
        del self.context[id]

    def render(self):
        self.redirect(self.url(self.context))
        

class GrokIMDB_XMLRPC(grok.XMLRPC):
    grok.context(GrokIMDB)
    def getMovieIDs(self):
        return list(self.context)
    def getMovie(self, movie_id):
        movie = self.context[movie_id]
        return {'title': movie.title,
                'year' : movie.year,
                'summary': movie.summary}


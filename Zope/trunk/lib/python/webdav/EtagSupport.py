from string import capitalize, split, join, strip
import time, Interface, re

class EtagBaseInterface(Interface.Base):
    """\
    Basic Etag support interface, meaning the object supports generating
    an Etag that can be used by certain HTTP and WebDAV Requests.
    """
    def http__etag(self):
        """\
        Entity tags are used for comparing two or more entities from
        the same requested resource.  Predominantly used for Caching,
        Etags can also be used to deal with the 'Lost Updates Problem'.
        An HTTP Client such as Amaya that supports PUT for editing can
        use the Etag value returned in the head of a GET response in the
        'if-match' header submitted with a PUT request.  If the Etag
        for the requested resource in the PUT request's 'if-match' header
        is different from the current Etag value returned by this method,
        the PUT will fail (it means that the state of the resource has
        changed since the last copy the Client recieved) because the
        precondition (the 'if-match') fails (the submitted Etag does not
        match the current Etag).
        """

    def http__refreshEtag(self):
        """\
        While it may make sense to use the ZODB Object Id or
        bobobase_modification_time to generate an Etag, this could
        fail on certain REQUESTS because:

         o The object is not stored in the ZODB, or

         o A Request such as PUT changes the oid or bobobase_modification_time
           *AFTER* the Response has been written out, but the Etag needs
           to be updated and returned with the Response of the PUT request.

        Thus, Etags need to be refreshed manually when an object changes.
        """

class EtagSupport:
    """\
    This class is the basis for supporting Etags in Zope.  It's main
    function right now is to support the *Lost Updates Problem* by
    allowing Etags and If-Match headers to be checked on PUT calls to
    provide a *Seatbelt* style functionality.  The Etags is based on
    the bobobase_modification_time, and thus is updated whenever the
    object is updated.  If a PUT request, or other HTTP or Dav request
    comes in with an Etag different than the current one, that request
    can be rejected according to the type of header (If-Match,
    If-None-Match).
    """
    __implements__ = (EtagBaseInterface,)

    def http__etag(self):
        try: etag = self.__etag
        except AttributeError:
            self.http__refreshEtag()
            etag = self.__etag
        return etag

    def http__refreshEtag(self):
        self.__etag = 'ts%s' % str(time.time())[2:]


    def http__parseMatchList(self, REQUEST, header="if-match"):
        # Return a sequence of strings found in the header specified
        # (should be one of {'if-match' or 'if-none-match'}).  If the
        # header is not in the request, returns None.  Otherwise,
        # returns a tuple of Etags.
        matchlist = REQUEST.get_header(header)
        if matchlist is None:
            # capitalize the words of the header, splitting on '-'
            tmp = map(capitalize, split(header, '-'))
            tmp = join(tmp,'-')
            matchlist = REQUEST.get_header(tmp)
            if matchlist is None:
                return None
        matchlist = map(strip, split(matchlist, ','))

        r = []
        for match in matchlist:
            if match == '*': r.insert(0, match)
            elif (match[0] + match[-1] == '""') and (len(match) > 2):
                    r.append(match[1:-1])
            
        return tuple(r)

    def http__processMatchHeaders(self, REQUEST=None):
        # Process if-match and if-none-match headers

        if REQUEST is None: REQUEST = self.aq_acquire('REQUEST')

        matchlist = self.http__parseMatchList(REQUEST, 'if-match')
        nonematch = self.http__parseMatchList(REQUEST, 'if-none-match')

        if matchlist is None:
            # There's no Matchlist, but 'if-none-match' might need processing
            pass
        elif ('*' in matchlist):
            return 1                    # * matches everything
        elif self.http__etag() not in matchlist:
            # The resource etag is not in the list of etags required
            # to match, as specified in the 'if-match' header.  The
            # condition fails and the HTTP Method may *not* execute.
            raise "Precondition Failed"
        elif self.http__etag() in matchlist:
            return 1

        if nonematch is None:
            # There's no 'if-none-match' header either, so there's no
            # problem continuing with the request
            return 1
        elif ('*' in nonelist):
            # if-none-match: * means that the operation should not
            # be performed if the specified resource exists
            # (webdav.NullResource will want to do special behavior
            # here)
            raise "Precondition Failed"
        elif self.http__etag() in nonelist:
            # The opposite of if-match, the condition fails
            # IF the resources Etag is in the if-none-match list
            raise "Precondition Failed"
        elif self.http__etag() not in nonelist:
            return 1
        


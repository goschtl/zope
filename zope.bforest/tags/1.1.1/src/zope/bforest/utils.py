try:
    from pytz import UTC, _UTC # we import _UTC so that pickles made by the
    # fallback code below can still be reinstantiated if pytz is added in.
except ImportError:
    import datetime
    class UTC(datetime.tzinfo):
        """UTC
        
        Identical to the reference UTC implementation given in Python docs except
        that it unpickles using the single module global instance defined beneath
        this class declaration.
    
        Also contains extra attributes and methods to match other pytz tzinfo
        instances.
        """
        zone = "UTC"
    
        def utcoffset(self, dt):
            return ZERO
    
        def tzname(self, dt):
            return "UTC"
    
        def dst(self, dt):
            return ZERO
        
        def __reduce__(self):
            return _UTC, ()
    
        def localize(self, dt, is_dst=False):
            '''Convert naive time to local time'''
            if dt.tzinfo is not None:
                raise ValueError, 'Not naive datetime (tzinfo is already set)'
            return dt.replace(tzinfo=self)
    
        def normalize(self, dt, is_dst=False):
            '''Correct the timezone information on the given datetime'''
            if dt.tzinfo is None:
                raise ValueError, 'Naive time - no tzinfo set'
            return dt.replace(tzinfo=self)
    
        def __repr__(self):
            return "<UTC>"
    
        def __str__(self):
            return "UTC"
    
    
    UTC = utc = UTC() # UTC is a singleton
    
    
    def _UTC():
        """Factory function for utc unpickling.
        
        Makes sure that unpickling a utc instance always returns the same 
        module global.
        
        These examples belong in the UTC class above, but it is obscured; or in
        the README.txt, but we are not depending on Python 2.4 so integrating
        the README.txt examples with the unit tests is not trivial.
        
        >>> import datetime, pickle
        >>> dt = datetime.datetime(2005, 3, 1, 14, 13, 21, tzinfo=utc)
        >>> naive = dt.replace(tzinfo=None)
        >>> p = pickle.dumps(dt, 1)
        >>> naive_p = pickle.dumps(naive, 1)
        >>> len(p), len(naive_p), len(p) - len(naive_p)
        (60, 43, 17)
        >>> new = pickle.loads(p)
        >>> new == dt
        True
        >>> new is dt
        False
        >>> new.tzinfo is dt.tzinfo
        True
        >>> utc is UTC is timezone('UTC')
        True
        >>> utc is timezone('GMT')
        False
        """
        return utc
    _UTC.__safe_for_unpickling__ = True

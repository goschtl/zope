from App import Extensions
import os

def patch_externalmethod(thebasket):
    """In an effort to make External Methods work with Basket, this function
    replaces App.Extensions.getPath with a custom getPath function.  See
    the getPath doc string for extra details. (Thanks to Rocky Burt)
    """
    
    _originalGetPath = Extensions.getPath
    
    def getPath(prefix, name, checkProduct=1, suffixes=('',)):
        """This getPath implementation checks the real getPath function for
        a result before it does any of its work.  If result returned is None
        it then proceeds to return the result of getEggedPath. (The original
        getPath only checked physical Product directories in the instance
        home).
        """

        result = _originalGetPath(prefix, name, checkProduct, suffixes)
        
        if result is None and checkProduct:
            result = getEggedPath(thebasket, prefix, name, suffixes)
        
        return result
    
    Extensions.getPath = getPath

def getEggedPath(basket, prefix, name, suffixes):
    """
    Checks all exploded Basket egg dirs for the path defined by the given
    args.
    """

    result = None

    l = name.find('.')
    if l > 0:
        realPrefix = os.path.join(name[:l], prefix)
        realName = name[l + 1:]

        # lets check all of the recorded tempdirs for exploded eggs
        for tempdir in basket.exploded_dirs:
            # now lets check the actual exploded egg dirs
            for product_dir in os.listdir(tempdir):
                product_dir = os.path.join(tempdir, product_dir)
                
                result = Extensions._getPath(product_dir, realPrefix, 
                                             realName, suffixes)
                if result is not None:
                    break
            if result is not None:
                break
    
    return result
    


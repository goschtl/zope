from App import Extensions, FactoryDispatcher
from Products.Five import fiveconfigure
import Products
from utils import EggProduct
import os

def product_packages(thebasket):
    results = []
    
    for dist in thebasket.product_distributions():
        entry = dist.get_entry_map().get('zope2.initialize', None)
        if entry:
            entryPoint = entry.get('initialize', None)
            if entryPoint:
                try:
                    m = __import__(entryPoint.module_name)
                    results.append(m)
                except ImportError, e:
                    pass
    
    return results    
    
def patch_ProductDispatcher__bobo_traverse__(thebasket):
    """Currently, z2's App.FactoryDispatcher.ProductDispatcher only checks
    the Products module for products to look up existing factory dispatchers
    on.  This needs to be fixed to look in all basket-enabled product packages
    as well.
    """
    
    from App.FactoryDispatcher import ProductDispatcher
    _original__bobo_traverse__ = ProductDispatcher.__bobo_traverse__
    
    def __bobo_traverse__(self, REQUEST, name):
        product=self.aq_acquire('_getProducts')()._product(name)

        productPkg = getattr(Products, name, None)
        if not productPkg:
            products = [x for x in self.aq_acquire('_getProducts')().objectValues() if isinstance(x, EggProduct)]
            packages = product_packages(thebasket)    
            packageDict = {}
            for x in packages:
                packageDict[x.__name__] = x
                
            productPkg = packageDict.get(name, None)

        # Try to get a custom dispatcher from a Python product
        dispatcher_class=getattr(
            productPkg,
            '__FactoryDispatcher__',
            FactoryDispatcher)

        dispatcher=dispatcher_class(product, self.aq_parent, REQUEST)
        return dispatcher.__of__(self)
    
    ProductDispatcher.__bobo_traverse__ = __bobo_traverse__
    
    


def patch_listDefaultTypeInformation(thebasket):
    """CMF's implementation of listing default type information checks against
    items contained within the import, "import Products".  This needs to
    be extended to check the basket product packages as well.
    """
    
    try:
        from Products.CMFCore.TypesTool import TypesTool
    except ImportError, e:
        # don't continue trying to monkey patch CMF if it doesn't exist
        return
    
    _originalListDefaultTypeInformation = TypesTool.listDefaultTypeInformation
    
    def listDefaultTypeInformation(self):
        res = _originalListDefaultTypeInformation(self)
        
        products = [x for x in self.aq_acquire('_getProducts')().objectValues() if isinstance(x, EggProduct)]
        packages = product_packages(thebasket)    
        packageDict = {}
        for x in packages:
            packageDict[x.__name__] = x
        
        for product in products:
            product_id = product.getId()

            package = packageDict[product_id]
            dispatcher = getattr(package, '__FactoryDispatcher__', None)
            ftis = getattr(dispatcher, 'factory_type_information', None)

            if ftis is not None:
                if callable(ftis):
                    ftis = ftis()

                for fti in ftis:
                    mt = fti.get('meta_type', None)
                    id = fti.get('id', '')

                    if mt:
                        p_id = '%s: %s (%s)' % (product_id, id, mt)
                        res.append( (p_id, fti) )

        return res
    
    TypesTool.listDefaultTypeInformation = listDefaultTypeInformation


def patch_findProducts(thebasket):
    """By default five's loading logic only checks the Products package
    for products.  This needs to be fixed.
    """
    _originalFindProducts = fiveconfigure.findProducts
    
    def findProducts():
        """This findProducts checks the original findProducts for results
        and then checks the basket for more initialized products.
        """
        
        originalProducts = _originalFindProducts()
        all = list(originalProducts)
        moreProducts = product_packages(thebasket)
        
        for product in moreProducts:
            if product not in all:
                all.append(product)
        
        return all

    fiveconfigure.findProducts = findProducts
    

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

        # lets check all basket's product_container_dir's
        for product_container_dir in basket.product_container_dirs:
            result = Extensions._getPath(product_container_dir, realPrefix, 
                                         realName, suffixes)
            if result is not None:
                break
    
    return result
    


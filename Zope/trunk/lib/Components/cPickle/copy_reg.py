dispatch_table = {}
safe_constructors = {}

def pickle(ob_type, pickle_function, constructor_ob = None):
    dispatch_table[ob_type] = pickle_function

    if (constructor_ob is not None):
        constructor(constructor_ob)

def constructor(object):
    safe_constructors[object] = 1

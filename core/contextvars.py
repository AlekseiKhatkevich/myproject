# encoding: utf-8
# module _contextvars
# from (pre-generated)
# by generator 1.146
""" Context Variables """
# no imports

# functions

def copy_context(*args, **kwargs): # real signature unknown
    pass

# classes

class Context(object):
    # no doc
    def copy(self, *args, **kwargs): # real signature unknown
        pass

    def get(self, *args, **kwargs): # real signature unknown
        pass

    def items(self, *args, **kwargs): # real signature unknown
        pass

    def keys(self, *args, **kwargs): # real signature unknown
        pass

    def run(self, *args, **kwargs): # real signature unknown
        pass

    def values(self, *args, **kwargs): # real signature unknown
        pass

    def __contains__(self, *args, **kwargs): # real signature unknown
        """ Return key in self. """
        pass

    def __eq__(self, *args, **kwargs): # real signature unknown
        """ Return self==value. """
        pass

    def __getattribute__(self, *args, **kwargs): # real signature unknown
        """ Return getattr(self, name). """
        pass

    def __getitem__(self, *args, **kwargs): # real signature unknown
        """ Return self[key]. """
        pass

    def __ge__(self, *args, **kwargs): # real signature unknown
        """ Return self>=value. """
        pass

    def __gt__(self, *args, **kwargs): # real signature unknown
        """ Return self>value. """
        pass

    def __init__(self, *args, **kwargs): # real signature unknown
        pass

    def __iter__(self, *args, **kwargs): # real signature unknown
        """ Implement iter(self). """
        pass

    def __len__(self, *args, **kwargs): # real signature unknown
        """ Return len(self). """
        pass

    def __le__(self, *args, **kwargs): # real signature unknown
        """ Return self<=value. """
        pass

    def __lt__(self, *args, **kwargs): # real signature unknown
        """ Return self<value. """
        pass

    @staticmethod # known case of __new__
    def __new__(*args, **kwargs): # real signature unknown
        """ Create and return a new object.  See help(type) for accurate signature. """
        pass

    def __ne__(self, *args, **kwargs): # real signature unknown
        """ Return self!=value. """
        pass

    __hash__ = None


class ContextVar(object):
    # no doc
    def get(self, *args, **kwargs): # real signature unknown
        pass

    def reset(self, *args, **kwargs): # real signature unknown
        pass

    def set(self, *args, **kwargs): # real signature unknown
        pass

    def __class_getitem__(self, *args, **kwargs): # real signature unknown
        pass

    def __getattribute__(self, *args, **kwargs): # real signature unknown
        """ Return getattr(self, name). """
        pass

    def __hash__(self, *args, **kwargs): # real signature unknown
        """ Return hash(self). """
        pass

    def __init__(self, *args, **kwargs): # real signature unknown
        pass

    @staticmethod # known case of __new__
    def __new__(*args, **kwargs): # real signature unknown
        """ Create and return a new object.  See help(type) for accurate signature. """
        pass

    def __repr__(self, *args, **kwargs): # real signature unknown
        """ Return repr(self). """
        pass


class Token(object):
    # no doc
    def __getattribute__(self, *args, **kwargs): # real signature unknown
        """ Return getattr(self, name). """
        pass

    def __init__(self, *args, **kwargs): # real signature unknown
        pass

    @staticmethod # known case of __new__
    def __new__(*args, **kwargs): # real signature unknown
        """ Create and return a new object.  See help(type) for accurate signature. """
        pass

    def __repr__(self, *args, **kwargs): # real signature unknown
        """ Return repr(self). """
        pass

    old_value = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default

    var = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default


    MISSING = None # (!) real value is ''
    __hash__ = None


# variables with complex values

__loader__ = None # (!) real value is ''

__spec__ = None # (!) real value is ''


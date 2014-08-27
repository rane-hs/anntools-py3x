#!/usr/bin/python
# -*- coding: ascii -*-
'''
Support for cooperative function annotation using decorators.

(C) 2007-2008 - Viktor Ferenczi (python@cx.hu) - Licence: GNU LGPL

This module provides a decorator to annotate functions.

You can use keyword arguments for the decorator on Python versions <3.0
instead of the new function annotation syntax available from Python 3.0.
Multiple decorators can be used on a single function to build the final
annotation cooperatively.

See also: PEP #3107 - Function annotations
http://www.python.org/dev/peps/pep-3107/

Example:

For Python 2.4 and 2.5:

from math import sqrt
from anntools.annotation import *

@annotate(Float, n=Int)
def square(n):
    return sqrt(n)

Is equivalent with the Python 3.0 syntax:

def square(n:Int) -> Float:
    return sqrt(n)

The cooperation module provides schemes to allow cooperative usage and future
compatibility with other function annotation based tools. See the
cooperation.py module for details.

For example, you can define your own decorator using a cooperation scheme:

from anntools.cooperation import ListCooperation
from anntools.annotation import *

annotate=AnnotationDecorator(ListCooperation())

The decorator above will use ListCooperation instead of the default
TupleCooperation. This way one can write

def suqare(n:[Int, Float]) -> Float:
    return sqrt(n)
    
instead of

def suqare(n:(Int, Float)) -> Float:
    return sqrt(n)
    
It can be useful if the annotation must be changed frequently. I don't know
about any real world usage of this yet, but it might be useful in the future.

Performance note:

The annotation decorators does not wrap the function, so they don't cause
any performance penalty when calling the function. Only the definition of
the function will take slightly more time.

'''

#============================================================================

import sys
from types import FunctionType

from anntools.cooperation import TupleCooperation

#============================================================================
# Exported symbols

__all__=['AnnotationDecorator', 'annotate']

#============================================================================

class AnnotationDecorator(object):
    '''Decorator for function annotation. Should be used only with
    Python 2.4 and 2.5, where no syntax exist for function annotation,
    but newer versions of Python should run this too without problems.
    Use the new Py3K style syntax with Python 3.0 and newer instead of
    this decorator wherever you don't require backward compatibility.'''
    _classfilter=object
    def __init__(self, cooperation_class, cooperation_keywords={}):
        '''Initialize the decorator for a specific cooperation scheme.'''
        self.cooperation_class=cooperation_class
        self.cooperation_keywords=cooperation_keywords
    def __call__(self, __return__=None, **kw):
        '''The decorator itself'''
        # Decorator
        def decorator(fn):
            '''Decorate a function'''
            # Determine the original function from a possible wrapper chain
            if hasattr(fn, '_original_function_'):
                ofn=fn._original_function_
            else:
                ofn=fn
            # Add an empty dict if no function annotations exists.
            if not hasattr(ofn, '__annotations__'):
                ofn.__annotations__={}
            # Add new annotations according to the current cooperation scheme
            cooperation=self.cooperate(ofn.__annotations__)
            for name, obj in kw.items():
                cooperation.key=name
                cooperation.add(obj)
            del cooperation
            # Optional wrapping of the decorated function
            wrapper=self.wrap(fn, ofn)
            if wrapper is not fn:
                wrapper._original_function_=fn
            return wrapper
        # Is this decorator used with an argument list (called)?
        if __return__ is None or type(__return__)!=FunctionType or kw:
            # Optional return value converter
            if __return__ is not None:
                kw['return']=__return__
            # Returns the decorator function to be called.
            return decorator
        # Calls the decorator function to decorate the target function
        return decorator(__return__)
    def cooperate(self, annotations):
        '''Returns a Cooperation instance to allow cooperative access of the
        annotation dictionary. The cooperation schemes is determined by the
        cooperation class used.'''
        # The object key must be set in the loop later
        # (reuse single Cooperation instance for performace)
        return self.cooperation_class(
            annotations, None, classfilter=self._classfilter,
            **self.cooperation_keywords
        )
    def wrap(self, fn, ofn):
        '''Does not wrap the function by default. Subclasses can override
        this function to wrap the annotated function. Note, that you must
        wrap the function to be able to add runtime (function call-time)
        functionality, since the decorator is only executed once at function
        definition time.'''
        return fn

#============================================================================

annotate=AnnotationDecorator(TupleCooperation)

#============================================================================

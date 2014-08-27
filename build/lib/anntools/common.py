#!/usr/bin/python
# -*- coding: ascii -*-
'''
Common utilities.

(C) 2007-2008 - Viktor Ferenczi (python@cx.hu) - Licence: GNU LGPL

'''

#============================================================================

import sys

#============================================================================

__all__ = ['wraps', 'get_function_argument_names']

#============================================================================
# Function wrapper decorator

if sys.version_info[:2]<(2,5):
    
    # Compatible implementation for Python versions <2.5
    def wraps(wrapped):
        '''Wrap a function preserving the module, name and docstring of the
        original one. This function is only a simple replacement for the
        wraps function defined in Python 2.5's functools module that is
        missing from Python 2.4. It is not intended for external use.
        @param wrapper: wrapper function to be updated with properties of the original (wrapped) function
        '''
        def update_wrapper(wrapper):
            for attr in ('__module__', '__name__', '__doc__'):
                setattr(wrapper, attr, getattr(wrapped, attr))
            wrapper.__dict__.update(getattr(wrapped, '__dict__', {}))
            return wrapper
        return update_wrapper
        
else:
    
    # Use the implementation from the standard library
    from functools import wraps
    
#============================================================================
# Retrieving the list of argument names for a function

if sys.version_info[:2]<(3,0):
    
    from inspect import getargspec
    
    def get_function_argument_names(fn):
        return getargspec(fn)[0]
        
else:
    
    from inspect import getfullargspec
    
    def get_function_argument_names(fn):
        return getfullargspec(fn)[0]

#============================================================================

#!/usr/bin/python
# -*- coding: ascii -*-
'''
Simple type checking for function arguments and return value.

(C) 2007-2008 - Viktor Ferenczi (python@cx.hu) - Licence: GNU LGPL

This module provides checking of data type at function call boundaries.
This solution is compatible with the function annotation notation included
in Python 3.0, but runs on Python 2.4 and up using decorator arguments.
See also:

See also: PEP #3107 - Function annotations
http://www.python.org/dev/peps/pep-3107/

Runtime type checking at function call boundaries is very useful in various
use cases. For example:

- The function receives it's input from an untrusted source, such as client
side JavaScript code running in the user's browser. It is a common use case
when implementing CherryPy and Django handlers.

- Catching bugs early in mission critical applications. Decorators can be
turned into NOPs in the release version for improved performance.

- Providing explicit type information for IDEs, JIT compilers or other tools.

Example:

from anntools.validation import *

For Python 2.4-2.6:

@typecheck(unicode, n=int)
def myfunc(n):
    return u'#'*n

For Python 3.0:

@typecheck
def myfunc(n:int) -> str:
    return '#'*n

Constraints:

Note, that cooperation between multiple tools is not possible when using
this type checker. No other function annotation based tool may be used on the
same function. The NoCooperation scheme is used in order to prevent other
tools from accessing the function annotations. Use the validation module
if you need cooperation and parallel usage with another tools, such as
data conversion or marshalling.

Note, that runtime validation decreases performance, since it costs CPU and
memory on each function call. Using it everywhere in your code is not
recommended. Use them only where they are absolutely needed (for security)
or very usful (for type information).

(Frequently means use cases where a slight performance penalty is multiplied
by millions of calls and causes significant increase in the CPU time required
by your application.)

You can turn your decorator into  lambda fn: fn  later to remove nearly all
the runtime costs. It's suggested to separate essential validators (that
provides security) from the ones you use for debugging and type information
only. Such a solution allows you to preserve only the essential ones, while
removing all the others.

'''

#============================================================================

import sys

from anntools.common import wraps, get_function_argument_names
from anntools.cooperation import NoCooperation
from anntools.annotation import AnnotationDecorator

#============================================================================
# Exported symbols

__all__=['TypeCheckDecorator', 'typecheck']

#============================================================================

class TypeCheckDecorator(AnnotationDecorator):
    '''Decorator for type checking at function boundaries. Instances are
    function decorators to be used with all functions require type checking.
    With Python 2.4 and 2.5 the decorator got keyword arguments to declare
    argument and return type checking. Note that you need to use the
    decorator even with Py3K. If you annotate the function and forget to add
    the decorator, the type checking will not happen.'''
    _classfilter=object
    def raiseError(self, fn, types, name, value):
        '''Raises ValidationError for an argument or return value.'''
        if isinstance(types, (tuple, list)):
            typenames=', '.join([repr(validator) for type in types])
        else:
            typenames=repr(types)
        if sys.version_info[0]<3:
            fn_name=fn.func_name
        else:
            fn_name=fn.__name__
        if name=='return':
            raise TypeError('Error checking type of return value of function %r with %s type(s): return value = %r'%(fn_name, typenames, value))
        else:
            raise TypeError('Error checking type of argument %r of function %r with %s type(s): %s = %r'%(name, fn_name, typenames, name, value))
    def checkArgument(self, fn, cooperation, name, value):
        '''Check type an argument. Raises TypeError if the type check fails.'''
        # Try to validate with each validator
        cooperation.key=name
        for types in cooperation:
            if isinstance(value, types):
                return
            self.raiseError(fn, types, name, value)
    def wrap(self, fn, ofn):
        '''Wraps the function to provide runtime type checking.'''
        argnames=get_function_argument_names(ofn)
        @wraps(fn) 
        def wrapper(*args, **kw):
            '''Wrapper to implement actual argument and return value
            type checking. The @wraps decorator is required to preserve
            function module, name and docstring.'''
            cooperation=self.cooperate(ofn.__annotations__)
            # Validate positional arguments
            for name, value in zip(argnames, args):
                self.checkArgument(fn, cooperation, name, value)
            # Validate keyword arguments
            for name, value in kw.items():
                self.checkArgument(fn, cooperation, name, value)
            # Call original function
            return_value=fn(*args, **kw)
            # Validate return value
            self.checkArgument(fn, cooperation, 'return', return_value)
            # Returns with the return value of the original function
            return return_value
        return wrapper

#============================================================================

typecheck=TypeCheckDecorator(NoCooperation)

#============================================================================

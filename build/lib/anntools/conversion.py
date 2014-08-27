#!/usr/bin/python
# -*- coding: ascii -*-
'''
Conversion support for function arguments and return values.

(C) 2007-2008 - Viktor Ferenczi (python@cx.hu) - Licence: GNU LGPL

This module provides a automatic data conversion at function call boundaries.
The solution is compatible with the forthcoming function annotation notation
expected to be included in Python 3000, but runs on Python 2.4 and up using
decorator arguments. See also:

See also: PEP #3107 - Function annotations
http://www.python.org/dev/peps/pep-3107/

Type conversion at function call boundaries can be useful in various use
cases. For example (not a complete list):

- The function receives it's input from a client that passes all things as
strings, but your code expects other data type. This is true for scripts
running in a WEB browser and passing back GET/POST argumens. For example
CherryPy allows implementing this easily.

- The return value of your function must be converted to some other type and
you don't want to include this code at the end of all such functions. For
example returning JSON or XML formatted data from a function is easy and
readable this way. You can use return at any point of your function and
without repeating the call to convert your return value. This yields readable
code and less bugs.

- Any use case when marshalling of you function input/output is required.

Example:

For Python 2.4-2.6:

from anntools.conversion import *

@convert(Unicode, n=Int)
def square(n):
    return n*n

For Python 3.0:

@convert
def square(n:Int) -> Str:
    return n*n

The cooperation module provides schemes to allow cooperative usage and future
compatibility with other function annotation based tools. The default
cooperation scheme is TupleCooperation, which cooperates well with the other
modules of this package. You can define your own decorator with a different
scheme easily. For example:

from anntools.cooperation import ListCooperation
from anntools.conversion import *

validate=ConversionDecorator(ListCooperation())

This tool will process only Converter instances, all other instances are
silently skipped. Multiple Converter instances are evaluated from left to
right as embedded function calls: (A,B) yields B(A(value))

You can implement your own converter by subclassing the Converter class and
overriding it's _convert class method and/or the check instance method.
You must override the instance method only if you require arguments for the
conversion process. Note, that string/unicode handling will change in Python
3000, so conversions involving strings will likely fail. You should check for
sys.version in if you require Python 3000 compatibility.

Note, that wrapping you function will slightly decrease it's performance, so
using it blindly everywhere in your code is not recommended. Do not use it in
conjuction with frequently called functions (unless you have a really good
reason to do so).

(Frequently means use cases where a slight performance penalty is multiplied
by millions of calls and causes significant increase in the runtime of your
application.)
'''

#============================================================================

import sys

from anntools.common import wraps, get_function_argument_names
from anntools.cooperation import TupleCooperation
from anntools.annotation import AnnotationDecorator

#============================================================================
# Exported symbols

__all__=[
    'ConversionError', 'Converter',
    'AsBool', 'AsInt', 'AsFloat', 'AsBytes', 'AsStr', 'AsUnicode',
    'ConversionDecorator', 'convert'
]

# Note: Converters are named As* to allow global usage in conjunction with
# the validation module and express their converting behavior.

#============================================================================
# Exceptions

class ConversionError(ValueError):
    '''Error raised when an argument or return value fails to convert.
    The original exception information is stored in the original_exc
    instance attribute as returned by sys.exc_info(). This allow rising
    the original error and debugging the converter itself.'''
    pass

#============================================================================
# Converters

class Converter(object):
    '''Abstract base class'''
    # The exception class to be raised when the conversion fails.
    # Re-raises the original exception from the converter's code instead
    # of raising ConversionError if this is set to None. Setting this in
    # the Converter class affects all subclasses, hence the whole library.
    # This is handy for debugging converters.
    _exception_class=ConversionError
    @staticmethod
    def call(converter, value, classtype=type(object)):
        '''Call a Converter class or instance to validate a value.
        Returns None for foreign annotation objects or a bool as a result.'''
        if type(converter) is classtype and issubclass(converter, Converter):
            return converter._convert(value)
        if isinstance(converter, Converter):
            return converter.convert(value)
        return value
    @classmethod
    def _convert(cls, value):
        '''This class method is called on simple converters not requiring any
        arguments. They are used in class form for performace. This is also
        called for complex converters when used in class form. Override this
        class method in subclasses to implement specific conversion logic.
        Returns the converted value.'''
        assert NotImplementedError()
    def __init__(self, allow_none=False):
        self.allow_none=allow_none
    def convert(self, value):
        '''This instance method is called on complex converters requiring
        arguments to validate a value. This is also called for simple
        converters when someone used them in (inefficient) instance form.
        Override this class method in subclasses to implement specific
        conversion logic. You can store arguments for conversion in the
        converter object (instance). Returns the converted value.'''
        assert NotImplementedError()

#----------------------------------------------------------------------------

class AsBool(Converter):
    @classmethod
    def _convert(cls, value):
        return bool(value)
    def convert(self, value):
        if self.allow_none and value is None:
            return None
        return bool(value)

#----------------------------------------------------------------------------

class AsInt(Converter):
    @classmethod
    def _convert(cls, value):
        return int(value)
    def convert(self, value):
        if self.allow_none and value is None:
            return None
        return int(value)

#----------------------------------------------------------------------------

class AsFloat(Converter):
    @classmethod
    def _convert(cls, value):
        return float(value)
    def convert(self, value):
        if self.allow_none and value is None:
            return None
        return float(value)

#----------------------------------------------------------------------------

# For Python 2.4-2.6
if sys.version_info[0]<3:
    class AsStr(Converter):
        @classmethod
        def _convert(cls, value):
            if isinstance(value, str):
                return value
            if isinstance(value, unicode):
                return value.encode('utf8')
            return str(value)
        def __init__(self, allow_none=False, encoding='utf8'):
            Converter.__init__(self, allow_none)
            self.encoding=encoding
        def convert(self, value):
            if self.allow_none and value is None:
                return None
            if isinstance(value, str):
                return value
            if isinstance(value, unicode):
                return value.encode(self.encoding)
            return str(value)
    class AsUnicode(Converter):
        @classmethod
        def _convert(cls, value):
            if isinstance(value, unicode):
                return value
            if isinstance(value, str):
                return value.decode('utf8')
            return unicode(value)
        def __init__(self, allow_none=False, encoding='utf8'):
            Converter.__init__(self, allow_none)
            self.encoding=encoding
        def convert(self, value):
            if self.allow_none and value is None:
                return None
            if isinstance(value, unicode):
                return value
            if isinstance(value, str):
                return value.decode(self.encoding)
            return unicode(value)
    class AsBytes(AsStr):
        pass

#----------------------------------------------------------------------------

# For Python 3.0
if sys.version_info[0]>=3:
    class AsBytes(Converter):
        @classmethod
        def _convert(cls, value):
            if isinstance(value, bytes):
                return value
            if isinstance(value, str):
                return value.encode('utf8')
            raise ValueError()
        def __init__(self, allow_none=False, encoding='utf8'):
            Converter.__init__(self, allow_none)
            self.encoding=encoding
        def convert(self, value):
            if self.allow_none and value is None:
                return None
            if isinstance(value, bytes):
                return value
            if isinstance(value, str):
                return value.encode(self.encoding)
            raise ValueError()
    class AsStr(Converter):
        @classmethod
        def _convert(cls, value):
            if isinstance(value, str):
                return value
            if isinstance(value, bytes):
                return value.decode('utf8')
            return str(value)
        def __init__(self, allow_none=False, encoding='utf8'):
            Converter.__init__(self, allow_none)
            self.encoding=encoding
        def convert(self, value):
            if self.allow_none and value is None:
                return None
            if isinstance(value, str):
                return value
            if isinstance(value, bytes):
                return value.decode(self.encoding)
            return str(value)
    class AsUnicode(AsStr):
        pass
    
#============================================================================

class ConversionDecorator(AnnotationDecorator):
    '''Decorator for conversion as function boundaries. Instances are
    function decorators to be used with all functions require conversion.
    With Python 2.4 and 2.5 the decorator got keyword arguments to declare
    argument and return value conversion. Note that you need to use the
    decorator even with Py3K. If you annotate the function and forget to add
    the decorator, the validation will not happen.'''
    _classfilter=(Converter, Converter.__class__)
    def raiseError(self, fn, converter, name, value):
        '''Raises ConversionError for an argument or return value.'''
        if isinstance(converter, Converter):
            converter=converter.__class__
        if converter._exception_class is None:
            # Reraise the converter's error
            raise
        if sys.version_info[0]<3:
            fn_name=fn.func_name
        else:
            fn_name=fn.__name__
        if name=='return':
            exc=ConversionError('Error converting return value of function %r by %s converter: return value = %r'%(fn_name, converter.__name__, value))
        else:
            exc=ConversionError('Error converting argument %r of function %r by %s converter: %s = %r'%(name, fn_name, converter.__name__, name, value))
        exc.original_exc=sys.exc_info()
        raise exc
    def convertArgument(self, fn, cooperation, name, value):
        '''Convert an argument with it's converters.
        Raises ConversionError if the conversion fails.'''
        cooperation.key=name
        for converter in cooperation:
            try:
                value=Converter.call(converter, value)
            except Exception:
                self.raiseError(fn, converter, name, value)
        return value
    def wrap(self, fn, ofn):
        '''Wraps the function to provide conversion.'''
        argnames=get_function_argument_names(ofn)
        @wraps(fn)
        def wrapper(*args, **kw):
            '''Wrapper to implement actual argument and return value
            conversion. The @wraps decorator is required to preserve
            function module, name and docstring.'''
            cooperation=self.cooperate(ofn.__annotations__)
            # Convert positional arguments
            args=[self.convertArgument(fn, cooperation, name, value) for name, value in zip(argnames, args)]
            # Convert keyword arguments
            kw=dict([(name, self.convertArgument(fn, cooperation, name, value)) for name, value in kw.items()])
            # Call original function
            return_value=fn(*args, **kw)
            # Convert return value
            return self.convertArgument(fn, cooperation, 'return', return_value)
        return wrapper

#============================================================================

convert=ConversionDecorator(TupleCooperation)

#============================================================================

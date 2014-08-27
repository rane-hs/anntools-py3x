#!/usr/bin/python
# -*- coding: ascii -*-
'''
Validation support for function arguments and return values.

(C) 2007-2008 - Viktor Ferenczi (python@cx.hu) - Licence: GNU LGPL

This module provides automatic data validation at function call boundaries.
The solution is compatible with the function annotation notation included
in Python 3.0, but runs on Python 2.4 and up using decorator arguments.
See also:

See also: PEP #3107 - Function annotations
http://www.python.org/dev/peps/pep-3107/

Runtime validation (such as type checking) at function call boundaries could
be very useful in various use cases. For example:

- The function receives it's input from an untrusted source, such as client
side JavaScript code running in the user's browser. It is a common use case
when implementing CherryPy and Django handlers.

- Catching bugs early in mission critical applications. Decorators can be
turned into NOPs in the release version for improved performance.

- Providing explicit type information for IDEs, JIT compilers or other tools.

Example:

from anntools.validation import *

For Python 2.4-2.6:

@validate(Unicode, n=Int)
def myfunc(n):
    return u'#'*n

For Python 3.0:

@validate
def myfunc(n:Int) -> Str:
    return '#'*n

The cooperation module provides schemes to allow cooperative usage and future
compatibility with other function annotation based tools. The default
cooperation scheme is TupleCooperation, which works well with all the other
modules in this package. You can define your own decorator with a different
scheme easily. For example:

from anntools.cooperation import ListCooperation
from anntools.validation import *

validate=ValidationDecorator(ListCooperation())

Constraints:

This tool will process only Validator instances, all other instances are
silently skipped. Multiple Validator instances are evaluated in the same way
as the Python "or" logical operator. This is a common behavior of all
cooperative schemes and allows easy listing of alternatives.

You can also build complex validators from basic ones as building blocks
using the And, Or and Not composite validators. Note, that subclassing the
Validator class and implementing your own complex valdation criteria directly
can is much more efficient than building a large composite validator.

Note, that the behaviour of the Str and Unicode validators will change when
used with Python 3.0: The Str validator will be identical to the Unicode one
and the new Byte validator will handle 8 bit binary objects.

Note, that runtime validation decreases performance, since it costs CPU and
memory on each function call. Using it everywhere in your code is not
recommended. Use them only where they are absolutely needed (for security)
or very usful (for type information).

It's suggested to implement this feature only on the public interface of
your application (module or package) and do not use it in conjuction with
frequently called functions (unless you have a really good reason to do so).

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
from anntools.cooperation import TupleCooperation
from anntools.annotation import AnnotationDecorator

#============================================================================
# Exported symbols

__all__=[
    'ValidationError', 'Validator', 'And', 'Or', 'Not', 'AllowNone',
    'Bool', 'Int', 'Float', 'Complex', 'Bytes', 'Str', 'Unicode',
    'Tuple', 'List', 'Dict', 'Set', 'InstanceOf', 'SubclassOf',
    'ValidationDecorator', 'validate'
]

#============================================================================
# Exceptions

class ValidationError(ValueError):
    '''Error raised when an argument or return value fails validation.'''
    pass

#============================================================================
# Validators

class Validator(object):
    '''Abstract base class'''
    @staticmethod
    def call(validator, value, classtype=type(object)):
        '''Call a Validator class or instance to validate a value.
        Returns None for foreign annotator objects or a bool as a result.'''
        if type(validator) is classtype and issubclass(validator, Validator):
            return validator._check(value)
        if isinstance(validator, Validator):
            return validator.check(value)
        return None
    @classmethod
    def _check(cls, value):
        '''This class method is called on simple validators not requiring any
        arguments. They are used in class form for performace. This is also
        called for complex validators when used in class form. Override this
        class method in subclasses to implement specific validation logic.
        Returns True is the value is valid, False if not.
        May not return None.'''
        assert NotImplementedError()
    def check(self, value):
        '''This instance method is called on complex validators requiring
        arguments to validate a value. This is also called for simple
        validators when someone used them in (inefficient) instance form.
        Override this class method in subclasses to implement specific
        validation logic. You can store arguments for validation in the
        validator object (instance). Returns True is the value is valid,
        False if not. May not return None.'''
        assert NotImplementedError()

#----------------------------------------------------------------------------

class And(Validator):
    @classmethod
    def _check(cls, *args):
        raise NotImplementedError('You have to instantiate this validator and pass child validators.')
    def __init__(self, *validators):
        '''Store child validators'''
        self.validators=validators
    def check(self, value, classtype=type(object)):
        '''Perform logical and on the result of child validators.
        Provides the same short-circuit behavior as the Python and operator.'''
        for v in self.validators:
            r=Validator.call(v, value)
            if r is not None and not r:
                return False
        return True

#----------------------------------------------------------------------------

class Or(Validator):
    @classmethod
    def _check(cls, *args):
        raise NotImplementedError('You have to instantiate this validator and pass child validators.')
    def __init__(self, *validators):
        '''Store child validators'''
        self.validators=validators
    def check(self, value, classtype=type(object)):
        '''Perform logical or on the result of child validators.
        Provides the same short-circuit behavior as the Python or operator.'''
        for v in self.validators:
            r=Validator.call(v, value)
            if r is not None and r:
                return True
        return False

#----------------------------------------------------------------------------

class Not(Validator):
    @classmethod
    def _check(cls, *args):
        raise NotImplementedError('You have to instantiate this validator and pass child validators.')
    def __init__(self, validator):
        '''Store child validator'''
        self.validator=validator
    def check(self, value, classtype=type(object)):
        '''Perform logical not on the result of the child validator.'''
        r=Validator.call(self.validator, value)
        if r is None:
            return None
        return not r

#----------------------------------------------------------------------------

class AllowNone(Validator):
    @classmethod
    def _check(cls, value):
        return value is None
    def check(self, value):
        return value is None

#----------------------------------------------------------------------------

class Bool(Validator):
    @classmethod
    def _check(cls, value):
        return isinstance(value, bool)
    def check(self, value):
        return isinstance(value, bool)

#----------------------------------------------------------------------------

class Int(Validator):
    @classmethod
    def _check(cls, value):
        return isinstance(value, int) and not isinstance(value, bool)
    def __init__(self, min=None, max=None):
        self.min=min
        self.max=max
    def check(self, value):
        if not isinstance(value, int) or isinstance(value, bool):
            return False
        if self.min is not None and value<self.min:
            return False
        if self.max is not None and value>self.max:
            return False
        return True

#----------------------------------------------------------------------------

class Float(Validator):
    @classmethod
    def _check(cls, value):
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    def __init__(self, min=None, max=None):
        self.min=min
        self.max=max
    def check(self, value):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return False
        if self.min is not None and value<self.min:
            return False
        if self.max is not None and value>self.max:
            return False
        return True

#----------------------------------------------------------------------------

class Complex(Validator):
    @classmethod
    def _check(cls, value):
        return isinstance(value, complex)
    def check(self, value):
        return isinstance(value, complex)

#----------------------------------------------------------------------------

# For Python 2.4-2.6
if sys.version_info[0]<3:
    class Str(Validator):
        @classmethod
        def _check(cls, value):
            return isinstance(value, str)
        def __init__(self, maxlen=None):
            self.maxlen=maxlen
        def check(self, value):
            if not isinstance(value, str):
                return False
            if self.maxlen is not None and len(value)>self.maxlen:
                return False
            return True
    class Unicode(Validator):
        @classmethod
        def _check(cls, value):
            return isinstance(value, unicode)
        def __init__(self, maxlen=None):
            self.maxlen=maxlen
        def check(self, value):
            if not isinstance(value, unicode):
                return False
            if self.maxlen is not None and len(value)>self.maxlen:
                return False
            return True
    class Bytes(Str):
        pass

#----------------------------------------------------------------------------

# For Python 3.0
if sys.version_info[0]>=3:
    class Bytes(Validator):
        @classmethod
        def _check(cls, value):
            return isinstance(value, bytes)
        def __init__(self, maxlen=None):
            self.maxlen=maxlen
        def check(self, value):
            if not isinstance(value, bytes):
                return False
            if self.maxlen is not None and len(value)>self.maxlen:
                return False
            return True
    class Str(Validator):
        @classmethod
        def _check(cls, value):
            return isinstance(value, str)
        def __init__(self, maxlen=None):
            self.maxlen=maxlen
        def check(self, value):
            if not isinstance(value, str):
                return False
            if self.maxlen is not None and len(value)>self.maxlen:
                return False
            return True
    class Unicode(Str):
        pass
    
#----------------------------------------------------------------------------

class Tuple(Validator):
    @classmethod
    def _check(cls, value):
        return isinstance(value, tuple)
    def check(self, value):
        return isinstance(value, tuple)

#----------------------------------------------------------------------------

class List(Validator):
    @classmethod
    def _check(cls, value):
        return isinstance(value, list)
    def check(self, value):
        return isinstance(value, list)

#----------------------------------------------------------------------------

class Dict(Validator):
    @classmethod
    def _check(cls, value):
        return isinstance(value, dict)
    def check(self, value):
        return isinstance(value, dict)

#----------------------------------------------------------------------------

class Set(Validator):
    @classmethod
    def _check(cls, value):
        return isinstance(value, set)
    def check(self, value):
        return isinstance(value, set)

#----------------------------------------------------------------------------

class InstanceOf(Validator):
    @classmethod
    def _check(cls, value):
        raise SyntaxError('No class specified for the InstanceOf validator!')
    def __init__(self, *args):
        self.cls=args
    def check(self, value):
        return isinstance(value, self.cls)

#----------------------------------------------------------------------------

class SubclassOf(Validator):
    @classmethod
    def _check(cls, value):
        raise SyntaxError('No class specified for the SubclassOf validator!')
    def __init__(self, *args):
        self.cls=args
    def check(self, value, classtype=type(object)):
        return type(value) is classtype and issubclass(value, self.cls)

#============================================================================

class ValidationDecorator(AnnotationDecorator):
    '''Decorator for function boundary validation. Instances are
    function decorators to be used with all functions require validation.
    With Python 2.4 and 2.5 the decorator got keyword arguments to declare
    argument and return value validation. Note that you need to use the
    decorator even with Py3K. If you annotate the function and forget to add
    the decorator, the validation will not happen.'''
    _classfilter=(Validator, Validator.__class__)
    def raiseError(self, fn, validators, name, value):
        '''Raises ValidationError for an argument or return value.'''
        def validator_class(validator):
            if isinstance(validator, Validator):
                return validator.__class__
            return validator
        validator_names=', '.join([validator_class(validator).__name__ for validator in validators])
        if len(validators)>1:
            s='s'
        else:
            s=''
        if sys.version_info[0]<3:
            fn_name=fn.func_name
        else:
            fn_name=fn.__name__
        if name=='return':
            raise ValidationError('Error checking return value of function %r with the %s validator%s: return value = %r'%(fn_name, validator_names, s, value))
        else:
            raise ValidationError('Error checking argument %r of function %r with the %s validator%s: %s = %r'%(name, fn_name, validator_names, s, name, value))
    def validateArgument(self, fn, cooperation, name, value):
        '''Validate an argument with it's validators.
        Raises ValidationError if there is at least one validator
        and all validators fail.'''
        # Try to validate against all validators
        validators=[]
        cooperation.key=name
        for validator in cooperation:
            valid=Validator.call(validator, value)
            if valid is None:
                # Not a validator
                continue
            if valid:
                # Return on the first successful validation
                return
            validators.append(validator)
        # No validators succeeded
        if validators:
            # There was at least one validator and all validators failed
            self.raiseError(fn, validators, name, value)
    def wrap(self, fn, ofn):
        '''Wraps the function to provide runtime validation.'''
        argnames=get_function_argument_names(ofn)
        @wraps(fn)
        def wrapper(*args, **kw):
            '''Wrapper to implement actual argument and return value
            validation. The @wraps decorator is required to preserve
            function module, name and docstring.'''
            cooperation=self.cooperate(ofn.__annotations__)
            # Validate positional arguments
            for name, value in zip(argnames, args):
                self.validateArgument(fn, cooperation, name, value)
            # Validate keyword arguments
            for name, value in kw.items():
                self.validateArgument(fn, cooperation, name, value)
            # Call original function
            return_value=fn(*args, **kw)
            # Validate return value
            self.validateArgument(fn, cooperation, 'return', return_value)
            # Returns with the return value of the original function
            return return_value
        return wrapper

#============================================================================

validate=ValidationDecorator(TupleCooperation)

#============================================================================

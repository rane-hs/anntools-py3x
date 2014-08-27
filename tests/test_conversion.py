#!/usr/bin/python
# -*- coding: ascii -*-
'''
Test cases for the converters and converter-validator cooperation.

(C) 2007-2008 - Viktor Ferenczi (python@cx.hu) - Licence: GNU LGPL

'''

#============================================================================

import sys
from math import pi
from unittest import main, TestCase

from anntools.cooperation import *
from anntools.validation import *
from anntools.conversion import *

#============================================================================

class ConverterTestCase(TestCase):
    '''Test case for all converters with default TupleCooperation.'''
    def testAsBool(self):
        @convert(b=AsBool)
        def fn1(b):
            return isinstance(b, bool)
        self.assert_(fn1(True))
        self.assert_(fn1(1))
        self.assert_(fn1(None))
        @convert(b=AsBool(allow_none=True))
        def fn2(b):
            return b
        self.assert_(fn2(True) is True)
        self.assert_(fn2(1) is True)
        self.assert_(fn2(None) is None)
        class C(object):
            if sys.version_info[0]<3:
                def __nonzero__(self):
                    raise ValueError()
            else:
                def __bool__(self):
                    raise ValueError()
        @convert(b=AsBool)
        def fn3(b):
            pass
        self.assertRaises(ConversionError, fn3, C())
    def testAsInt(self):
        @convert(i=AsInt)
        def fn1(i):
            return i
        self.assertEqual(fn1(False), 0)
        self.assertEqual(fn1(True), 1)
        self.assertEqual(fn1('10'), 10)
        self.assertRaises(ConversionError, fn1, 'abc')
        self.assertRaises(ConversionError, fn1, fn1)
    def testAsFloat(self):
        @convert(f=AsFloat)
        def fn1(f):
            return f
        self.assertEqual(fn1(False), 0)
        self.assertEqual(fn1(True), 1)
        self.assertEqual(fn1('1.5'), 1.5)
        self.assertRaises(ConversionError, fn1, 'abc')
        self.assertRaises(ConversionError, fn1, fn1)
    if sys.version_info[0]<3:
        # Python 2.4-2.6
        def testAsStr(self):            
            class C(object):
                def __str__(self):
                    raise ValueError()
            @convert(s=AsStr)
            def fn(s):
                return s
            self.assertEqual(fn(''), '')
            self.assertEqual(fn(123), '123')
            self.assert_(isinstance(fn(123), str))
            self.assertRaises(ConversionError, fn, C())
        def testAsUnicode(self):
            class C(object):
                def __str__(self):
                    raise ValueError()
            @convert(s=AsUnicode)
            def fn(s):
                return s
            self.assertEqual(fn(''), eval("u''"))
            self.assertEqual(fn(123), eval("u'123'"))
            self.assert_(isinstance(fn(123), unicode))
            self.assertRaises(ConversionError, fn, C())
    else:
        # Python 3.0
        def testAsBytes(self):            
            class C(object):
                def __str__(self):
                    raise ValueError()
            @convert(s=AsBytes)
            def fn(s):
                return s
            self.assertEqual(fn(eval("b''")), eval("b''"))
            self.assert_(isinstance(fn('abc'), bytes))
            self.assertRaises(ConversionError, fn, 123)
            self.assertRaises(ConversionError, fn, C())
        def testAsStr(self):
            class C(object):
                def __str__(self):
                    raise ValueError()
            @convert(s=AsStr)
            def fn(s):
                return s
            self.assertEqual(fn(''), '')
            self.assertEqual(fn(123), '123')
            self.assert_(isinstance(fn(123), str))
            self.assertRaises(ConversionError, fn, C())

#============================================================================

class ConverterValidatorTestCase(TestCase):
    '''Test case for converter-validator interoperability
    using the default TupleCooperation.'''
    def testAsBool(self):
        @validate(Str, x=(Int,Float)) # Outer: validation
        @convert(AsStr, x=AsFloat) # Inner: conversion
        def fn(x):
            return isinstance(x, float)
        self.assertEqual(fn(1), 'True')
        self.assertEqual(fn(pi), 'True')
        self.assertRaises(ValidationError, fn, 'abc')

#============================================================================

if __name__=='__main__':
    main()

#============================================================================

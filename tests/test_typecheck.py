#!/usr/bin/python
# -*- coding: ascii -*-
'''
Test cases for the type checker.

(C) 2007-2008 - Viktor Ferenczi (python@cx.hu) - Licence: GNU LGPL

'''

#============================================================================

import sys
from math import pi
from unittest import main, TestCase

from anntools.typecheck import *

#============================================================================

class TypeCheckerTestCase(TestCase):
    '''Test case for all validators with default TupleCooperation.'''
    if sys.version_info[0]<3:
        _u_empty=eval("u''")
        _u_x=eval("u'x'")
        _u_abc=eval("u'abc'")
    else:
        _u_empty=''
        _u_x='x'
        _u_abc='abc'
        _b_empty=eval("b''")
        _b_x=eval("b'x'")
        _b_abc=eval("b'abc'")
    def testNone(self):
        NoneType=type(None)
        @typecheck(a=NoneType, b=(int, NoneType), c=int)
        def fn(a, b, c):
            return b
        self.assert_(fn(None, 1, 3))
        self.assert_(not fn(None, None, 3))
        self.assertRaises(TypeError, fn, 1, 2, 3)
        self.assertRaises(TypeError, fn, 'x', 2, 3)
        self.assertRaises(TypeError, fn, None, 1, None)
    def testBool(self):
        @typecheck(b=bool)
        def fn(b):
            return b
        self.assert_(fn(True))
        self.assert_(not fn(False))
        self.assertRaises(TypeError, fn, 1)
        self.assertRaises(TypeError, fn, 'x')
    def testInt(self):
        @typecheck(i=int)
        def fn(i):
            return i
        self.assertEqual(fn(10), 10)
        self.assertEqual(fn(0), 0)
        self.assertEqual(fn(False), 0)
        self.assertRaises(TypeError, fn, 'x')
    def testFloat(self):
        @typecheck(f=float)
        def fn(f):
            return f
        self.assertEqual(fn(0.0), 0.0)
        self.assertEqual(fn(1.0), 1.0)
        self.assertEqual(int(fn(pi)), 3)
        self.assertRaises(TypeError, fn, 0)
        self.assertRaises(TypeError, fn, False)
        self.assertRaises(TypeError, fn, 'x')
    def testComplex(self):
        @typecheck(c=complex)
        def fn(c):
            return c
        self.assertEqual(fn(1+2j), 1+2j)
        self.assertRaises(TypeError, fn, False)
        self.assertRaises(TypeError, fn, 0)
        self.assertRaises(TypeError, fn, 1.0)
        self.assertRaises(TypeError, fn, pi)
        self.assertRaises(TypeError, fn, 'x')
        self.assertRaises(TypeError, fn, self._u_x)
    if sys.version_info[0]<3:
        # Python 2.4-2.6
        def testStr(self):
            @typecheck(s=str)
            def fn(s):
                return s
            self.assertEqual(fn(''), '')
            self.assertEqual(fn('abc'), 'abc')
            self.assertRaises(TypeError, fn, 1)
            self.assertRaises(TypeError, fn, False)
            self.assertRaises(TypeError, fn, int)
            self.assertRaises(TypeError, fn, self._u_x)
        def testUnicode(self):
            @typecheck(s=unicode)
            def fn(s):
                return s
            self.assertEqual(fn(self._u_empty), self._u_empty)
            self.assertEqual(fn(self._u_abc), self._u_abc)
            self.assertRaises(TypeError, fn, 1)
            self.assertRaises(TypeError, fn, False)
            self.assertRaises(TypeError, fn, int)
            self.assertRaises(TypeError, fn, 'x')
    else:
        # Python 3.0
        def testBytes(self):
            @typecheck(s=bytes)
            def fn(s):
                return s
            b1=self._b_empty
            b2=self._b_abc
            self.assertEqual(fn(b1), b1)
            self.assertEqual(fn(b2), b2)
            self.assertRaises(TypeError, fn, 1)
            self.assertRaises(TypeError, fn, False)
            self.assertRaises(TypeError, fn, int)
            self.assertRaises(TypeError, fn, 'x')
            self.assertRaises(TypeError, fn, self._u_x)
        def testStr(self):
            @typecheck(s=str)
            def fn(s):
                return s
            self.assertEqual(fn(''), '')
            self.assertEqual(fn('abc'), 'abc')
            self.assertRaises(TypeError, fn, 1)
            self.assertRaises(TypeError, fn, False)
            self.assertRaises(TypeError, fn, int)
    def testTuple(self):
        @typecheck(v=tuple)
        def fn(v):
            return True
        self.assertEqual(fn((2,3)), True)
        self.assertRaises(TypeError, fn, 1)
        self.assertRaises(TypeError, fn, 1.0)
        self.assertRaises(TypeError, fn, 3.14)
        self.assertRaises(TypeError, fn, self._u_x)
    def testList(self):
        @typecheck(v=list)
        def fn(v):
            return True
        self.assertEqual(fn([2,3]), True)
        self.assertRaises(TypeError, fn, 1)
        self.assertRaises(TypeError, fn, 1.0)
        self.assertRaises(TypeError, fn, 'x')
        self.assertRaises(TypeError, fn, self._u_x)
    def testDict(self):
        @typecheck(v=dict)
        def fn(v):
            return True
        self.assertEqual(fn({2:3}), True)
        self.assertRaises(TypeError, fn, 1)
        self.assertRaises(TypeError, fn, 1.0)
        self.assertRaises(TypeError, fn, 'x')
        self.assertRaises(TypeError, fn, self._u_x)
    def testSet(self):
        @typecheck(v=set)
        def fn(v):
            return True
        self.assertEqual(fn(set([1,2,3])), True)
        self.assertRaises(TypeError, fn, 1)
        self.assertRaises(TypeError, fn, 1.0)
        self.assertRaises(TypeError, fn, 'x')
        self.assertRaises(TypeError, fn, self._u_x)

#============================================================================

if __name__=='__main__':
    main()

#============================================================================

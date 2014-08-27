#!/usr/bin/python
# -*- coding: ascii -*-
'''
Test cases for the validators and validator cooperation.

(C) 2007-2008 - Viktor Ferenczi (python@cx.hu) - Licence: GNU LGPL

'''

#============================================================================

import sys
from math import pi
from unittest import main, TestCase

from anntools.cooperation import *
from anntools.validation import *

#============================================================================

class ValidatorTestCase(TestCase):
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
    def testAllowNone(self):
        @validate(a=AllowNone, b=(Int, AllowNone), c=Int)
        def fn(a, b, c):
            return b
        self.assert_(fn(None, 1, 3))
        self.assert_(not fn(None, None, 3))
        self.assertRaises(ValidationError, fn, 1, 2, 3)
        self.assertRaises(ValidationError, fn, 'x', 2, 3)
        self.assertRaises(ValidationError, fn, None, 1, None)
    def testBool(self):
        @validate(b=Bool)
        def fn(b):
            return b
        self.assert_(fn(True))
        self.assert_(not fn(False))
        self.assertRaises(ValidationError, fn, 1)
        self.assertRaises(ValidationError, fn, 'x')
    def testInt(self):
        @validate(i=Int)
        def fn(i):
            return i
        self.assertEqual(fn(10), 10)
        self.assertEqual(fn(0), 0)
        self.assertRaises(ValidationError, fn, False)
        self.assertRaises(ValidationError, fn, 'x')
    def testIntRange(self):
        @validate(i=Int(min=5, max=10))
        def fn(i):
            return i
        self.assertEqual(fn(5), 5)
        self.assertEqual(fn(10), 10)
        self.assertRaises(ValidationError, fn, True)
        self.assertRaises(ValidationError, fn, 'x')
        self.assertRaises(ValidationError, fn, 1)
        self.assertRaises(ValidationError, fn, 11)
    def testFloat(self):
        @validate(f=Float)
        def fn(f):
            return f
        self.assertEqual(fn(0), 0)
        self.assertEqual(fn(0.0), 0.0)
        self.assertEqual(fn(1.0), 1.0)
        self.assertEqual(int(fn(pi)), 3)
        self.assertRaises(ValidationError, fn, False)
        self.assertRaises(ValidationError, fn, 'x')
    def testFloatRange(self):
        @validate(
            Float(min=-3, max=3),
            f=Float(min=-2.5, max=2.5)
        )
        def fn(f):
            return f*2
        self.assertEqual(fn(1.0), 2.0)
        self.assertEqual(fn(-1.0), -2.0)
        self.assertRaises(ValidationError, fn, True)
        self.assertRaises(ValidationError, fn, -5)
        self.assertRaises(ValidationError, fn, -2)
        self.assertRaises(ValidationError, fn, 2)
        self.assertRaises(ValidationError, fn, pi)
        self.assertRaises(ValidationError, fn, 5)
        self.assertRaises(ValidationError, fn, 'x')
        self.assertRaises(ValidationError, fn, self._u_x)
    def testComplex(self):
        @validate(c=Complex)
        def fn(c):
            return c
        self.assertEqual(fn(1+2j), 1+2j)
        self.assertRaises(ValidationError, fn, False)
        self.assertRaises(ValidationError, fn, 0)
        self.assertRaises(ValidationError, fn, 1.0)
        self.assertRaises(ValidationError, fn, pi)
        self.assertRaises(ValidationError, fn, 'x')
        self.assertRaises(ValidationError, fn, self._u_x)
    if sys.version_info[0]<3:
        # Python 2.4-2.6
        def testStr(self):
            @validate(s=Str)
            def fn(s):
                return s
            self.assertEqual(fn(''), '')
            self.assertEqual(fn('abc'), 'abc')
            self.assertRaises(ValidationError, fn, 1)
            self.assertRaises(ValidationError, fn, False)
            self.assertRaises(ValidationError, fn, int)
            self.assertRaises(ValidationError, fn, self._u_x)
        def testStrMaxLength(self):
            @validate(
                Str(maxlen=6),
                s=Str(maxlen=4)
            )
            def fn(s):
                return s+s
            self.assertEqual(fn(''), '')
            self.assertEqual(fn('abc'), 'abcabc')
            self.assertRaises(ValidationError, fn, 1)
            self.assertRaises(ValidationError, fn, False)
            self.assertRaises(ValidationError, fn, int)
            self.assertRaises(ValidationError, fn, self._u_x)
            self.assertRaises(ValidationError, fn, 'abcd')
            self.assertRaises(ValidationError, fn, 'abcde')
        def testUnicode(self):
            @validate(s=Unicode)
            def fn(s):
                return s
            self.assertEqual(fn(self._u_empty), self._u_empty)
            self.assertEqual(fn(self._u_abc), self._u_abc)
            self.assertRaises(ValidationError, fn, 1)
            self.assertRaises(ValidationError, fn, False)
            self.assertRaises(ValidationError, fn, int)
            self.assertRaises(ValidationError, fn, 'x')
        def testUnicodeMaxLength(self):
            @validate(
                Unicode(maxlen=6),
                s=Unicode(maxlen=4)
            )
            def fn(s):
                return s+s
            self.assertEqual(fn(self._u_empty), self._u_empty)
            self.assertEqual(fn(eval(r"u'\u00e1bc'")), eval(r"u'\u00e1bc\u00e1bc'"))
            self.assertRaises(ValidationError, fn, 1)
            self.assertRaises(ValidationError, fn, False)
            self.assertRaises(ValidationError, fn, int)
            self.assertRaises(ValidationError, fn, 'x')
            self.assertRaises(ValidationError, fn, eval(r"u'\u00e1bcd'"))
            self.assertRaises(ValidationError, fn, eval(r"u'\u00e1bcde'"))
    else:
        # Python 3.0
        def testBytes(self):
            @validate(s=Bytes)
            def fn(s):
                return s
            b1=self._b_empty
            b2=self._b_abc
            self.assertEqual(fn(b1), b1)
            self.assertEqual(fn(b2), b2)
            self.assertRaises(ValidationError, fn, 1)
            self.assertRaises(ValidationError, fn, False)
            self.assertRaises(ValidationError, fn, int)
            self.assertRaises(ValidationError, fn, 'x')
            self.assertRaises(ValidationError, fn, self._u_x)
        def testBytesMaxLength(self):
            @validate(
                Bytes(maxlen=6),
                s=Bytes(maxlen=4)
            )
            def fn(s):
                return s+s
            b1=self._b_empty
            b2=self._b_abc
            b2d=self._b_abc+self._b_abc
            b3=self._b_abc+self._b_abc[:1]
            b4=self._b_abc+self._b_abc[:2]
            self.assertEqual(fn(b1), b1)
            self.assertEqual(fn(b2), b2d)
            self.assertRaises(ValidationError, fn, 1)
            self.assertRaises(ValidationError, fn, False)
            self.assertRaises(ValidationError, fn, int)
            self.assertRaises(ValidationError, fn, 'x')
            self.assertRaises(ValidationError, fn, self._u_x)
            self.assertRaises(ValidationError, fn, b3)
            self.assertRaises(ValidationError, fn, b4)
        def testStr(self):
            @validate(s=Str)
            def fn(s):
                return s
            self.assertEqual(fn(''), '')
            self.assertEqual(fn('abc'), 'abc')
            self.assertRaises(ValidationError, fn, 1)
            self.assertRaises(ValidationError, fn, False)
            self.assertRaises(ValidationError, fn, int)
        def testStrMaxLength(self):
            @validate(
                Str(maxlen=6),
                s=Str(maxlen=4)
            )
            def fn(s):
                return s+s
            self.assertEqual(fn(''), '')
            self.assertEqual(fn('abc'), 'abcabc')
            self.assertRaises(ValidationError, fn, 1)
            self.assertRaises(ValidationError, fn, False)
            self.assertRaises(ValidationError, fn, int)
            self.assertRaises(ValidationError, fn, 'abcd')
            self.assertRaises(ValidationError, fn, 'abcde')
        def testUnicode(self):
            @validate(s=Unicode)
            def fn(s):
                return s
            self.assertEqual(fn(self._u_empty), self._u_empty)
            self.assertEqual(fn(self._u_abc), self._u_abc)
            self.assertRaises(ValidationError, fn, 1)
            self.assertRaises(ValidationError, fn, False)
            self.assertRaises(ValidationError, fn, int)
            self.assertRaises(ValidationError, fn, self._b_x)
        def testUnicodeMaxLength(self):
            @validate(
                Unicode(maxlen=6),
                s=Unicode(maxlen=4)
            )
            def fn(s):
                return s+s
            self.assertEqual(fn(self._u_empty), self._u_empty)
            self.assertEqual(fn('\u00e1bc'), '\u00e1bc\u00e1bc')
            self.assertRaises(ValidationError, fn, 1)
            self.assertRaises(ValidationError, fn, False)
            self.assertRaises(ValidationError, fn, int)
            self.assertRaises(ValidationError, fn, self._b_x)
            self.assertRaises(ValidationError, fn, '\u00e1bcd')
            self.assertRaises(ValidationError, fn, '\u00e1bcde')
    def testTuple(self):
        @validate(v=Tuple)
        def fn(v):
            return True
        self.assertEqual(fn((2,3)), True)
        self.assertRaises(ValidationError, fn, 1)
        self.assertRaises(ValidationError, fn, 1.0)
        self.assertRaises(ValidationError, fn, 'x')
        self.assertRaises(ValidationError, fn, self._u_x)
    def testList(self):
        @validate(v=List)
        def fn(v):
            return True
        self.assertEqual(fn([2,3]), True)
        self.assertRaises(ValidationError, fn, 1)
        self.assertRaises(ValidationError, fn, 1.0)
        self.assertRaises(ValidationError, fn, 'x')
        self.assertRaises(ValidationError, fn, self._u_x)
    def testDict(self):
        @validate(v=Dict)
        def fn(v):
            return True
        self.assertEqual(fn({2:3}), True)
        self.assertRaises(ValidationError, fn, 1)
        self.assertRaises(ValidationError, fn, 1.0)
        self.assertRaises(ValidationError, fn, 'x')
        self.assertRaises(ValidationError, fn, self._u_x)
    def testSet(self):
        @validate(v=Set)
        def fn(v):
            return True
        self.assertEqual(fn(set([1,2,3])), True)
        self.assertRaises(ValidationError, fn, 1)
        self.assertRaises(ValidationError, fn, 1.0)
        self.assertRaises(ValidationError, fn, 'x')
        self.assertRaises(ValidationError, fn, self._u_x)
    def testInstanceOf(self):
        @validate(v=InstanceOf(Exception))
        def fn(v):
            return True
        self.assertEqual(fn(TypeError()), True)
        self.assertRaises(ValidationError, fn, 1)
    def testSubclassOf(self):
        @validate(v=SubclassOf(int))
        def fn(v):
            return True
        self.assertEqual(fn(bool), True)
        self.assertRaises(ValidationError, fn, 1)
        self.assertRaises(ValidationError, fn, float)
    def testNot(self):
        @validate(x=Not(Int))
        def fn(x):
            return True
        self.assert_(fn('x'))
        self.assert_(fn(pi))
        self.assertRaises(ValidationError, fn, 3)
    def testAnd(self):
        @validate(x=And(Int(min=0), Int(max=9)))
        def fn(x):
            return x
        self.assertEqual(fn(3), 3)
        self.assertRaises(ValidationError, fn, -1)
        self.assertRaises(ValidationError, fn, 10)
        self.assertRaises(ValidationError, fn, 'x')
    def testOr(self):
        @validate(x=Or(Int(min=0), Float(max=9)))
        def fn(x):
            return x
        self.assertEqual(fn(-1), -1)
        self.assertEqual(fn(3), 3)
        self.assertEqual(int(fn(pi)), 3)
        self.assertRaises(ValidationError, fn, 10.5)
        self.assertRaises(ValidationError, fn, 'x')

#============================================================================

class ValidatorCooperationTestCase(TestCase):
    '''Test case for cooperation scheme compatibility.'''
    def testNoCooperation(self):
        validate=ValidationDecorator(NoCooperation)
        # Empty validation list.
        @validate
        def fn1(a):
            return True
        self.assert_(fn1('x'))
        # Non-cooperative simple annotation,
        # validation occours and raises exception normally:
        @validate(Bool, a=Int)
        def fn2(a):
            return True
        self.assertRaises(ValidationError, fn2, 'x')
        # Multiple annotations for different arguments works without cooperation:
        @validate(a=Int)
        @validate(b=Str)
        def fn3(a, b):
            return True
        self.assert_(fn3(1, 'x'))
        self.assertRaises(ValidationError, fn3, 'x', 1)
        # Multiple annotations for the same argument won't work:
        def fn4def():
            @validate(a=Int)
            @validate(a=Str)
            def fn4(a):
                return True
        self.assertRaises(NoCooperationError, fn4def)
        # Multiple annotations for the return value won't work:
        def fn5def():
            @validate(Int)
            @validate(Str)
            def fn5(a):
                return True
        self.assertRaises(NoCooperationError, fn5def)
    def testTupleCooperation(self):
        validate=ValidationDecorator(TupleCooperation)
        # Single annotation:
        @validate(Bool, a=Int)
        def fn1(a):
            return True
        self.assert_(fn1(1))
        self.assertRaises(ValidationError, fn1, None)
        # Multiple validators with single annotation:
        @validate(Bool, a=(AllowNone, Int))
        def fn2(a):
            return True
        self.assert_(fn2(None))
        self.assert_(fn2(1))
        self.assertRaises(ValidationError, fn2, 'x')
        # Multiple annotations for a single argument (cooperation) works:
        @validate(a=Bool)
        @validate(a=Str)
        def fn3(a):
            return True
        self.assert_(fn3(True))
        self.assert_(fn3('x'))
        self.assertRaises(ValidationError, fn3, 1)
    def testListCooperation(self):
        validate=ValidationDecorator(ListCooperation)
        # Single annotation:
        @validate(Bool, a=Int)
        def fn1(a):
            return True
        self.assert_(fn1(1))
        self.assertRaises(ValidationError, fn1, None)
        # Multiple validators with single annotation:
        @validate(Bool, a=[AllowNone, Int])
        def fn2(a):
            return True
        self.assert_(fn2(None))
        self.assert_(fn2(1))
        self.assertRaises(ValidationError, fn2, 'x')
        # Multiple annotations for a single argument (cooperation) works:
        @validate(a=Bool)
        @validate(a=Str)
        def fn3(a):
            return True
        self.assert_(fn3(True))
        self.assert_(fn3('x'))
        self.assertRaises(ValidationError, fn3, 1)
    def testDictCooperation(self):
        validateA=ValidationDecorator(DictCooperation, dict(storekey='A'))
        validateB=ValidationDecorator(DictCooperation, dict(storekey='B'))
        # Single annotation:
        @validateA(Bool, a=Int)
        def fn1(a):
            return True
        self.assert_(fn1(1))
        self.assertRaises(ValidationError, fn1, None)
        # Multiple validators with single annotation, must use composite:
        @validateA(Bool, a=Or(AllowNone, Int))
        def fn2(a):
            return True
        self.assert_(fn2(None))
        self.assert_(fn2(1))
        self.assertRaises(ValidationError, fn2, 'x')
        # Multiple annotations for a single argument (cooperation) works,
        # but validates independently (no logical or between validators):
        @validateA(a=Int)
        @validateB(a=Float)
        def fn3(a):
            return True
        self.assert_(fn3(1))
        self.assertRaises(ValidationError, fn3, pi)
        self.assertRaises(ValidationError, fn3, True)
        self.assertRaises(ValidationError, fn3, 'x')
        # Multiple annotations for a single argument (no-cooperation) fails:
        def fn4def():
            @validateA(a=Bool)
            @validateA(a=Str)
            def fn4(a):
                pass
        self.assertRaises(DictCooperationError, fn4def)

#============================================================================

if __name__=='__main__':
    main()

#============================================================================

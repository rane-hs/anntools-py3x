#!/usr/bin/python
# -*- coding: ascii -*-
'''
Test cases for the scheme schemes.

(C) 2007-2008 - Viktor Ferenczi (python@cx.hu) - Licence: GNU LGPL

'''

#============================================================================

from unittest import main, TestCase

from anntools.cooperation import *

#============================================================================

class CooperationTestCase(TestCase):
    '''Test case for scheme schemes.'''
    def testNoCooperation(self):
        class T(object): pass
        space={}
        scheme=NoCooperation(space, 'name')
        def add():
            scheme.add(T())
        add()
        self.assertEqual(len(space), 1)
        self.assertRaises(NoCooperationError, add)
        self.assertEqual(len(space), 1)
        for ann in scheme:
            self.assert_(isinstance(ann, T))
            scheme.remove(ann)
            break
        self.assert_(not space)
    def testTupleCooperation(self):
        class T(object): pass
        space={}
        scheme=TupleCooperation(space, 'name')
        def add():
            scheme.add(T())
        add()
        self.assertEqual(len(space), 1)
        self.assert_(not isinstance(space['name'], tuple))
        add()
        self.assertEqual(len(space), 1)
        self.assert_(isinstance(space['name'], tuple))
        self.assertEqual(len(space['name']), 2)
        for ann in scheme:
            self.assert_(isinstance(ann, T))
        for ann in scheme:
            self.assert_(isinstance(ann, T))
            scheme.remove(ann)
            break
        self.assertEqual(len(space), 1)
        self.assert_(not isinstance(space['name'], tuple))
        for ann in scheme:
            self.assert_(isinstance(ann, T))
            scheme.remove(ann)
            break
        self.assert_(not space)
    def testListCooperation(self):
        class T(object): pass
        space={}
        scheme=ListCooperation(space, 'name')
        def add():
            scheme.add(T())
        add()
        self.assertEqual(len(space), 1)
        self.assert_(not isinstance(space['name'], list))
        add()
        self.assertEqual(len(space), 1)
        self.assert_(isinstance(space['name'], list))
        self.assertEqual(len(space['name']), 2)
        for ann in scheme:
            self.assert_(isinstance(ann, T))
        for ann in scheme:
            self.assert_(isinstance(ann, T))
            scheme.remove(ann)
            break
        self.assertEqual(len(space), 1)
        self.assert_(not isinstance(space['name'], list))
        for ann in scheme:
            self.assert_(isinstance(ann, T))
            scheme.remove(ann)
            break
        self.assert_(not space)
    def testDictCooperation(self):
        class T(object): pass
        space={}
        cooperationA=DictCooperation(space, 'name', 'A')
        cooperationB=DictCooperation(space, 'name', 'B')
        def addA():
            cooperationA.add(T())
        def addB():
            cooperationB.add(T())
        addA()
        self.assertEqual(len(space), 1)
        self.assertEqual(len(space['name']), 1)
        self.assert_('A' in space['name'])
        self.assertRaises(DictCooperationError, addA)
        addB()
        self.assertEqual(len(space), 1)
        self.assertEqual(len(space['name']), 2)
        self.assert_('A' in space['name'])
        self.assert_('B' in space['name'])
        self.assertRaises(DictCooperationError, addB)
        for ann in cooperationA:
            self.assert_(isinstance(ann, T))
            cooperationA.remove(ann)
            break
        self.assertEqual(len(space), 1)
        self.assertEqual(len(space['name']), 1)
        self.assert_('A' not in space['name'])
        self.assert_('B' in space['name'])
        for ann in cooperationB:
            self.assert_(isinstance(ann, T))
            cooperationB.remove(ann)
            break
        self.assert_(not space)

#============================================================================

if __name__=='__main__':
    main()

#============================================================================

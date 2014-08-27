#!/usr/bin/python
# -*- coding: ascii -*-
'''
Cooperation schemes.

(C) 2007-2008 - Viktor Ferenczi (python@cx.hu) - Licence: GNU LGPL

This module provides cooperation schemes. It is very useful whenever forward
compatibility is required between tools operating on a common object space.

Cooperation instances allows cooperative access to the values of a
dictionary, which stores the object space. The object space stores individual
objects or storage objects. The type of the storage object depends on the
cooperation scheme used. Using cooperation schemes does not require to
change the class of the object space or store special objects in it as long
as a single object is stored for each key. This allows limited compatibility
with tools not compatible with cooperation schemes.

Example: You can add the ability of cooperation to your function annotation
based tool easily. Whenever you need to access the annotation (iterate, add,
remove, check) of an argument or return value just use your Cooperation
instance instead of direct access. Let the user of your library to specify
the Cooperation subclass to be used:

class MyTool:
    def addAnnotation(self, fn, argname, annotator):
        TupleCooperation(fn.__annotations__, argname).add(annotator)
        
NOTE: On Python 3.0 annotations are stored in fn.__annotations__ instead.

See the source code of other modules in this packages for more information.

You can subclass Cooperation and implement your scheme if none of the 
predefined schemes fit your needs. Note that specifying __slots__ in
each of your subclasses can improve performace, since no __dict__ will be
created for the instances of you subclass. Please drop me a mail if you would
like your scheme to be included in this module. I could include it if it's
generic enough, could be usable for a wide range of applications and has the
essential unit test cases.

TODO: Optimization
TODO: SetCooperation
'''

#============================================================================
# Exported symbols

__all__=[
    'CooperationError', 'NoCooperationError', 'DictCooperationError',
    'CooperationFailed', 'DictCooperationFailed',
    'Cooperation', 'NoCooperation',  'TupleCooperation', 'ListCooperation',
    'DictCooperation',
]

#============================================================================
# Exceptions

class CooperationError(ValueError):
    '''Raised when an existing object is about to be overwritten.
    This means that an error at our side prevent correct cooperation.'''
    pass

#----------------------------------------------------------------------------

class NoCooperationError(CooperationError):
    '''Raised when an existing object is about to be overwritten
    by the NoCooperation scheme. This means that an error at our side
    prevent correct cooperation.'''
    pass

#----------------------------------------------------------------------------

class DictCooperationError(CooperationError):
    '''Raised when an existing object is about to be overwritten
    by the DictCooperation scheme. This means that an error at our side
    prevent correct cooperation.'''
    pass

#----------------------------------------------------------------------------

class CooperationFailed(CooperationError):
    '''Riased when the cooperation is failed due to an incompatible object
    stored by someone else. This means that cooperation cannot be continued
    due to an error or incompatibility in another tool accessing the same
    object space.'''
    pass

#----------------------------------------------------------------------------

class DictCooperationFailed(CooperationFailed):
    '''Riased when DictCooperation is failed due to an incompatible object
    stored by someone else. This means that cooperation cannot be continued
    due to an error or incompatibility in another tool accessing the same
    object space.'''
    pass

#============================================================================
# Cooperation schemes

class Cooperation(object):
    '''Base class for cooperation schemes. Note that objects are stored in a
    separate object space, not in the Cooperation instance itself, so the
    interface of Cooperation instances are like a proxy to a set, but
    without the support for set operations (union, etc.). The Cooperation
    object also does not guarantee uniqueness of stored values, but it could
    be guaranteed by specific cooperation schemes. It is allowed to set
    the space and key properties of a Cooperation instance, since it
    does not store any objects or state information (stateless). This allows
    fast reuse of a single Cooperation instance for operations with differnt
    object keys or even object spaces. The class filter should not be
    modified. While this is technically possible it would change the set of
    accepted objects in a counter-intuitive way.'''
    # NOTE: __slots__ should be defined for each subclass for performance
    __slots__=['space', 'key', 'classfilter']
    def __init__(self, space, key, classfilter=object):
        '''Initialize cooperation for a given object space and object key.
        An optional class or tuple of classes can be defined to filter
        objects by their class. This is a convenient feature to easily
        spearate sets of objects for different purposes.
        @param space: The object space (dictionary) to operate on.
        @param key: Object space key to identify the objects to be accessed.
        @param classfilter: Optional class filter to separate objects for different purposes. Must be a class or a tuple of classes.
        '''
        self.space=space
        self.key=key
        self.classfilter=classfilter
    # Informational methods
    def iter(self):
        '''Iterates on stored objects. Yields only those instances that fit
        the class filter, which is an easy way to separate objects belonging
        to differenct tools or serving different purposes. Note that the
        called must specify an exact class filter or check object in the
        loop and silently skip all foreign (unknown) objects it encounters
        to ensure future compatibility.
        IMPORTANT NOTE:
        It's not recommended to store built-in Python objects, since they
        are universal and cannot be associated for a single purpose.'''
        raise NotImplementedError()
    def len(self):
        '''Returns the total number of objects could be iterated.'''
        cnt=0
        for obj in self:
            cnt+=1
        return cnt
    def contains(self, obj):
        '''Returns True if the object space contains the given object.
        Always returns False, if the object does not fit the class filter.
        @param obj: Object to search for.'''
        if isinstance(obj, self.classfilter):
            for o in self:
                if o is obj: return True
        return False
    # Provides a set like interface
    __iter__=iter
    __len__=len
    __contains__=contains
    # Set like manipulation methods
    def add(self, obj):
        '''Adds an object. Does not guarantee, that the object is unique,
        but it can be guaranteed by a specific cooperation schemes. Must
        preserve any existing objects or raise a subclass of CooperationError
        if the operation cannot be completed for some reason. Note, that the
        object to be added must fit the class filter or ValueError raised.
        This restriction is due to mathematical correctness, since if an
        object could be added that does not fit the filter it cannot be
        accessed later by the same Cooperation instance.
        @param obj: The object to be added.
        @raise ValueError: Raised when the object to be added does not fit the class filter.
        @raise CooperationError: Raised when an existing object is about to be overwritten.
        @raise CooperationFailed: Raised when an incompatible object is in the way.
        '''
        raise NotImplementedError()
    def remove(self, obj):
        '''Removes an object. Does not guarantee, that all instances of this
        object will be removed, only guarantees that at least one is removed.
        Subclasses may provide different behavior regarding uniqueness. Note
        that the object is searched by it's identity, not by it's value. The
        object is checked against the class filter to prevent accidental
        removal of foreign objects or other incorrect usage.
        @param obj: The object to be removed.
        @raise ValueError: Raised when the object to be removed does not fit the class filter.
        '''
        raise NotImplementedError()

#----------------------------------------------------------------------------

class NoCooperation(Cooperation):
    '''No cooperation allowed. At most one object can be stored. Trying to
    add a second object will raise NoCooperationError.'''
    __slots__=['space', 'key', 'classfilter']
    def iter(self):
        '''Yields at most one object.'''
        if self.key in self.space:
            obj=self.space[self.key]
            if isinstance(obj, self.classfilter):
                yield obj
    __iter__=iter
    def add(self, obj):
        '''Stores the object. Raises NoCooperationError if an existing object
        is about to be overwritten. Raises ValueError if the object does not
        fit the class filter.
        @param obj: The object to be appended.
        @raise ValueError: Raised when the object to be added does not fit the class filter.
        @raise NoCooperationError: Raised when an existing object is about to be overwritten.
        '''
        if not isinstance(obj, self.classfilter):
            raise ValueError('Object does not fit the class filter: key=%r, classfilter=%r'%(self.key, self.classfilter))
        if self.key not in self.space:
            self.space[self.key]=obj
        else:
            raise NoCooperationError('Trying to overwrite an existing object! key=%r'%(self.key,))
    def remove(self, obj):
        '''Removes the object. Does nothing if no object is stored or the
        stored object is not the given object. This behavior is for
        compatibility with other cooperation schemes. Raises ValueError if
        the object does not fit the class filter.
        @param obj: The object to be removed.
        @raise ValueError: Raised when the object to be removed does not fit the class filter.
        '''
        if not isinstance(obj, self.classfilter):
            raise ValueError('Object does not fit the class filter: key=%r, classfilter=%r'%(self.key, self.classfilter))
        if self.key in self.space and self.space[self.key] is obj:
            del self.space[self.key]

#----------------------------------------------------------------------------

class TupleCooperation(Cooperation):
    '''Cooperation scheme that stores objects in a tuple.
    This is the default cooperation scheme for all modules in the anntools
    package, since it provides a simple way of cooperation without too much
    overhead or restrictions imposed on what type of objects can be stored.
    This should cover most of the use cases while giving reasonably good
    performance as long as the number of objects is not very high. This is
    also a convenient scheme if you have to specify a singel object or a
    tuple of objects by hand as in the case of function annotations.'''
    __slots__=['space', 'key', 'classfilter']
    def iter(self):
        '''Yields all stored objects fitting the class filter.'''
        if self.key not in self.space:
            return
        storage=self.space[self.key]
        classfilter=self.classfilter
        if isinstance(storage, tuple):
            for obj in storage:
                if isinstance(obj, classfilter):
                    yield obj
        elif isinstance(storage, classfilter):
            yield storage
    __iter__=iter
    def add(self, obj):
        '''Adds the object, introduces a tuple as storage object if more than
        one objects are stored in the object space. Adding a tuple appends
        it's contents.
        @param obj: The object to be appended.
        @raise ValueError: Raised when the object to be added does not fit the class filter.
        '''
        if isinstance(obj, tuple):
            for o in obj:
                self.add(o)
            return
        if not isinstance(obj, self.classfilter):
            raise ValueError('Object does not fit the class filter: key=%r, classfilter=%r'%(self.key, self.classfilter))
        space=self.space
        key=self.key
        if key in space:
            storage=space[key]
            if isinstance(storage, tuple):
                space[key]=storage+(obj,)
            else:
                space[key]=(storage, obj)
        else:
            space[key]=obj
    def remove(self, obj):
        '''Removes an object from the object space.
        Replaces tuple by a single object if only one object left.
        Deletes the key from the object space if no objects left.
        @param obj: The object to be removed.
        @raise ValueError: Raised when the object to be removed does not fit the class filter.
        '''
        if isinstance(obj, tuple):
            for o in obj:
                self.remove(o)
            return
        if not isinstance(obj, self.classfilter):
            raise ValueError('Object does not fit the class filter: key=%r, classfilter=%r'%(self.key, self.classfilter))
        space=self.space
        key=self.key
        if key not in space:
            return
        storage=space[key]
        if isinstance(storage, tuple):
            filtered=[a for a in storage if a is not obj]
            if len(filtered)<len(storage):
                if not filtered:
                    del space[key]
                elif len(filtered)<2:
                    space[key]=filtered[0]
                else:
                    space[key]=tuple(filtered)
        elif storage is obj:
            del space[key]

#----------------------------------------------------------------------------

class ListCooperation(Cooperation):
    '''Cooperation scheme that stores objects in a list.'''
    __slots__=['space', 'key', 'classfilter']
    def iter(self):
        '''Yields all stored objects fitting the class filter.'''
        if self.key not in self.space:
            return
        storage=self.space[self.key]
        classfilter=self.classfilter
        if isinstance(storage, list):
            for obj in storage:
                if isinstance(obj, classfilter):
                    yield obj
        elif isinstance(storage, classfilter):
            yield storage
    __iter__=iter
    def add(self, obj):
        '''Adds the object, introduces a list as storage object if more than
        one objects are stored in the object space. Adding a list appends
        it's contents.
        @param obj: The object to be appended.
        @raise ValueError: Raised when the object to be added does not fit the class filter.
        '''
        if isinstance(obj, list):
            for o in obj:
                self.add(o)
            return
        if not isinstance(obj, self.classfilter):
            raise ValueError('Object does not fit the class filter: key=%r, classfilter=%r'%(self.key, self.classfilter))
        space=self.space
        key=self.key
        if key in space:
            storage=space[key]
            if isinstance(storage, list):
                storage.append(obj)
            else:
                space[key]=[storage, obj]
        else:
            space[key]=obj
    def remove(self, obj):
        '''Removes an object from the object space.
        Replaces list by a single object if only one object left.
        Deletes the key from the object space if no objects left.
        @param obj: The object to be removed.
        @raise ValueError: Raised when the object to be removed does not fit the class filter.
        '''
        if isinstance(obj, list):
            for o in obj:
                self.remove(o)
            return
        if not isinstance(obj, self.classfilter):
            raise ValueError('Object does not fit the class filter: key=%r, classfilter=%r'%(self.key, self.classfilter))
        space=self.space
        key=self.key
        if key not in space:
            return
        storage=space[key]
        if isinstance(storage, list):
            idx=[i for i,o in enumerate(storage) if o is obj]
            for i in idx:
                del storage[i]
            if not storage:
                del space[key]
            elif len(storage)<2:
                space[key]=storage[0]
        elif storage is obj:
            del space[key]

#----------------------------------------------------------------------------

class DictCooperation(Cooperation):
    '''Cooperation scheme that stores objects in a dictionary. An additional
    key must be given to the constructor that identifies the objects to be
    accessed in the dictionary used as the storage. Note, that only one
    object can be stored by this scheme for each cooperative partner using
    different storage keys. This scheme does not allow single objects in the
    objects space. The object space can only contain dictionaries.'''
    __slots__=['space', 'key', 'classfilter', 'storekey']
    def __init__(self, space, key, storekey, classfilter=object):
        '''Initialize cooperation scheme.
        @param storekey Hashable key to identify our object in the object storage.
        '''
        Cooperation.__init__(self, space, key, classfilter)
        self.storekey=storekey
    def iter(self):
        '''Yields a single object if exists.'''
        if self.key in self.space:
            storage=self.space[self.key]
            if self.storekey in storage:
                obj=storage[self.storekey]
                if isinstance(obj, self.classfilter):
                    yield obj
    __iter__=iter
    def add(self, obj):
        '''Adds a new object. Introduces a dictionary into the object space
        if no object already exists with the object key. Raises ValueError
        if the object to be added does not fit the class filter. Riases
        DictCooperationError if an object already stored. Raises
        DictCooperationFailed if the object space contains a non-dictionary
        (hence incompatible) object.
        @param obj: The object to be appended.
        @raise ValueError: Raised when trying to add an object that does not fit the class filter.
        @raise DictCooperationError: Raised when an existing object is about to be overwritten.
        @raise DictCooperationFailed: Raised when cooperation is failed due to an incompatible object found in the object space.
        '''
        if not isinstance(obj, self.classfilter):
            raise ValueError('Object does not fit the class filter: key=%r, classfilter=%r'%(self.key, self.classfilter))
        space=self.space
        key=self.key
        if key in space:
            storage=space[key]
            if not isinstance(storage, dict):
                raise DictCooperationFailed('Incompatible object found in object space! Dicionary cooperation failed. key=%r'%(self.key,))
            storekey=self.storekey
            if storekey in storage:
                raise DictCooperationError('Trying to overwrite an existing object! key=%r, storekey=%r'%(self.key, self.storekey))
            storage[storekey]=obj
        else:
            space[key]={self.storekey:obj}            
    def remove(self, obj):
        '''Removes the given object.
        @param obj: The object to be removed.
        @raise ValueError: Raised when trying to remove an object that does not fit the class filter.
        '''
        if not isinstance(obj, self.classfilter):
            raise ValueError('Object does not fit the class filter: key=%r, classfilter=%r'%(self.key, self.classfilter))
        space=self.space
        key=self.key
        if key in space:
            storage=space[key]
            if not isinstance(storage, dict):
                raise DictCooperationFailed('Incompatible object found in object space! Dicionary cooperation failed. key=%r'%(self.key,))
            storekey=self.storekey
            if storekey in storage:
                del storage[storekey]
                if not storage:
                    del space[key]

#============================================================================

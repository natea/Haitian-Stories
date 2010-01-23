# Copyright (c) 2007-2009 The PyAMF Project.
# See LICENSE for details.

"""
Compatibility classes/functions for Flex.

@note: Not available in ActionScript 1.0 and 2.0.
@see: U{Flex on Wikipedia (external)
<http://en.wikipedia.org/wiki/Adobe_Flex>}

@since: 0.1.0
"""

import pyamf

__all__ = ['ArrayCollection', 'ObjectProxy']

class ArrayCollection(list):
    """
    I represent the ActionScript 3 based class
    C{flex.messaging.io.ArrayCollection} used in the Flex framework.

    The C{ArrayCollection} class is a wrapper class that exposes an Array
    as a collection that can be accessed and manipulated using the
    methods and properties of the C{ICollectionView} or C{IList}
    interfaces in the Flex framework.

    @see: U{ArrayCollection on Livedocs (external)
    <http://livedocs.adobe.com/flex/201/langref/mx/collections/ArrayCollection.html>}

    @note: This class does not implement the RemoteObject part of the
        documentation.

    @ivar length: [read-only] The number of items in this collection.
        Introduced in 0.4.
    @type length: C{int}
    """

    def __init__(self, source=None):
        if source is not None:
            if isinstance(source, dict):
                raise TypeError('Cannot convert dicts to ArrayCollection')

            if hasattr(source, '__iter__'):
                self.extend(source)

    def __repr__(self):
        return "<flex.messaging.io.ArrayCollection %s>" % list.__repr__(self)

    def __readamf__(self, input):
        data = input.readObject()

        if not hasattr(data, '__iter__'):
            raise pyamf.DecodeError('Unable to read a list when decoding ArrayCollection')

        self.extend(data)

    def __writeamf__(self, output):
        output.encoder.writeList(list(self), use_references=True, _use_proxies=False)

    def _get_length(self):
        return len(self)

    def _set_length(self, length):
        raise RuntimeError("Property length is read-only")

    length = property(_get_length, _set_length)

    def addItem(self, item):
        """
        Adds the specified item to the end of the list.

        @param item: The object to add to the collection.
        @type item: C{mixed}.
        @since: 0.4
        """
        self.append(item)

    def addItemAt(self, item, index):
        """
        Adds the item at the specified index.

        @param item: The object to add to the collection.
        @type item: C{mixed}.
        @param index: The index at which to place the item.
        @raise IndexError: If index is less than 0 or greater than the length
            of the list.
        @since: 0.4
        """
        if index < 0:
            raise IndexError

        if index > len(self):
            raise IndexError

        self.insert(index, item)

    def getItemAt(self, index, prefetch=0):
        """
        Gets the item at the specified index.

        @param index: The index in the list from which to retrieve the item.
        @type index: C{int}
        @param prefetch: This param is ignored and is only here as part of the
            interface.
        @raise IndexError: if C{index < 0} or C{index >= length}
        @return: The item at index C{index}.
        @rtype: C{mixed}.
        @since: 0.4
        """
        if index < 0:
            raise IndexError

        if index > len(self):
            raise IndexError

        return self.__getitem__(index)

    def getItemIndex(self, item):
        """
        Returns the index of the item if it is in the list such that
        C{getItemAt(index) == item}.

        @param item: The item to find.
        @type item: C{mixed}.
        @return: The index of the item or -1 if the item is not in the list.
        @rtype: C{int}
        @since: 0.4
        """
        try:
            return self.index(item)
        except ValueError:
            return -1

    def removeAll(self):
        """
        Removes all items from the list.

        @since: 0.4
        """
        while len(self) > 0:
            self.pop()

    def removeItemAt(self, index):
        """
        Removes the item at the specified index and returns it. Any items that
        were after this index are now one index earlier.

        @param index: The index from which to remove the item.
        @return: The item that was removed.
        @rtype: C{mixed}.
        @raise IndexError: If index is less than 0 or greater than length.
        @since: 0.4
        """
        if index < 0:
            raise IndexError

        if index > len(self):
            raise IndexError

        x = self[index]

        del self[index]

        return x

    def setItemAt(self, item, index):
        """
        Places the item at the specified index. If an item was already at that
        index the new item will replace it and it will be returned.

        @param item: The new item to be placed at the specified index.
        @type item: C{mixed}.
        @param index: The index at which to place the item.
        @type index: C{int}
        @return: The item that was replaced, or C{None}.
        @rtype: C{mixed} or C{None}.
        @raise IndexError: If index is less than 0 or greater than length.
        @since: 0.4
        """
        if index < 0:
            raise IndexError

        if index > len(self):
            raise IndexError

        tmp = self.__getitem__(index)
        self.__setitem__(index, item)

        return tmp

    def toArray(self):
        """
        Returns an Array that is populated in the same order as the C{IList}
        implementation.

        @return: The array.
        @rtype: C{list}
        """
        return self

pyamf.register_class(ArrayCollection, 'flex.messaging.io.ArrayCollection',
    metadata=['external', 'amf3'])

class ObjectProxy(object):
    """
    I represent the ActionScript 3 based class C{flex.messaging.io.ObjectProxy}
    used in the Flex framework. Flex's C{ObjectProxy} class allows an anonymous,
    dynamic ActionScript Object to be bindable and report change events.

    @see: U{ObjectProxy on Livedocs (external)
    <http://livedocs.adobe.com/flex/201/langref/mx/utils/ObjectProxy.html>}
    """

    def __init__(self, object=None):
        if object is None:
            self._amf_object = pyamf.ASObject()
        else:
            self._amf_object = object

    def __repr__(self):
        return "<flex.messaging.io.ObjectProxy %s>" % self._amf_object

    def __getattr__(self, name):
        if name == '_amf_object':
            return self.__dict__['_amf_object']

        return getattr(self.__dict__['_amf_object'], name)

    def __setattr__(self, name, value):
        if name == '_amf_object':
            self.__dict__['_amf_object'] = value
        else:
            setattr(self._amf_object, name, value)

    def __readamf__(self, input):
        self._amf_object = input.readObject()

    def __writeamf__(self, output):
        output.writeObject(self._amf_object)

pyamf.register_class(ObjectProxy, 'flex.messaging.io.ObjectProxy',
    metadata=['external', 'amf3'])

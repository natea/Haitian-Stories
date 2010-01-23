# Copyright (c) 2007-2009 The PyAMF Project.
# See LICENSE for details.

"""
PyAMF SQLAlchemy adapter tests.

@since 0.4
"""

import unittest

import sqlalchemy
from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, \
                       create_engine
from sqlalchemy.orm import mapper, relation, sessionmaker, clear_mappers, attributes

import pyamf.flex
from pyamf.tests.util import Spam
from pyamf.adapters import _sqlalchemy as adapter

class BaseObject(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class User(BaseObject):
    def __init__(self, **kwargs):
        BaseObject.__init__(self, **kwargs)

        self.lazy_loaded = [LazyLoaded()]

class Address(BaseObject):
    pass

class LazyLoaded(BaseObject):
    pass

class AnotherLazyLoaded(BaseObject):
    pass

class BaseTestCase(unittest.TestCase):
    """
    Initialise up all table/mappers.
    """

    def setUp(self):
        # Create DB and map objects
        self.metadata = MetaData()
        self.engine = create_engine('sqlite:///:memory:', echo=False)

        Session = sessionmaker(bind=self.engine)

        self.session = Session()
        self.tables = {}

        self.tables['users'] = Table('users', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(64)))

        self.tables['addresses'] = Table('addresses', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('user_id', Integer, ForeignKey('users.id')),
            Column('email_address', String(128)))

        self.tables['lazy_loaded'] = Table('lazy_loaded', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('user_id', Integer, ForeignKey('users.id')))

        self.tables['another_lazy_loaded'] = Table('another_lazy_loaded', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('user_id', Integer, ForeignKey('users.id')))

        self.mappers = {}

        self.mappers['user'] = mapper(User, self.tables['users'], properties={
            'addresses': relation(Address, backref='user', lazy=False),
            'lazy_loaded': relation(LazyLoaded, lazy=True),
            'another_lazy_loaded': relation(AnotherLazyLoaded, lazy=True)
        })

        self.mappers['addresses'] = mapper(Address, self.tables['addresses'])
        self.mappers['lazy_loaded'] = mapper(LazyLoaded,
            self.tables['lazy_loaded'])
        self.mappers['another_lazy_loaded'] = mapper(AnotherLazyLoaded,
            self.tables['another_lazy_loaded'])

        self.metadata.create_all(self.engine)

        pyamf.register_class(User, 'server.User')
        pyamf.register_class(Address, 'server.Address')
        pyamf.register_class(LazyLoaded, 'server.LazyLoaded')

    def tearDown(self):
        clear_mappers()

        pyamf.unregister_class(User)
        pyamf.unregister_class(Address)
        pyamf.unregister_class(LazyLoaded)

    def _build_obj(self):
        user = User()
        user.name = "test_user"
        user.addresses.append(Address(email_address="test@example.org"))

        return user

    def _save(self, obj):
        # this covers deprecation warnings etc.
        if hasattr(self.session, 'add'):
            self.session.add(obj)
        elif hasattr(self.session, 'save'):
            self.session.save(user)
        else:
            raise AttributeError('Don\'t know how to save an object')

    def _clear(self):
        # this covers deprecation warnings etc.
        if hasattr(self.session, 'expunge_all'):
            self.session.expunge_all()
        elif hasattr(self.session, 'clear'):
            self.session.clear()
        else:
            raise AttributeError('Don\'t know how to clear session')

class SATestCase(BaseTestCase):
    def _test_obj(self, encoded, decoded):
        self.assertEquals(User, decoded.__class__)
        self.assertEquals(encoded.name, decoded.name)
        self.assertEquals(encoded.addresses[0].email_address, decoded.addresses[0].email_address)

    def test_encode_decode_transient(self):
        user = self._build_obj()

        encoder = pyamf.get_encoder(pyamf.AMF3)
        encoder.writeElement(user)
        encoded = encoder.stream.getvalue()
        decoded = pyamf.get_decoder(pyamf.AMF3, encoded).readElement()

        self._test_obj(user, decoded)

    def test_encode_decode_persistent(self):
        user = self._build_obj()
        self._save(user)
        self.session.commit()
        self.session.refresh(user)

        encoder = pyamf.get_encoder(pyamf.AMF3)
        encoder.writeElement(user)
        encoded = encoder.stream.getvalue()
        decoded = pyamf.get_decoder(pyamf.AMF3, encoded).readElement()

        self._test_obj(user, decoded)

    def test_encode_decode_list(self):
        max = 5
        for i in range(0, max):
            user = self._build_obj()
            user.name = "%s" % i
            self._save(user)

        self.session.commit()
        users = self.session.query(User).all()

        encoder = pyamf.get_encoder(pyamf.AMF3)

        encoder.writeElement(users)
        encoded = encoder.stream.getvalue()
        decoded = pyamf.get_decoder(pyamf.AMF3, encoded).readElement()
        self.assertEquals([].__class__, decoded.__class__)

        for i in range(0, max):
            self._test_obj(users[i], decoded[i])

    def test_sa_merge(self):
        user = self._build_obj()

        for i, string in enumerate(['one', 'two', 'three']):
            addr = Address(email_address="%s@example.org" % string)
            user.addresses.append(addr)

        self._save(user)
        self.session.commit()
        self.session.refresh(user)

        encoder = pyamf.get_encoder(pyamf.AMF3)
        encoder.writeElement(user)
        encoded = encoder.stream.getvalue()

        decoded = pyamf.get_decoder(pyamf.AMF3, encoded).readElement()
        del decoded.addresses[0]
        del decoded.addresses[1]

        merged_user = self.session.merge(decoded)
        self.assertEqual(len(merged_user.addresses), 2)

    def test_lazy_load_attributes(self):
        user = self._build_obj()

        self._save(user)
        self.session.commit()
        self._clear()
        user = self.session.query(User).first()

        encoder = pyamf.get_encoder(pyamf.AMF3)
        encoder.writeElement(user)
        encoded = encoder.stream.getvalue()

        decoded = pyamf.get_decoder(pyamf.AMF3, encoded).readElement()
        self.assertFalse(decoded.__dict__.has_key('lazy_loaded'))

        if hasattr(attributes, 'instance_state'):
            obj_state = attributes.instance_state(decoded)
            self.assertFalse(obj_state.committed_state.has_key('lazy_loaded'))
            self.assertFalse(obj_state.dict.has_key('lazy_loaded'))

    def test_merge_with_lazy_loaded_attrs(self):
        user = self._build_obj()

        self._save(user)
        self.session.commit()
        self._clear()
        user = self.session.query(User).first()

        encoder = pyamf.get_encoder(pyamf.AMF3)
        encoder.writeElement(user)
        encoded = encoder.stream.getvalue()

        decoded = pyamf.get_decoder(pyamf.AMF3, encoded).readElement()
        self.assertFalse(decoded.__dict__.has_key('lazy_loaded'))
        self.session.merge(user)
        self.session.commit()

        user = self.session.query(User).first()
        self.assertTrue(len(user.lazy_loaded) == 1)

    def test_encode_decode_with_references(self):
        user = self._build_obj()
        self._save(user)
        self.session.commit()
        self.session.refresh(user)

        max = 5
        users = []
        for i in range(0, max):
            users.append(user)

        encoder = pyamf.get_encoder(pyamf.AMF3)
        encoder.writeElement(users)
        encoded = encoder.stream.getvalue()

        decoded = pyamf.get_decoder(pyamf.AMF3, encoded).readElement()

        for i in range(0, max):
            self.assertEquals(id(decoded[0]), id(decoded[i]))

class ClassAliasTestCase(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)

        self.alias = pyamf.get_class_alias(User)

    def test_type(self):
        self.assertEquals(self.alias.__class__, adapter.SaMappedClassAlias)

    def test_get_mapper(self):
        self.assertFalse(hasattr(self.alias, 'primary_mapper'))

        mapper = self.alias._getMapper(User())

        self.assertTrue(hasattr(self.alias, 'primary_mapper'))
        self.assertEquals(id(mapper), id(self.alias.primary_mapper))

    def test_get_attrs(self):
        u = self._build_obj()
        static, dynamic = self.alias.getAttrs(u)

        self.assertEquals(static, [
            'sa_key',
            'sa_lazy',
            'lazy_loaded',
            'addresses',
            'another_lazy_loaded',
            'id',
            'name'
        ])

        self.assertEquals(dynamic, [])

    def test_get_attributes(self):
        u = self._build_obj()

        self.assertFalse(u in self.session)
        self.assertEquals([None], self.mappers['user'].primary_key_from_instance(u))
        static, dynamic = self.alias.getAttributes(u)

        self.assertEquals(static, {
            'sa_lazy': ['another_lazy_loaded'],
            'sa_key': [None],
            'addresses': u.addresses,
            'lazy_loaded': u.lazy_loaded,
            'another_lazy_loaded': pyamf.Undefined,
            'id': None,
            'name': 'test_user'
        })
        self.assertEquals(dynamic, {})

class ApplyAttributesTestCase(ClassAliasTestCase):
    def test_undefined(self):
        u = self.alias.createInstance()

        attrs = {
            'sa_lazy': ['another_lazy_loaded'],
            'sa_key': [None],
            'addresses': [],
            'lazy_loaded': [],
            'another_lazy_loaded': pyamf.Undefined, # <-- the important bit
            'id': None,
            'name': 'test_user'
        }

        self.alias.applyAttributes(u, attrs)

        d = u.__dict__.copy()

        if sqlalchemy.__version__.startswith('0.4'):
            self.assertTrue('_state' in d)
            del d['_state']
        elif sqlalchemy.__version__.startswith('0.5'):
            self.assertTrue('_sa_instance_state' in d)
            del d['_sa_instance_state']

        self.assertEquals(d, {
            'lazy_loaded': [],
            'addresses': [],
            'name': 'test_user',
            'id': None
        })

    def test_decode_unaliased(self):
        u = self.alias.createInstance()

        attrs = {
            'sa_lazy': [],
            'sa_key': [None],
            'addresses': [],
            'lazy_loaded': [],
            # this is important because we haven't registered AnotherLazyLoaded
            # as an alias and the decoded object for an untyped object is an
            # instance of pyamf.ASObject
            'another_lazy_loaded': [pyamf.ASObject({'id': 1, 'user_id': None})],
            'id': None,
            'name': 'test_user'
        }

        # sqlalchemy can't find any state to work with
        self.assertRaises(AttributeError, self.alias.applyAttributes, u, attrs)

class AdapterTestCase(BaseTestCase):
    """
    Checks to see if the adapter will actually intercept a class correctly
    """

    def test_mapped(self):
        self.assertNotEquals(None, adapter.class_mapper(User))
        self.assertTrue(adapter.is_class_sa_mapped(User))

    def test_instance(self):
        u = User()

        self.assertTrue(adapter.is_class_sa_mapped(u))

    def test_not_mapped(self):
        self.assertRaises(adapter.UnmappedInstanceError, adapter.class_mapper, Spam)
        self.assertFalse(adapter.is_class_sa_mapped(Spam))

def suite():
    suite = unittest.TestSuite()

    try:
        import pysqlite2
    except ImportError:
        return suite

    classes = [
        SATestCase,
        AdapterTestCase,
        ClassAliasTestCase,
        ApplyAttributesTestCase
    ]

    for x in classes:
        suite.addTest(unittest.makeSuite(x))

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

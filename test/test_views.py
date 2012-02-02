import unittest
import confit

def _root(*sources):
    return confit.RootView(sources)

class SingleSourceTest(unittest.TestCase):
    def test_dict_access(self):
        config = _root({'foo': 'bar'})
        value = config['foo'].get()
        self.assertEqual(value, 'bar')

    def test_list_access(self):
        config = _root(['foo', 'bar'])
        value = config[1].get()
        self.assertEqual(value, 'bar')

    def test_nested_dict_list_access(self):
        config = _root({'foo': ['bar', 'baz']})
        value = config['foo'][1].get()
        self.assertEqual(value, 'baz')

    def test_nested_list_dict_access(self):
        config = _root([{'foo': 'bar'}, {'baz': 'qux'}])
        value = config[1]['baz'].get()
        self.assertEqual(value, 'qux')

    def test_missing_key(self):
        config = _root({'foo': 'bar'})
        with self.assertRaises(confit.NotFoundError):
            config['baz'].get()

    def test_missing_index(self):
        config = _root(['foo', 'bar'])
        with self.assertRaises(confit.NotFoundError):
            config[5].get()

class TypeCheckTest(unittest.TestCase):
    def test_str_type_correct(self):
        config = _root({'foo': 'bar'})
        value = config['foo'].get(str)
        self.assertEqual(value, 'bar')

    def test_str_type_incorrect(self):
        config = _root({'foo': 2})
        with self.assertRaises(confit.ConfigTypeError):
            config['foo'].get(str)

    def test_int_type_correct(self):
        config = _root({'foo': 2})
        value = config['foo'].get(int)
        self.assertEqual(value, 2)

    def test_int_type_incorrect(self):
        config = _root({'foo': 'bar'})
        with self.assertRaises(confit.ConfigTypeError):
            config['foo'].get(int)

class ConverstionTest(unittest.TestCase):
    def test_str_conversion_from_str(self):
        config = _root({'foo': 'bar'})
        value = str(config['foo'])
        self.assertEqual(value, 'bar')

    def test_str_conversion_from_int(self):
        config = _root({'foo': 2})
        value = str(config['foo'])
        self.assertEqual(value, '2')

    def test_unicode_conversion_from_int(self):
        config = _root({'foo': 2})
        value = unicode(config['foo'])
        self.assertEqual(value, u'2')

    def test_bool_conversion_from_bool(self):
        config = _root({'foo': True})
        value = bool(config['foo'])
        self.assertEqual(value, True)

    def test_bool_conversion_from_int(self):
        config = _root({'foo': 0})
        value = bool(config['foo'])
        self.assertEqual(value, False)

    def test_iterate_list(self):
        config = _root({'foo': ['bar', 'baz']})
        value = list(config['foo'])
        self.assertEqual(value, ['bar', 'baz'])

    def test_length_list(self):
        config = _root({'foo': ['bar', 'baz']})
        length = len(config['foo'])
        self.assertEqual(length, 2)

    def test_length_int(self):
        config = _root({'foo': 2})
        with self.assertRaises(confit.ConfigTypeError):
            len(config['foo'])

class NameTest(unittest.TestCase):
    def test_root_name(self):
        config = _root(None)
        name = config.name()
        self.assertEqual(name, 'root')

    def test_string_access_name(self):
        config = _root(None)
        name = config['foo'].name()
        self.assertEqual(name, "root['foo']")

    def test_int_access_name(self):
        config = _root(None)
        name = config[5].name()
        self.assertEqual(name, "root[5]")

    def test_nested_access_name(self):
        config = _root(None)
        name = config[5]['foo']['bar'][20].name()
        self.assertEqual(name, "root[5]['foo']['bar'][20]")

class MultipleSourceTest(unittest.TestCase):
    def test_dict_access_shadowed(self):
        config = _root({'foo': 'bar'}, {'foo': 'baz'})
        value = config['foo'].get()
        self.assertEqual(value, 'bar')

    def test_dict_access_fall_through(self):
        config = _root({'qux': 'bar'}, {'foo': 'baz'})
        value = config['foo'].get()
        self.assertEqual(value, 'baz')

    def test_dict_access_missing(self):
        config = _root({'qux': 'bar'}, {'foo': 'baz'})
        with self.assertRaises(confit.NotFoundError):
            config['fred'].get()

    def test_list_access_shadowed(self):
        config = _root(['a', 'b'], ['c', 'd', 'e'])
        value = config[1].get()
        self.assertEqual(value, 'b')

    def test_list_access_fall_through(self):
        config = _root(['a', 'b'], ['c', 'd', 'e'])
        value = config[2].get()
        self.assertEqual(value, 'e')

    def test_list_access_missing(self):
        config = _root(['a', 'b'], ['c', 'd', 'e'])
        with self.assertRaises(confit.NotFoundError):
            config[3].get()

    def test_access_dict_replaced(self):
        config = _root({'foo': {'bar': 'baz'}}, {'foo': {'qux': 'fred'}})
        value = config['foo'].get()
        self.assertEqual(value, {'bar': 'baz'})

    def test_access_dict_iteration_merged(self):
        config = _root({'foo': {'bar': 'baz'}}, {'foo': {'qux': 'fred'}})
        keys = list(config['foo'])
        self.assertEqual(set(keys), set(['bar', 'qux']))

    def test_access_dict_length_merged(self):
        config = _root({'foo': {'bar': 'baz'}}, {'foo': {'qux': 'fred'}})
        length = len(config['foo'])
        self.assertEqual(length, 2)

    def test_merged_dicts_iteration_not_duplicated(self):
        config = _root({'foo': {'bar': 'baz'}}, {'foo': {'bar': 'fred'}})
        value = list(config['foo'])
        self.assertEqual(value, ['bar'])

    def test_merged_dicts_length_not_duplicated(self):
        config = _root({'foo': {'bar': 'baz'}}, {'foo': {'bar': 'fred'}})
        length = len(config['foo'])
        self.assertEqual(length, 1)


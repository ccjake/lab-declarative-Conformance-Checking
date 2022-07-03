import unittest
#
#
# class MyTestCase(unittest.TestCase):
#     def test_something(self):
#         self.assertEqual(True, False)
#
#
# if __name__ == '__main__':
#     unittest.main()

model = {'equivalence': [('a', 'c'), ('b', 'c'), ('d', 'c'), ('e', 'a'), ('e', 'b'), ('e', 'c'), ('e', 'f'), ('f', 'c'), ('x', 'a'), ('x', 'b'), ('x', 'c'), ('x', 'e'), ('x', 'f')], 'always_after': [('a', 'c'), ('e', 'f'), ('x', 'e'), ('x', 'f')], 'always_before': [('d', 'c'), ('e', 'a'), ('e', 'b'), ('e', 'c'), ('f', 'c'), ('x', 'a'), ('x', 'b'), ('x', 'c')], 'never_together': [('d', 'x'), ('x', 'd')], 'directly_follows': [('e', 'f'), ('x', 'e')], 'activ_freq': {'a': '[0, 1]', 'b': '[0, 1]', 'c': '[1]', 'd': '[0, 1]', 'e': '[0, 1]', 'f': '[0, 1]', 'x': '[0, 1]'}}
import json
b = json.dumps(model)
f2 = open('aa.json','w')
f2.write(b)
f2.close()
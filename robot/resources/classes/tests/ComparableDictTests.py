from pathlib import Path
import sys

home = str(Path.home())
parentsDirectory = str(Path().resolve().parent.parent.parent)
sys.path.append(home + "/HSI/resources/classes/")

from ComparableDict import ComparableDict
import unittest


"""
Tests for ComparableDict.
"""


class ComparableDictTests(unittest.TestCase):

    def setUp(self):
        self.sqObj = ComparableDict()

    def tearDown(self):
        self.sqObj = None

    def test_ComparableDictEqual(self):
        '''
        Test whether one dictionary can compare and equal to another dict. 
        '''
        comparable_dict_A = ComparableDict({'id': 1140, 'priority' : 3})
        comparable_dict_B = comparable_dict_A

        self.assertEqual(comparable_dict_A, comparable_dict_B)

    def test_ComparableDictGreaterThan(self):
        '''
        Test whether one dictionary can compare and greater than another dict. 
        '''
        comparable_dict_A = ComparableDict({'id': 1140, 'priority' : 3})
        comparable_dict_B = ComparableDict({'id': 500, 'priority' : 3})

        self.assertGreater(comparable_dict_A, comparable_dict_B)

    def test_ComparableDictLessThan(self):
        '''
        Test whether one dictionary can compare and less than another dict. 
        '''
        comparable_dict_A = ComparableDict({'id': 500, 'priority' : 3})
        comparable_dict_B = ComparableDict({'id': 1140, 'priority' : 3})

        self.assertLess(comparable_dict_A, comparable_dict_B)

    def test_SetComparableDict(self):
        '''
        Test whether ComparableDict can set items. 
        '''
        comparable_dict_A = ComparableDict()
        comparable_dict_B = {'id': 500, 'priority' : 3, 'clientAddress' : '10.148.13.133'}

        for key, value in comparable_dict_B.items():
            comparable_dict_A[key] = value

        self.assertEqual(len(comparable_dict_A), len(comparable_dict_B))

    def test_DelComparableDict(self):
        '''
        Test whether ComparableDict can delete items.  
        '''
        comparable_dict_A = ComparableDict({'id': 500, 'priority' : 3, 'clientAddress' : '10.148.13.133'})
        original_dict_A_len = len(comparable_dict_A)
        comparable_dict_B = {'clientAddress' : '10.148.13.133'}

        for key in comparable_dict_B:
            del comparable_dict_A[key]

        self.assertEqual(len(comparable_dict_A), original_dict_A_len - len(comparable_dict_B))


if __name__ == '__main__':
    unittest.main()

from unittest import TestCase, main
from pdf_sorter import data_explorer

class TestDataExplorer(TestCase):

  TEST_EXTRACTED_DATA1 = [
    ['cat', 'name', '', 'tigger'],
    ['cat', 'name', '', 'pepper'],
    ['cat', 'name', '', 'salt'],
    ['cat', 'name', '', 'milo'],
    ['cat', 'name', '', 'lucy']
  ]

  TEST_EXTRACTED_DATA2 = [
    ['cat', 'name', '', 'tigger'],
    ['cat', 'name', '', 'pepper'],
    ['dog', 'height', '1m', '','weight','50lbs'],
    ['cat', 'color', 'tabby', '', 'name', '', 'salt'],
    ['cat', 'name', '', 'milo'],
    ['cat', 'name', '', 'lucy', 'age', '', 'kitten']
  ]

  def test_get_relative_indexes(self):
    test_index = 2
    test_list = ['a', 'b', 'c', 'd', 'e', 'f']
    expected_result = {
      -2: 'a',
      -1: 'b',
      0: 'c',
      1: 'd',
      2: 'e',
      3: 'f'
    }
    actual_result = data_explorer.get_relative_indexes_for_page(test_list, test_index)
    self.assertEqual(actual_result, expected_result)

  def test_get_relative_indexes_not_found(self):
    test_index = -1
    test_list = ['a', 'b', 'c', 'd', 'e', 'f']
    expected_result = {}
    actual_result = data_explorer.get_relative_indexes_for_page(test_list, test_index)
    self.assertEqual(actual_result, expected_result)
  
  def test_determine_indexes_relative_to_criteria(self):
    """ Case where document pages are identical in format """
    test_criteria = 'name'
    expected_result = {
      -1: ['cat', 'cat', 'cat', 'cat', 'cat'],
      0: ['name', 'name', 'name', 'name', 'name'],
      1: ['', '', '', '', ''],
      2: ['tigger', 'pepper', 'salt', 'milo', 'lucy']
    }
    actual_result = data_explorer.build_relative_index_matrix(self.TEST_EXTRACTED_DATA1, test_criteria)
    self.assertEqual(actual_result, expected_result)
  
  def test_determine_indexes_relative_to_criteria_not_all_match(self):
    """ Case where document pages are not identical in format """
    test_criteria = 'name'
    expected_result = {
      -4: ['', '', '', 'cat', '', ''],
      -3: ['', '', '', 'color', '', ''],
      -2: ['', '', '', 'tabby', '', ''],
      -1: ['cat', 'cat', '', '', 'cat', 'cat'],
      0: ['name', 'name', '', 'name', 'name', 'name'],
      1: ['', '', '', '', '', ''],
      2: ['tigger', 'pepper', '', 'salt', 'milo', 'lucy'],
      3: ['', '', '', '', '', 'age'],
      4: ['', '', '', '', '', ''],
      5: ['', '', '', '', '', 'kitten']
    }
    actual_result = data_explorer.build_relative_index_matrix(self.TEST_EXTRACTED_DATA2, test_criteria)
    self.assertEqual(actual_result, expected_result)

  def test_determine_indexes_relative_to_criteria_no_match(self):
    """ Case where criteria is not found in any document pages """
    test_criteria = 'dog'
    expected_result = {}
    actual_result = data_explorer.build_relative_index_matrix(self.TEST_EXTRACTED_DATA1, test_criteria)
    self.assertEqual(actual_result, expected_result)

if __name__ == '__main__':
    main()
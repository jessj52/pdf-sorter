from unittest import TestCase, main
from unittest.mock import patch, mock_open
from pdf_sorter import fs_helper
from textwrap import dedent

class TestFsHelper(TestCase):

  TEST_SORT_FILE = dedent("""
        Fee
        Fi
        Fo
        Fum
        """).strip()
  
  TEST_SORT_FILE_PATH = 'some-path'

  @patch("builtins.open", mock_open(read_data=TEST_SORT_FILE))
  def test_get_sort_list(self):
    """ Case where sort order is as found in file """
    sort_list = fs_helper.get_sort_list(self.TEST_SORT_FILE_PATH)
    expected_sort_list = ['Fee', 'Fi', 'Fo', 'Fum']
    self.assertEqual(sort_list, expected_sort_list)
  
  @patch("builtins.open", mock_open(read_data=TEST_SORT_FILE))
  def test_get_sort_list_reverse(self):
    """ Case where sort order is reversed from arg """
    sort_list = fs_helper.get_sort_list(self.TEST_SORT_FILE_PATH, True)
    expected_sort_list = ['Fum', 'Fo', 'Fi', 'Fee']
    self.assertEqual(sort_list, expected_sort_list)

if __name__ == '__main__':
    main()
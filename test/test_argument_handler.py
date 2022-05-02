import logging
from unittest import TestCase, main, mock
from unittest.mock import patch
from pdf_sorter  import argument_handler

class TestArgumentHandler(TestCase):

  EXISTS = 'existsyepyep'

  VALID_SORT_FILE =  EXISTS + '.txt'
  INVALID_SORT_FILE_EXTENSION = 'bad_extension.bla'
  INVALID_SORT_FILE_NOT_EXISTS = 'not_exists.txt'

  VALID_INPUT_PDF_FILE = EXISTS + '.pdf'
  INVALID_PDF_FILE_EXTENSION = 'bad_extension.bla'
  INVALID_INPUT_PDF_FILE_NOT_EXISTS = 'not_exists.pdf'

  VALID_OUTPUT_PDF_FILE = 'not_exists.pdf'
  INVALID_OUTPUT_PDF_FILE_EXISTS = EXISTS + '.pdf'

  VALID_CRITERIA = 'id'
  INVALID_CRITERIA = '99'

  VALID_INDEX = '10'
  INVALID_INDEX = '0'

  VALID_QUADRANT1 = '1'
  VALID_QUADRANT2 = ['1', '2', '3']
  VALID_QUADRANT3 = ['1', '2', '3', '4']
  INVALID_QUADRANT = ['5']

  VALID_DPI = '125'
  INVALID_DPI = '50'


  def mock_file_exists(self, arg):
    return self.EXISTS in arg
  

  def get_arg(self, key, value):
    if value is None:
      return []
    elif isinstance(value, list):
      return [key] + value
    else:
      return [key, value]
  
  def build_sys_args(self, short, sort, files, output, criteria, index = None, quadrant = None, dpi = None, flags = None):
    short_names = {
      'sort': '-s',
      'files': '-f',
      'output': '-o',
      'criteria': '-c',
      'index': '-i',
      'dpi': '-d',
      'quadrant': '-q'
    }
    long_names = {key: '--' + key for key in short_names.keys()}
    nameset = short_names if short else long_names

    index_arg = self.get_arg(nameset['index'], index)
    quadrant_arg = self.get_arg(nameset['quadrant'], quadrant)
    dpi_arg = self.get_arg(nameset['dpi'], dpi)
    settings = flags.split() if flags else []

    return [nameset['sort'], sort, nameset['files'], files, nameset['output'], output, nameset['criteria'], criteria] + index_arg + quadrant_arg + dpi_arg + settings

  def setUp(self):
    self.patcher = patch('pdf_sorter.argument_handler.os.path.exists')
    self.mock_os_path_exists = self.patcher.start()
    self.mock_os_path_exists.side_effect = self.mock_file_exists
  
  def tearDown(self):
    self.patcher.stop()

  
  """ Required Fields """

  def test_valid_arguments_required_short(self):
    args_short = self.build_sys_args(True, self.VALID_SORT_FILE, self.VALID_INPUT_PDF_FILE, self.VALID_OUTPUT_PDF_FILE, self.VALID_CRITERIA)
    actual = argument_handler.get_valid_arguments(args_short)
    
    self.assertEqual(actual.sort, self.VALID_SORT_FILE)
    self.assertEqual(actual.files, [self.VALID_INPUT_PDF_FILE])
    self.assertEqual(actual.output, './output/' + self.VALID_OUTPUT_PDF_FILE)
    self.assertEqual(actual.criteria, self.VALID_CRITERIA)
  
  def test_valid_arguments_required_long(self):
    args_long = self.build_sys_args(False, self.VALID_SORT_FILE, self.VALID_INPUT_PDF_FILE, self.VALID_OUTPUT_PDF_FILE, self.VALID_CRITERIA)
    actual = argument_handler.get_valid_arguments(args_long)
    
    self.assertEqual(actual.sort, self.VALID_SORT_FILE)
    self.assertEqual(actual.files, [self.VALID_INPUT_PDF_FILE])
    self.assertEqual(actual.output, './output/' + self.VALID_OUTPUT_PDF_FILE)
    self.assertEqual(actual.criteria, self.VALID_CRITERIA)

  """ Default values """

  def test_valid_arguments_defaults(self):
    test_args = self.build_sys_args(True, self.VALID_SORT_FILE, self.VALID_INPUT_PDF_FILE, self.VALID_OUTPUT_PDF_FILE, self.VALID_CRITERIA)
    actual = argument_handler.get_valid_arguments(test_args)

    self.assertEqual(actual.index, 1)
    self.assertEqual(actual.quadrant, [0])
    self.assertEqual(actual.dpi, 300)
    self.assertEqual(actual.reverse, False)
    self.assertEqual(actual.loglevel, logging.WARNING)
    self.assertEqual(actual.override, False)
    self.assertEqual(actual.multipage, False)
    self.assertEqual(actual.explore, False)

  """ Sort file tests """

  def test_invalid_sort_file_extension(self):
    test_args = self.build_sys_args(True, self.INVALID_SORT_FILE_EXTENSION, self.VALID_INPUT_PDF_FILE, self.VALID_OUTPUT_PDF_FILE, self.VALID_CRITERIA)

    with self.assertRaises(SystemExit):
      argument_handler.get_valid_arguments(test_args)
  
  def test_invalid_sort_file_not_exist(self):
    test_args = self.build_sys_args(True, self.INVALID_SORT_FILE_NOT_EXISTS, self.VALID_INPUT_PDF_FILE, self.VALID_OUTPUT_PDF_FILE, self.VALID_CRITERIA)

    with self.assertRaises(SystemExit):
      argument_handler.get_valid_arguments(test_args)

  """ Input file tests """

  def test_invalid_input_file_extension(self):
    test_args = self.build_sys_args(True, self.VALID_SORT_FILE, self.INVALID_PDF_FILE_EXTENSION, self.VALID_OUTPUT_PDF_FILE, self.VALID_CRITERIA)

    with self.assertRaises(SystemExit):
      argument_handler.get_valid_arguments(test_args)
  
  def test_invalid_input_file_not_exist(self):
    test_args = self.build_sys_args(True, self.VALID_SORT_FILE, self.INVALID_INPUT_PDF_FILE_NOT_EXISTS, self.VALID_OUTPUT_PDF_FILE, self.VALID_CRITERIA)

    with self.assertRaises(SystemExit):
      argument_handler.get_valid_arguments(test_args)

  """ Output file tests """

  def test_invalid_output_file_extension(self):
    test_args = self.build_sys_args(True, self.VALID_SORT_FILE, self.VALID_INPUT_PDF_FILE, self.INVALID_PDF_FILE_EXTENSION, self.VALID_CRITERIA)

    with self.assertRaises(SystemExit):
      argument_handler.get_valid_arguments(test_args)
  
  def test_invalid_output_file_exists(self):
    test_args = self.build_sys_args(True, self.VALID_SORT_FILE, self.VALID_INPUT_PDF_FILE, self.INVALID_OUTPUT_PDF_FILE_EXISTS, self.VALID_CRITERIA)

    with self.assertRaises(SystemExit):
      argument_handler.get_valid_arguments(test_args)
  
  def test_invalid_output_file_exists_with_override(self):
    test_args = self.build_sys_args(True, self.VALID_SORT_FILE, self.VALID_INPUT_PDF_FILE, self.INVALID_OUTPUT_PDF_FILE_EXISTS, self.VALID_CRITERIA, flags = '--override')

    with mock.patch('pdf_sorter.argument_handler.sys.argv', '--override'):
      actual = argument_handler.get_valid_arguments(test_args)
    
      self.assertEqual(actual.sort, self.VALID_SORT_FILE)
      self.assertEqual(actual.files, [self.VALID_INPUT_PDF_FILE])
      self.assertEqual(actual.output, './output/' + self.INVALID_OUTPUT_PDF_FILE_EXISTS)
      self.assertEqual(actual.criteria, self.VALID_CRITERIA)
      self.assertEqual(actual.override, True)

  """ Index value tests """

  def test_invalid_index(self):
    test_args = self.build_sys_args(True, self.VALID_SORT_FILE, self.VALID_INPUT_PDF_FILE, self.VALID_OUTPUT_PDF_FILE, self.VALID_CRITERIA, index = self.INVALID_INDEX)

    with self.assertRaises(SystemExit):
      argument_handler.get_valid_arguments(test_args)
  
  def test_valid_index_negative(self):
    test_args = self.build_sys_args(True, self.VALID_SORT_FILE, self.VALID_INPUT_PDF_FILE, self.VALID_OUTPUT_PDF_FILE, self.VALID_CRITERIA, index = '-10')
    actual = argument_handler.get_valid_arguments(test_args)

    self.assertEqual(actual.sort, self.VALID_SORT_FILE)
    self.assertEqual(actual.files, [self.VALID_INPUT_PDF_FILE])
    self.assertEqual(actual.output, './output/' + self.VALID_OUTPUT_PDF_FILE)
    self.assertEqual(actual.criteria, self.VALID_CRITERIA)
    self.assertEqual(actual.index, -10)

  """ DPI value tests """

  def test_valid_dpi(self):
    test_args = self.build_sys_args(True, self.VALID_SORT_FILE, self.VALID_INPUT_PDF_FILE, self.VALID_OUTPUT_PDF_FILE, self.VALID_CRITERIA, dpi = self.VALID_DPI)
    actual = argument_handler.get_valid_arguments(test_args)

    self.assertEqual(actual.dpi, int(self.VALID_DPI))
  
  def test_invalid_dpi(self):
    test_args = self.build_sys_args(True, self.VALID_SORT_FILE, self.VALID_INPUT_PDF_FILE, self.VALID_OUTPUT_PDF_FILE, self.VALID_CRITERIA, dpi = self.INVALID_DPI)

    with self.assertRaises(SystemExit):
      argument_handler.get_valid_arguments(test_args)

  """ Quadrant value tests """

  def test_valid_quadrant_one_value(self):
    test_args = self.build_sys_args(True, self.VALID_SORT_FILE, self.VALID_INPUT_PDF_FILE, self.VALID_OUTPUT_PDF_FILE, self.VALID_CRITERIA, quadrant = self.VALID_QUADRANT1)
    actual = argument_handler.get_valid_arguments(test_args)

    self.assertEqual(actual.quadrant, [1])
  
  def test_valid_quadrant_multi_value(self):
    test_args = self.build_sys_args(True, self.VALID_SORT_FILE, self.VALID_INPUT_PDF_FILE, self.VALID_OUTPUT_PDF_FILE, self.VALID_CRITERIA, quadrant = self.VALID_QUADRANT2)
    actual = argument_handler.get_valid_arguments(test_args)

    self.assertEqual(actual.quadrant, [1, 2, 3])
  
  def test_valid_quadrant_override(self):
    test_args = self.build_sys_args(True, self.VALID_SORT_FILE, self.VALID_INPUT_PDF_FILE, self.VALID_OUTPUT_PDF_FILE, self.VALID_CRITERIA, quadrant = self.VALID_QUADRANT3)
    actual = argument_handler.get_valid_arguments(test_args)

    self.assertEqual(actual.quadrant, [0])

  def test_invalid_quadrant(self):
    test_args = self.build_sys_args(True, self.VALID_SORT_FILE, self.VALID_INPUT_PDF_FILE, self.VALID_OUTPUT_PDF_FILE, self.VALID_CRITERIA, quadrant = self.INVALID_QUADRANT)

    with self.assertRaises(SystemExit):
      argument_handler.get_valid_arguments(test_args)

  """ Flag values """

  def test_flag_explore(self):
    test_args = self.build_sys_args(True, self.VALID_SORT_FILE, self.VALID_INPUT_PDF_FILE, self.VALID_OUTPUT_PDF_FILE, self.VALID_CRITERIA, flags = "--explore")
    actual = argument_handler.get_valid_arguments(test_args)

    self.assertEqual(actual.explore, True)
  
  def test_flag_multipage(self):
    test_args = self.build_sys_args(True, self.VALID_SORT_FILE, self.VALID_INPUT_PDF_FILE, self.VALID_OUTPUT_PDF_FILE, self.VALID_CRITERIA, flags = "--multipage")
    actual = argument_handler.get_valid_arguments(test_args)

    self.assertEqual(actual.multipage, True)
  
  def test_flag_reverse(self):
    test_args = self.build_sys_args(True, self.VALID_SORT_FILE, self.VALID_INPUT_PDF_FILE, self.VALID_OUTPUT_PDF_FILE, self.VALID_CRITERIA, flags = "--reverse")
    actual = argument_handler.get_valid_arguments(test_args)

    self.assertEqual(actual.reverse, True)
  
  def test_flag_debug(self):
    test_args = self.build_sys_args(True, self.VALID_SORT_FILE, self.VALID_INPUT_PDF_FILE, self.VALID_OUTPUT_PDF_FILE, self.VALID_CRITERIA, flags = "--debug")
    actual = argument_handler.get_valid_arguments(test_args)

    self.assertEqual(actual.loglevel, logging.DEBUG)
  
  def test_flag_verbose(self):
    test_args = self.build_sys_args(True, self.VALID_SORT_FILE, self.VALID_INPUT_PDF_FILE, self.VALID_OUTPUT_PDF_FILE, self.VALID_CRITERIA, flags = "--verbose")
    actual = argument_handler.get_valid_arguments(test_args)

    self.assertEqual(actual.loglevel, logging.INFO)

if __name__ == '__main__':
    main()


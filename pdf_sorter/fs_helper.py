from collections import Counter
import time
from PyPDF2 import PdfFileMerger, PdfFileReader
import os
import logging

logger = logging.getLogger('pdf_sorter')

def create_subdirectory_if_needed(subdirectory_path):
  check_folder = os.path.isdir(subdirectory_path)
  if not check_folder:
      logger.info("No subdirectory %s found. Creating." % subdirectory_path)
      os.makedirs(subdirectory_path)
  return './' + subdirectory_path + '/'

def get_sort_list(sort_filename,reverse = False):
  """ Extract sorted list of values from input, reverse if flag was provdied """
  sort_file = open(sort_filename, 'r')
  sorted_values = [line.strip() for line in sort_file]
    # Reverse the order so it prints in the order to place in the bins
  if reverse:
    logger.info("Reversing sort order")
    sorted_values.reverse()
  
  duplicated_values = [item for item, count in Counter(sorted_values).items() if count > 1]
  if len(duplicated_values) > 0:
    logger.warning("Found duplicated values in input sort list: %s. Pages with these values will be duplicated in sorted output file." % " ,".join(sorted_values))
  
  return sorted_values

def merge_documents(documents):
  """ Merge input pdf documents into single file based on original input order """
  merged_pdf_filename = "./output/_merged.pdf"
  merger = PdfFileMerger()
  (merger.append(PdfFileReader(open(doc), 'rb')) for doc in documents)
  merger.write(merged_pdf_filename)
  logger.info("Merged documents into file %s" % merged_pdf_filename)
  return merged_pdf_filename


class ColorLoggingFormatter(logging.Formatter):

  def __init__(self, logging_format): 

    end = "\x1b[0m"
    debug = "\x1b[36;20m" # grey background
    info = "\x1b[38;20m" #grey
    warning = "\x1b[33;20m" #yellow
    error = "\x1b[31;20m" #red
    critical = 	"\x1b[41m" #red background

    self.custom_level_format = {
      logging.DEBUG: debug + logging_format + end,
      logging.INFO: info + logging_format + end,
      logging.WARNING: warning + logging_format + end,
      logging.ERROR: error + logging_format + end,
      logging.CRITICAL: critical + logging_format + end
    }

  def format(self, record):
    level_format = self.custom_level_format.get(record.levelno)
    formatter = logging.Formatter(level_format)
    return formatter.format(record)



def setup_logging(explore, log_level):
  """ Log based on input setings. Logs print to console and save to file in /output/logs"""
  mode = 'explore' if explore else 'sort'
  print_format = '%(asctime)s.%(msecs)d %(levelname)s %(message)s'

  logging_subdirectory = 'output/logs'
  filename = str(time.time()) + '_' + mode + '.txt'
  logging_path = create_subdirectory_if_needed(logging_subdirectory) + filename
  logger = logging.getLogger('pdf_sorter')
  logger.setLevel(log_level)

  stream_logger = logging.StreamHandler()
  stream_logger.setFormatter(ColorLoggingFormatter(print_format))
  logger.addHandler(stream_logger)

  file_logger = logging.FileHandler(logging_path)
  file_logger.setFormatter(logging.Formatter(print_format))
  logger.addHandler(file_logger)
  

  
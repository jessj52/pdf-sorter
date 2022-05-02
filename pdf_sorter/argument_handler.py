from abc import abstractmethod
import argparse
import logging
import os
import sys
# from . fs_helper import create_subdirectory_if_needed
# from src import fs_helper
from pdf_sorter import fs_helper

logger = logging.getLogger('pdf_sorter')

class ArgumentValidator(argparse.Action):
    """
    Main argument validation base class.
    All input argument validators should extend ArgumentValidator
    """
    @abstractmethod
    def __call__(self, parser, namespace, values, option_string=None):
        pass


class SortValidator(ArgumentValidator):
    """
    Validates input for sorted list of values
    Flags: -s --sort
    Expect: .txt file type, file should exist
    """
    def __call__(self, parser, namespace, values, option_string=None):
        ext = os.path.splitext(values)[-1].lower()
        if ext != '.txt':
            raise argparse.ArgumentError(self,
                'Expected file with list of sorted values to be .txt. Instead receieved %s' % values)
        if not os.path.exists(values):
            raise argparse.ArgumentError(self, 'File %s not found' % (values))
        setattr(namespace, self.dest, values)


class FileValidator(ArgumentValidator):
    """
    Validates input for pdf file(s) to sort
    Flags: -f --files
    Expect: .pdf file type(s), file(s) should exist
    """
    def __call__(self, parser, namespace, values, option_string=None):
        files = []
        for i, file in enumerate(values):
            ext = os.path.splitext(file)[-1].lower()
            if ext != '.pdf':
                raise argparse.ArgumentError(self,'Expected all input files to be .pdf. Instead receieved %d input as %s' % (i, file))
            if not os.path.exists(file):
                raise argparse.ArgumentError(self, 'File %s not found' % file)
            files.append(file)
        setattr(namespace, self.dest, files)


class OutputValidator(ArgumentValidator):
    """
    Validates naming convention of output file
    Flags: -o --output
    Expect: .pdf file, cannot override file without --override flag
    """
    def __call__(self, parser, namespace, values, option_string=None):
        subdirectory = fs_helper.create_subdirectory_if_needed('output')
        file_path = subdirectory + values
        ext = os.path.splitext(values)[-1].lower()
        if ext != '.pdf':
            raise argparse.ArgumentError(self, 'Expected output file to be .pdf. Instead receieved %s' % values)
        if os.path.exists(file_path) and '--override' not in sys.argv:
            raise argparse.ArgumentError(self, 'Output file %s already exists in subdirectory %s. Please rename file or use --override flag to override output file.' % (values, subdirectory))
        setattr(namespace, self.dest, file_path)


class IndexValidator(ArgumentValidator):
    """
    Validates input for value index lookup
    Flags: -i --index
    Expect: cannot be the same index as lookup criteria (!=0)
    """
    def __call__(self, parser, namespace, values, option_string=None):
        if values == 0:
            raise argparse.ArgumentError(self,
                'Expected value index to be different than index of criteria key (i > criteria or criteria < i)')
        setattr(namespace, self.dest, values)


class QuadrantValidator(ArgumentValidator):
    """
    Validates input for parsing document pages into quadrants to improve processing times
    Flags: -q --quadrants
    Expect: quadrants are between 0-4; 0 indicates use whole page
    Modifications: ignore duplicates, ignore values out of range, override [1,2,3,4] with [0]
    """
    def __call__(self, parser, namespace, values, option_string=None):
        nvalues = len(values)
        quadrants = set()

        for quadrant in values:
            if quadrant < 0 or quadrant > 4:
                raise argparse.ArgumentError(self,
                "Invalid quadrant value. Expected a value between 0-4 but receievd %d" % quadrant)
            if quadrant in quadrants:
                logger.warning(
                    "Quadrant %d already listed. Ignorinig" % quadrant)
                continue
            if quadrant == 0 and nvalues > 1:
                logger.warning(
                    "Found 0 in list of quadrants. Defaulting to converting whole pages to text via OCR. To prevent this in the future, remove value 0 from list of quadrants" % quadrant)
                setattr(namespace, self.dest, [0])
                return
            quadrants.add(quadrant)

        if len(quadrants) == 4:
            setattr(namespace, self.dest, [0])
        else:
            setattr(namespace, self.dest, values)


class DPIValidator(ArgumentValidator):
    """
    Validates input for dots per inch
    Flags: -d --dpi
    Expect: minimum dpi of 100
    """
    def __call__(self, parser, namespace, values, option_string=None):
        if values < 100:
            raise argparse.ArgumentError(self,
                'Expected dpi value of at least 100. Instead receieved %s' % values)
        setattr(namespace, self.dest, values)

def get_valid_arguments(args):
    """
    Set up expected input arguments, and validation. Returns validated arguments.
    """
    parser = argparse.ArgumentParser(
        description='Re-sort image-based PDFs based on internal document values')

    parser.add_argument('-s', '--sort', action=SortValidator, type=str, required=True,
                        help='<Required> The new order to re-sort the document(s). Input is expected to be a newline delimeted textfile of expected values.')

    parser.add_argument('-f', '--files', nargs='+', action=FileValidator, type=str, required=True,
                        help='<Required> The original input file(s). Requires minimum 1 .pdf format file; program can merge multiple files together and then sort.')

    parser.add_argument('-o', '--output', action=OutputValidator, type=str, required=True,
                        help='<Required> The name of the output .pdf file to be created.')

    parser.add_argument('-c', '--criteria', action='store', type=str, required=True,
                        help='<Required> The criteria key to search within the document, eg. "Order"')

    parser.add_argument('-i', '--index', action=IndexValidator, type=int, required=False,
                        default=1,
                        help='Optional (default = 1): The index of the lookup value. Default is the index directly after the criteria key (+1). Can accept negative values')

    parser.add_argument('-q', '--quadrant', nargs='+', action=QuadrantValidator, type=int, required=False,
                        default=[0],
                        help='Optional (default = 0): Specify the quadrant (1,2,3 and/or 4) of each page convert to text and scan. Default is to convert the whole page, but providing quadrant(s) and narrowing the scope can decrease processing time.')

    parser.add_argument('-d', '--dpi', action=DPIValidator, type=int, required=False,
                        default=300,
                        help='Optional (default = 300): Dots per inch (dpi). Control the resolution of the image converted from the orignal PDF. Higher values will produce higher resolution images, which may improve character recognition but can increase processing times. Minimum value is 100.')
    
    parser.add_argument('--override', action='store_true', required=False,
                        help='[FLAG] Override the output file if a file of that name already exists.')
    
    parser.add_argument('--reverse', action='store_true', required=False,
                        help='[FLAG] Return the document in the reverse order of the list (useful for some printer setups)')
    
    parser.add_argument('--multipage', action='store_true', required=False,
                        help='[FLAG] Indicate that original document may have criteria values that can span multiple pages (eg. multi-page orders), but the value itself may not be included on every page. Including this flag to assume blank pages (without criteria found) are connected to the previous page. Excluding this flag means the blank pages will be excluded from the final document.')


    parser.add_argument('--explore', action='store_true', required=False,
                        help='[FLAG] Run in explore mode (-d=explore) to return OCR output. This is useful for determining parameters for -c and -i inputs.')
    
    parser.add_argument('--debug', action="store_const", required=False,
                        dest="loglevel",
                        const=logging.DEBUG,
                        default=logging.WARNING,
                        help='[FLAG] Include debug logs in logging output (lowest log level, captures all logs)')
    
    parser.add_argument('--verbose', action="store_const", required=False,
                        dest="loglevel",
                        const=logging.INFO,
                        default=logging.WARNING,
                        help='[FLAG] Include descriptive statements in logging output (excludes debug logging statements)')

    return parser.parse_args(args)

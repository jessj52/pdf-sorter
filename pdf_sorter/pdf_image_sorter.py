import logging
import pytesseract
from pdf2image import pdfinfo_from_path, convert_from_path
from PyPDF2 import PdfFileWriter, PdfFileReader
from pytesseract import Output
from typing import OrderedDict

logger = logging.getLogger('pdf_sorter')

def get_crop_height_ratio(quadrants):
  top = False
  bottom = False
  for quad in quadrants:
    if quad == 0:
      top, bottom = True, True
    elif quad == 1 or quad == 2:
      top = True
    elif quad == 3 or quad == 4:
      bottom = True
    else:
      logger.error("Unexpected quarant value %d. Scanning whole height of document instead." % quad)
      top, bottom = True, True
    
    return (0 if top else 0.5, 1 if bottom else 0.5)
  
def get_crop_width_ratio(quadrants):
  left = False
  right = False

  for quad in quadrants:
    if quad == 0:
      left, right = True, True
    elif quad == 1 or quad == 3:
      left = True
    elif quad == 2 or quad == 4:
      right = True
    else:
      logger.warning("Unexpected quarant value %d. Scanning whole width of document instead." % quad)
      left, right = True, True
    
    return (0 if left else 0.5, 1 if right else 0.5)


def convert_document_to_images(pdf_path, dpi, quadrants):
  page_count = pdfinfo_from_path(pdf_path)["Pages"]
  crop_height = get_crop_height_ratio(quadrants)
  crop_width = get_crop_width_ratio(quadrants)
  return (page.crop((page.width*crop_width[0], page.height*crop_height[0], page.width*crop_width[1], page.height*crop_height[1])) for page in convert_from_path(pdf_path,dpi=dpi, thread_count=page_count))


def extract_key_values_from_images(images, criteria_key, value_index, multi_page):
    """
    Returns a dict of extracted values mapped to their page number
    """
    logger.info("Extracting %s from images" % criteria_key)
    value_page_map = OrderedDict()
    previous_value = ''

    for page_index, page in enumerate(images):
        extracted_text = extract_text_from_image(page)
        
        if criteria_key in extracted_text:
            criteria_index = extracted_text.index(criteria_key)
            criteria_value = extracted_text[criteria_index + value_index]
            
            logger.info("%d: Extracted %s value %s from image" % (page_index, criteria_key, criteria_value))
            
            if value_page_map.get(criteria_value):
                logger.info("Found duplicate %s value %s, including page %d" % (criteria_key, criteria_value, page_index))
                value_page_map[criteria_value].append(page_index)
            
            else:
                value_page_map[criteria_value]= [page_index]
            previous_value = criteria_value
        
        elif not multi_page or page_index == 0:
          logger.warning("Could not find %s on page %d. Discarding page." % (criteria_key, page_index))
        
        elif multi_page:
            logger.info("Detected possible multi-page. Assuming page %d is connected to order %s" %
                  (page_index, previous_value))
            value_page_map[previous_value].append(page_index)
      
    return value_page_map


def generate_sorted_document(pdf_path, value_page_lookup, new_sort_list, output_filename): 
    """
    Sorts the original document(s) based on the provided sort list, and the map of values to
    page numbers scraped from the document. Saves the newly sorted file to '/output' directory
    """
    current_value_order = value_page_lookup.keys()
    
    logger.info("Current Order List:")
    logger.info(current_value_order)
    logger.info("Modified Order List:")
    logger.info(new_sort_list)

    if len(new_sort_list) != len(current_value_order):
        logger.warning("The number of criteria values in the sorted list doesn't match the PDF(s). Is that expected? PDF Order Count = %d; Text File Order Count = %d" % (
            len(current_value_order), len(new_sort_list)))

    with open(pdf_path, "rb") as original_pdf:
      unsorted_pdf_file = PdfFileReader(original_pdf)
      pdf_writer = PdfFileWriter()

      for value in new_sort_list:
          matched_pages = value_page_lookup.get(value)
          
          if matched_pages:
          
              for page_number in matched_pages:
                  pdf_writer.addPage(unsorted_pdf_file.getPage(page_number))
          
          else:
              logger.warning("Missing value # %s in PDF file" % (value))

      with open(output_filename, 'wb') as sorted_pdf_file:
          pdf_writer.write(sorted_pdf_file)
      
      sorted_pdf_file.close()
    original_pdf.close()

    logger.info("New sorted file created: %s" % (output_filename))


def extract_text_from_image(image):
    return pytesseract.image_to_data(image, lang='eng', output_type=Output.DICT).get('text')


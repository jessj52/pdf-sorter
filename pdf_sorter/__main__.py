import sys
from pdf_sorter import argument_handler
from pdf_sorter import data_explorer
from pdf_sorter import fs_helper
from pdf_sorter import pdf_image_sorter
import logging


def main(args):

    documents_to_sort = args.files
    sortable_list = args.sort
    output_filename = args.output
    dpi = args.dpi
    quadrant = args.quadrant
    criteria_key = args.criteria
    value_index = args.index
    reverse = args.reverse
    multi_page = args.multipage
    explore = args.explore
    loglevel = args.loglevel

    fs_helper.setup_logging(explore, loglevel)
    logger = logging.getLogger('pdf_sorter')

    logger.info("Hello! I'm going to re-sort %s because you asked me to!" % (documents_to_sort))

    pdf_path = (fs_helper.merge_documents(documents_to_sort) if len(documents_to_sort) > 1 else documents_to_sort[0])

    # Convert the original pdf(s) to a generator function
    document_as_images = pdf_image_sorter.convert_document_to_images(pdf_path, dpi, quadrant)

    if explore:
      logger.debug("Running in explore mode")
      extracted_text = [pdf_image_sorter.extract_text_from_image(image) for image in document_as_images]
      relative_indexes = data_explorer.build_relative_index_matrix(extracted_text, criteria_key)
      data_explorer.generate_explore_csv(relative_indexes)
      logger.info('Success! Data exploration complete.')
      exit(0)
    
    else:
      logger.debug("Running in sort mode")
      # Map of values from document to page index
      value_page_lookup = pdf_image_sorter.extract_key_values_from_images(document_as_images, criteria_key, value_index, multi_page)

      # Get the new order to sort by (based on the route)
      sorted_list_of_values = fs_helper.get_sort_list(sortable_list, reverse)

      pdf_image_sorter.generate_sorted_document(pdf_path, value_page_lookup, sorted_list_of_values, output_filename)

      logger.info("Success! Document sorting complete.")
      exit(0)


if __name__ == "__main__":
  args = argument_handler.get_valid_arguments(sys.argv[1:])
  main(args)







    

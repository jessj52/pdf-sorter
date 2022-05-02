import csv
import logging
import time

logger = logging.getLogger('pdf_sorter')

def build_relative_index_matrix(extracted_text_pages, criteria_key):
    """
    Builds a matrix of positional indexes for all document pages relative
    to the index of the criteria key.
    * Output is a dict of N keys, where N is the max number of text values
        scraped from a single document page
    * Each key maps to an array of values of length K, where K is the number of pages
        in document. Values of the array are the item found in that position,
        on that page
    * If criteria key is not found on page, all values for that page are an empty string ""
    * Index of criteria key is 0
    * Items found in page before criteria key are negative indexed relative
        to criteria key
    """
    all_relative_indexes = {}

    for page_index, page_text in enumerate(extracted_text_pages):
        criteria_index = -1
        for t, text in enumerate(page_text):
            if text == criteria_key:
                criteria_index = t
                break

        relative_index = get_relative_indexes_for_page(page_text, criteria_index)

        for index in relative_index:
            if index in all_relative_indexes:
                all_relative_indexes[index].append(relative_index[index])
            else:
                all_relative_indexes[index] = [""]*page_index
                all_relative_indexes[index].append(relative_index[index])

        empty_indexes = [key for key in all_relative_indexes if key not in relative_index]
        for empty in empty_indexes:
            all_relative_indexes[empty].append("")
            
    return all_relative_indexes

        
def get_relative_indexes_for_page(page_text, criteria_index):
    """
    Determines position of values from a single scraped
    document page relative to the index of the criteria key.
    Output considers new index for criteria position to be 0,
    items in list before this position are negative indexed.
    """
    relative_indexes = {}
    if criteria_index == -1:
        logger.debug("Criteria not found on page (criteria_index = -1)")
        return relative_indexes
    index = -criteria_index if criteria_index > 0 else 0

    for value in page_text:
        relative_indexes[index] = value
        index += 1
    
    return relative_indexes

def generate_explore_csv(relative_indexes):
    """ 
    Builds CSV based on scraped data from documents. File is saved to output/data.
    Left-most column is relative index (-x > criteria index < +y). Each column
    represents page in document.
    """
    indexes = relative_indexes.keys()
    headers = ['Relative Index'] + ['Page ' + str(i) for i in range(1, len(relative_indexes[0])+1)]
    min_index = min(indexes)
    max_index = max(indexes)
    curr_index = min_index

    curr_time = time.time()
    explore_file = ('./output/data/pdf_sorter_explore_data_%d.csv' % curr_time)
    with open(explore_file, 'w') as explore_data:
        writer = csv.writer(explore_data)
        writer.writerow(headers)
        while curr_index <= max_index:
            row = [curr_index] + relative_indexes[curr_index]
            writer.writerow(row)
            curr_index += 1
    explore_data.close()
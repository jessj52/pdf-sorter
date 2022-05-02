# pdf-sorter

This is a dockerized python project that allows you to sort non-searchable/image-based PDF files based on criteria found within the document pages. `pdf_sorter` first converts document pages to images, then extracts text from the images using pytesseract (a python wrapper for the Tesseract OCR Engine). `pdf_sorter` was originally written to sort an exported WooCommerce Packing List based on the delivery order determined by routing software (Routific), but has since been expanded to be more agnostic. You can run `python3 -m pdf_sorter -h` to see the required inputs and available settings, or read more below.

Check out `/example_files` for some sample input and output files.

Argument | Type | Default | Description
--- | --- | --- | ---
| -s / --sort | Required | | Path to the file containing the new sort order (.txt) |
| -f / --files | Required | | Path to the file(s) to be sorted. Can include multiple PDF files, which will be merged in the order provided (.pdf) |
| -o / --output | Required | | Name of the final output file. This will be saved to ./output (.pdf). If you wish to overwrite an existing output file with the same name include the `--override` flag |
| -c / --criteria | Required | | Criteria key to search in document pages (eg. "Order"). If the key is not found on the page, a page will be discarded unless flag `--multiflag` is provided |
| -i / --index | Optional | 1 | Position of the sort value relative to criteria key provided by `c`. If you are unsure, you can run the program in `--explore` mode to generate a CSV with the relative index of the scraped text strings to the criteria key |
| -d / --dpi | Optional | 300 | Dots per inch. Used to toggle the resolution of the images converted from document pages. Higher values will increase CPU usage, but lower values may distort the image output such that OCR is less reliable and provides faulty outputs. Minimum 100 dpi required |
| -q / --quadrant | Optional | 0 | Allows user to crop the generated images to decrease processing times. This is most useful when the criteria key is found in the same region of the document on all pages. User can inlcude 1 or multiple quadrants: where `0 = whole page; 1 = NW; 2= NE; 3 = SW; 4 = SE` |
| --override | Flag | False | Override existing an existing output file with the same name. Output files save to `./output` |
| --reverse | Flag | False | Save the final sorted PDF in the reverse order provided in the original `--sort` list. This is useful for some printer setups |
| --multipage | Flag | False | If a criteria key is not found on a given document page, assume this page is associated with the criteria value from the previous page (eg. an Order page that spans multiple pages where the Order is only indicated on the first page) |
| --explore | Flag | False | Used to generate a CSV output of the relative position of page values to the criteria for each page. This mode does not produce a sorted output, but instead saves the scraped values to a csv output in `./output/data` |
| --debug / --verbose | Flag | Warning | Toggle the loglevel of the program. `--debug` is lowest and will capture all logs, whereas `--verbose` captures the next level. Logs are printed to terminal and also saved to `./output/logs` | 


## Steps to run locally:

`pdf_sorter` can be run in a docker container with the following steps:

1. Build local docker image `docker build -t sort_pdf .`
1. Run pdf_sorter a docker container using the above image with `./sort-pdfs-by-input-value.sh` and passing in the appropriate arguments, eg. `./sort-pdfs-by-input-value.sh -s ./example_files/SortedList.txt -f ./example_files/Example.pdf --c "Color:" -o Example_Output.pdf`

## Run Tests

Run `python3 -m unitttest disover test`



FROM python:3.9

COPY . ./
WORKDIR ./

RUN apt-get update && apt-get -y install \
    libleptonica-dev python3-pil tesseract-ocr libtesseract-dev tesseract-ocr-eng tesseract-ocr-script-latn poppler-utils

RUN pip3 install -r requirements.txt

ENV PYTHONPATH ./pdf_sorter

ENTRYPOINT ["python3", "-m", "pdf_sorter"]
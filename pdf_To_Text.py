#!/usr/bin/env python

# Extracting Text from a PDF file
# Using the pdfminer library, extracts text directly PDF if PDF allows direct text extraction
# If this fails, indirectly uses Tesseract's OCR library to extract text

import os
import sys
import subprocess
from wand.image import Image
from PIL import Image as PI
from pytesseract import image_to_string
from pyPdf import PdfFileReader
from datetime import datetime

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO

def extract_Text_Directly(file_name):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'ascii'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = file(file_name, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue().strip()

    fp.close()
    device.close()
    retstr.close()
    return text


def extract_Using_OCR(file_name):
    # file_name = 'Math20250_HW1.pdf'
    output_file = 'output'
    image_pdf = Image(filename='./' + file_name, resolution=300)
    if (image_pdf.format != 'PDF'):
        print "Not a PDF document."
        return ""
    else:
        pdf = PdfFileReader(open(file_name,'rb'))
        num_pages = pdf.getNumPages()
        # convert PDF to jpegs(s)
        image_jpeg = image_pdf.convert('jpeg')
        image_jpeg.save(filename=output_file + '.jpeg')
        text = ""
        # read in text from the jpeg(s)
        if num_pages == 1:
            temp_file_name = output_file + '.jpeg'
            text += image_to_string(PI.open(temp_file_name))
            removeFile(temp_file_name)
        else:
            for i in range(0, num_pages):
                temp_file_name = output_file + '-' + str(i) + '.jpeg'
                text += image_to_string(PI.open(temp_file_name))
                removeFile(temp_file_name)
        return text.strip()


def removeFile(file_name):
    command = 'rm ' + file_name
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    # print output, error


def valid_Extension(file_name):
    extension = file_name.split('.')[-1] if '.' in file_name else None
    return extension != None and extension.lower() == 'pdf'


if __name__ == '__main__':
    # working only in utf-8 encoding to avoid conversion/writing errors with ascii
    reload(sys)
    sys.setdefaultencoding('utf8')

    startTime = datetime.now()
    result = ""
    num_args = len(sys.argv)
    if num_args > 1 and os.path.isfile(sys.argv[1]):
        if valid_Extension(sys.argv[1]):
            try:
                result = extract_Text_Directly(sys.argv[1])
                if result == "":
                    result = extract_Using_OCR(sys.argv[1])
            except:
                result = extract_Using_OCR(sys.argv[1])
        else:
            print "Not a PDF document."
            sys.exit()
    else:
        print "Usage: python pdf_To_Text pdf_file.pdf [output_file]"
        sys.exit()

    # result = result.encode('utf-8')
    if (num_args > 2):
        try:
            with open(sys.argv[2], 'w') as output_file:
                print "Printing to file: %s" % sys.argv[2]
                output_file.write(result)
        except:
            print "Output File error"
            print result + '\n'
    else:
        print result + '\n'

    print "Took %f seconds to complete" % float((datetime.now() - startTime).total_seconds())

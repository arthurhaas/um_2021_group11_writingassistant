# pdf
import PyPDF2
from io import StringIO
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
# default
import os
import errno
from configparser import ConfigParser, NoSectionError
# nlp
from nltk.tokenize import sent_tokenize, word_tokenize, wordpunct_tokenize
import string


# file paths
FOLDER_INPUT = "original"
FOLDER_OUTPUT = "processed"
FILE_TMP = "tmp.pdf"

# define config for each file
DOC_CONFIG = dict()
DOC_CONFIG[1] = {"page_start":2, "page_end":10}
DOC_CONFIG[2] = {"page_start":3, "page_end":35}
DOC_CONFIG[3] = {"page_start":1, "page_end":8, "skip_until_string":"Abstract"}
DOC_CONFIG[4] = {"page_start":4, "page_end":74}
DOC_CONFIG[5] = {"page_start":2, "page_end":15}


def extract_pages(filepath, page_start, page_end, tmp_path):
    reader = PyPDF2.PdfFileReader(filepath)
    writer = PyPDF2.PdfFileWriter()
    for page in range( max(0,page_start-1), page_end):
        writer.addPage(reader.getPage(page))
    
    with open(tmp_path, 'wb') as output:
        writer.write(output)


def extract_text(filepath):
    from io import StringIO

    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams
    from pdfminer.pdfdocument import PDFDocument
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.pdfpage import PDFPage
    from pdfminer.pdfparser import PDFParser

    output_string = StringIO()
    with open(filepath, 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)
    return output_string.getvalue()

def clean_raw_text(raw_text):
    # replace new line inside a word to concat word parts split over lines
    clean = raw_text.replace("-\n", "")
    # split text into paragraphs based on multiple line breaks
    clean = clean.split("\n\n")
    # remove remaining new line tokens
    clean = [paragraph.replace("\n", " ") for paragraph in clean]
    # remove very short paragraphs indicating not containing sentences, but page numbers, sections titles, ...
    clean = [paragraph for paragraph in clean if (len([word for word in word_tokenize(paragraph) if not word in string.punctuation]) > 3)]

    return clean

def skip_strings(text, skip_until_string):
    pos_delete_until = text.find(skip_until_string)
    print(f".. removing {pos_delete_until} characters until the skipped string.")
    return text[pos_delete_until:]

def export_file(data, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as fp:
        for paragraph in data:
            fp.write(f"{paragraph}\n")

def silentremove(filename):
    """
    credits:
    https://stackoverflow.com/questions/10840533/most-pythonic-way-to-delete-a-file-which-may-not-exist
    """
    try:
        os.remove(filename)
    except OSError as e:
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occurred

def get_config(filename):
    # open config file
    config = ConfigParser()
    config.read('config.ini')

    # for file in original try finding file in config
    #   and getting all three values (fallback None)

    try:
        page_start = config.getint(filename, "page_start")
        page_end = config.getint(filename, "page_end")
        skip_until_string = config.get(filename, "skip_until_string", fallback=None)
    except NoSectionError:
        # except create section with keys
        config.add_section(filename)
        config.set(filename, 'page_start', "")
        config.set(filename, 'page_end', "")
        raise NameError(f"ERROR: No config for {filename} found in config.ini. Was created. Please, define configuration values.") 
    except ValueError:
        raise NameError(f"ERROR: No configuration values for {filename} found in config.ini") 
    finally:
        config_sorted = sort_config(config)
        with open('config.ini', 'w') as f:
            config_sorted.write(f)
    
    return (page_start, page_end, skip_until_string)

def sort_config(config):
    sections = config.sections()
    sections.sort()

    config_sorted = ConfigParser()
    for section in sections:
        config_sorted.add_section(section)
        for key,value in config[section].items():
            config_sorted.set(section, key, value)
    return config_sorted
    

if __name__ == "__main__":

    docs = []
    for f in os.listdir(FOLDER_INPUT):
        filepath = os.path.join(FOLDER_INPUT,f)
        if os.path.isfile(filepath) and f.endswith(".pdf"):
            docs.append(f)
    print(f"Start processing {len(docs)} files.")

    # split doc and save into temporary file
    for i, doc_name in enumerate(docs):
        print(f"{i+1}/{len(docs)} - {doc_name}")
        try:
            (page_start, page_end, skip_until_string) = get_config(doc_name)
        except NameError as e:
            print(e)
            continue
        #page_start = config["page_start"]
        #page_end = config["page_end"]
        #skip_until_string = config.get("skip_until_string")
        print(f"..Reading from page {page_start} to {page_end}.{f' Skipping text until string: {skip_until_string}' if skip_until_string else ''}")
        
        try:
            tmp_path_doc_extracted = os.path.join(FILE_TMP)
            extract_pages(os.path.join(FOLDER_INPUT, doc_name), page_start, page_end, tmp_path_doc_extracted)
            output_string = extract_text(tmp_path_doc_extracted)
            if skip_until_string:
                output_string = skip_strings(output_string, skip_until_string)
            cleaned_string = clean_raw_text(output_string)
            export_file(cleaned_string, os.path.join(FOLDER_OUTPUT, doc_name.replace(".pdf", ".txt")))
        except Exception as e:
            raise e
        finally:
            # in any case, remove temporary file
            silentremove(tmp_path_doc_extracted)
    
    print("done")
